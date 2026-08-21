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
import re

try:
    from lib_site import load_site
except ImportError:
    from scripts.lib_site import load_site

MARKER_RE = re.compile(r"<!-- NAV:START -->.*?<!-- NAV:END -->", re.DOTALL)


def render_nav(nav_template: str, **substitutions) -> str:
    return nav_template.format(**substitutions).strip()


def build_block(nav_template: str, **substitutions) -> str:
    return f"<!-- NAV:START -->\n{render_nav(nav_template, **substitutions)}\n<!-- NAV:END -->"


def inject(text: str, block: str) -> str | None:
    """Returns the updated text, or None if there's nothing to replace or no change."""
    if not MARKER_RE.search(text):
        return None
    new_text = MARKER_RE.sub(block, text)
    return new_text if new_text != text else None


def find_targets(site_dir: pathlib.Path) -> list[pathlib.Path]:
    targets = list(site_dir.glob("*.html")) + list(site_dir.glob("posts/*/index.html"))
    # resume.html is a standalone print document with no site nav.
    return [p for p in targets if p.name != "resume.html"]


def sync(repo_root: pathlib.Path) -> list[pathlib.Path]:
    site_dir = repo_root / "site"
    nav_template = (repo_root / "templates" / "nav.html").read_text()
    site = load_site(repo_root)

    changed = []
    for path in find_targets(site_dir):
        depth = len(path.relative_to(site_dir).parts) - 1
        block = build_block(nav_template, root="../" * depth, **site)
        text = path.read_text()
        new_text = inject(text, block)
        if new_text is not None:
            path.write_text(new_text)
            changed.append(path.relative_to(site_dir))
    return changed


def main():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    changed = sync(repo_root)
    for p in changed:
        print(f"updated nav: {p}")
    if not changed:
        print("nav already in sync")


if __name__ == "__main__":
    main()
