#!/usr/bin/env python3
"""Stamps SEO/social meta tags (description, canonical, OpenGraph, Twitter card)
into every page under site/, between <!-- SEO:START --> / <!-- SEO:END -->
markers. Top-level pages come from data/pages.json;
every post under site/posts/*/ is discovered automatically (via lib_posts) and
needs no registration — add a new posts/<slug>/index.html and this fills in
its SEO tags on the next commit. Site-wide constants (name, base URL, default
image) come from data/site.json via lib_site, not hardcoded here. Run
directly (`python3 scripts/sync_seo.py`), wired into the pre-commit hook.
"""
import json
import pathlib
from dataclasses import dataclass

from lib_blocks import replace_block, wrap, write_if_changed
from lib_posts import all_posts
from lib_site import REPO_ROOT, load_pages, load_site, page_url

TITLE_END = "</title>\n"
NOINDEX = '<meta name="robots" content="noindex">'


def esc(s: str) -> str:
    return s.replace('"', "&quot;")


@dataclass(frozen=True)
class SeoMeta:
    url: str
    title: str
    description: str
    og_type: str
    image: str
    extra: tuple[str, ...] = ()  # more <head> lines, for example noindex or structured data


def build_block(meta: SeoMeta) -> str:
    lines = [
        f'<meta name="description" content="{esc(meta.description)}">',
        f'<link rel="canonical" href="{meta.url}">',
        f'<meta property="og:type" content="{meta.og_type}">',
        f'<meta property="og:title" content="{esc(meta.title)}">',
        f'<meta property="og:description" content="{esc(meta.description)}">',
        f'<meta property="og:url" content="{meta.url}">',
        f'<meta property="og:image" content="{meta.image}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(meta.title)}">',
        f'<meta name="twitter:description" content="{esc(meta.description)}">',
        f'<meta name="twitter:image" content="{meta.image}">',
        *meta.extra,
    ]
    return wrap("SEO", "\n".join(lines))


def inject(text: str, block: str) -> str | None:
    """text with the SEO block in place: replaced if present, else added after
    </title>. None if the page has neither."""
    replaced = replace_block(text, "SEO", block)
    if replaced is not None:
        return replaced
    if TITLE_END not in text:
        return None
    return text.replace(TITLE_END, TITLE_END + block + "\n", 1)


def post_url(base_url: str, slug: str) -> str:
    return f"{base_url}/posts/{slug}/"


def post_image(base_url: str, default_image: str, post: dict) -> str:
    if post["image"]:
        return f"{base_url}/posts/{post['slug']}/{post['image']}"
    return default_image


def page_block(site: dict, page: dict) -> str:
    return build_block(SeoMeta(
        page_url(site["base_url"], page["file"]),
        page["title"].format(name=site["name"]),
        page["description"].format(name=site["name"]),
        page["og_type"],
        site["default_og_image"],
    ))


def json_ld(data: dict) -> str:
    """A structured-data script tag. "</" is escaped so the data cannot close the tag."""
    body = json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{body}\n</script>'


def blog_posting(site: dict, post: dict, url: str, image: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["excerpt"],
        "url": url,
        "image": image,
        "author": {"@type": "Person", "name": site["name"], "url": page_url(site["base_url"], "index.html")},
    }
    if post["date"]:
        data["datePublished"] = post["date"].isoformat()
    return json_ld(data)


def post_block(site: dict, post: dict) -> str:
    """A draft stays reachable by URL, but noindex keeps it out of search results."""
    url = post_url(site["base_url"], post["slug"])
    image = post_image(site["base_url"], site["default_og_image"], post)
    extra = NOINDEX if post["draft"] else blog_posting(site, post, url, image)
    return build_block(SeoMeta(url, f"{post['title']} — {site['name']}", post["excerpt"], "article", image, (extra,)))


def targets(repo_root: pathlib.Path, site: dict) -> list[tuple[str, pathlib.Path, str]]:
    """(name relative to site/, path, SEO block) for every page and post."""
    site_dir = repo_root / "site"
    pages = [
        (page["file"], site_dir / page["file"], page_block(site, page))
        for page in load_pages(repo_root)
        if (site_dir / page["file"]).exists()
    ]
    posts = [
        (f"posts/{post['slug']}/index.html", site_dir / "posts" / post["slug"] / "index.html", post_block(site, post))
        for post in all_posts(site_dir)
    ]
    return pages + posts


def write_block(path: pathlib.Path, block: str) -> bool:
    new_text = inject(path.read_text(), block)
    return new_text is not None and write_if_changed(path, new_text)


def sync(repo_root: pathlib.Path) -> list[str]:
    site = load_site(repo_root)
    changed = []
    for name, path, block in targets(repo_root, site):
        if write_block(path, block):
            changed.append(name)
    return changed


def main():
    changed = sync(REPO_ROOT)
    for c in changed:
        print(f"updated seo: {c}")
    if not changed:
        print("seo already in sync")


if __name__ == "__main__":
    main()
