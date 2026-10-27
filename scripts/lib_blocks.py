"""Generated blocks between <!-- NAME:START --> and <!-- NAME:END --> markers.

Every generator stamps its output into a file this way, so the files stay
plain static HTML or Markdown while the content keeps one source. A CSS file
uses /* NAME:START */ and /* NAME:END */ markers instead. Text outside the
markers is never touched.
"""
import functools
import pathlib
import re


@functools.cache
def _marker_re(name: str) -> re.Pattern:
    start = rf"(?:<!-- {name}:START -->|/\* {name}:START \*/)"
    end = rf"(?:<!-- {name}:END -->|/\* {name}:END \*/)"
    return re.compile(f"{start}.*?{end}", re.DOTALL)


HTML_MARKER = "<!-- {name}:{edge} -->"
CSS_MARKER = "/* {name}:{edge} */"


def wrap(name: str, body: str, css: bool = False) -> str:
    """body between START and END markers. css=True writes /* */ markers for a stylesheet."""
    marker = CSS_MARKER if css else HTML_MARKER
    return f"{marker.format(name=name, edge='START')}\n{body}\n{marker.format(name=name, edge='END')}"


def replace_block(text: str, name: str, block: str) -> str | None:
    """text with its NAME block replaced by block, or None if text has no NAME
    markers. A splice, not re.sub: sub would read backslashes in block as escapes."""
    match = _marker_re(name).search(text)
    if not match:
        return None
    return text[: match.start()] + block + text[match.end():]


def write_if_changed(path: pathlib.Path, text: str) -> bool:
    if path.exists() and path.read_text() == text:
        return False
    path.write_text(text)
    return True


def sync_block(path: pathlib.Path, name: str, block: str) -> bool:
    """Writes block into the NAME markers in path. Returns whether the file changed."""
    new_text = replace_block(path.read_text(), name, block)
    return new_text is not None and write_if_changed(path, new_text)
