#!/usr/bin/env python3
"""Generates the script list in scripts/AGENTS.md from the first sentence of each script's docstring or leading comment.

Each script describes itself once, in its own file. The list in
scripts/AGENTS.md is a generated copy, so it can never drift. Run directly
(`python3 scripts/gen_script_index.py`) or through `make sync`.
"""
import ast
import pathlib
import re

from lib_blocks import sync_block, wrap
from lib_site import REPO_ROOT

SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s")
MARKUP_RE = re.compile(r"(<!--.*?-->|<[^>]+>)")
SCRIPT_SUFFIXES = (".py", ".sh")


def first_sentence(text: str) -> str:
    paragraph = " ".join(text.strip().split("\n\n")[0].split())
    return SENTENCE_END_RE.split(paragraph)[0]


def python_summary(source: str) -> str:
    return first_sentence(ast.get_docstring(ast.parse(source)) or "")


def shell_summary(source: str) -> str:
    lines = source.splitlines()[1:]
    comments = [line.removeprefix("#").strip() for line in lines[: _comment_count(lines)]]
    return first_sentence(" ".join(comments))


def _comment_count(lines: list[str]) -> int:
    """How many lines at the top are comments."""
    return next((i for i, line in enumerate(lines) if not line.startswith("#")), len(lines))


SUMMARIES = {".py": python_summary, ".sh": shell_summary}


def as_markdown(summary: str) -> str:
    """Shows HTML tags and comments as code, so Markdown does not hide them."""
    return MARKUP_RE.sub(r"`\1`", summary)


def build_block(scripts_dir: pathlib.Path) -> str:
    paths = sorted(p for p in scripts_dir.iterdir() if p.suffix in SCRIPT_SUFFIXES)
    lines = [f"- `{p.name}`: {as_markdown(SUMMARIES[p.suffix](p.read_text()))}" for p in paths]
    return wrap("SCRIPTS", "\n".join(lines))


def sync(repo_root: pathlib.Path) -> bool:
    scripts_dir = repo_root / "scripts"
    return sync_block(scripts_dir / "AGENTS.md", "SCRIPTS", build_block(scripts_dir))


def main():
    if sync(REPO_ROOT):
        print("updated scripts/AGENTS.md script list")
    else:
        print("script list already in sync")


if __name__ == "__main__":
    main()
