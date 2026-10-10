#!/usr/bin/env python3
"""Regenerates the post listing in site/index.html from posts under site/posts/
(auto-discovered via lib_posts, newest first, drafts excluded). Adding a new
post needs no edits here — just create posts/<slug>/index.html. Stamped
between <!-- POSTLIST:START --> / <!-- POSTLIST:END --> markers. Run directly
(`python3 scripts/gen_blog_index.py`), wired into the pre-commit hook.
"""
import pathlib

from lib_blocks import sync_block, wrap
from lib_posts import all_posts
from lib_site import REPO_ROOT


def render_item(post: dict) -> str:
    cat_html = ""
    if post["categories"]:
        cat_html = " &middot; " + "".join(f'<span class="cat">{c}</span>' for c in post["categories"])
    date_str = post["date"].strftime("%B %-d, %Y") if post["date"] else ""
    href = f'posts/{post["slug"]}/index.html'

    thumb = ""
    if post["image"]:
        thumb = (
            f'\n    <a class="post-card-thumb" href="{href}" tabindex="-1" aria-hidden="true">'
            f'<img src="posts/{post["slug"]}/{post["image"]}" alt="" loading="lazy"></a>'
        )

    return (
        '  <li class="post-card">\n'
        '    <div class="post-card-text">\n'
        f'      <a class="post-title" href="{href}">{post["title"]}</a>\n'
        f'      <p class="post-date">{date_str}{cat_html}</p>\n'
        "    </div>"
        f"{thumb}\n"
        "  </li>"
    )


def build_block(posts: list[dict]) -> str:
    return wrap("POSTLIST", "\n".join(render_item(p) for p in posts))


def published_posts(site_dir: pathlib.Path) -> list[dict]:
    return [p for p in all_posts(site_dir) if not p["draft"]]


def sync(repo_root: pathlib.Path) -> bool:
    """Writes the regenerated listing into site/index.html if it changed."""
    site_dir = repo_root / "site"
    return sync_block(site_dir / "index.html", "POSTLIST", build_block(published_posts(site_dir)))


def main():
    if sync(REPO_ROOT):
        print(f"updated site/index.html post listing ({len(published_posts(REPO_ROOT / 'site'))} posts)")
    else:
        print("blog index already in sync")


if __name__ == "__main__":
    main()
