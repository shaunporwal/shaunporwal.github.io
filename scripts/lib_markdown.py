"""Converts the body of a post's index.html to Markdown for llms-full.txt.

Handles the tags the posts use: paragraphs, headings, list items, code blocks,
quotes, figures, and the inline links, bold, italic and code. The post title and
the meta line are left out, because the caller writes them as a header.
"""
import html
import re
import urllib.parse

from lib_html import main_inner, strip_tags

META_END_RE = re.compile(r'<p class="[^"]*\bpage-meta\b[^"]*">.*?</p>', re.DOTALL)
BLOCK_RE = re.compile(
    r"(?P<img><img\b[^>]*>)|<(?P<tag>p|h[2-4]|li|pre|blockquote|figcaption)\b[^>]*>(?P<body>.*?)</(?P=tag)>",
    re.DOTALL,
)
INLINE = (
    (re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL), r"[\2](\1)"),
    (re.compile(r"<strong>(.*?)</strong>", re.DOTALL), r"**\1**"),
    (re.compile(r"<em>(.*?)</em>", re.DOTALL), r"*\1*"),
    (re.compile(r"<code>(.*?)</code>", re.DOTALL), r"`\1`"),
)
ATTRIBUTE_RE = re.compile(r'(\w+)="([^"]*)"')
IMAGE_PARAGRAPH_RE = re.compile(r"<p>\s*(<img\b[^>]*>)\s*</p>")


def inline_text(markup: str) -> str:
    """Inline markup as Markdown on one line, with other tags removed and entities decoded."""
    for pattern, replacement in INLINE:
        markup = pattern.sub(replacement, markup)
    return html.unescape(re.sub(r"\s+", " ", strip_tags(markup)))


def heading(level: int, body: str) -> str:
    return f"{'#' * (level + 1)} {inline_text(body)}"


def code_block(body: str) -> str:
    return "```\n" + html.unescape(strip_tags(body)).strip("\n") + "\n```"


def image(tag: str, base: str) -> str:
    attributes = dict(ATTRIBUTE_RE.findall(tag))
    return f"![{attributes.get('alt', '')}]({urllib.parse.urljoin(base, attributes.get('src', ''))})"


def list_item(body: str) -> str:
    text = inline_text(body)
    return f"- {text}" if text else ""


def quote(body: str) -> str:
    text = inline_text(body)
    return f"> {text}" if text else ""


def caption(body: str) -> str:
    text = inline_text(body)
    return f"*{text}*" if text else ""


TAG_HANDLERS = {"p": inline_text, "li": list_item, "blockquote": quote, "figcaption": caption, "pre": code_block}


def block_markdown(match: re.Match, base: str) -> str:
    if match.group("img"):
        return image(match.group("img"), base)
    tag, body = match.group("tag"), match.group("body")
    if tag in TAG_HANDLERS:
        return TAG_HANDLERS[tag](body)
    return heading(int(tag[1]), body)


def main_body(page: str) -> str:
    """The post body with the meta line removed and each image-only paragraph reduced to its image."""
    body = META_END_RE.sub("", main_inner(page), count=1)
    return IMAGE_PARAGRAPH_RE.sub(r"\1", body)


def post_markdown(page: str, base: str) -> str:
    """The post body as Markdown blocks separated by blank lines. base is the post URL, for image links."""
    blocks = (block_markdown(match, base) for match in BLOCK_RE.finditer(main_body(page)))
    return "\n\n".join(block for block in blocks if block)
