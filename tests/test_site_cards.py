"""Facts that must hold for the Work cards on the built home page: every card has a picture whose files exist,
the cards match the data, and the card text keeps the brand and honesty rules."""
import pathlib
import re
import unittest

import context
import sync_home
from lib_blocks import wrap
from lib_site import load_site

SITE_DIR = context.REPO_ROOT / "site"
INDEX = SITE_DIR / "index.html"
WORK_RE = re.compile(r"<!-- WORK:START -->.*?<!-- WORK:END -->", re.DOTALL)
MAX_SUMMARY_CHARACTERS = 100
FILE_KEYS = ("still", "mp4", "webm", "image")
# Claims that a card must never make: compliance, prices and finished hardware.
CLAIMS_TO_AVOID = ("part 11", "e2500", "compliant", "certified", "$", "hardware is built", "shipping")


def work_block() -> str:
    return WORK_RE.search(INDEX.read_text()).group(0)


def media_files(site: dict) -> list[pathlib.Path]:
    pictures = [project["picture"] for project in site["projects"]]
    return [SITE_DIR / picture[key].lstrip("/") for picture in pictures for key in FILE_KEYS if key in picture]


def project_named(site: dict, name: str) -> dict:
    return next(project for project in site["projects"] if project["name"] == name)


class TestWorkCards(unittest.TestCase):
    def setUp(self):
        self.site = load_site(context.REPO_ROOT)

    def test_the_home_page_block_is_what_the_generator_writes(self):
        block = wrap("WORK", sync_home.render_work(self.site, SITE_DIR))
        self.assertEqual(work_block(), block)

    def test_every_picture_file_exists(self):
        missing = [str(path) for path in media_files(self.site) if not path.is_file()]
        self.assertEqual(missing, [])

    def test_every_project_has_a_picture_with_alt_text(self):
        for project in self.site["projects"]:
            self.assertGreater(len(project["picture"]["alt"]), 20, project["name"])

    def test_each_summary_is_short(self):
        for project in self.site["projects"]:
            self.assertLessEqual(len(project["summary"]), MAX_SUMMARY_CHARACTERS, project["name"])

    def test_the_cards_never_say_software(self):
        self.assertNotIn("software", work_block().lower())

    def test_the_cards_hold_no_email_address(self):
        self.assertNotIn(self.site["email"], work_block())
        self.assertNotIn("mailto:", work_block())

    def test_the_cards_make_no_claim_the_brand_rules_forbid(self):
        text = work_block().lower()
        self.assertEqual([claim for claim in CLAIMS_TO_AVOID if claim in text], [])

    def test_the_dcurves_card_keeps_the_approved_wording(self):
        summary = project_named(self.site, "dcurves")["summary"]
        self.assertIn("I created it at Memorial Sloan Kettering Cancer Center", summary)

    def test_the_bench_bridge_card_says_demo_and_sample_data(self):
        text = project_named(self.site, "Bench Bridge")["picture"]["alt"].lower()
        self.assertIn("demo", text)
        self.assertIn("sample data", text)

    def test_the_curve_says_in_words_that_it_is_not_real_data(self):
        self.assertIn("Illustration only. Not real data.", work_block())


if __name__ == "__main__":
    unittest.main()
