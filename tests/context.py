"""Puts scripts/ on sys.path so tests can `import lib_posts`, `import sync_nav`, etc.
without scripts/ needing to be a package."""
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
