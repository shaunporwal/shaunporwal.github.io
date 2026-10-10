"""Shared mini-markup parser for data/resume.json content.

Bullet/sub/title strings in resume.json may contain:
  [text](url)   -> a link
  `text`        -> inline code
  **text**      -> bold (use sparingly — real impact metrics/standout tech
                   only, not every phrase; tastefully, not decoratively)
  *text*        -> italic (for species names and similar; never write a
                   bare * as a multiplication sign)
  {dcurves}     -> the live dcurves download count (span in HTML, plain
                   count in text output; the actual live value is filled
                   in by update-dcurves-downloads.sh right after
                   gen_resume.py runs, so the placeholder here just needs
                   to carry the right CSS class/marker through)

render_html() escapes plain-text runs and emits real <a>/<code>/<strong>/
<em>/<span> tags for the rest. render_text() produces a plain-text version
(links as "text (url)", code/bold/italic as bare text) for pasting into
LinkedIn etc. — plain text can't carry bold or italics, so the **/* markers
are just stripped there.

No nesting: **bold {dcurves}** or **[link](url)** etc. won't work — the
inner token is captured as literal text, not re-parsed. Keep tokens
side by side instead of nested (e.g. "**bold** {dcurves}", not
"**{dcurves}**"); {dcurves} already renders bold on its own via the
`.dcurves-downloads` CSS class, so it never needs a ** wrapper anyway.
"""
import re
import html

TOKEN_RE = re.compile(
    r"(?P<dcurves>\{dcurves\})"
    r"|\[(?P<link_label>[^\]]+)\]\((?P<link_url>[^)]+)\)"
    r"|\*\*(?P<bold>[^*]+)\*\*"
    r"|\*(?P<italic>[^*]+)\*"
    r"|`(?P<code>[^`]+)`"
)

DCURVES_PLACEHOLDER_HTML = '<span class="dcurves-downloads">72k+</span>'
DCURVES_PLACEHOLDER_TEXT = "72k+"


def _dcurves_token(m):
    return ("dcurves",)


def _link_token(m):
    return ("link", m.group("link_label"), m.group("link_url"))


def _bold_token(m):
    return ("bold", m.group("bold"))


def _italic_token(m):
    return ("italic", m.group("italic"))


def _code_token(m):
    return ("code", m.group("code"))


# Keyed by the regex's last matched group name; a link's last group is its url.
TOKEN_BUILDERS = {
    "dcurves": _dcurves_token,
    "link_url": _link_token,
    "bold": _bold_token,
    "italic": _italic_token,
    "code": _code_token,
}


def _tokenize(text: str):
    """Yields ("text", s) | ("link", label, url) | ("bold", s) | ("italic", s) | ("code", s) | ("dcurves",)."""
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            yield ("text", text[pos:m.start()])
        yield TOKEN_BUILDERS[m.lastgroup](m)
        pos = m.end()
    if pos < len(text):
        yield ("text", text[pos:])


def _html_text(tok):
    return html.escape(tok[1])


def _html_link(tok):
    _, label, url = tok
    return f'<a href="{html.escape(url)}">{html.escape(label)}</a>'


def _html_bold(tok):
    return f"<strong>{html.escape(tok[1])}</strong>"


def _html_italic(tok):
    return f"<em>{html.escape(tok[1])}</em>"


def _html_code(tok):
    return f"<code>{html.escape(tok[1])}</code>"


def _html_dcurves(tok):
    return DCURVES_PLACEHOLDER_HTML


HTML_RENDERERS = {
    "text": _html_text,
    "link": _html_link,
    "bold": _html_bold,
    "italic": _html_italic,
    "code": _html_code,
    "dcurves": _html_dcurves,
}


def _text_plain(tok):
    return tok[1]


def _text_link(tok):
    _, label, url = tok
    return f"{label} ({url})"


def _text_dcurves(tok):
    return DCURVES_PLACEHOLDER_TEXT


TEXT_RENDERERS = {
    "text": _text_plain,
    "link": _text_link,
    "bold": _text_plain,
    "italic": _text_plain,
    "code": _text_plain,
    "dcurves": _text_dcurves,
}


def render_html(text: str) -> str:
    return "".join(HTML_RENDERERS[tok[0]](tok) for tok in _tokenize(text))


def render_text(text: str) -> str:
    return "".join(TEXT_RENDERERS[tok[0]](tok) for tok in _tokenize(text))
