"""Pure checks for where printed page breaks fall in the resume.

The input is the text of the printed PDF with a form feed between pages
(what `pdftotext` writes), plus the ordered headings and entries that the
resume HTML contains. A block is one heading or one entry. The rules:

  - an entry never splits across pages;
  - a heading never sits alone at the bottom of a page;
  - a short section never splits across pages, so it moves whole to the
    next page. Only a section marked long (Experience) may span pages,
    and it breaks only between entries.

Nothing here touches files or runs programs, so it tests on its own.
"""
import html
import re
from dataclasses import dataclass

from lib_html import strip_tags

PAGE_BREAK = "\f"

SECTION_RE = re.compile(
    r'<section class="resume-section(?P<long> resume-section-long)?">\s*'
    r'<h2 class="resume-heading">(?P<heading>.*?)</h2>(?P<body>.*?)</section>',
    re.DOTALL,
)
ENTRY_TITLE_RE = re.compile(r'class="entry-title">(?P<title>.*?)</(?:span|div)>', re.DOTALL)
LONE_HEADING_RE = re.compile(rf"[^\S{PAGE_BREAK}]*{PAGE_BREAK}")


class BlockNotFound(Exception):
    """A heading or entry from the HTML does not appear in the printed text."""


@dataclass(frozen=True)
class Block:
    kind: str
    text: str
    long: bool = False


def _plain(markup: str) -> str:
    return html.unescape(strip_tags(markup)).strip()


def blocks_from_html(page_html: str) -> list[Block]:
    blocks = []
    for section in SECTION_RE.finditer(page_html):
        blocks.append(Block("heading", _plain(section["heading"]), long=bool(section["long"])))
        blocks.extend(Block("entry", _plain(m["title"])) for m in ENTRY_TITLE_RE.finditer(section["body"]))
    return blocks


def find_starts(text: str, blocks: list[Block]) -> list[int]:
    starts, cursor = [], 0
    for block in blocks:
        match = re.compile(re.escape(block.text), re.IGNORECASE).search(text, cursor)
        if match is None:
            raise BlockNotFound(block.text)
        starts.append(match.start())
        cursor = match.end()
    return starts


def _spans(text: str, starts: list[int]) -> list[str]:
    ends = starts[1:] + [len(text)]
    return [text[start:end] for start, end in zip(starts, ends, strict=True)]


def _entry_problems(block: Block, span: str) -> list[str]:
    return [f'Entry "{block.text}" splits across pages.'] if PAGE_BREAK in span.rstrip() else []


def _heading_problems(block: Block, span: str) -> list[str]:
    after_heading = span[len(block.text):]
    if not LONE_HEADING_RE.match(after_heading):
        return []
    return [f'Heading "{block.text}" sits alone at the bottom of a page.']


BLOCK_CHECKS = {"entry": _entry_problems, "heading": _heading_problems}


def _section_problems(text: str, blocks: list[Block], starts: list[int]) -> list[str]:
    heading_starts = [(b, s) for b, s in zip(blocks, starts, strict=True) if b.kind == "heading"]
    ends = [s for _, s in heading_starts[1:]] + [len(text)]
    return [
        f'Section "{block.text}" splits across pages.'
        for (block, start), end in zip(heading_starts, ends, strict=True)
        if not block.long and PAGE_BREAK in text[start:end].rstrip()
    ]


def find_problems(text: str, blocks: list[Block]) -> list[str]:
    starts = find_starts(text, blocks)
    block_problems = [
        problem
        for block, span in zip(blocks, _spans(text, starts), strict=True)
        for problem in BLOCK_CHECKS[block.kind](block, span)
    ]
    return block_problems + _section_problems(text, blocks, starts)
