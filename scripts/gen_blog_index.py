#!/usr/bin/env python3
"""Regenerates the post listing in site/index.html from posts under site/posts/
(auto-discovered via lib_posts, newest first, drafts excluded). Adding a new
post needs no edits here — just create posts/<slug>/index.html. Stamped
between <!-- POSTLIST:START --> / <!-- POSTLIST:END --> markers. Run directly
(`python3 scripts/gen_blog_index.py`), wired into the pre-commit hook.
"""
import html
import pathlib

from lib_blocks import sync_block, wrap
from lib_images import size_attributes
from lib_posts import all_posts
from lib_site import REPO_ROOT


def date_markup(post: dict) -> str:
    if not post["date"]:
        return ""
    iso, shown = post["date"].isoformat(), post["date"].strftime("%B %-d, %Y")
    return f'    <time class="post-date" datetime="{iso}">{shown}</time>\n'


def categories_markup(post: dict) -> str:
    cats = "".join(f'<span class="cat">{html.escape(category)}</span>' for category in post["categories"])
    return f'      <p class="post-cats">{cats}</p>\n' if cats else ""


def thumb_markup(post: dict, site_dir: pathlib.Path) -> str:
    if not post["image"]:
        return ""
    src = f'posts/{post["slug"]}/{post["image"]}'
    sizes = size_attributes(site_dir / src)
    return f'    <img class="post-thumb" src="{src}" alt=""{sizes} loading="lazy" decoding="async">\n'


def render_item(post: dict, site_dir: pathlib.Path) -> str:
    href = f'posts/{post["slug"]}/index.html'
    return (
        '  <li class="post-row" data-reveal-item>\n'
        f"{date_markup(post)}"
        '    <div class="post-body">\n'
        f'      <a class="post-title" href="{href}">{html.escape(post["title"])}</a>\n'
        f"{categories_markup(post)}"
        "    </div>\n"
        f"{thumb_markup(post, site_dir)}"
        "  </li>"
    )


def build_block(posts: list[dict], site_dir: pathlib.Path) -> str:
    return wrap("POSTLIST", "\n".join(render_item(p, site_dir) for p in posts))


def published_posts(site_dir: pathlib.Path) -> list[dict]:
    return [p for p in all_posts(site_dir) if not p["draft"]]


def sync(repo_root: pathlib.Path) -> bool:
    """Writes the regenerated listing into site/index.html if it changed."""
    site_dir = repo_root / "site"
    return sync_block(site_dir / "index.html", "POSTLIST", build_block(published_posts(site_dir), site_dir))


def main():
    if sync(REPO_ROOT):
        print(f"updated site/index.html post listing ({len(published_posts(REPO_ROOT / 'site'))} posts)")
    else:
        print("blog index already in sync")


if __name__ == "__main__":
    main()
