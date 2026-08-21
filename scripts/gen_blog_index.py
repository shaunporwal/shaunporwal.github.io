#!/usr/bin/env python3
"""Regenerates the post listing in site/index.html from posts under site/posts/
(auto-discovered via lib_posts, newest first, drafts excluded). Adding a new
post needs no edits here — just create posts/<slug>/index.html. Stamped
between <!-- POSTLIST:START --> / <!-- POSTLIST:END --> markers. Run directly
(`python3 scripts/gen_blog_index.py`), wired into the pre-commit hook.
"""
import re
import pathlib

try:
    from lib_posts import all_posts
except ImportError:
    from scripts.lib_posts import all_posts

MARKER_RE = re.compile(r"<!-- POSTLIST:START -->.*?<!-- POSTLIST:END -->", re.DOTALL)


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
    items_html = "\n".join(render_item(p) for p in posts)
    return f"<!-- POSTLIST:START -->\n{items_html}\n<!-- POSTLIST:END -->"


def published_posts(site_dir: pathlib.Path) -> list[dict]:
    return [p for p in all_posts(site_dir) if not p["draft"]]


def sync(site_dir: pathlib.Path) -> bool:
    """Writes the regenerated listing into site/index.html if it changed."""
    index_path = site_dir / "index.html"
    text = index_path.read_text()
    if not MARKER_RE.search(text):
        return False
    block = build_block(published_posts(site_dir))
    new_text = MARKER_RE.sub(block, text)
    if new_text != text:
        index_path.write_text(new_text)
        return True
    return False


def main():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    site_dir = repo_root / "site"
    if not MARKER_RE.search((site_dir / "index.html").read_text()):
        print("gen-blog-index: no POSTLIST markers found in site/index.html, skipping")
        return
    if sync(site_dir):
        print(f"updated site/index.html post listing ({len(published_posts(site_dir))} posts)")
    else:
        print("blog index already in sync")


if __name__ == "__main__":
    main()
