"""Shared helpers for reading post metadata straight out of each post's index.html.

There's no front matter anymore (no Quarto/.qmd) — a post's title, date, and
categories all live in the rendered HTML itself (<h1 class="page-title">,
<p class="page-meta">). A post is a draft (excluded from the blog listing and
sitemap, but still reachable by direct URL) iff a `.draft` file sits in its
directory. This one parser backs sync-seo.py, gen-sitemap.py, and
gen-blog-index.py so all three agree on what a "post" is.
"""
import re
import pathlib
import datetime

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


def parse_post(post_dir: pathlib.Path):
    index = post_dir / "index.html"
    if not index.exists():
        return None
    text = index.read_text()

    title_match = TITLE_RE.search(text)
    title = strip_tags(title_match.group(1)) if title_match else post_dir.name

    date_obj = None
    categories = []
    meta_match = META_RE.search(text)
    if meta_match:
        meta_raw = meta_match.group(1)
        categories = [strip_tags(c) for c in CAT_RE.findall(meta_raw)]
        date_text = strip_tags(re.split(r"&middot;", meta_raw)[0])
        m = re.match(r"(\w+)\s+(\d+),\s+(\d+)", date_text)
        if m:
            month_name, day, year = m.groups()
            month = MONTHS.get(month_name)
            if month:
                date_obj = datetime.date(int(year), month, int(day))

    main_start = text.find('<main class="page">')
    body = text[main_start:] if main_start != -1 else text
    excerpt_match = FIRST_P_RE.search(body)
    excerpt = strip_tags(excerpt_match.group(1)) if excerpt_match else title
    excerpt = re.sub(r"\s+", " ", excerpt)
    if len(excerpt) > 155:
        excerpt = excerpt[:152].rsplit(" ", 1)[0] + "..."

    image = None
    for f in sorted(post_dir.iterdir()):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and f.name != "index.html":
            image = f.name
            break

    return {
        "slug": post_dir.name,
        "title": title,
        "date": date_obj,
        "categories": categories,
        "excerpt": excerpt,
        "image": image,
        "draft": (post_dir / ".draft").exists(),
    }


def all_posts(site_dir: pathlib.Path):
    posts = []
    posts_dir = site_dir / "posts"
    if not posts_dir.exists():
        return posts
    for post_dir in sorted(posts_dir.iterdir()):
        if not post_dir.is_dir():
            continue
        parsed = parse_post(post_dir)
        if parsed:
            posts.append(parsed)
    posts.sort(key=lambda p: p["date"] or datetime.date.min, reverse=True)
    return posts
