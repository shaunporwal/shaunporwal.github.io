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
import pathlib

from lib_blocks import replace_block, wrap, write_if_changed
from lib_posts import all_posts
from lib_site import REPO_ROOT, load_pages, load_site, page_url

TITLE_END = "</title>\n"


def esc(s: str) -> str:
    return s.replace('"', "&quot;")


def build_block(url: str, title: str, description: str, og_type: str, image: str) -> str:
    body = (
        f'<meta name="description" content="{esc(description)}">\n'
        f'<link rel="canonical" href="{url}">\n'
        f'<meta property="og:type" content="{og_type}">\n'
        f'<meta property="og:title" content="{esc(title)}">\n'
        f'<meta property="og:description" content="{esc(description)}">\n'
        f'<meta property="og:url" content="{url}">\n'
        f'<meta property="og:image" content="{image}">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{esc(title)}">\n'
        f'<meta name="twitter:description" content="{esc(description)}">\n'
        f'<meta name="twitter:image" content="{image}">'
    )
    return wrap("SEO", body)


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
    return build_block(
        page_url(site["base_url"], page["file"]),
        page["title"].format(name=site["name"]),
        page["description"].format(name=site["name"]),
        page["og_type"],
        site["default_og_image"],
    )


def post_block(site: dict, post: dict) -> str:
    return build_block(
        post_url(site["base_url"], post["slug"]),
        f"{post['title']} — {site['name']}",
        post["excerpt"],
        "article",
        post_image(site["base_url"], site["default_og_image"], post),
    )


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
