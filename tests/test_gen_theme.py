import unittest

import context
import gen_theme

CSS = "body { color: var(--foreground); }\n/* THEME:START */\nold\n/* THEME:END */\n"


class TestRenderTokens(unittest.TestCase):
    def setUp(self):
        self.css = gen_theme.render_tokens(context.FAKE_THEME)

    def test_root_holds_the_light_colors_and_the_fixed_tokens(self):
        root = self.css.split("@media")[0]
        self.assertIn("  --primary: #aa3300;", root)
        self.assertIn("  --font-serif: serif;", root)
        self.assertIn("  color-scheme: light;", root)

    def test_dark_colors_sit_in_a_media_query(self):
        dark = self.css.split("@media (prefers-color-scheme: dark) {")[1]
        self.assertIn("    --primary: #ff9966;", dark)
        self.assertIn("    color-scheme: dark;", dark)
        self.assertNotIn("--font-serif", dark)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.css_path = self.repo_root / "site" / "styles" / "site.css"
        self.css_path.parent.mkdir()
        self.css_path.write_text(CSS)

    def test_replaces_the_theme_block_only(self):
        self.assertTrue(gen_theme.sync(self.repo_root))
        text = self.css_path.read_text()
        self.assertIn("--primary: #aa3300;", text)
        self.assertTrue(text.startswith("body { color: var(--foreground); }"))
        self.assertNotIn("\nold\n", text)

    def test_second_run_changes_nothing(self):
        gen_theme.sync(self.repo_root)
        self.assertFalse(gen_theme.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
