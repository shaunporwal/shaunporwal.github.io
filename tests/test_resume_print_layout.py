"""Prints site/resume.html to a PDF with the same Chrome and code as the publish step, and checks where pages break.

The resume PDF has a page limit (data/pages.json). It must never split an entry or a short
section across pages, or leave a heading alone at the bottom of a page.
Needs Chrome (see scripts/render_pdf.py for where it looks) and poppler's tools (see tests/pdf_support.py).
Skips without them locally; fails in CI, where they must exist.
"""
import unittest

import context  # noqa: F401
import pdf_support
import render_pdf
from lib_pagebreaks import blocks_from_html, find_problems


class TestResumePrintLayout(unittest.TestCase):
    def setUp(self):
        self.chrome = pdf_support.require_tools(self)

    def test_every_section_is_wrapped_so_the_check_sees_it(self):
        page_html = pdf_support.RESUME_PATH.read_text()
        headings = [b for b in blocks_from_html(page_html) if b.kind == "heading"]
        self.assertEqual(len(headings), page_html.count('<h2 class="resume-heading"'))

    def test_page_breaks_never_split_a_block(self):
        blocks = blocks_from_html(pdf_support.RESUME_PATH.read_text())
        try:
            text = pdf_support.layout_text(pdf_support.printed_pdf(self.chrome))
        except render_pdf.PrintFailed as error:
            self.fail(f"PDF render failed: {error}")
        self.assertEqual(find_problems(text, blocks), [])


if __name__ == "__main__":
    unittest.main()
