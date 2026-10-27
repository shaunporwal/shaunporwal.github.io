"""Puts scripts/ on sys.path so tests can `import lib_posts`, `import sync_nav`, etc.
without scripts/ needing to be a package. Also holds the shared test fixtures."""
import json
import pathlib
import struct
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib_images import PNG_SIGNATURE  # noqa: E402  (needs scripts/ on sys.path)

PNG_8X8 = PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 8, 8) + b"\x08\x06\x00\x00\x00"

CLIP_PICTURE = {
    "kind": "clip",
    "alt": "A clip of the Gadget app: a table of gadgets.",
    "still": "/media/projects/gadget.png",
    "mp4": "/media/projects/gadget.mp4",
    "webm": "/media/projects/gadget.webm",
}
LOGO_PICTURE = {"kind": "logo", "alt": "The Acme logo, a letter A.", "image": "/media/projects/acme.png"}
CURVE_PICTURE = {
    "kind": "decision-curve",
    "alt": "A sample decision curve: the model line stays above both reference lines.",
    "note": "Illustration only. Not real data.",
    "prevalence": 0.2,
    "separation": 1.5,
    "threshold": 0.15,
    "lines": {"model": "Model", "all": "Treat all", "none": "Treat none"},
}


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
        {"name": "Acme Company", "url": "https://acme.example/", "summary": "Makes widgets.", "picture": LOGO_PICTURE},
        {"name": "Gadget", "url": "https://gadget.example/", "summary": "Makes gadgets.", "picture": CLIP_PICTURE},
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
     "sitemap": True, "nav": False, "menu": {"label": "Resume", "new_tab": True}, "pdf": "resume.pdf"},
]


ALIVE_TOKENS = {
    "glow-tint": "rgba(1, 2, 3, 0.1)",
    "glow-on-primary": "rgba(255, 255, 255, 0.2)",
    "sheen": "rgba(255, 255, 255, 0.9)",
    "shadow-raise": "0 0 0 black",
    "shadow-raise-primary": "0 0 0 black",
    "shadow-header": "0 0 0 black",
}
FAKE_THEME = {
    "light": {
        **ALIVE_TOKENS,
        "background": "#ffffff", "foreground": "#111111", "card": "#ffffff", "secondary": "#eeeeee",
        "muted-foreground": "#555555", "border": "#dddddd", "input": "#cccccc",
        "primary": "#aa3300", "primary-foreground": "#ffffff", "ring": "#aa3300",
    },
    "dark": {
        **ALIVE_TOKENS,
        "background": "#000000", "foreground": "#eeeeee", "card": "#111111", "secondary": "#222222",
        "muted-foreground": "#aaaaaa", "border": "#333333", "input": "#444444",
        "primary": "#ff9966", "primary-foreground": "#000000", "ring": "#ff9966",
    },
    "fixed": {
        "font-sans": "sans-serif", "font-serif": "serif", "radius": "0.5rem",
        "ease-out": "ease-out", "shell": "72rem", "measure": "40rem", "shadow-menu": "0 0 0 black",
        "glow-size": "220px", "motion-glow": "400ms", "motion-follow": "220ms", "sheen-duration": "6s",
    },
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


def write_project_media(site_dir: pathlib.Path) -> None:
    """Writes the still and the logo that LOGO_PICTURE and CLIP_PICTURE name, as 8 by 8 PNG files."""
    projects_dir = site_dir / "media" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    for name in ("acme.png", "gadget.png"):
        (projects_dir / name).write_bytes(PNG_8X8)


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
