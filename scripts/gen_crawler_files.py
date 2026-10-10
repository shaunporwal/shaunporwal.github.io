#!/usr/bin/env python3
"""Generates site/CNAME, site/robots.txt, and site/llms.txt from the data files and the published posts.

- CNAME holds the host of `base_url` in data/site.json, so GitHub Pages and
  every canonical URL agree on one domain.
- robots.txt allows every crawler, AI crawlers included, and names the sitemap.
- llms.txt (https://llmstxt.org) gives language models a short map of the
  site: the summary and current role, the pages, the published posts, and
  the contact links.
Run directly (`python3 scripts/gen_crawler_files.py`) or through `make sync`.
"""
import pathlib
from urllib.parse import urlparse

from lib_blocks import write_if_changed
from lib_posts import all_posts
from lib_record import load_record
from lib_site import REPO_ROOT, load_pages, load_site, page_url

CONTACT_LABELS = (("Email", "email"), ("GitHub", "github"), ("X", "x"), ("LinkedIn", "linkedin"))


def load_inputs(repo_root: pathlib.Path) -> dict:
    return {
        "site": load_site(repo_root),
        "pages": load_pages(repo_root),
        "posts": [post for post in all_posts(repo_root / "site") if not post["draft"]],
        "record": load_record(repo_root),
    }


def render_cname(inputs: dict) -> str:
    return urlparse(inputs["site"]["base_url"]).netloc + "\n"


def render_robots(inputs: dict) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {inputs['site']['base_url']}/sitemap.xml\n"


def current_role(record: dict) -> str:
    roles = [f"{e['title']} at {e['org']}" for e in record["experience"] if e["end"] == "present"]
    return f" Currently {' and '.join(roles)}." if roles else ""


def _page_line(site: dict, page: dict) -> str:
    title = page["title"].format(name=site["name"])
    description = page["description"].format(name=site["name"])
    return f"- [{title}]({page_url(site['base_url'], page['file'])}): {description}"


def _post_line(site: dict, post: dict) -> str:
    return f"- [{post['title']}]({site['base_url']}/posts/{post['slug']}/): {post['excerpt']}"


def render_llms(inputs: dict) -> str:
    site = inputs["site"]
    sections = [
        f"# {site['name']}\n\n> {site['summary']}{current_role(inputs['record'])}",
        "## Pages\n\n" + "\n".join(_page_line(site, p) for p in inputs["pages"] if p["sitemap"]),
        "## Posts\n\n" + "\n".join(_post_line(site, p) for p in inputs["posts"]),
        "## Contact\n\n" + "\n".join(f"- {label}: {site[key]}" for label, key in CONTACT_LABELS),
    ]
    return "\n\n".join(sections) + "\n"


FILES = {"CNAME": render_cname, "robots.txt": render_robots, "llms.txt": render_llms}


def sync(repo_root: pathlib.Path) -> list[str]:
    """Writes each file that changed. Returns the names it wrote."""
    inputs = load_inputs(repo_root)
    site_dir = repo_root / "site"
    return [name for name, render in FILES.items() if write_if_changed(site_dir / name, render(inputs))]


def main():
    changed = sync(REPO_ROOT)
    for name in changed:
        print(f"updated site/{name}")
    if not changed:
        print("crawler files already in sync")


if __name__ == "__main__":
    main()
