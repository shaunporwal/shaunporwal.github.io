#!/usr/bin/env python3
"""Keeps every page's footer block in sync with templates/footer.html.

The footer holds the links to the author's other profiles, the feed and llms.txt, and the
script tag that loads the motion script. It goes between <!-- FOOTER:START --> / <!-- FOOTER:END -->
markers just before </body>. A page with no markers gets the block added. Pages follow the same rules
as the header: a page with `nav` off in data/pages.json gets no footer.
Run directly (`python3 scripts/sync_footer.py`), wired into the pre-commit hook.
"""
import pathlib

from lib_blocks import replace_block, wrap, write_if_changed
from lib_html import PROFILE_TAB
from lib_site import REPO_ROOT, load_pages, load_site, profile_links
from sync_nav import find_targets, page_root

BODY_END = "</body>"
PROFILE_ANCHOR = '      <a href="{url}"{tab}>{label}</a>'


def profile_anchors(site: dict) -> str:
    return "\n".join(PROFILE_ANCHOR.format(url=url, tab=PROFILE_TAB, label=label) for label, url in profile_links(site))


def footer_values(site: dict, root: str) -> dict:
    """The values the footer template fills in: the site facts, the page root and the profile links."""
    return {**site, "root": root, "profile_anchors": profile_anchors(site)}


def build_block(footer_template: str, **substitutions) -> str:
    return wrap("FOOTER", footer_template.format(**substitutions).strip())


def inject(text: str, block: str) -> str | None:
    """text with the footer block in place: replaced if present, else added before </body>.
    None if the page has neither."""
    replaced = replace_block(text, "FOOTER", block)
    if replaced is not None:
        return replaced
    if BODY_END not in text:
        return None
    return text.replace(BODY_END, block + "\n" + BODY_END, 1)


def write_footer(path: pathlib.Path, block: str) -> bool:
    new_text = inject(path.read_text(), block)
    return new_text is not None and write_if_changed(path, new_text)


def sync(repo_root: pathlib.Path) -> list[pathlib.Path]:
    site_dir = repo_root / "site"
    footer_template = (repo_root / "templates" / "footer.html").read_text()
    site, pages = load_site(repo_root), load_pages(repo_root)
    changed = []
    for path in find_targets(site_dir, pages):
        relative = path.relative_to(site_dir)
        block = build_block(footer_template, **footer_values(site, page_root(relative, pages)))
        if write_footer(path, block):
            changed.append(relative)
    return changed


def main():
    changed = sync(REPO_ROOT)
    for p in changed:
        print(f"updated footer: {p}")
    if not changed:
        print("footer already in sync")


if __name__ == "__main__":
    main()
