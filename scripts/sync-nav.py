#!/usr/bin/env python3
"""Keeps every page's <nav class="site-nav"> block in sync with templates/nav.html.

Single source of truth for the nav lives in templates/nav.html (with a {root}
placeholder for the relative path prefix). This script stamps that template into
every page between <!-- NAV:START --> / <!-- NAV:END --> markers, so the site
stays plain static HTML at serve time (no runtime include/fetch) while the nav
itself stays DRY at the source level. Run via scripts/sync-nav.sh, wired into
the pre-commit hook.
"""
import pathlib
import re

root_dir = pathlib.Path(__file__).resolve().parent.parent
nav_template = (root_dir / "templates" / "nav.html").read_text()

MARKER_RE = re.compile(
    r"<!-- NAV:START -->.*?<!-- NAV:END -->", re.DOTALL
)

targets = list(root_dir.glob("*.html")) + list(root_dir.glob("posts/*/index.html"))
# resume.html is a standalone print document with no site nav.
targets = [p for p in targets if p.name != "resume.html"]

changed = []
for path in targets:
    depth = len(path.relative_to(root_dir).parts) - 1
    rel_root = "../" * depth
    rendered = nav_template.format(root=rel_root).strip()
    block = f"<!-- NAV:START -->\n{rendered}\n<!-- NAV:END -->"

    text = path.read_text()
    if not MARKER_RE.search(text):
        print(f"skip (no NAV markers): {path.relative_to(root_dir)}")
        continue
    new_text = MARKER_RE.sub(block, text)
    if new_text != text:
        path.write_text(new_text)
        changed.append(path.relative_to(root_dir))

for p in changed:
    print(f"updated nav: {p}")
if not changed:
    print("nav already in sync")
