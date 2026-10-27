"""Puts scripts/ on sys.path so tests can `import lib_posts`, `import sync_nav`, etc.
without scripts/ needing to be a package. Also holds the shared test fixtures."""
import json
import pathlib
import sys
import tempfile
import unittest

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
    "profiles": [
        {"label": "GitHub", "key": "github"},
        {"label": "X", "key": "x"},
        {"label": "LinkedIn", "key": "linkedin"},
    ],
    "og_image_path": "/media/avatar.jpg",
    "summary": "A test summary.",
    "job_title": "Test engineer",
    "avatar_path": "/media/avatar.jpg",
    "work": {"eyebrow": "Work", "title": "What I build"},
    "icons": {
        "svg": "/media/favicon.svg",
        "png": "/media/favicon-48.png",
        "apple": "/media/apple-touch-icon.png",
        "manifest": [{"path": "/media/icon-192.png", "size": 192}, {"path": "/media/icon-512.png", "size": 512}],
    },
    "hero": {"lead": "A test lead."},
    "projects": [
        {"name": "Acme Company", "url": "https://acme.example/", "summary": "Makes widgets."},
        {"name": "Gadget", "url": "https://gadget.example/", "summary": "Makes gadgets."},
    ],
    "seo": {
        "crawlers": ["*", "TestBot"],
        "agents": {
            "summary": "A test site with no form.",
            "may": ["Read each public page."],
            "may_not": ["Post a form."],
        },
    },
}


FAKE_PAGES = [
    {"file": "index.html", "title": "{name}", "description": "Home of {name}.", "og_type": "website",
     "sitemap": True, "nav": True},
    {"file": "about.html", "title": "About — {name}", "description": "About {name}.", "og_type": "website",
     "sitemap": True, "nav": True, "menu": {"label": "About", "new_tab": False}},
    {"file": "resume.html", "title": "{name} — Resume", "description": "Resume of {name}.", "og_type": "website",
     "sitemap": True, "nav": False, "menu": {"label": "Resume", "new_tab": True}},
]


FAKE_THEME = {
    "light": {"background": "#ffffff", "foreground": "#111111", "card": "#ffffff", "secondary": "#eeeeee",
              "muted-foreground": "#555555", "border": "#dddddd", "input": "#cccccc",
              "primary": "#aa3300", "primary-foreground": "#ffffff", "ring": "#aa3300"},
    "dark": {"background": "#000000", "foreground": "#eeeeee", "card": "#111111", "secondary": "#222222",
             "muted-foreground": "#aaaaaa", "border": "#333333", "input": "#444444",
             "primary": "#ff9966", "primary-foreground": "#000000", "ring": "#ff9966"},
    "fixed": {"font-sans": "sans-serif", "font-serif": "serif", "radius": "0.5rem",
              "ease-out": "ease-out", "shell": "72rem", "measure": "40rem"},
}


def write_fake_site_data(repo_root: pathlib.Path) -> None:
    """Writes data/site.json, data/pages.json, data/theme.json, and the real schemas under
    repo_root, for tests of scripts that load them via lib_site."""
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "site.json").write_text(json.dumps(FAKE_SITE))
    (data_dir / "pages.json").write_text(json.dumps(FAKE_PAGES))
    (data_dir / "theme.json").write_text(json.dumps(FAKE_THEME))
    for schema in ("site.schema.json", "pages.schema.json", "theme.schema.json"):
        (data_dir / schema).write_text((REPO_ROOT / "data" / schema).read_text())


def temp_repo(test: unittest.TestCase) -> pathlib.Path:
    """A temporary repo with site/ and the fake site data. The test cleans it up."""
    repo_root = pathlib.Path(test.enterContext(tempfile.TemporaryDirectory()))
    (repo_root / "site").mkdir()
    write_fake_site_data(repo_root)
    return repo_root


SAMPLE_RECORD = {
    "contact": [
        {"label": "Location", "value": "City, ST", "resume": True},
        {"label": "Email", "site": "email", "resume": True},
        {"label": "GitHub", "site": "github"},
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
