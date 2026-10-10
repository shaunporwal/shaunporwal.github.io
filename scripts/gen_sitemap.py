#!/usr/bin/env python3
"""Regenerates site/sitemap.xml from the top-level pages + non-draft posts
under site/. Top-level pages come from data/pages.json; add a new post by just creating
posts/<slug>/index.html (auto-discovered, no registration needed) — drop a
`.draft` file in the post's directory to keep it out of the sitemap. Run
directly (`python3 scripts/gen_sitemap.py`), wired into the pre-commit hook.
"""
import pathlib

from lib_blocks import write_if_changed
from lib_posts import all_posts
from lib_site import REPO_ROOT, load_pages, load_site, page_url


def collect_urls(repo_root: pathlib.Path) -> list[tuple[str, object]]:
    base_url = load_site(repo_root)["base_url"]
    pages = [(page_url(base_url, page["file"]), None) for page in load_pages(repo_root) if page["sitemap"]]
    posts = [
        (f"{base_url}/posts/{post['slug']}/", post["date"])
        for post in all_posts(repo_root / "site")
        if not post["draft"]
    ]
    return pages + posts


def render_sitemap(urls: list[tuple[str, object]]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url, date in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        if date:
            lines.append(f"    <lastmod>{date.isoformat()}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def sync(repo_root: pathlib.Path) -> bool:
    """Writes sitemap.xml if it changed. Returns whether it changed."""
    return write_if_changed(repo_root / "site" / "sitemap.xml", render_sitemap(collect_urls(repo_root)))


def main():
    if sync(REPO_ROOT):
        print(f"updated sitemap.xml ({len(collect_urls(REPO_ROOT))} urls)")
    else:
        print("sitemap.xml already in sync")


if __name__ == "__main__":
    main()
