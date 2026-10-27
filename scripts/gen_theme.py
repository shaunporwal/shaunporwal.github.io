#!/usr/bin/env python3
"""Generates the THEME token block in site/styles/site.css from data/theme.json.

The block holds the light colors, the fixed tokens (fonts, radius, ease, grid) and a
dark-mode override that follows the operating system. The rest of the stylesheet only
reads these tokens with var(). Run directly (`python3 scripts/gen_theme.py`) or
through `make sync`.
"""
import pathlib

from lib_blocks import sync_block, wrap
from lib_site import REPO_ROOT, load_theme


def declarations(tokens: dict, indent: str) -> list[str]:
    return [f"{indent}--{name}: {value};" for name, value in tokens.items()]


def scheme_block(selector: str, scheme: str, tokens: dict, indent: str) -> list[str]:
    inner = indent + "  "
    return [f"{indent}{selector} {{", f"{inner}color-scheme: {scheme};", *declarations(tokens, inner), f"{indent}}}"]


def render_tokens(theme: dict) -> str:
    root = scheme_block(":root", "light", {**theme["light"], **theme["fixed"]}, "")
    dark = scheme_block(":root", "dark", theme["dark"], "  ")
    return "\n".join([*root, "", "@media (prefers-color-scheme: dark) {", *dark, "}"])


def sync(repo_root: pathlib.Path) -> bool:
    """Writes the token block into site/styles/site.css. Returns whether the file changed."""
    block = wrap("THEME", render_tokens(load_theme(repo_root)), css=True)
    return sync_block(repo_root / "site" / "styles" / "site.css", "THEME", block)


def main():
    if sync(REPO_ROOT):
        print("updated site/styles/site.css theme block")
    else:
        print("theme block already in sync")


if __name__ == "__main__":
    main()
