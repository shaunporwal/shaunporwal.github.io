#!/usr/bin/env python3
"""Generates site/llms-full.txt, the full text of every published post as Markdown, from the posts.

A language model can read the whole blog from this one file. It follows the
llms.txt convention (https://llmstxt.org): llms.txt is the map and this file is
the content. Drafts stay out. Run directly (`python3 scripts/gen_llms_full.py`)
or through `make sync`.
"""
import pathlib

from lib_blocks import write_if_changed
from lib_markdown import post_markdown
from lib_posts import all_posts
from lib_site import REPO_ROOT, load_site


def post_header(site: dict, post: dict) -> str:
    url = f"{site['base_url']}/posts/{post['slug']}/"
    lines = [f"## {post['title']}", f"URL: {url}"]
    if post["date"]:
        lines.append(f"Published: {post['date'].strftime('%B %-d, %Y')}")
    if post["categories"]:
        lines.append(f"Categories: {', '.join(post['categories'])}")
    return "\n".join(lines)


def render_post(site: dict, post: dict, page: str) -> str:
    base = f"{site['base_url']}/posts/{post['slug']}/"
    return post_header(site, post) + "\n\n" + post_markdown(page, base)


def render_full(site: dict, posts: list[tuple[dict, str]]) -> str:
    intro = f"# {site['name']}: full text\n\n> {site['summary']}\n\nIndex: {site['base_url']}/llms.txt"
    return "\n\n---\n\n".join([intro, *(render_post(site, post, page) for post, page in posts)]) + "\n"


def published_with_text(site_dir: pathlib.Path) -> list[tuple[dict, str]]:
    posts = [post for post in all_posts(site_dir) if not post["draft"]]
    return [(post, (site_dir / "posts" / post["slug"] / "index.html").read_text()) for post in posts]


def sync(repo_root: pathlib.Path) -> bool:
    """Writes llms-full.txt if it changed. Returns whether it changed."""
    text = render_full(load_site(repo_root), published_with_text(repo_root / "site"))
    return write_if_changed(repo_root / "site" / "llms-full.txt", text)


def main():
    if sync(REPO_ROOT):
        print("updated site/llms-full.txt")
    else:
        print("llms-full.txt already in sync")


if __name__ == "__main__":
    main()
