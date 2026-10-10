"""Small HTML text helpers shared by the generators and checks."""
import re

TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(markup: str) -> str:
    return TAG_RE.sub("", markup).strip()
