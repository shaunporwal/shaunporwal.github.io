"""Pure checks that the printed resume PDF carries the record and nothing else.

The inputs are the text that `pdftotext -raw` wrote for the PDF, the output of `pdfinfo` and
`pdffonts`, the resume view of the record, and the record. The checks:

  - every string that the resume view holds appears in the PDF text;
  - no string that the record holds off the resume appears in the PDF text;
  - the PDF is Letter size, has no more pages than data/pages.json allows, and embeds exactly the
    typefaces in site/fonts, so a font that failed to load, or a fallback font, cannot pass unseen.

Text is compared with its case, its white space and the live dcurves count removed, because the
PDF breaks lines, sets the headings in capitals and shows the live download count.

Nothing here touches files or runs programs, so it tests on its own.
"""
import re

from lib_record import contact_value, on_resume
from lib_resume import render_visible

COUNT_RE = re.compile(r"\d+k\+")
PAGES_RE = re.compile(r"^Pages:\s+(\d+)", re.MULTILINE)
SIZE_RE = re.compile(r"^Page size:\s+([\d.]+) x ([\d.]+) pts", re.MULTILINE)
SUBSET_PREFIX_RE = re.compile(r"^[A-Z]{6}\+")
LETTER_POINTS = (612.0, 792.0)
FONT_TABLE_HEADER_LINES = 2
REPLACEABLE = ("experience", "education", "projects", "skills")
FONT_FILE_RE = re.compile(r"^(?P<family>.+?)-latin-")


def squash(text: str) -> str:
    """The text in lower case, with the live count of dcurves downloads as `n` and no white space."""
    return re.sub(r"\s+", "", COUNT_RE.sub("n", text.lower()))


def page_count(pdfinfo: str) -> int:
    return int(PAGES_RE.search(pdfinfo).group(1))


def page_size(pdfinfo: str) -> tuple[float, float]:
    width, height = SIZE_RE.search(pdfinfo).groups()
    return float(width), float(height)


def is_letter(size: tuple[float, float]) -> bool:
    return size == LETTER_POINTS


def font_names(pdffonts: str) -> list[str]:
    """The names of the embedded fonts, without the six-letter prefix of a subset."""
    rows = pdffonts.splitlines()[FONT_TABLE_HEADER_LINES:]
    return sorted({SUBSET_PREFIX_RE.sub("", row.split()[0]) for row in rows if row.strip()})


def _experience_strings(entry: dict) -> list[str]:
    return [entry["title"], entry["org"], entry["period"], entry["place"], *entry["bullets"]]


def _project_strings(project: dict) -> list[str]:
    return [project["title"], project["links"], project["description"]]


def _education_strings(entry: dict) -> list[str]:
    honors = [entry["sub"]] if "sub" in entry else []
    return [entry["degree"], entry["school"], entry["period"], entry["place"], *honors]


SECTION_STRINGS = (
    ("experience", _experience_strings),
    ("projects", _project_strings),
    ("education", _education_strings),
)


def required_strings(view: dict) -> list[str]:
    """Every string that a reader of the resume sees, from the resume view of the record."""
    raw = [view["name"], *view["contact"]]
    for key, strings in SECTION_STRINGS:
        raw += [text for item in view[key] for text in strings(item)]
    raw += [text for pair in view["skills"].items() for text in pair]
    return [render_visible(text) for text in raw]


def _off_resume(items: list[dict], name: str) -> list[str]:
    return [item[name] for item in items if not on_resume(item) and name in item]


def _replaced_fields(items: list[dict]) -> list[str]:
    """The record wording of every field that a `resume` object replaces."""
    objects = [(item, item["resume"]) for item in items if isinstance(item.get("resume"), dict)]
    return [item[name] for item, fields in objects for name in fields if isinstance(item.get(name), str)]


def _bullets_shown_differently(record: dict) -> list[str]:
    bullets = [b for e in record["experience"] for g in e["groups"] for b in g["bullets"]]
    return [b["text"] for b in bullets if b.get("resume") is not True and "text" in b]


def _off_resume_contacts(record: dict, site: dict) -> list[str]:
    return [contact_value(item, site) for item in record["contact"] if not on_resume(item)]


def unlisted_strings(record: dict, site: dict, required: list[str]) -> list[str]:
    """The strings that the record holds off the resume, minus any that a resume string already holds."""
    candidates = [
        *_off_resume(record["experience"], "title"),
        *_off_resume(record["experience"], "org"),
        *_off_resume(record["education"], "degree"),
        *_off_resume(record["projects"], "title"),
        *_off_resume(record["skills"], "label"),
        *_off_resume_contacts(record, site),
        *_bullets_shown_differently(record),
        *[text for key in REPLACEABLE for text in _replaced_fields(record[key])],
    ]
    shown = squash(" ".join(required))
    return [render_visible(text) for text in candidates if squash(render_visible(text)) not in shown]


def missing_strings(pdf_text: str, required: list[str]) -> list[str]:
    haystack = squash(pdf_text)
    return [text for text in required if squash(text) not in haystack]


def leaked_strings(pdf_text: str, unlisted: list[str]) -> list[str]:
    haystack = squash(pdf_text)
    return [text for text in unlisted if squash(text) in haystack]


def _family(name: str) -> str:
    """The family of a font name, as lower-case letters and digits: Inter-SemiBold and inter-latin-600 give `inter`."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def shipped_families(font_files: list[str]) -> set[str]:
    """The families of the font files in site/fonts, named `<family>-latin-<weight>-<style>.woff2`."""
    matches = [FONT_FILE_RE.match(name) for name in font_files]
    return {_family(match["family"]) for match in matches if match}


def font_problems(embedded: list[str], font_files: list[str]) -> list[str]:
    shipped = shipped_families(font_files)
    used = {_family(name.split("-")[0]) for name in embedded}
    return [f"font not embedded: {name}" for name in sorted(shipped - used)] + [
        f"font not shipped: {name}" for name in sorted(used - shipped)
    ]
