#!/usr/bin/env python3
"""Keeps every page's header block in sync with templates/nav.html.

Single source of truth for the header lives in templates/nav.html (with a {root}
placeholder for the relative path prefix, plus {name}/{cal} filled in from
data/site.json). This module stamps that template into every page between
<!-- NAV:START --> / <!-- NAV:END --> markers, so the site stays plain static HTML
at serve time (no runtime include/fetch) while the header itself stays DRY at the
source level. It marks the current page with aria-current. A post marks the home
link, because the posts are listed there. Run directly (`python3 scripts/sync_nav.py`),
wired into the pre-commit hook.
"""
import pathlib

from lib_blocks import sync_block, wrap
from lib_html import NEW_TAB
from lib_site import REPO_ROOT, load_pages, load_site

HOME_FILE = "index.html"
LINK_STYLES = {
    "nav": '      <a class="nav-link" href="{href}"{current}{target}>{label}</a>',
    "menu": '      <a class="menu-link" href="{href}"{current}{target}>{label}</a>',
}


def render_nav(nav_template: str, **substitutions) -> str:
    return nav_template.format(**substitutions).strip()


def page_link(page: dict, root: str, current: tuple[str, str], style: str) -> str:
    target = NEW_TAB if page["menu"]["new_tab"] else ""
    marked = f' aria-current="{current[1]}"' if page["file"] == current[0] else ""
    href, label = f"{root}{page['file']}", page["menu"]["label"]
    return LINK_STYLES[style].format(href=href, current=marked, target=target, label=label)


def page_links(pages: list[dict], root: str, current: tuple[str, str] = ("", ""), style: str = "nav") -> str:
    """One link for each page with a `menu` entry, in data/pages.json order. current is (file, aria-current value)."""
    return "\n".join(page_link(page, root, current, style) for page in pages if "menu" in page)


def build_block(nav_template: str, **substitutions) -> str:
    return wrap("NAV", render_nav(nav_template, **substitutions))


def find_targets(site_dir: pathlib.Path, pages: list[dict]) -> list[pathlib.Path]:
    """Every page and post, except pages whose `nav` is off in data/pages.json
    (resume.html is a standalone print document with no site nav)."""
    no_nav = {page["file"] for page in pages if not page["nav"]}
    targets = list(site_dir.glob("*.html")) + list(site_dir.glob("posts/*/index.html"))
    return [p for p in targets if p.relative_to(site_dir).as_posix() not in no_nav]


def page_root(relative: pathlib.Path, pages: list[dict]) -> str:
    """The path prefix to the site root: "/" for a page marked absolute, else one "../" per directory."""
    absolute = {page["file"] for page in pages if page.get("absolute")}
    return "/" if relative.as_posix() in absolute else "../" * (len(relative.parts) - 1)


def current_page(relative: pathlib.Path) -> tuple[str, str]:
    """(file, aria-current value) of the link to mark. A post marks the home link."""
    if len(relative.parts) > 1:
        return (HOME_FILE, "true")
    return (relative.name, "page")


def substitutions(relative: pathlib.Path, pages: list[dict], site: dict) -> dict:
    """The template values for one page: the root prefix, both link lists, and the site data."""
    root, current = page_root(relative, pages), current_page(relative)
    links = {"page_links": page_links(pages, root, current), "menu_links": page_links(pages, root, current, "menu")}
    return {"root": root, **links, **site}


def sync(repo_root: pathlib.Path) -> list[pathlib.Path]:
    site_dir = repo_root / "site"
    nav_template = (repo_root / "templates" / "nav.html").read_text()
    site, pages = load_site(repo_root), load_pages(repo_root)
    changed = []
    for path in find_targets(site_dir, pages):
        relative = path.relative_to(site_dir)
        if sync_block(path, "NAV", build_block(nav_template, **substitutions(relative, pages, site))):
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
