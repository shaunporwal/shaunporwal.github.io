#!/usr/bin/env python3
"""Regenerates site/sitemap.xml from the top-level pages + non-draft posts
under site/. Add a new page here by hand; add a new post by just creating
posts/<slug>/index.html (auto-discovered, no registration needed) — drop a
`.draft` file in the post's directory to keep it out of the sitemap. Run
directly (`python3 scripts/gen_sitemap.py`), wired into the pre-commit hook.
"""
import pathlib

try:
    from lib_posts import all_posts
    from lib_site import load_site
except ImportError:
    from scripts.lib_posts import all_posts
    from scripts.lib_site import load_site

TOP_LEVEL_PAGES = ["", "about.html", "stuff.html", "resume.html"]


def collect_urls(site_dir: pathlib.Path) -> list[tuple[str, object]]:
    base_url = load_site(site_dir.parent)["base_url"]
    urls = [(f"{base_url}/{page}", None) for page in TOP_LEVEL_PAGES]
    for post in all_posts(site_dir):
        if post["draft"]:
            continue
        urls.append((f"{base_url}/posts/{post['slug']}/", post["date"]))
    return urls


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


def sync(site_dir: pathlib.Path) -> bool:
    """Writes sitemap.xml if it changed. Returns whether it changed."""
    urls = collect_urls(site_dir)
    new_content = render_sitemap(urls)
    sitemap_path = site_dir / "sitemap.xml"
    old_content = sitemap_path.read_text() if sitemap_path.exists() else None
    if new_content != old_content:
        sitemap_path.write_text(new_content)
        return True
    return False


def main():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    site_dir = repo_root / "site"
    if sync(site_dir):
        urls = collect_urls(site_dir)
        print(f"updated sitemap.xml ({len(urls)} urls)")
    else:
        print("sitemap.xml already in sync")


if __name__ == "__main__":
    main()
