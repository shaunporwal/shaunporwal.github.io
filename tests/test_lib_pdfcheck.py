"""The pure checks on the printed resume PDF: what must appear, what must not, and the page facts."""
import unittest

import context
import lib_pdfcheck
import lib_record

VIEW = lib_record.resume_view(context.SAMPLE_RECORD, context.FAKE_SITE)
REQUIRED = lib_pdfcheck.required_strings(VIEW)
UNLISTED = lib_pdfcheck.unlisted_strings(context.SAMPLE_RECORD, context.FAKE_SITE, REQUIRED)

PDFINFO = "Title:  Resume\nPages:           2\nPage size:       612 x 792 pts (letter)\n"
PDFFONTS = (
    "name                                 type              encoding         emb sub uni object ID\n"
    "------------------------------------ ----------------- ---------------- --- --- --- ---------\n"
    "AAAAAA+SourceSerif4-SemiBold         CID TrueType      Identity-H       yes yes yes      4  0\n"
    "BAAAAA+Inter-Regular                 CID TrueType      Identity-H       yes yes yes      5  0\n"
    "CAAAAA+Inter-Regular                 CID TrueType      Identity-H       yes yes yes      6  0\n"
)


def pdf_text_of(strings: list[str]) -> str:
    """What a PDF of these strings reads like: capitals for some, line breaks inside the words."""
    return "\n".join(strings).upper().replace(" ", "\n ")


class TestSquash(unittest.TestCase):
    def test_ignores_case_and_white_space(self):
        self.assertEqual(lib_pdfcheck.squash("Self-\n  Hosted   Thing"), "self-hostedthing")

    def test_ignores_the_live_dcurves_count(self):
        self.assertEqual(lib_pdfcheck.squash("72k+ downloads"), lib_pdfcheck.squash("79k+ DOWNLOADS"))


class TestPageFacts(unittest.TestCase):
    def test_reads_the_page_count(self):
        self.assertEqual(lib_pdfcheck.page_count(PDFINFO), 2)

    def test_reads_the_page_size(self):
        self.assertEqual(lib_pdfcheck.page_size(PDFINFO), (612.0, 792.0))

    def test_letter_is_letter_and_a4_is_not(self):
        self.assertTrue(lib_pdfcheck.is_letter((612.0, 792.0)))
        self.assertFalse(lib_pdfcheck.is_letter((595.28, 841.89)))

    def test_lists_each_embedded_font_once_without_its_subset_prefix(self):
        self.assertEqual(lib_pdfcheck.font_names(PDFFONTS), ["Inter-Regular", "SourceSerif4-SemiBold"])


FONT_FILES = [
    "inter-latin-400-normal.woff2",
    "inter-latin-600-normal.woff2",
    "source-serif-4-latin-600-normal.woff2",
    "OFL-Inter.txt",
]


class TestFontProblems(unittest.TestCase):
    def test_names_the_shipped_families(self):
        self.assertEqual(lib_pdfcheck.shipped_families(FONT_FILES), {"inter", "sourceserif4"})

    def test_passes_when_the_pdf_embeds_exactly_the_shipped_families(self):
        embedded = lib_pdfcheck.font_names(PDFFONTS)
        self.assertEqual(lib_pdfcheck.font_problems(embedded, FONT_FILES), [])

    def test_finds_a_shipped_font_that_the_pdf_lacks(self):
        self.assertEqual(lib_pdfcheck.font_problems(["Inter-Regular"], FONT_FILES), ["font not embedded: sourceserif4"])

    def test_finds_a_fallback_font(self):
        embedded = [*lib_pdfcheck.font_names(PDFFONTS), "Menlo-Regular"]
        self.assertEqual(lib_pdfcheck.font_problems(embedded, FONT_FILES), ["font not shipped: menlo"])


class TestRequiredStrings(unittest.TestCase):
    def test_shows_a_link_by_its_label_and_never_its_address(self):
        self.assertIn("widget.com", REQUIRED)
        self.assertNotIn("https://example.com", " ".join(REQUIRED))

    def test_holds_the_name_the_dates_the_places_and_every_bullet(self):
        expected = ("Test Person", "Engineer", "Acme", "Jan 2020 – Present", "City, ST", "Short detail", "Resume only")
        for text in expected:
            self.assertIn(text, REQUIRED)

    def test_holds_the_education_the_projects_and_the_skills(self):
        for text in ("B.S., Widgetry", "Cum laude", "Widget", "widget.com", "A widget.", "Programming", "Python, Go"):
            self.assertIn(text, REQUIRED)


class TestUnlistedStrings(unittest.TestCase):
    def test_holds_what_the_record_keeps_off_the_resume(self):
        for text in ("Intern", "Hidden Co", "Gadget", "Visualization", "github.com/testperson", "Record only"):
            self.assertIn(text, UNLISTED)

    def test_holds_the_record_wording_that_the_resume_replaces(self):
        for text in ("Full detail", "Bachelor's in Widgetry", "Programming (Proficient)"):
            self.assertIn(text, UNLISTED)

    def test_leaves_out_a_string_that_the_resume_shows_too(self):
        record = {**context.SAMPLE_RECORD, "skills": [{"label": "Hidden Co", "text": "x"}]}
        self.assertNotIn("Hidden Co", lib_pdfcheck.unlisted_strings(record, context.FAKE_SITE, ["Hidden Co shown"]))


class TestProblems(unittest.TestCase):
    def test_a_pdf_with_every_string_and_no_other_passes(self):
        text = pdf_text_of(REQUIRED)
        self.assertEqual(lib_pdfcheck.missing_strings(text, REQUIRED), [])
        self.assertEqual(lib_pdfcheck.leaked_strings(text, UNLISTED), [])

    def test_finds_a_string_that_the_pdf_lacks(self):
        text = pdf_text_of([text for text in REQUIRED if text != "Resume only"])
        self.assertEqual(lib_pdfcheck.missing_strings(text, REQUIRED), ["Resume only"])

    def test_finds_a_string_that_the_pdf_must_not_hold(self):
        text = pdf_text_of([*REQUIRED, "Hidden Co"])
        self.assertEqual(lib_pdfcheck.leaked_strings(text, UNLISTED), ["Hidden Co"])

    def test_finds_the_old_wording_of_a_replaced_field(self):
        text = pdf_text_of([*REQUIRED, "Bachelor's in Widgetry"])
        self.assertEqual(lib_pdfcheck.leaked_strings(text, UNLISTED), ["Bachelor's in Widgetry"])


if __name__ == "__main__":
    unittest.main()
