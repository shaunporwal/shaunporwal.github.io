"""Shared helpers for reading post metadata straight out of each post's index.html.

There's no front matter anymore (no Quarto/.qmd) — a post's title, date, and
categories all live in the rendered HTML itself (<h1 class="page-title">,
<p class="page-meta">). A post is a draft (excluded from the blog listing and
sitemap, but still reachable by direct URL) iff a `.draft` file sits in its
directory. This one parser backs sync-seo.py, gen-sitemap.py, and
gen-blog-index.py so all three agree on what a "post" is.
"""
import datetime
import pathlib
import re

TAG_RE = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r'<h1 class="page-title">(.*?)</h1>', re.DOTALL)
META_RE = re.compile(r'<p class="page-meta">(.*?)</p>', re.DOTALL)
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


def strip_tags(s):
    return TAG_RE.sub("", s).strip()


IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
EXCERPT_LIMIT = 155


def _title(text: str, fallback: str) -> str:
    match = TITLE_RE.search(text)
    return strip_tags(match.group(1)) if match else fallback


def _date(meta_raw: str):
    date_text = strip_tags(re.split(r"&middot;", meta_raw)[0])
    match = re.match(r"(\w+)\s+(\d+),\s+(\d+)", date_text)
    month = MONTHS.get(match.group(1)) if match else None
    if not month:
        return None
    return datetime.date(int(match.group(3)), month, int(match.group(2)))


def _meta(text: str) -> tuple:
    """(date, categories) from the post's page-meta line."""
    match = META_RE.search(text)
    if not match:
        return None, []
    meta_raw = match.group(1)
    return _date(meta_raw), [strip_tags(c) for c in CAT_RE.findall(meta_raw)]


def _excerpt(text: str, fallback: str) -> str:
    main_start = text.find('<main class="page">')
    body = text[main_start:] if main_start != -1 else text
    match = FIRST_P_RE.search(body)
    excerpt = re.sub(r"\s+", " ", strip_tags(match.group(1)) if match else fallback)
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
