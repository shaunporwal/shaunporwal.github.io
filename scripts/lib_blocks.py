"""Generated blocks between <!-- NAME:START --> and <!-- NAME:END --> markers.

Every generator stamps its output into a file this way, so the files stay
plain static HTML or Markdown while the content keeps one source. Text
outside the markers is never touched.
"""
import functools
import pathlib
import re


@functools.cache
def _marker_re(name: str) -> re.Pattern:
    return re.compile(rf"<!-- {name}:START -->.*?<!-- {name}:END -->", re.DOTALL)


def wrap(name: str, body: str) -> str:
    return f"<!-- {name}:START -->\n{body}\n<!-- {name}:END -->"


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
