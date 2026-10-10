"""Single source of truth for site-wide constants (name, base URL, social
links) in data/site.json, and for the top-level pages in data/pages.json.
Everything that needs these (sync_seo.py, gen_sitemap.py, sync_nav.py, the
about.html social block) reads them from here instead of hardcoding its own
copy.
"""
import json
import pathlib

from lib_schema import validate

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_site(repo_root: pathlib.Path) -> dict:
    site = json.loads((repo_root / "data" / "site.json").read_text())
    site["default_og_image"] = site["base_url"] + site["og_image_path"]
    return site


def load_pages(repo_root: pathlib.Path) -> list[dict]:
    """Reads data/pages.json and validates it against data/pages.schema.json."""
    data_dir = repo_root / "data"
    pages = json.loads((data_dir / "pages.json").read_text())
    validate(pages, json.loads((data_dir / "pages.schema.json").read_text()))
    return pages


def page_url(base_url: str, file: str) -> str:
    return f"{base_url}/" if file == "index.html" else f"{base_url}/{file}"
