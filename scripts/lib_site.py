"""Single source of truth for site-wide constants (name, base URL, social
links) — data/site.json. Everything that needs these (sync_seo.py,
gen_sitemap.py, sync_nav.py, the about.html social block) reads them from
here instead of hardcoding its own copy.
"""
import json
import pathlib


def load_site(repo_root: pathlib.Path) -> dict:
    site = json.loads((repo_root / "data" / "site.json").read_text())
    site["default_og_image"] = site["base_url"] + site["og_image_path"]
    return site
