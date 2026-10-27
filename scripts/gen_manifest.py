#!/usr/bin/env python3
"""Generates site/manifest.webmanifest, the web app manifest, from data/site.json and data/theme.json.

The manifest names the site, its colors and its icons for browsers and phones. The icon files and
paths come from `icons` in data/site.json, and the colors from the light theme. Run directly
(`python3 scripts/gen_manifest.py`) or through `make sync`.
"""
import json
import pathlib

from lib_blocks import write_if_changed
from lib_site import REPO_ROOT, load_site, load_theme


def png_icon(entry: dict) -> dict:
    size = f"{entry['size']}x{entry['size']}"
    return {"src": entry["path"], "sizes": size, "type": "image/png"}


def icon_list(icons: dict) -> list[dict]:
    """The PNG icons, then the SVG icon at any size."""
    return [*map(png_icon, icons["manifest"]), {"src": icons["svg"], "sizes": "any", "type": "image/svg+xml"}]


def render_manifest(site: dict, theme: dict) -> str:
    background = theme["light"]["background"]
    data = {
        "name": site["name"],
        "short_name": site["name"],
        "description": site["summary"],
        "start_url": "/",
        "scope": "/",
        "display": "browser",
        "background_color": background,
        "theme_color": background,
        "icons": icon_list(site["icons"]),
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def sync(repo_root: pathlib.Path) -> bool:
    """Writes manifest.webmanifest if it changed. Returns whether it changed."""
    text = render_manifest(load_site(repo_root), load_theme(repo_root))
    return write_if_changed(repo_root / "site" / "manifest.webmanifest", text)


def main():
    if sync(REPO_ROOT):
        print("updated site/manifest.webmanifest")
    else:
        print("manifest.webmanifest already in sync")


if __name__ == "__main__":
    main()
