import unittest

import context  # noqa: F401
from lib_markdown import post_markdown

BASE = "https://example.com/posts/demo/"

POST = """<main class="page">
  <h1 class="page-title">Demo</h1>
  <p class="page-meta">March 5, 2025 &middot; <span class="cat">One</span></p>

<p>First <strong>bold</strong> and <em>slanted</em> with <code>code()</code> &amp; a <a href="https://x.dev/a">link</a>.</p>
<h2>Part two</h2>
<p>Second
paragraph.</p>
<figure><img src="pic.png" alt="A picture"><figcaption>Seen here</figcaption></figure>
<ul><li>Item one</li><li>Item two</li></ul>
<pre>a = 1
b = 2</pre>
<blockquote>Quoted</blockquote>
</main>
"""


class TestPostMarkdown(unittest.TestCase):
    def setUp(self):
        self.lines = post_markdown(POST, BASE).split("\n\n")

    def test_skips_the_title_and_the_meta_line(self):
        self.assertNotIn("Demo", self.lines[0])
        self.assertNotIn("March 5", "\n".join(self.lines))

    def test_converts_inline_markup(self):
        self.assertEqual(self.lines[0], "First **bold** and *slanted* with `code()` & a [link](https://x.dev/a).")

    def test_converts_a_heading_one_level_down(self):
        self.assertIn("### Part two", self.lines)

    def test_joins_a_wrapped_paragraph_on_one_line(self):
        self.assertIn("Second paragraph.", self.lines)

    def test_converts_an_image_with_an_absolute_url_and_its_caption(self):
        self.assertIn("![A picture](https://example.com/posts/demo/pic.png)", self.lines)
        self.assertIn("*Seen here*", self.lines)

    def test_converts_list_items_code_and_quotes(self):
        self.assertIn("- Item one", self.lines)
        self.assertIn("```\na = 1\nb = 2\n```", self.lines)
        self.assertIn("> Quoted", self.lines)


if __name__ == "__main__":
    unittest.main()
