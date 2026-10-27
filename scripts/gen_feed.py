#!/usr/bin/env python3
"""Generates site/feed.xml, an Atom feed of the published posts, newest first, from the posts.

Readers and agents use the feed to find new posts. Each entry holds the title, the link, the
date, the excerpt and the categories. Drafts stay out, and so do posts with no date. Run
directly (`python3 scripts/gen_feed.py`) or through `make sync`.
"""
import pathlib
from xml.sax.saxutils import escape, quoteattr

from lib_blocks import write_if_changed
from lib_posts import all_posts
from lib_site import REPO_ROOT, load_site

EMPTY_FEED_DATE = "1970-01-01T00:00:00Z"


def xml_text(text: str) -> str:
    """text from a post, XML-escaped. The post parser has already decoded its HTML entities."""
    return escape(text)


def timestamp(date) -> str:
    return f"{date.isoformat()}T00:00:00Z"


def render_entry(site: dict, post: dict) -> str:
    url = f"{site['base_url']}/posts/{post['slug']}/"
    categories = [f"    <category term={quoteattr(name)}/>" for name in post["categories"]]
    lines = [
        "  <entry>",
        f"    <title>{xml_text(post['title'])}</title>",
        f'    <link href="{url}" rel="alternate" type="text/html"/>',
        f"    <id>{url}</id>",
        f"    <updated>{timestamp(post['date'])}</updated>",
        f"    <summary>{xml_text(post['excerpt'])}</summary>",
        *categories,
        "  </entry>",
    ]
    return "\n".join(lines)


def feed_head(site: dict, updated: str) -> list[str]:
    """The lines of the feed from the XML declaration to the author."""
    base = site["base_url"]
    return [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"  <title>{escape(site['name'])}</title>",
        f"  <subtitle>{escape(site['summary'])}</subtitle>",
        f'  <link href="{base}/feed.xml" rel="self" type="application/atom+xml"/>',
        f'  <link href="{base}/" rel="alternate" type="text/html"/>',
        f"  <id>{base}/</id>",
        f"  <updated>{updated}</updated>",
        f"  <author><name>{escape(site['name'])}</name><uri>{base}/</uri></author>",
    ]


def render_feed(site: dict, posts: list[dict]) -> str:
    updated = timestamp(posts[0]["date"]) if posts else EMPTY_FEED_DATE
    entries = [render_entry(site, post) for post in posts]
    return "\n".join([*feed_head(site, updated), *entries, "</feed>"]) + "\n"


def dated_posts(site_dir: pathlib.Path) -> list[dict]:
    return [post for post in all_posts(site_dir) if post["date"] and not post["draft"]]


def sync(repo_root: pathlib.Path) -> bool:
    """Writes feed.xml if it changed. Returns whether it changed."""
    text = render_feed(load_site(repo_root), dated_posts(repo_root / "site"))
    return write_if_changed(repo_root / "site" / "feed.xml", text)


def main():
    if sync(REPO_ROOT):
        print("updated site/feed.xml")
    else:
        print("feed.xml already in sync")


if __name__ == "__main__":
    main()
