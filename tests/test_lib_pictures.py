"""Tests for scripts/lib_pictures.py and scripts/lib_curve_svg.py: the picture at the top of each Work card."""
import re
import unittest

import context
import lib_pictures

COLOR_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(")


class PictureTestCase(unittest.TestCase):
    def setUp(self):
        self.site_dir = context.temp_repo(self) / "site"
        context.write_project_media(self.site_dir)


class TestDispatch(PictureTestCase):
    def test_the_table_names_each_kind_the_schema_allows(self):
        self.assertEqual(set(lib_pictures.RENDERERS), {"clip", "logo", "decision-curve"})

    def test_a_picture_goes_to_the_renderer_for_its_kind(self):
        logo = lib_pictures.render_picture(context.LOGO_PICTURE, self.site_dir)
        self.assertIn('class="card-media card-media-logo"', logo)


class TestClip(PictureTestCase):
    def setUp(self):
        super().setUp()
        self.markup = lib_pictures.render_picture(context.CLIP_PICTURE, self.site_dir)

    def test_the_clip_is_silent_looping_inline_and_loads_nothing_before_it_plays(self):
        for attribute in ("muted", "loop", "playsinline", 'preload="none"'):
            self.assertIn(f" {attribute}", self.markup)
        self.assertNotIn("autoplay", self.markup)
        self.assertNotIn("controls", self.markup)

    def test_the_still_is_the_poster_and_has_its_size(self):
        self.assertIn('poster="media/projects/gadget.png"', self.markup)
        self.assertIn('width="8" height="8"', self.markup)

    def test_the_mp4_source_comes_before_the_webm_source(self):
        mp4 = self.markup.index('<source src="media/projects/gadget.mp4" type="video/mp4">')
        webm = self.markup.index('<source src="media/projects/gadget.webm" type="video/webm">')
        self.assertLess(mp4, webm)

    def test_the_clip_has_alt_text(self):
        self.assertIn('role="img" aria-label="A clip of the Gadget app: a table of gadgets."', self.markup)

    def test_the_plate_marks_its_kind_for_the_script(self):
        self.assertTrue(self.markup.startswith('<div class="card-media card-media-clip">'))


class TestLogo(PictureTestCase):
    def test_the_logo_is_an_image_with_alt_text_and_its_size_that_loads_late(self):
        markup = lib_pictures.render_picture(context.LOGO_PICTURE, self.site_dir)
        self.assertIn('<img class="card-logo" src="media/projects/acme.png"', markup)
        self.assertIn('alt="The Acme logo, a letter A."', markup)
        self.assertIn('width="8" height="8"', markup)
        self.assertIn('loading="lazy"', markup)

    def test_alt_text_is_escaped(self):
        picture = {**context.LOGO_PICTURE, "alt": 'A "quoted" <b>'}
        self.assertIn('alt="A &quot;quoted&quot; &lt;b&gt;"', lib_pictures.render_picture(picture, self.site_dir))


class TestDecisionCurve(PictureTestCase):
    def setUp(self):
        super().setUp()
        self.markup = lib_pictures.render_picture(context.CURVE_PICTURE, self.site_dir)

    def test_the_svg_is_an_image_for_screen_readers_with_alt_text(self):
        opening = '<svg class="curve-svg" viewBox="0 0 320 200" role="img" aria-label="A sample decision'
        self.assertIn(opening, self.markup)

    def test_the_label_says_the_curve_is_an_illustration(self):
        self.assertIn('<span class="card-note">Illustration only. Not real data.</span>', self.markup)

    def test_the_three_lines_and_the_area_have_their_own_classes(self):
        for name in ("curve-area", "curve-model", "curve-all", "curve-none"):
            self.assertIn(f'class="{name}', self.markup)

    def test_the_treat_all_line_is_clipped_below_the_plot(self):
        self.assertIn('<clipPath id="curve-clip"><rect ', self.markup)
        self.assertIn('<g clip-path="url(#curve-clip)">', self.markup)

    def test_the_model_line_can_draw_in(self):
        self.assertRegex(self.markup, r'<path class="curve-model" pathLength="1" d="M')

    def test_a_live_point_with_a_ring_sits_on_the_model_line(self):
        self.assertIn('class="curve-ping"', self.markup)
        self.assertIn('class="curve-dot"', self.markup)

    def test_each_line_has_a_direct_label_from_the_data(self):
        for text in ("Model", "Treat all", "Treat none"):
            self.assertRegex(self.markup, rf"<text [^>]*>{text}</text>")

    def test_the_picture_holds_no_color_so_the_page_tokens_own_every_color(self):
        self.assertEqual(COLOR_LITERAL_RE.findall(self.markup), [])
        self.assertNotIn("style=", self.markup)

    def test_the_picture_holds_no_script_and_no_link(self):
        self.assertNotIn("<script", self.markup)
        self.assertNotIn("<a ", self.markup)

    def test_the_picture_is_small(self):
        self.assertLess(len(self.markup.encode()), 8_000)


if __name__ == "__main__":
    unittest.main()
