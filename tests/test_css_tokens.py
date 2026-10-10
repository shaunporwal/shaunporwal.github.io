"""Every color in site/styles/site.css is a :root token, so the palette has
one home and a color change is one edit."""
import re
import unittest

import context

CSS_PATH = context.REPO_ROOT / "site" / "styles" / "site.css"
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
ROOT_RE = re.compile(r":root\s*\{[^}]*\}")
COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(")


def color_literals_outside_root(css: str) -> list[str]:
    outside = ROOT_RE.sub("", COMMENT_RE.sub("", css))
    return COLOR_RE.findall(outside)


class TestCssTokens(unittest.TestCase):
    def test_finds_a_literal_outside_root(self):
        self.assertEqual(color_literals_outside_root("a { color: #fff; }"), ["#fff"])

    def test_ignores_root_and_comments(self):
        css = ":root { --x: rgba(0, 0, 0, 0.5); }\n/* #abc */\na { color: var(--x); }"
        self.assertEqual(color_literals_outside_root(css), [])

    def test_site_css_uses_only_tokens(self):
        self.assertEqual(color_literals_outside_root(CSS_PATH.read_text()), [])


if __name__ == "__main__":
    unittest.main()
