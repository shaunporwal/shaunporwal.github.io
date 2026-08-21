import unittest

import context  # noqa: F401
from lib_resume import render_html, render_text


class TestRenderHtml(unittest.TestCase):
    def test_plain_text_is_escaped(self):
        self.assertEqual(render_html("A & B < C"), "A &amp; B &lt; C")

    def test_link_renders_anchor(self):
        self.assertEqual(
            render_html("See [my site](https://example.com) for more"),
            'See <a href="https://example.com">my site</a> for more',
        )

    def test_code_renders_code_tag(self):
        self.assertEqual(render_html("Uses `smb-pipe` internally"), "Uses <code>smb-pipe</code> internally")

    def test_dcurves_token_renders_span(self):
        self.assertEqual(
            render_html("{dcurves} downloads"),
            '<span class="dcurves-downloads">72k+</span> downloads',
        )

    def test_bold_renders_strong_tag(self):
        self.assertEqual(render_html("Delivered **$1M+** in value"), "Delivered <strong>$1M+</strong> in value")

    def test_bold_content_is_escaped(self):
        self.assertEqual(render_html("**A & B**"), "<strong>A &amp; B</strong>")

    def test_mixed_tokens(self):
        result = render_html("[a](https://a.com) & `b` {dcurves} **c**")
        self.assertIn('<a href="https://a.com">a</a>', result)
        self.assertIn("&amp;", result)
        self.assertIn("<code>b</code>", result)
        self.assertIn('<span class="dcurves-downloads">', result)
        self.assertIn("<strong>c</strong>", result)


class TestRenderText(unittest.TestCase):
    def test_link_renders_label_and_url(self):
        self.assertEqual(
            render_text("See [my site](https://example.com) for more"),
            "See my site (https://example.com) for more",
        )

    def test_code_renders_bare_text(self):
        self.assertEqual(render_text("Uses `smb-pipe` internally"), "Uses smb-pipe internally")

    def test_dcurves_token_renders_plain_count(self):
        self.assertEqual(render_text("{dcurves} downloads"), "72k+ downloads")

    def test_no_html_escaping(self):
        self.assertEqual(render_text("A & B"), "A & B")

    def test_bold_markers_are_stripped(self):
        self.assertEqual(render_text("Delivered **$1M+** in value"), "Delivered $1M+ in value")


if __name__ == "__main__":
    unittest.main()
