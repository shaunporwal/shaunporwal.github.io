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
