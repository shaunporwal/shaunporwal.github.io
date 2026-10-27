"""The printed resume PDF is the resume. It carries every item of the record's resume view and none of the
rest, reads in the order of the page, is on Letter pages within the limit in data/pages.json, and embeds
exactly the typefaces in site/fonts.

It prints the real page with the same Chrome and code as the publish step, so the test fails when the page,
the stylesheet or the record drifts from what the PDF shows. Needs Chrome and poppler's tools: see
tests/pdf_support.py. Skips without them locally; fails in CI, where they must exist.
"""
import unittest

import context
import pdf_support
import render_pdf
from lib_pagebreaks import blocks_from_html, find_starts
from lib_pdfcheck import (
    font_names,
    font_problems,
    is_letter,
    leaked_strings,
    missing_strings,
    page_count,
    page_size,
    required_strings,
    unlisted_strings,
)
from lib_record import load_record, resume_view
from lib_site import load_pages, load_site, pdf_max_pages

FONT_DIR = context.REPO_ROOT / "site" / "fonts"
RESUME_HTML = pdf_support.RESUME_PATH


def printed_or_fail(test: unittest.TestCase, chrome: str) -> bytes:
    try:
        return pdf_support.printed_pdf(chrome)
    except render_pdf.PrintFailed as error:
        test.fail(f"PDF render failed: {error}")


class TestResumePdfMatchesRecord(unittest.TestCase):
    def setUp(self):
        self.pdf = printed_or_fail(self, pdf_support.require_tools(self))
        self.record = load_record(context.REPO_ROOT)
        self.site = load_site(context.REPO_ROOT)
        self.required = required_strings(resume_view(self.record, self.site))

    def test_every_item_of_the_resume_view_is_in_the_pdf(self):
        self.assertEqual(missing_strings(pdf_support.raw_text(self.pdf), self.required), [])

    def test_no_item_kept_off_the_resume_is_in_the_pdf(self):
        unlisted = unlisted_strings(self.record, self.site, self.required)
        self.assertTrue(unlisted, "the record keeps nothing off the resume, so this check proves nothing")
        self.assertEqual(leaked_strings(pdf_support.raw_text(self.pdf), unlisted), [])

    def test_the_pdf_reads_in_the_order_of_the_page(self):
        blocks = blocks_from_html(RESUME_HTML.read_text())
        self.assertEqual(len(find_starts(pdf_support.raw_text(self.pdf), blocks)), len(blocks))

    def test_the_section_headings_read_as_whole_words(self):
        # Wide letter spacing makes a parser return "E X P E R I E N C E", and then it finds no section.
        text = pdf_support.plain_text(self.pdf).lower()
        headings = [b.text for b in blocks_from_html(RESUME_HTML.read_text()) if b.kind == "heading"]
        self.assertEqual([heading for heading in headings if heading.lower() not in text], [])

    def test_the_pdf_is_letter_size(self):
        self.assertTrue(is_letter(page_size(pdf_support.info(self.pdf))))

    def test_the_pdf_is_within_the_page_limit(self):
        limit = pdf_max_pages(load_pages(context.REPO_ROOT), "resume.html")
        self.assertLessEqual(page_count(pdf_support.info(self.pdf)), limit)

    def test_the_pdf_embeds_exactly_the_shipped_typefaces(self):
        files = [path.name for path in FONT_DIR.iterdir()]
        self.assertEqual(font_problems(font_names(pdf_support.fonts(self.pdf)), files), [])


if __name__ == "__main__":
    unittest.main()
