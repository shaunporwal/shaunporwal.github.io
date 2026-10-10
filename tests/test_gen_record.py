import pathlib
import unittest

import context  # noqa: F401
import gen_record

SAMPLE_RECORD = context.SAMPLE_RECORD

RECORD_TEMPLATE = """# Record

Hand-written intro.

<!-- RECORD:START -->
OLD CONTENT
<!-- RECORD:END -->
"""


class TestBuildBlock(unittest.TestCase):
    def setUp(self):
        self.block = gen_record.build_block(SAMPLE_RECORD)

    def test_is_wrapped_in_markers(self):
        self.assertTrue(self.block.startswith("<!-- RECORD:START -->\n"))
        self.assertTrue(self.block.endswith("\n<!-- RECORD:END -->"))

    def test_contact_lists_every_item(self):
        self.assertIn("Location: City, ST | Phone: 555", self.block)

    def test_shows_every_entry_with_record_wording(self):
        self.assertIn("### Acme Company — Engineer\nJanuary 2020 to Present | City, ST", self.block)
        self.assertIn("### Hidden Co — Intern\nJune 2019 | Town, ST", self.block)

    def test_shows_record_bullets_not_resume_wording(self):
        self.assertIn("- Full detail\n- Record only", self.block)
        self.assertNotIn("Short **detail**", self.block)
        self.assertNotIn("Resume only", self.block)
        self.assertNotIn("Group summary", self.block)

    def test_group_heading_sits_above_its_bullets(self):
        self.assertIn("Project\n- Kept as is", self.block)

    def test_education(self):
        self.assertIn(
            "**Acme University**\nBachelor's in Widgetry\nCompleted: May 2019 | City, ST\nCum laude",
            self.block,
        )

    def test_projects(self):
        self.assertIn("**Widget**\n[widget.com](https://example.com)\nA widget.", self.block)
        self.assertIn("**Gadget**\n- Record only", self.block)

    def test_skills_skip_derived_rows(self):
        self.assertIn("**Programming (Proficient):** Python, Go", self.block)
        self.assertNotIn("**Languages:**", self.block)

    def test_languages_section(self):
        self.assertIn("## Languages\n\n- English — Native\n- Mandarin Chinese — Fluent", self.block)

    def test_publications(self):
        self.assertIn("## Publications\n\n- A paper", self.block)


class TestSync(unittest.TestCase):
    def make_repo(self, text: str) -> pathlib.Path:
        root = context.temp_repo(self)
        context.write_record_fixture(root, SAMPLE_RECORD)
        (root / "docs").mkdir()
        (root / "docs" / "all-experiences.md").write_text(text)
        return root

    def test_replaces_marker_block_and_keeps_the_intro(self):
        root = self.make_repo(RECORD_TEMPLATE)
        self.assertTrue(gen_record.sync(root))
        text = (root / "docs" / "all-experiences.md").read_text()
        self.assertIn("Hand-written intro.", text)
        self.assertNotIn("OLD CONTENT", text)
        self.assertIn("### Acme Company — Engineer", text)

    def test_second_run_changes_nothing(self):
        root = self.make_repo(RECORD_TEMPLATE)
        gen_record.sync(root)
        self.assertFalse(gen_record.sync(root))

    def test_no_markers_returns_false(self):
        self.assertFalse(gen_record.sync(self.make_repo("no markers")))


if __name__ == "__main__":
    unittest.main()
