#!/usr/bin/env python3
"""Single source of truth for resume content: data/resume.json.

- `python3 scripts/gen_resume.py` regenerates the <!-- RESUME:START -->
  block in site/resume.html from data/resume.json. Wired into
  .githooks/pre-commit (via `make sync`) so resume.html can't drift from
  the JSON.
- `python3 scripts/gen_resume.py --text` prints a plain-text version
  (links as "text (url)") to stdout, meant for copy-pasting into
  LinkedIn or anywhere else that doesn't take HTML — one source, two
  outputs, no separately hand-maintained LinkedIn copy.

The dcurves download count placeholder this writes is a static "72k+";
update-dcurves-downloads.sh (run right after this in the pre-commit
hook / `make sync`) overwrites it with the live figure by targeting the
same `dcurves-downloads` CSS class, so ordering matters but content
doesn't need to be re-fetched here.
"""
import argparse
import json
import pathlib
import re
import urllib.request

try:
    from lib_resume import render_html, render_text, DCURVES_PLACEHOLDER_TEXT
except ImportError:
    from scripts.lib_resume import render_html, render_text, DCURVES_PLACEHOLDER_TEXT

MARKER_RE = re.compile(r"<!-- RESUME:START -->.*?<!-- RESUME:END -->", re.DOTALL)


def load_data(repo_root: pathlib.Path) -> dict:
    return json.loads((repo_root / "data" / "resume.json").read_text())


def _experience_html(e: dict) -> str:
    # Each bullet is its own <div> (not a <ul>/<li>) with a literal "- "
    # text prefix rather than a CSS list marker, matching LinkedIn's own
    # dash convention on copy/paste. A blank-line gap between bullets can't
    # be done with CSS margin — margin is layout, not text, so it never
    # survives copy/paste. A zero-height spacer div doesn't work either:
    # browsers use a rendering-aware algorithm for copy (like innerText),
    # which skips content with no visible height. So each pair of bullets
    # gets a spacer div with a small but real, visibly rendered height (see
    # .bullet-break in the page's <style>) — a little more breathing room
    # on the page itself, traded for a real blank line surviving paste.
    parts = []
    for i, b in enumerate(e["bullets"]):
        if i > 0:
            parts.append('    <div class="bullet-break">&nbsp;</div>')
        parts.append(f'    <div class="bullet">- {render_html(b)}</div>')
    bullets = "\n".join(parts)
    return (
        '<div class="entry">\n'
        '  <div class="entry-head">\n'
        f'    <div class="entry-head-title"><span class="entry-title">{render_html(e["title"])}</span> — <span class="entry-org">{render_html(e["org"])}</span></div>\n'
        f'    <div class="entry-meta">{render_html(e["meta"])}</div>\n'
        "  </div>\n"
        '  <div class="bullets">\n'
        f"{bullets}\n"
        "  </div>\n"
        "</div>"
    )


def _project_html(p: dict) -> str:
    return (
        '<div class="entry projects">\n'
        f'  <div class="entry-title">{render_html(p["title"])}</div>\n'
        f'  <div class="entry-sub">{render_html(p["sub"])}</div>\n'
        "</div>"
    )


def _education_html(ed: dict) -> str:
    sub = f'\n  <div class="entry-sub">{render_html(ed["sub"])}</div>' if ed.get("sub") else ""
    return (
        '<div class="entry">\n'
        '  <div class="entry-head">\n'
        f'    <div class="entry-title">{render_html(ed["title"])}</div>\n'
        f'    <div class="entry-meta">{render_html(ed["meta"])}</div>\n'
        "  </div>" + sub + "\n"
        "</div>"
    )


def build_html_block(data: dict) -> str:
    contact = "\n".join(f"    <span>{render_html(c)}</span>" for c in data["contact"])
    experience = "\n\n".join(_experience_html(e) for e in data["experience"])
    projects = "\n".join(_project_html(p) for p in data["projects"])
    education = "\n".join(_education_html(ed) for ed in data["education"])
    skills = "\n".join(
        f"  <dt>{render_html(label)}</dt><dd>{render_html(value)}</dd>"
        for label, value in data["skills"].items()
    )

    body = f"""<div class="print-note">To save as PDF: File → Print → Save as PDF. For a clean copy (no date/title/page-number strip), open "More settings" in the print dialog and uncheck "Headers and footers".</div>

<header class="resume-header">
  <h1>{render_html(data["name"])}</h1>
  <div class="contact">
{contact}
  </div>
</header>

<h2 class="section">Experience</h2>

{experience}

<h2 class="section">Selected Projects</h2>

{projects}

<h2 class="section">Education</h2>

{education}

<h2 class="section">Skills &amp; Certifications</h2>

<dl class="skills-grid">
{skills}
</dl>"""

    return f"<!-- RESUME:START -->\n{body}\n<!-- RESUME:END -->"


def sync(repo_root: pathlib.Path) -> bool:
    resume_path = repo_root / "site" / "resume.html"
    text = resume_path.read_text()
    if not MARKER_RE.search(text):
        return False
    block = build_html_block(load_data(repo_root))
    new_text = MARKER_RE.sub(block, text)
    if new_text != text:
        resume_path.write_text(new_text)
        return True
    return False


def fetch_live_dcurves_label() -> str | None:
    """Best-effort live count for --text output; None if the network call fails."""
    url = (
        "https://static.pepy.tech/personalized-badge/dcurves"
        "?period=total&units=none&left_color=grey&right_color=blue&left_text=downloads"
    )
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            svg = resp.read().decode()
        matches = re.findall(r">([0-9,]+)<", svg)
        if not matches:
            return None
        count = int(matches[-1].replace(",", ""))
        return f"{count // 1000}k+"
    except Exception:
        return None


def render_plaintext(data: dict) -> str:
    lines = [data["name"], " | ".join(render_text(c) for c in data["contact"]), ""]

    lines.append("EXPERIENCE")
    lines.append("")
    for e in data["experience"]:
        lines.append(f'{render_text(e["title"])} — {render_text(e["org"])}')
        lines.append(render_text(e["meta"]))
        for b in e["bullets"]:
            lines.append(f"- {render_text(b)}")
        lines.append("")

    lines.append("SELECTED PROJECTS")
    lines.append("")
    for p in data["projects"]:
        lines.append(render_text(p["title"]))
        lines.append(render_text(p["sub"]))
        lines.append("")

    lines.append("EDUCATION")
    lines.append("")
    for ed in data["education"]:
        lines.append(f'{render_text(ed["title"])} ({render_text(ed["meta"])})')
        if ed.get("sub"):
            lines.append(render_text(ed["sub"]))
        lines.append("")

    lines.append("SKILLS & CERTIFICATIONS")
    lines.append("")
    for label, value in data["skills"].items():
        lines.append(f"{label}: {render_text(value)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true", help="print a plain-text version instead of writing resume.html")
    args = parser.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parent.parent
    data = load_data(repo_root)

    if args.text:
        text = render_plaintext(data)
        live_label = fetch_live_dcurves_label()
        if live_label:
            text = text.replace(DCURVES_PLACEHOLDER_TEXT, live_label)
        print(text)
        return

    if sync(repo_root):
        print("updated site/resume.html from data/resume.json")
    else:
        print("resume already in sync")


if __name__ == "__main__":
    main()
