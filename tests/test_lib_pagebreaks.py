import unittest

import context  # noqa: F401
from lib_pagebreaks import Block, BlockNotFound, blocks_from_html, find_problems

BLOCKS = [
    Block("heading", "Experience", long=True),
    Block("entry", "Job A"),
    Block("entry", "Job B"),
    Block("heading", "Selected Projects"),
    Block("entry", "Project X"),
    Block("entry", "Project Y"),
]

PAGE_BREAK = "\f"


def printed(*pages: str) -> str:
    return PAGE_BREAK.join(pages)


class TestFindProblems(unittest.TestCase):
    def test_break_between_entries_of_a_long_section_is_fine(self):
        text = printed(
            "EXPERIENCE\nJob A — Org\n- bullet\n",
            "Job B — Org\n- bullet\nSELECTED PROJECTS\nProject X\nProject Y\n",
        )
        self.assertEqual(find_problems(text, BLOCKS), [])

    def test_break_inside_an_entry_is_reported(self):
        text = printed(
            "EXPERIENCE\nJob A — Org\n",
            "- bullet\nJob B — Org\n- bullet\nSELECTED PROJECTS\nProject X\nProject Y\n",
        )
        problems = find_problems(text, BLOCKS)
        self.assertEqual(len(problems), 1)
        self.assertIn("Job A", problems[0])

    def test_heading_alone_at_the_end_of_a_page_is_reported(self):
        text = printed(
            "EXPERIENCE\nJob A — Org\n- bullet\nJob B — Org\n- bullet\nSELECTED PROJECTS\n",
            "Project X\nProject Y\n",
        )
        problems = find_problems(text, BLOCKS)
        self.assertTrue(any("Selected Projects" in p and "alone" in p for p in problems))

    def test_break_inside_a_short_section_is_reported(self):
        text = printed(
            "EXPERIENCE\nJob A — Org\n- bullet\nJob B — Org\n- bullet\nSELECTED PROJECTS\nProject X\n",
            "Project Y\n",
        )
        problems = find_problems(text, BLOCKS)
        self.assertTrue(any("Selected Projects" in p and "split" in p for p in problems))

    def test_whole_short_section_moved_to_the_next_page_is_fine(self):
        text = printed(
            "EXPERIENCE\nJob A — Org\n- bullet\nJob B — Org\n- bullet\n",
            "SELECTED PROJECTS\nProject X\nProject Y\n",
        )
        self.assertEqual(find_problems(text, BLOCKS), [])

    def test_trailing_page_break_after_a_last_heading_is_fine(self):
        blocks = [Block("heading", "Skills")]
        text = printed("SKILLS\nPython\nGo\n", "")
        self.assertEqual(find_problems(text, blocks), [])

    def test_split_section_is_not_also_called_a_lone_heading(self):
        blocks = [Block("heading", "Skills")]
        text = printed("SKILLS\nPython\n", "Go\n")
        problems = find_problems(text, blocks)
        self.assertEqual(len(problems), 1)
        self.assertIn("splits", problems[0])

    def test_missing_block_text_raises(self):
        with self.assertRaises(BlockNotFound):
            find_problems(printed("EXPERIENCE\nJob A\n"), BLOCKS)


SAMPLE_HTML = """
<section class="resume-section resume-section-long">
<h2 class="section">Experience</h2>
<div class="entry"><div class="entry-head"><div class="entry-head-title"><span class="entry-title">Founder &amp; Engineer</span> — <span class="entry-org">Acme</span></div></div></div>
</section>
<section class="resume-section">
<h2 class="section">Selected Projects</h2>
<div class="entry"><div class="entry-head"><div class="entry-title">widget</div></div></div>
</section>
<section class="resume-section">
<h2 class="section">Skills &amp; Certifications</h2>
<dl><dt>Programming</dt><dd>Python</dd></dl>
</section>
"""


class TestBlocksFromHtml(unittest.TestCase):
    def test_sections_and_entries_come_out_in_document_order(self):
        blocks = blocks_from_html(SAMPLE_HTML)
        self.assertEqual(
            blocks,
            [
                Block("heading", "Experience", long=True),
                Block("entry", "Founder & Engineer"),
                Block("heading", "Selected Projects"),
                Block("entry", "widget"),
                Block("heading", "Skills & Certifications"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
