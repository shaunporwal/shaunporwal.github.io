"""Every color in a stylesheet under site/styles/ is a :root token, so the palette has
one home and a color change is one edit. The resume print palette is a :root block too."""
import re
import unittest

import context

CSS_PATHS = sorted((context.REPO_ROOT / "site" / "styles").glob("*.css"))
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

    def test_every_stylesheet_uses_only_tokens(self):
        self.assertTrue(CSS_PATHS)
        for path in CSS_PATHS:
            with self.subTest(stylesheet=path.name):
                self.assertEqual(color_literals_outside_root(path.read_text()), [])


if __name__ == "__main__":
    unittest.main()
