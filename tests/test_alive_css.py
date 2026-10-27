"""The alive effects in site/styles/site.css: each registered property exists, the pointer light turns on only where a
pointer can hover, no later shorthand erases the glow image, and reduced motion switches the loops off."""
import re
import unittest

import context

CSS = (context.REPO_ROOT / "site" / "styles" / "site.css").read_text()
REGISTERED = ("--glow", "--gx", "--gy", "--hx", "--hy", "--turn")
GLOW_SURFACES = (".btn-primary", ".btn-outline", ".card")
HOVER_MEDIA = "@media (hover: hover) and (pointer: fine)"
REDUCED_MEDIA = "@media (prefers-reduced-motion: reduce)"


def media_block(css: str, header: str) -> str:
    """The text of the first block that opens with the media query header, up to its closing brace in column 0."""
    start = css.index(header)
    return css[start : css.index("\n}\n", start)]


def rule_body(css: str, selector: str) -> str:
    match = re.search(rf"(?m)^{re.escape(selector)} \{{([^}}]*)\}}", css)
    return match.group(1) if match else ""


class TestMediaBlock(unittest.TestCase):
    def test_returns_the_block_that_follows_the_header(self):
        css = "@media (a) {\n  x { y: z; }\n}\nrest { }\n"
        self.assertIn("x { y: z; }", media_block(css, "@media (a)"))
        self.assertNotIn("rest", media_block(css, "@media (a)"))


class TestAliveCss(unittest.TestCase):
    def test_each_animated_custom_property_is_registered(self):
        for name in REGISTERED:
            self.assertIn(f"@property {name} {{", CSS)

    def test_the_pointer_light_turns_on_only_inside_the_hover_media_query(self):
        outside = CSS.replace(media_block(CSS, HOVER_MEDIA), "")
        self.assertNotIn("--glow: 1", outside)
        self.assertIn("--glow: 1", media_block(CSS, HOVER_MEDIA))

    def test_no_shorthand_background_erases_the_glow_image(self):
        for selector in GLOW_SURFACES:
            self.assertNotRegex(rule_body(CSS, selector), r"(?m)^\s*background:")

    def test_reduced_motion_hides_the_edge_light_and_the_lit_dots(self):
        block = media_block(CSS, REDUCED_MEDIA)
        self.assertIn(".btn-sheen::after", block)
        self.assertIn(".hero-lit", block)


if __name__ == "__main__":
    unittest.main()
