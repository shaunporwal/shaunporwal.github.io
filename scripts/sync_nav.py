#!/usr/bin/env python3
"""Keeps every page's <nav class="site-nav"> block in sync with templates/nav.html.

Single source of truth for the nav lives in templates/nav.html (with a {root}
placeholder for the relative path prefix, plus {name}/{github}/{x}/{cal} filled
in from data/site.json). This module stamps that template into every page
between <!-- NAV:START --> / <!-- NAV:END --> markers, so the site stays plain
static HTML at serve time (no runtime include/fetch) while the nav itself stays
DRY at the source level. Run directly (`python3 scripts/sync_nav.py`), wired
into the pre-commit hook.
"""
import pathlib

from lib_blocks import sync_block, wrap
from lib_site import REPO_ROOT, load_pages, load_site


def render_nav(nav_template: str, **substitutions) -> str:
    return nav_template.format(**substitutions).strip()


def build_block(nav_template: str, **substitutions) -> str:
    return wrap("NAV", render_nav(nav_template, **substitutions))


def find_targets(repo_root: pathlib.Path) -> list[pathlib.Path]:
    """Every page and post, except pages whose `nav` is off in data/pages.json
    (resume.html is a standalone print document with no site nav)."""
    site_dir = repo_root / "site"
    no_nav = {page["file"] for page in load_pages(repo_root) if not page["nav"]}
    targets = list(site_dir.glob("*.html")) + list(site_dir.glob("posts/*/index.html"))
    return [p for p in targets if p.relative_to(site_dir).as_posix() not in no_nav]


def sync(repo_root: pathlib.Path) -> list[pathlib.Path]:
    site_dir = repo_root / "site"
    nav_template = (repo_root / "templates" / "nav.html").read_text()
    site = load_site(repo_root)

    changed = []
    for path in find_targets(repo_root):
        relative = path.relative_to(site_dir)
        block = build_block(nav_template, root="../" * (len(relative.parts) - 1), **site)
        if sync_block(path, "NAV", block):
            changed.append(relative)
    return changed


def main():
    changed = sync(REPO_ROOT)
    for p in changed:
        print(f"updated nav: {p}")
    if not changed:
        print("nav already in sync")


if __name__ == "__main__":
    main()
