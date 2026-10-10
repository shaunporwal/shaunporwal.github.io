"""Puts scripts/ on sys.path so tests can `import lib_posts`, `import sync_nav`, etc.
without scripts/ needing to be a package."""
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


FAKE_SITE = {
    "name": "Test Person",
    "base_url": "https://example.com",
    "email": "test@example.com",
    "github": "https://github.com/testperson",
    "x": "https://x.com/testperson",
    "linkedin": "https://linkedin.com/in/testperson",
    "cal": "https://cal.com/testperson",
    "og_image_path": "/media/avatar.jpg",
}


def write_fake_site_json(repo_root: pathlib.Path) -> None:
    """Writes a data/site.json fixture under repo_root, for tests of scripts
    that load site-wide config via lib_site.load_site()."""
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "site.json").write_text(json.dumps(FAKE_SITE))


SAMPLE_RECORD = {
    "name": "Test Person",
    "contact": [
        {"label": "Location", "value": "City, ST", "resume": True},
        {"label": "Phone", "value": "555"},
    ],
    "experience": [
        {
            "title": "Engineer",
            "org": "Acme Company",
            "start": "2020-01",
            "end": "present",
            "location": "City, ST",
            "groups": [
                {"bullets": [{"text": "Full detail", "resume": "Short **detail**"}, {"text": "Record only"}]},
                {"heading": "Project", "resume": "Group summary", "bullets": [{"text": "Kept as is", "resume": True}]},
                {"bullets": [{"resume": "Resume only"}]},
            ],
            "resume": {"org": "Acme"},
        },
        {
            "title": "Intern",
            "org": "Hidden Co",
            "start": "2019-06",
            "end": "2019-06",
            "location": "Town, ST",
            "groups": [{"bullets": [{"text": "Not on the resume"}]}],
        },
    ],
    "education": [
        {
            "degree": "Bachelor's in Widgetry",
            "school": "Acme University",
            "end": "2019-05",
            "location": "City, ST",
            "honors": "Cum laude",
            "resume": {"degree": "B.S., Widgetry"},
        }
    ],
    "projects": [
        {"title": "Widget", "links": ["[widget.com](https://example.com)"], "description": "A widget.", "resume": True},
        {"title": "Gadget", "links": [], "bullets": [{"text": "Record only"}]},
    ],
    "skills": [
        {"label": "Programming (Proficient)", "text": "Python, Go", "resume": {"label": "Programming"}},
        {"label": "Visualization", "text": "ggplot2"},
        {"label": "Languages", "derive": "languages", "resume": True},
    ],
    "languages": [
        {"name": "English", "level": "native"},
        {"name": "Mandarin Chinese", "level": "fluent"},
        {"name": "Hindi", "level": "fluent"},
        {"name": "Japanese", "level": "conversational"},
    ],
    "publications": {"notes": [], "items": ["A paper"]},
}


def write_record_fixture(repo_root: pathlib.Path, record: dict) -> None:
    """Writes data/experiences.json and the real schema under repo_root, for
    tests of scripts that load the record via lib_record.load_record()."""
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "experiences.json").write_text(json.dumps(record))
    schema = (REPO_ROOT / "data" / "experiences.schema.json").read_text()
    (data_dir / "experiences.schema.json").write_text(schema)
