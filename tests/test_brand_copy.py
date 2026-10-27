"""The built site never calls Junto a software company. data/site.json names the phrases to avoid."""
import pathlib
import unittest

import context
from lib_site import load_site

SITE_DIR = context.REPO_ROOT / "site"
DISCOVERY_FILES = ("llms.txt", "agents.txt", "feed.xml", "manifest.webmanifest")


def copy_files() -> list[pathlib.Path]:
    pages = sorted(path for path in SITE_DIR.glob("*.html") if path.name != "resume.html")
    return pages + [SITE_DIR / name for name in DISCOVERY_FILES]


def phrases_found(text: str, phrases: list[str]) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in phrases if phrase.lower() in lowered]


def offenders(files: list[pathlib.Path], phrases: list[str]) -> list[str]:
    return [f"{path.name}: {phrase}" for path in files for phrase in phrases_found(path.read_text(), phrases)]


class TestPhrasesFound(unittest.TestCase):
    def test_finds_a_phrase_in_any_case(self):
        self.assertEqual(phrases_found("Builds Software for chemistry labs", ["builds software"]), ["builds software"])

    def test_finds_nothing_in_clean_text(self):
        self.assertEqual(phrases_found("It modernizes chemistry labs.", ["builds software"]), [])


class TestBrandCopy(unittest.TestCase):
    def test_the_data_names_the_phrases_to_avoid(self):
        self.assertGreaterEqual(len(load_site(context.REPO_ROOT)["brand"]["avoid"]), 3)

    def test_no_built_page_or_discovery_file_uses_one(self):
        self.assertEqual(offenders(copy_files(), load_site(context.REPO_ROOT)["brand"]["avoid"]), [])


if __name__ == "__main__":
    unittest.main()
