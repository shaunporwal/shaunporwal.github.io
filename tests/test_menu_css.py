"""The phone menu must not stretch its rows: some WebKit browsers spread grid rows over the whole panel."""
import re
import unittest

import context

CSS = (context.REPO_ROOT / "site" / "styles" / "site.css").read_text()


def rule_body(selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    return match.group(1) if match else ""


class TestMenuCss(unittest.TestCase):
    def test_the_panel_has_the_height_of_its_content(self):
        self.assertIn("height: fit-content", rule_body(".menu-panel"))

    def test_the_open_panel_is_a_column_that_starts_at_the_top(self):
        body = rule_body(".menu-panel:popover-open")
        self.assertIn("display: flex", body)
        self.assertIn("flex-direction: column", body)
        self.assertNotIn("grid", body)

    def test_each_menu_row_keeps_its_own_height(self):
        self.assertIn("flex: none", rule_body(".menu-link"))


if __name__ == "__main__":
    unittest.main()
