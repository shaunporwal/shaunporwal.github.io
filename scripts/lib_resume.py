"""Shared mini-markup parser for data/resume.json content.

Bullet/sub/title strings in resume.json may contain:
  [text](url)   -> a link
  `text`        -> inline code
  {dcurves}     -> the live dcurves download count (span in HTML, plain
                   count in text output; the actual live value is filled
                   in by update-dcurves-downloads.sh right after
                   gen_resume.py runs, so the placeholder here just needs
                   to carry the right CSS class/marker through)

render_html() escapes plain-text runs and emits real <a>/<code>/<span>
tags for the rest. render_text() produces a plain-text version (links as
"text (url)", code as bare text) for pasting into LinkedIn etc.
"""
import re
import html

TOKEN_RE = re.compile(r"\{dcurves\}|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`")

DCURVES_PLACEHOLDER_HTML = '<span class="dcurves-downloads">72k+</span>'
DCURVES_PLACEHOLDER_TEXT = "72k+"


def _tokenize(text: str):
    """Yields ("text", s) | ("link", label, url) | ("code", s) | ("dcurves",)."""
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            yield ("text", text[pos:m.start()])
        if m.group(0) == "{dcurves}":
            yield ("dcurves",)
        elif m.group(1) is not None:
            yield ("link", m.group(1), m.group(2))
        else:
            yield ("code", m.group(3))
        pos = m.end()
    if pos < len(text):
        yield ("text", text[pos:])


def render_html(text: str) -> str:
    parts = []
    for tok in _tokenize(text):
        if tok[0] == "text":
            parts.append(html.escape(tok[1]))
        elif tok[0] == "link":
            _, label, url = tok
            parts.append(f'<a href="{html.escape(url)}">{html.escape(label)}</a>')
        elif tok[0] == "code":
            parts.append(f"<code>{html.escape(tok[1])}</code>")
        elif tok[0] == "dcurves":
            parts.append(DCURVES_PLACEHOLDER_HTML)
    return "".join(parts)


def render_text(text: str) -> str:
    parts = []
    for tok in _tokenize(text):
        if tok[0] == "text":
            parts.append(tok[1])
        elif tok[0] == "link":
            _, label, url = tok
            parts.append(f"{label} ({url})")
        elif tok[0] == "code":
            parts.append(tok[1])
        elif tok[0] == "dcurves":
            parts.append(DCURVES_PLACEHOLDER_TEXT)
    return "".join(parts)
