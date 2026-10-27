"""The resume page keeps its print rules: a plain page, with no site header, no footer and no download button.
It ships its typefaces, and the page preloads exactly the font files that the stylesheet names."""
import re
import unittest

import context

CSS_PATH = context.REPO_ROOT / "site" / "styles" / "resume.css"
PAGE_PATH = context.REPO_ROOT / "site" / "resume.html"
FONT_DIR = context.REPO_ROOT / "site" / "fonts"
FONT_URL_RE = re.compile(r'url\("\.\./fonts/([^"]+)"\)')
PRELOAD_RE = re.compile(r'<link rel="preload" href="\./fonts/([^"]+)" as="font"')
HIDDEN_WHEN_PRINTED = (".skip-link", ".site-header", ".site-footer", ".resume-actions")


def print_block(css: str) -> str:
    """The text after the first `@media print` rule: the print rules are the last in the file."""
    return css.split("@media print", 1)[1] if "@media print" in css else ""


def hidden_selectors(block: str) -> str:
    """The text of the rule that sets display: none, from its selectors up to the brace."""
    end = block.index("display: none")
    return block[block.rindex("}", 0, end) + 1:end]


class TestResumePrintRules(unittest.TestCase):
    def setUp(self):
        self.block = print_block(CSS_PATH.read_text())

    def test_finds_the_selectors_of_the_hiding_rule(self):
        self.assertEqual(hidden_selectors("a { x: y; } .b, .c { display: none; }").strip(), ".b, .c {")

    def test_there_are_print_rules(self):
        self.assertIn("display: none", self.block)

    def test_the_print_rules_hide_the_site_chrome_and_the_button(self):
        selectors = hidden_selectors(self.block)
        for selector in HIDDEN_WHEN_PRINTED:
            self.assertIn(selector, selectors)

    def test_the_print_page_is_light_whatever_the_theme(self):
        self.assertIn("color-scheme: light", self.block)
        self.assertIn("--background: #fff", self.block)


class TestResumeTypefaces(unittest.TestCase):
    def setUp(self):
        self.css = CSS_PATH.read_text()
        self.named = sorted(FONT_URL_RE.findall(self.css))

    def test_finds_the_font_files_a_stylesheet_names(self):
        self.assertEqual(FONT_URL_RE.findall('src: url("../fonts/a.woff2") format("woff2");'), ["a.woff2"])

    def test_the_stylesheet_names_the_font_files(self):
        self.assertTrue(self.named)

    def test_every_named_font_file_exists_and_no_font_file_goes_unused(self):
        shipped = sorted(path.name for path in FONT_DIR.glob("*.woff2"))
        self.assertEqual(shipped, self.named)

    def test_the_page_preloads_exactly_the_named_fonts(self):
        self.assertEqual(sorted(PRELOAD_RE.findall(PAGE_PATH.read_text())), self.named)

    def test_the_fonts_ship_with_their_licence(self):
        licences = [path.read_text() for path in FONT_DIR.glob("OFL-*.txt")]
        self.assertGreaterEqual(len(licences), 2)
        self.assertTrue(all("SIL OPEN FONT LICENSE" in text.upper() for text in licences))

    def test_the_pdf_page_is_letter_size(self):
        self.assertRegex(self.css, r"@page\s*\{[^}]*size:\s*letter")


if __name__ == "__main__":
    unittest.main()
