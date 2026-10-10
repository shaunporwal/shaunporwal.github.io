#!/usr/bin/env python3
"""Regenerates the JSON-LD Person block and the visible social-links row on site/about.html from data/site.json.

Those github/x/linkedin/email URLs used to be hand-duplicated in two places
on that one page. Stamped between
<!-- SOCIAL_JSONLD:START/END --> and <!-- SOCIAL_LINKS:START/END --> markers.
Run directly (`python3 scripts/sync_social.py`), wired into the pre-commit
hook.
"""
import pathlib

from lib_blocks import replace_block, wrap, write_if_changed
from lib_site import REPO_ROOT, load_site


def build_jsonld_block(site: dict) -> str:
    body = (
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Person",\n'
        f'  "name": "{site["name"]}",\n'
        f'  "url": "{site["base_url"]}",\n'
        f'  "email": "mailto:{site["email"]}",\n'
        '  "sameAs": [\n'
        f'    "{site["github"]}",\n'
        f'    "{site["x"]}",\n'
        f'    "{site["linkedin"]}"\n'
        "  ]\n"
        "}"
    )
    return wrap("SOCIAL_JSONLD", f'<script type="application/ld+json">\n{body}\n</script>')


def build_links_block(site: dict) -> str:
    return (
        "<!-- SOCIAL_LINKS:START -->\n"
        f'      <a class="nav-link" href="{site["x"]}" target="_blank" rel="noopener">X</a>\n'
        f'      <a class="nav-link" href="{site["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a>\n'
        f'      <a class="nav-link" href="{site["github"]}" target="_blank" rel="noopener">GitHub</a>\n'
        f'      <a class="nav-link" href="mailto:{site["email"]}" target="_blank" rel="noopener">Email</a>\n'
        "      <!-- SOCIAL_LINKS:END -->"
    )


BLOCKS = (("SOCIAL_JSONLD", build_jsonld_block), ("SOCIAL_LINKS", build_links_block))


def apply_blocks(text: str, site: dict) -> str:
    """Stamps every social block into text."""
    for name, build in BLOCKS:
        new_text = replace_block(text, name, build(site))
        if new_text is not None:
            text = new_text
    return text


def sync(repo_root: pathlib.Path) -> bool:
    """Updates site/about.html if either block changed. Returns whether it changed."""
    about_path = repo_root / "site" / "about.html"
    if not about_path.exists():
        return False
    text = about_path.read_text()
    return write_if_changed(about_path, apply_blocks(text, load_site(repo_root)))


def main():
    if sync(REPO_ROOT):
        print("updated site/about.html social blocks")
    else:
        print("social blocks already in sync")


if __name__ == "__main__":
    main()
