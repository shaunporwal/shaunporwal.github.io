#!/usr/bin/env python3
"""Generates site/media/favicon.svg, the site icon, from the light colors in data/theme.json.

The icon is a rounded square in the primary color with a white-on-accent S drawn as one stroke, so it needs no font.
The PNG icons (favicon-48, apple-touch-icon, icon-192, icon-512) are rendered from this file; see site/AGENTS.md.
Run directly (`python3 scripts/gen_icon.py`) or through `make sync`.
"""
import pathlib

from lib_blocks import write_if_changed
from lib_site import REPO_ROOT, load_theme

S_PATH = " ".join(
    (
        "M22.2 10.2C20.9 8.6 18.8 7.8 16.4 7.8c-3.3 0-5.5 1.7-5.5 4.1 0 2.8 2.7 3.5 5.6 4.3",
        "3 .8 5.6 1.7 5.6 4.5 0 2.6-2.3 4.4-5.8 4.4-2.7 0-5-1-6.4-2.8",
    )
)
STROKE = 'fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round"'


def render_icon(theme: dict) -> str:
    light = theme["light"]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">\n'
        f'  <rect width="32" height="32" rx="7" fill="{light["primary"]}"/>\n'
        f'  <path d="{S_PATH}" {STROKE.format(color=light["primary-foreground"])}/>\n'
        "</svg>\n"
    )


def sync(repo_root: pathlib.Path) -> bool:
    """Writes favicon.svg if it changed. Returns whether it changed."""
    path = repo_root / "site" / "media" / "favicon.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    return write_if_changed(path, render_icon(load_theme(repo_root)))


def main():
    if sync(REPO_ROOT):
        print("updated site/media/favicon.svg")
    else:
        print("favicon.svg already in sync")


if __name__ == "__main__":
    main()
