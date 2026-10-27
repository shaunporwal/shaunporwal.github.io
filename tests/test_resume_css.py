"""The resume page keeps its print rules: a plain page, with no site header, no footer and no download button."""
import unittest

import context

CSS_PATH = context.REPO_ROOT / "site" / "styles" / "resume.css"
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


if __name__ == "__main__":
    unittest.main()
