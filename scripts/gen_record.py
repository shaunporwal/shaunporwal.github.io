#!/usr/bin/env python3
"""Generates the <!-- RECORD:START --> block in docs/all-experiences.md from
data/experiences.json, the single record behind the resume.

The record shows every item with its own wording, whether or not the item is
on the resume. Resume-only wording (a `resume` string or object) never shows
here. Wired into .githooks/pre-commit and `make sync`.
"""
import pathlib
import re

try:
    from lib_record import format_month, format_period, load_record
except ImportError:
    from scripts.lib_record import format_month, format_period, load_record

MARKER_RE = re.compile(r"<!-- RECORD:START -->.*?<!-- RECORD:END -->", re.DOTALL)
RECORD_PATH = pathlib.Path("docs") / "all-experiences.md"


def _joined(parts: list[str], separator: str = "\n") -> str:
    """Joins the parts that are not empty."""
    return separator.join(part for part in parts if part)


def _bullets(bullets: list[dict]) -> str:
    return _joined([f"- {b['text']}" for b in bullets if "text" in b])


def _group(group: dict) -> str:
    bullets = _bullets(group["bullets"])
    return _joined([group.get("heading", ""), bullets]) if bullets else ""


def _experience(entry: dict) -> str:
    head = _joined([
        f"### {entry['org']} — {entry['title']}",
        f"{format_period(entry['start'], entry['end'], 'record')} | {entry['location']}",
        *entry.get("notes", []),
    ])
    groups = [_group(group) for group in entry["groups"]]
    return _joined([head, *groups, _joined(entry.get("footer", []))], "\n\n")


def _education(entry: dict) -> str:
    return _joined([
        f"**{entry['school']}**",
        entry["degree"],
        f"Completed: {format_month(entry['end'], 'record')} | {entry['location']}",
        entry.get("honors", ""),
    ])


def _project(project: dict) -> str:
    period = f" ({project['period']})" if "period" in project else ""
    return _joined([
        f"**{project['title']}**{period}",
        " | ".join(project["links"]),
        project.get("description", ""),
        _bullets(project.get("bullets", [])),
    ])


def _skills(skills: list[dict]) -> str:
    return _joined([f"**{s['label']}:** {s['text']}" for s in skills if "text" in s])


def _language(language: dict) -> str:
    note = f" ({language['note']})" if "note" in language else ""
    return f"- {language['name']} — {language['level'].capitalize()}{note}"


def _publications(publications: dict) -> str:
    items = _joined([f"- {item}" for item in publications["items"]])
    return _joined([_joined(publications["notes"]), items], "\n\n")


def _section(heading: str, body: str) -> str:
    return f"## {heading}\n\n{body}"


def build_block(record: dict) -> str:
    contact = " | ".join(f"{c['label']}: {c['value']}" for c in record["contact"])
    sections = [
        _section("Professional Experience", "\n\n".join(map(_experience, record["experience"]))),
        _section("Education", "\n\n".join(map(_education, record["education"]))),
        _section("Projects & Notable Achievements", "\n\n".join(map(_project, record["projects"]))),
        _section("Skills", _skills(record["skills"])),
        _section("Languages", "\n".join(map(_language, record["languages"]))),
        _section("Publications", _publications(record["publications"])),
    ]
    body = "\n\n".join([contact, *sections])
    return f"<!-- RECORD:START -->\n{body}\n<!-- RECORD:END -->"


def sync(repo_root: pathlib.Path) -> bool:
    path = repo_root / RECORD_PATH
    text = path.read_text()
    match = MARKER_RE.search(text)
    if not match:
        return False
    # A splice, not MARKER_RE.sub: sub would read backslashes in the record as escapes.
    new_text = text[: match.start()] + build_block(load_record(repo_root)) + text[match.end():]
    if new_text == text:
        return False
    path.write_text(new_text)
    return True


def main():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    if sync(repo_root):
        print(f"updated {RECORD_PATH} from data/experiences.json")
    else:
        print("record already in sync")


if __name__ == "__main__":
    main()
