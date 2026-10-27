"""Single source of truth for site-wide constants (name, base URL, social
links) in data/site.json, for the top-level pages in data/pages.json, and for
the color and type tokens in data/theme.json.
Everything that needs these (sync_seo.py, gen_sitemap.py, sync_nav.py, the
about.html social block) reads them from here instead of hardcoding its own
copy.
"""
import json
import pathlib

from lib_schema import validate

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_site(repo_root: pathlib.Path) -> dict:
    """Reads data/site.json, validates it against data/site.schema.json, and
    adds the full default social image URL."""
    data_dir = repo_root / "data"
    site = json.loads((data_dir / "site.json").read_text())
    validate(site, json.loads((data_dir / "site.schema.json").read_text()))
    site["default_og_image"] = site["base_url"] + site["og_image_path"]
    return site


def load_pages(repo_root: pathlib.Path) -> list[dict]:
    """Reads data/pages.json and validates it against data/pages.schema.json."""
    data_dir = repo_root / "data"
    pages = json.loads((data_dir / "pages.json").read_text())
    validate(pages, json.loads((data_dir / "pages.schema.json").read_text()))
    return pages


def load_theme(repo_root: pathlib.Path) -> dict:
    """Reads data/theme.json and validates it against data/theme.schema.json."""
    data_dir = repo_root / "data"
    theme = json.loads((data_dir / "theme.json").read_text())
    validate(theme, json.loads((data_dir / "theme.schema.json").read_text()))
    return theme


def profile_links(site: dict) -> list[tuple[str, str]]:
    """(label, url) for each of the author's profiles, in display order."""
    return [(profile["label"], site[profile["key"]]) for profile in site["profiles"]]


def profile(site: dict, key: str) -> tuple[str, str]:
    """(label, url) of the profile with this key."""
    label = next(entry["label"] for entry in site["profiles"] if entry["key"] == key)
    return label, site[key]


def pdf_pages(pages: list[dict]) -> list[dict]:
    """The pages that name a `pdf` in data/pages.json: the publish step prints each one to that PDF."""
    return [page for page in pages if "pdf" in page]


def pdf_of(pages: list[dict], file: str) -> str:
    """The PDF name that the page `file` prints to."""
    return next(page["pdf"] for page in pdf_pages(pages) if page["file"] == file)


def pdf_max_pages(pages: list[dict], file: str) -> int:
    """The most pages the PDF that the page `file` prints to may have."""
    return next(page["pdf_max_pages"] for page in pdf_pages(pages) if page["file"] == file)


def page_url(base_url: str, file: str) -> str:
    return f"{base_url}/" if file == "index.html" else f"{base_url}/{file}"
