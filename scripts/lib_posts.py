"""Shared helpers for reading post metadata straight out of each post's index.html.

There's no front matter anymore (no Quarto/.qmd) — a post's title, date, and
categories all live in the rendered HTML itself (<h1 class="page-title">,
<p class="page-meta">). A post is a draft (excluded from the blog listing and
sitemap, but still reachable by direct URL) iff a `.draft` file sits in its
directory. This one parser backs sync-seo.py, gen-sitemap.py, and
gen-blog-index.py so all three agree on what a "post" is.
"""
import datetime
import html
import pathlib
import re

from lib_html import main_inner, strip_tags

TITLE_RE = re.compile(r'<h1 class="[^"]*\bpage-title\b[^"]*">(.*?)</h1>', re.DOTALL)
META_RE = re.compile(r'<p class="[^"]*\bpage-meta\b[^"]*">(.*?)</p>', re.DOTALL)
CAT_RE = re.compile(r'<span class="cat">(.*?)</span>')
FIRST_P_RE = re.compile(r"<p>(.*?)</p>", re.DOTALL)

MONTHS = {
    m: i
    for i, m in enumerate(
        [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ],
        start=1,
    )
}



IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
EXCERPT_LIMIT = 155


def _title(text: str, fallback: str) -> str:
    match = TITLE_RE.search(text)
    return html.unescape(strip_tags(match.group(1))) if match else fallback


def _date(meta_raw: str):
    date_text = strip_tags(re.split(r"&middot;", meta_raw)[0])
    match = re.match(r"(\w+)\s+(\d+),\s+(\d+)", date_text)
    month = MONTHS.get(match.group(1)) if match else None
    if not month:
        return None
    try:
        return datetime.date(int(match.group(3)), month, int(match.group(2)))
    except ValueError:
        return None


def _meta(text: str) -> tuple:
    """(date, categories) from the post's page-meta line."""
    match = META_RE.search(text)
    if not match:
        return None, []
    meta_raw = match.group(1)
    return _date(meta_raw), [html.unescape(strip_tags(c)) for c in CAT_RE.findall(meta_raw)]


def _first_text(body: str, fallback: str) -> str:
    """The text of the first plain paragraph that holds any, so an image-only paragraph is skipped."""
    for match in FIRST_P_RE.finditer(body):
        text = strip_tags(match.group(1))
        if text:
            return text
    return fallback


def _excerpt(text: str, fallback: str) -> str:
    excerpt = re.sub(r"\s+", " ", html.unescape(_first_text(main_inner(text), fallback)))
    if len(excerpt) > EXCERPT_LIMIT:
        excerpt = excerpt[: EXCERPT_LIMIT - 3].rsplit(" ", 1)[0] + "..."
    return excerpt


def _first_image(post_dir: pathlib.Path):
    images = [f.name for f in sorted(post_dir.iterdir()) if f.suffix.lower() in IMAGE_SUFFIXES]
    return images[0] if images else None


def parse_post(post_dir: pathlib.Path):
    index = post_dir / "index.html"
    if not index.exists():
        return None
    text = index.read_text()
    title = _title(text, post_dir.name)
    date_obj, categories = _meta(text)
    return {
        "slug": post_dir.name,
        "title": title,
        "date": date_obj,
        "categories": categories,
        "excerpt": _excerpt(text, title),
        "image": _first_image(post_dir),
        "draft": (post_dir / ".draft").exists(),
    }


def _newest_first(post: dict) -> datetime.date:
    return post["date"] or datetime.date.min


def all_posts(site_dir: pathlib.Path):
    posts_dir = site_dir / "posts"
    if not posts_dir.exists():
        return []
    parsed = [parse_post(d) for d in sorted(posts_dir.iterdir()) if d.is_dir()]
    return sorted(filter(None, parsed), key=_newest_first, reverse=True)
