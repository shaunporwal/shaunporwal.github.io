#!/usr/bin/env python3
"""Regenerates the ProfilePage JSON-LD block and the visible link buttons on site/about.html from data/site.json.

The profile URLs used to be hand-duplicated in two places on that one page. Stamped between
<!-- SOCIAL_JSONLD:START/END --> and <!-- SOCIAL_LINKS:START/END --> markers. The page holds no email
address: the buttons link the profiles and the booking page. Run directly
(`python3 scripts/sync_social.py`), wired into the pre-commit hook.
"""
import pathlib

from lib_blocks import replace_block, wrap, write_if_changed
from lib_html import NEW_TAB, PROFILE_TAB
from lib_jsonld import profile_page, script_tag
from lib_record import load_record
from lib_site import REPO_ROOT, load_site, profile_links

LINK_BUTTON = '      <a class="btn btn-outline" href="{href}"{tab}>{label}</a>'


def build_jsonld_block(site: dict, record: dict) -> str:
    return wrap("SOCIAL_JSONLD", script_tag(profile_page(site, record)))


def build_links_block(site: dict) -> str:
    profiles = [LINK_BUTTON.format(href=url, tab=PROFILE_TAB, label=label) for label, url in profile_links(site)]
    buttons = [*profiles, LINK_BUTTON.format(href=site["cal"], tab=NEW_TAB, label="Book a call")]
    return "<!-- SOCIAL_LINKS:START -->\n" + "\n".join(buttons) + "\n      <!-- SOCIAL_LINKS:END -->"


def apply_blocks(text: str, site: dict, record: dict) -> str:
    """Stamps every social block into text."""
    blocks = {"SOCIAL_JSONLD": build_jsonld_block(site, record), "SOCIAL_LINKS": build_links_block(site)}
    for name, block in blocks.items():
        text = replace_block(text, name, block) or text
    return text


def sync(repo_root: pathlib.Path) -> bool:
    """Updates site/about.html if either block changed. Returns whether it changed."""
    about_path = repo_root / "site" / "about.html"
    if not about_path.exists():
        return False
    text = apply_blocks(about_path.read_text(), load_site(repo_root), load_record(repo_root))
    return write_if_changed(about_path, text)


def main():
    if sync(REPO_ROOT):
        print("updated site/about.html social blocks")
    else:
        print("social blocks already in sync")


if __name__ == "__main__":
    main()
