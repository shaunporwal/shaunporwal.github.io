"""Facts that must hold for the built site: each page has one main landmark that the skip link
targets, and no discovery file or structured data holds the email address."""
import json
import pathlib
import re
import unittest

import context

SITE_DIR = context.REPO_ROOT / "site"
DISCOVERY_FILES = (
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "llms-full.txt",
    "agents.txt",
    ".well-known/agents.json",
    "feed.xml",
    "manifest.webmanifest",
)
MAIN_LANDMARK = re.compile(r'<main id="main"[ >]')
JSON_LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


def site_pages(site_dir: pathlib.Path) -> list[pathlib.Path]:
    return sorted(site_dir.rglob("*.html"))


def pages_without_main(pages: list[pathlib.Path]) -> list[str]:
    return [str(page) for page in pages if not MAIN_LANDMARK.search(page.read_text())]


def structured_data(page: pathlib.Path) -> str:
    return "\n".join(JSON_LD.findall(page.read_text()))


def files_with(text: str, paths: list[pathlib.Path], read) -> list[str]:
    return [str(path) for path in paths if text in read(path)]


def read_text(path: pathlib.Path) -> str:
    return path.read_text()


def email_of_site() -> str:
    return json.loads((context.REPO_ROOT / "data" / "site.json").read_text())["email"]


class TestSiteContract(unittest.TestCase):
    def test_finds_a_page_without_main(self):
        site_dir = context.temp_repo(self) / "site"
        (site_dir / "a.html").write_text('<main id="main" class="page">x</main>')
        (site_dir / "b.html").write_text("<main>x</main>")
        self.assertEqual(len(pages_without_main(site_pages(site_dir))), 1)

    def test_every_page_has_the_main_landmark(self):
        self.assertEqual(pages_without_main(site_pages(SITE_DIR)), [])

    def test_no_discovery_file_holds_the_email(self):
        paths = [SITE_DIR / name for name in DISCOVERY_FILES]
        self.assertEqual(files_with(email_of_site(), paths, read_text), [])

    def test_no_structured_data_holds_the_email(self):
        self.assertEqual(files_with(email_of_site(), site_pages(SITE_DIR), structured_data), [])

    def test_the_about_page_holds_no_email(self):
        self.assertNotIn(email_of_site(), (SITE_DIR / "about.html").read_text())


if __name__ == "__main__":
    unittest.main()
