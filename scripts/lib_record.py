"""Loads data/experiences.json, the single record of every experience fact,
and builds the resume view of it.

The `resume` key on an item is the switch that puts it on the resume:
- `true` shows the item as it is.
- A string (on a bullet) or an object of fields (on an entry) replaces the
  wording on the resume only. The record keeps its own wording.
- A group's `resume` string is one resume bullet that sums up the group.

resume_view() returns the same shape that gen_resume.py renders:
{name, contact, experience, projects, education, skills}.
"""
import calendar
import itertools
import json
import operator
import pathlib

from lib_schema import validate

PERIOD_STYLES = {
    "resume": {"months": calendar.month_abbr, "range": " – ", "present": "Present"},
    "record": {"months": calendar.month_name, "range": " to ", "present": "Present"},
}

META_SEPARATOR = " · "
LINK_SEPARATOR = " · "


def load_record(repo_root: pathlib.Path) -> dict:
    """Reads the record and validates it against data/experiences.schema.json."""
    data_dir = repo_root / "data"
    record = json.loads((data_dir / "experiences.json").read_text())
    validate(record, json.loads((data_dir / "experiences.schema.json").read_text()))
    return record


def format_month(month: str, style: str) -> str:
    style_config = PERIOD_STYLES[style]
    if month == "present":
        return style_config["present"]
    year, number = month.split("-")
    return f"{style_config['months'][int(number)]} {year}"


def format_period(start: str, end: str, style: str) -> str:
    if start == end:
        return format_month(start, style)
    return format_month(start, style) + PERIOD_STYLES[style]["range"] + format_month(end, style)


def on_resume(item: dict) -> bool:
    return "resume" in item


def resume_fields(item: dict) -> dict:
    """The item with its resume overrides applied."""
    overrides = item["resume"] if isinstance(item["resume"], dict) else {}
    return {**item, **overrides}


def bullet_text(bullet: dict) -> str:
    return bullet["text"] if bullet["resume"] is True else bullet["resume"]


def group_bullets(group: dict) -> list[str]:
    summary = [group["resume"]] if "resume" in group else []
    return summary + [bullet_text(b) for b in group["bullets"] if on_resume(b)]


def _resume_experience(entry: dict) -> dict:
    fields = resume_fields(entry)
    period = format_period(entry["start"], entry["end"], "resume")
    return {
        "title": fields["title"],
        "org": fields["org"],
        "meta": period + META_SEPARATOR + entry["location"],
        "bullets": [text for group in entry["groups"] for text in group_bullets(group)],
    }


def _resume_education(entry: dict) -> dict:
    fields = resume_fields(entry)
    view = {
        "degree": fields["degree"],
        "school": fields["school"],
        "meta": format_month(entry["end"], "resume") + META_SEPARATOR + entry["location"],
    }
    if "honors" in entry:
        view["sub"] = entry["honors"]
    return view


def _resume_project(project: dict) -> dict:
    fields = resume_fields(project)
    links = fields["links"]
    return {
        "title": fields["title"],
        "links": links if isinstance(links, str) else LINK_SEPARATOR.join(links),
        "description": fields["description"],
    }


def format_languages(languages: list[dict]) -> str:
    """English (native); Mandarin Chinese, Hindi (fluent) — consecutive
    languages at the same level share one group."""
    groups = itertools.groupby(languages, key=operator.itemgetter("level"))
    return "; ".join(f"{', '.join(language['name'] for language in group)} ({level})" for level, group in groups)


DERIVED_SKILLS = {"languages": format_languages}


def skill_text(skill: dict, record: dict) -> str:
    if "derive" in skill:
        return DERIVED_SKILLS[skill["derive"]](record[skill["derive"]])
    return skill["text"]


def _resume_skills(record: dict) -> dict:
    skills = {}
    for skill in filter(on_resume, record["skills"]):
        fields = resume_fields(skill)
        skills[fields["label"]] = fields["text"] if "text" in fields else skill_text(skill, record)
    return skills


def resume_view(record: dict) -> dict:
    return {
        "name": record["name"],
        "contact": [c["value"] for c in filter(on_resume, record["contact"])],
        "experience": [_resume_experience(e) for e in filter(on_resume, record["experience"])],
        "projects": [_resume_project(p) for p in filter(on_resume, record["projects"])],
        "education": [_resume_education(e) for e in filter(on_resume, record["education"])],
        "skills": _resume_skills(record),
    }
