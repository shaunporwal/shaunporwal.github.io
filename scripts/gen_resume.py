#!/usr/bin/env python3
"""Renders the resume from data/experiences.json, the single experience record.

Only the items whose `resume` switch is set reach the resume (see
lib_record.py). The record itself is rendered by gen_record.py.

- `python3 scripts/gen_resume.py` regenerates the <!-- RESUME:START -->
  block in site/resume.html. Wired into .githooks/pre-commit (via
  `make sync`) so resume.html can't drift from the record.
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
import html
import pathlib
import re
import urllib.request

from lib_blocks import sync_block, wrap
from lib_record import load_record, resume_view
from lib_resume import DCURVES_PLACEHOLDER_TEXT, render_html, render_text
from lib_site import REPO_ROOT, load_pages, load_site, pdf_of


def load_data(repo_root: pathlib.Path) -> dict:
    """The resume view of the record: {name, contact, experience, projects, education, skills}."""
    return resume_view(load_record(repo_root), load_site(repo_root))


def _bullets_html(bullets: list[str]) -> str:
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
    for i, b in enumerate(bullets):
        if i > 0:
            parts.append('    <div class="bullet-break">&nbsp;</div>')
        parts.append(f'    <div class="bullet">- {render_html(b)}</div>')
    return "\n".join(parts)


def _when_where_html(item: dict) -> str:
    # The dot is a literal separator, so a copy of the page keeps "date · place". The
    # stylesheet hides it where the date and the place sit on separate lines.
    return (
        '<div class="entry-meta">'
        f'<span class="entry-period">{render_html(item["period"])}</span>'
        '<span class="sep"> · </span>'
        f'<span class="entry-place">{render_html(item["place"])}</span></div>'
    )


def _title_org_html(e: dict) -> str:
    return (
        '<div class="entry-head-title">'
        f'<span class="entry-title">{render_html(e["title"])}</span>'
        '<span class="sep"> — </span>'
        f'<span class="entry-org">{render_html(e["org"])}</span></div>'
    )


def _experience_html(e: dict) -> str:
    return (
        '<div class="entry">\n'
        '  <div class="entry-head">\n'
        f"    {_title_org_html(e)}\n"
        f"    {_when_where_html(e)}\n"
        "  </div>\n"
        '  <div class="bullets">\n'
        f"{_bullets_html(e['bullets'])}\n"
        "  </div>\n"
        "</div>"
    )


def _project_html(p: dict) -> str:
    # Title + links share a row (same entry-head pattern as experience/
    # education), so the link never drifts onto its own separate line below
    # the project name; the description carries the "what it does" impact.
    return (
        '<div class="entry projects">\n'
        '  <div class="entry-head">\n'
        f'    <div class="entry-title">{render_html(p["title"])}</div>\n'
        f'    <div class="entry-meta">{render_html(p["links"])}</div>\n'
        "  </div>\n"
        f'  <div class="entry-sub">{render_html(p["description"])}</div>\n'
        "</div>"
    )


def _education_html(ed: dict) -> str:
    # Degree + dates/location share a row; school name is its own line below
    # rather than joined inline with the degree, so a long school name can
    # never push the dates onto their own separate line (the failure mode
    # this replaced — see PR doc Tier 12 for before/after).
    sub = f'\n  <div class="entry-sub">{render_html(ed["sub"])}</div>' if ed.get("sub") else ""
    return (
        '<div class="entry">\n'
        '  <div class="entry-head">\n'
        f'    <div class="entry-title">{render_html(ed["degree"])}</div>\n'
        f"    {_when_where_html(ed)}\n"
        "  </div>\n"
        f'  <div class="entry-sub">{render_html(ed["school"])}</div>' + sub + "\n"
        "</div>"
    )


RESUME_FILE = "resume.html"


def pdf_link(pages: list[dict], site: dict) -> dict:
    """The PDF the resume links to: its name from data/pages.json, and the file name a download gets."""
    person = site["name"].replace(" ", "-")
    return {"href": pdf_of(pages, RESUME_FILE), "filename": f"{person}-Resume.pdf"}


def _actions_html(pdf: dict) -> str:
    href, filename = html.escape(pdf["href"]), html.escape(pdf["filename"])
    button = f'<a class="btn btn-primary" href="{href}" download="{filename}">Download PDF</a>'
    return f'  <div class="btn-row resume-actions">\n    {button}\n  </div>\n'


def _header_html(data: dict, pdf: dict) -> str:
    contact = "\n".join(f"    <span>{render_html(c)}</span>" for c in data["contact"])
    return (
        '<header class="resume-header">\n'
        f'  <h1 class="title">{render_html(data["name"])}</h1>\n'
        '  <div class="contact">\n'
        f"{contact}\n"
        "  </div>\n"
        f"{_actions_html(pdf)}"
        "</header>"
    )


def _skills_html(skills: dict) -> str:
    rows = "\n".join(
        f"  <dt>{render_html(label)}</dt><dd>{render_html(value)}</dd>" for label, value in skills.items()
    )
    return f'<dl class="skills-grid">\n{rows}\n</dl>'


def _section_html(heading: str, content: str, long: bool = False) -> str:
    """Wraps a heading and its content so the print stylesheet can keep a short
    section on one page. Only a long section (Experience) may span pages."""
    css_class = "resume-section resume-section-long" if long else "resume-section"
    return f'<section class="{css_class}">\n<h2 class="resume-heading">{heading}</h2>\n\n{content}\n</section>'


def build_html_block(data: dict, pdf: dict) -> str:
    sections = [
        _section_html("Experience", "\n\n".join(_experience_html(e) for e in data["experience"]), long=True),
        _section_html("Selected Projects", "\n".join(_project_html(p) for p in data["projects"])),
        _section_html("Education", "\n".join(_education_html(ed) for ed in data["education"])),
        _section_html("Skills &amp; Certifications", _skills_html(data["skills"])),
    ]
    body = "\n\n".join([_header_html(data, pdf), *sections])
    return wrap("RESUME", body)


def sync(repo_root: pathlib.Path) -> bool:
    pdf = pdf_link(load_pages(repo_root), load_site(repo_root))
    return sync_block(repo_root / "site" / RESUME_FILE, "RESUME", build_html_block(load_data(repo_root), pdf))


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


def _experience_text(e: dict) -> list[str]:
    head = [f'{render_text(e["title"])} — {render_text(e["org"])}', render_text(e["meta"])]
    return head + [f"- {render_text(b)}" for b in e["bullets"]] + [""]


def _project_text(p: dict) -> list[str]:
    return [render_text(p["title"]), render_text(p["links"]), render_text(p["description"]), ""]


def _education_text(ed: dict) -> list[str]:
    sub = [render_text(ed["sub"])] if ed.get("sub") else []
    return [f'{render_text(ed["degree"])} ({render_text(ed["meta"])})', render_text(ed["school"]), *sub, ""]


PLAINTEXT_SECTIONS = (
    ("EXPERIENCE", "experience", _experience_text),
    ("SELECTED PROJECTS", "projects", _project_text),
    ("EDUCATION", "education", _education_text),
)


def render_plaintext(data: dict) -> str:
    lines = [data["name"], " | ".join(render_text(c) for c in data["contact"]), ""]
    for heading, key, render in PLAINTEXT_SECTIONS:
        lines += [heading, ""] + [line for item in data[key] for line in render(item)]
    lines += ["SKILLS & CERTIFICATIONS", ""]
    lines += [f"{label}: {render_text(value)}" for label, value in data["skills"].items()]
    return "\n".join(lines)


def plaintext_with_live_count(data: dict) -> str:
    text = render_plaintext(data)
    live_label = fetch_live_dcurves_label()
    return text.replace(DCURVES_PLACEHOLDER_TEXT, live_label) if live_label else text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true", help="print a plain-text version instead of writing resume.html")
    args = parser.parse_args()
    if args.text:
        print(plaintext_with_live_count(load_data(REPO_ROOT)))
        return
    if sync(REPO_ROOT):
        print("updated site/resume.html from data/experiences.json")
    else:
        print("resume already in sync")


if __name__ == "__main__":
    main()
