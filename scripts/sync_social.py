#!/usr/bin/env python3
"""Regenerates the JSON-LD Person block and the visible social-links row on
site/about.html from data/site.json — those github/x/linkedin/email URLs
used to be hand-duplicated in two places on that one page. Stamped between
<!-- SOCIAL_JSONLD:START/END --> and <!-- SOCIAL_LINKS:START/END --> markers.
Run directly (`python3 scripts/sync_social.py`), wired into the pre-commit
hook.
"""
import pathlib
import re

try:
    from lib_site import load_site
except ImportError:
    from scripts.lib_site import load_site

JSONLD_MARKER_RE = re.compile(r"<!-- SOCIAL_JSONLD:START -->.*?<!-- SOCIAL_JSONLD:END -->", re.DOTALL)
LINKS_MARKER_RE = re.compile(r"<!-- SOCIAL_LINKS:START -->.*?<!-- SOCIAL_LINKS:END -->", re.DOTALL)


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
    return (
        "<!-- SOCIAL_JSONLD:START -->\n"
        '<script type="application/ld+json">\n'
        f"{body}\n"
        "</script>\n"
        "<!-- SOCIAL_JSONLD:END -->"
    )


def build_links_block(site: dict) -> str:
    return (
        "<!-- SOCIAL_LINKS:START -->\n"
        f'      <a class="nav-link" href="{site["x"]}" target="_blank" rel="noopener">X</a>\n'
        f'      <a class="nav-link" href="{site["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a>\n'
        f'      <a class="nav-link" href="{site["github"]}" target="_blank" rel="noopener">Github</a>\n'
        f'      <a class="nav-link" href="mailto:{site["email"]}" target="_blank" rel="noopener">Email</a>\n'
        "      <!-- SOCIAL_LINKS:END -->"
    )


def inject(text: str, marker_re: re.Pattern, block: str) -> str | None:
    if not marker_re.search(text):
        return None
    new_text = marker_re.sub(block, text)
    return new_text if new_text != text else None


BLOCKS = ((JSONLD_MARKER_RE, build_jsonld_block), (LINKS_MARKER_RE, build_links_block))


def apply_blocks(text: str, site: dict) -> str:
    """Stamps every social block into text."""
    for marker_re, build in BLOCKS:
        new_text = inject(text, marker_re, build(site))
        if new_text is not None:
            text = new_text
    return text


def sync(repo_root: pathlib.Path) -> bool:
    """Updates site/about.html if either block changed. Returns whether it changed."""
    about_path = repo_root / "site" / "about.html"
    if not about_path.exists():
        return False
    text = about_path.read_text()
    new_text = apply_blocks(text, load_site(repo_root))
    if new_text == text:
        return False
    about_path.write_text(new_text)
    return True


def main():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    if sync(repo_root):
        print("updated site/about.html social blocks")
    else:
        print("social blocks already in sync")


if __name__ == "__main__":
    main()
