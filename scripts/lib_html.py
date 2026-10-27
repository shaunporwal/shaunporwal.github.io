"""Small HTML text helpers shared by the generators and checks."""
import re

TAG_RE = re.compile(r"<[^>]+>")
MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL)
NEW_TAB = ' target="_blank" rel="noopener"'
PROFILE_TAB = ' target="_blank" rel="me noopener"'


def strip_tags(markup: str) -> str:
    return TAG_RE.sub("", markup).strip()


def main_inner(page: str) -> str:
    """The markup inside the first <main> element, or the whole page when it has none."""
    match = MAIN_RE.search(page)
    return match.group(1) if match else page
