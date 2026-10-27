"""The picture on each Work card in site/styles/site.css: a 16:10 plate that clips its own picture and not the card,
picture colors that come from tokens, motion that runs only while the script marks the picture as playing,
and no motion at all when the visitor asks for less."""
import re
import unittest

import context
from test_alive_css import HOVER_MEDIA, REDUCED_MEDIA, media_block, rule_body

CSS = (context.REPO_ROOT / "site" / "styles" / "site.css").read_text()
ANIMATED_RULES = (".curve-ping", ".curve-model", ".curve-area")
PLAYING = '.card-media[data-playing="true"]'


def declarations(css: str, selector: str) -> str:
    return " ".join(rule_body(css, selector).split())


def selectors_with(css: str, text: str) -> list[str]:
    """The selector lines that mention text, with the declarations ignored."""
    return [line for line in css.splitlines() if line.rstrip().endswith("{") and text in line]


class TestPlate(unittest.TestCase):
    def test_the_plate_has_the_16_to_10_ratio(self):
        self.assertIn("aspect-ratio: 16 / 10;", declarations(CSS, ".card-media"))

    def test_the_plate_clips_its_picture_and_the_card_does_not(self):
        self.assertIn("overflow: hidden;", declarations(CSS, ".card-media"))
        self.assertNotIn("overflow", declarations(CSS, ".card"))

    def test_the_picture_fills_the_plate(self):
        for selector in (".card-media video", ".card-media .curve-svg"):
            body = declarations(CSS, selector)
            self.assertIn("width: 100%;", body, selector)
            self.assertIn("height: 100%;", body, selector)

    def test_the_clip_covers_the_plate(self):
        self.assertIn("object-fit: cover;", declarations(CSS, ".card-media video"))

    def test_the_clip_is_a_picture_so_it_takes_no_click_and_shows_no_player_bar(self):
        self.assertIn("pointer-events: none;", declarations(CSS, ".card-media video"))
        self.assertIn("display: none", declarations(CSS, ".card-media video::-webkit-media-controls"))

    def test_the_logo_sits_in_the_middle_of_a_quiet_plate(self):
        body = declarations(CSS, ".card-media-logo")
        self.assertIn("place-items: center;", body)
        self.assertIn("var(--secondary)", declarations(CSS, ".card-media"))

    def test_the_note_is_visible_text_inside_the_plate(self):
        body = declarations(CSS, ".card-note")
        self.assertIn("position: absolute;", body)
        self.assertIn("color: var(--muted-foreground);", body)


class TestCurveColors(unittest.TestCase):
    def test_each_curve_part_takes_its_color_from_a_page_token(self):
        for selector in (".curve-model", ".curve-all", ".curve-none", ".curve-area", ".curve-dot", ".curve-label"):
            self.assertRegex(declarations(CSS, selector), r"(?:stroke|fill): var\(--", selector)

    def test_the_curve_draws_no_filled_shape_without_a_token(self):
        self.assertNotRegex(CSS, r"\.curve-[a-z-]+ \{[^}]*(?:fill|stroke): (?!var\(|none)")


class TestMotion(unittest.TestCase):
    def test_no_curve_rule_animates_until_the_script_marks_the_picture_as_playing(self):
        for selector in ANIMATED_RULES:
            self.assertNotIn("animation:", declarations(CSS, selector), selector)

    def test_the_playing_state_runs_the_draw_in_and_the_ring(self):
        self.assertIn("animation:", declarations(CSS, f"{PLAYING} .curve-ping"))
        self.assertIn("animation:", declarations(CSS, f"{PLAYING} .curve-model"))

    def test_reduced_motion_switches_each_curve_animation_off(self):
        block = media_block(CSS, REDUCED_MEDIA)
        for selector in ANIMATED_RULES:
            self.assertIn(selector, block)
        self.assertIn("animation: none !important;", block)

    def test_the_picture_adds_no_hover_rule_outside_the_hover_media_query(self):
        outside = CSS.replace(media_block(CSS, HOVER_MEDIA), "")
        hovering = [line for line in selectors_with(outside, ":hover") if re.search(r"card-media|curve-", line)]
        self.assertEqual(hovering, [])


if __name__ == "__main__":
    unittest.main()
