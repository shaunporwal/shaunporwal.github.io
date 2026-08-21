import datetime
import pathlib
import tempfile
import unittest

import context  # noqa: F401  (sets up sys.path for scripts/)
from lib_posts import parse_post, all_posts

POST_HTML = """<!doctype html>
<html><head><title>Test Post</title></head><body>
<main class="page">
  <h1 class="page-title">A Test Post</h1>
  <p class="page-meta">March 5, 2025 &middot; <span class="cat">Testing</span><span class="cat">Python</span></p>
<p>This is the first paragraph, used as the excerpt for SEO purposes.</p>
<p>A second paragraph that should not be used as the excerpt.</p>
</main>
</body></html>
"""

POST_HTML_NO_META = """<!doctype html>
<html><head><title>No Meta</title></head><body>
<main class="page">
  <h1 class="page-title">No Meta Post</h1>
<p>Just one paragraph here.</p>
</main>
</body></html>
"""


class TestParsePost(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site_dir = pathlib.Path(self.tmp.name)
        self.posts_dir = self.site_dir / "posts"
        self.posts_dir.mkdir()

    def make_post(self, slug, html, image_name=None, draft=False):
        post_dir = self.posts_dir / slug
        post_dir.mkdir()
        (post_dir / "index.html").write_text(html)
        if image_name:
            (post_dir / image_name).write_bytes(b"fake-image-bytes")
        if draft:
            (post_dir / ".draft").touch()
        return post_dir

    def test_parses_title_date_categories_excerpt(self):
        post_dir = self.make_post("a-test-post", POST_HTML)
        post = parse_post(post_dir)

        self.assertEqual(post["title"], "A Test Post")
        self.assertEqual(post["date"], datetime.date(2025, 3, 5))
        self.assertEqual(post["categories"], ["Testing", "Python"])
        self.assertEqual(
            post["excerpt"], "This is the first paragraph, used as the excerpt for SEO purposes."
        )
        self.assertFalse(post["draft"])
        self.assertIsNone(post["image"])

    def test_detects_draft_marker(self):
        post_dir = self.make_post("draft-post", POST_HTML, draft=True)
        post = parse_post(post_dir)
        self.assertTrue(post["draft"])

    def test_picks_up_first_image(self):
        post_dir = self.make_post("with-image", POST_HTML, image_name="cover.png")
        post = parse_post(post_dir)
        self.assertEqual(post["image"], "cover.png")

    def test_missing_page_meta_leaves_date_and_categories_empty(self):
        post_dir = self.make_post("no-meta", POST_HTML_NO_META)
        post = parse_post(post_dir)
        self.assertIsNone(post["date"])
        self.assertEqual(post["categories"], [])

    def test_long_excerpt_is_truncated(self):
        long_para = "word " * 60  # well over 155 chars
        html = POST_HTML.replace(
            "<p>This is the first paragraph, used as the excerpt for SEO purposes.</p>",
            f"<p>{long_para.strip()}</p>",
        )
        post_dir = self.make_post("long-excerpt", html)
        post = parse_post(post_dir)
        self.assertLessEqual(len(post["excerpt"]), 155)
        self.assertTrue(post["excerpt"].endswith("..."))

    def test_missing_index_returns_none(self):
        post_dir = self.posts_dir / "empty"
        post_dir.mkdir()
        self.assertIsNone(parse_post(post_dir))

    def test_all_posts_sorted_newest_first(self):
        self.make_post("older", POST_HTML.replace("March 5, 2025", "January 1, 2024"))
        self.make_post("newer", POST_HTML.replace("March 5, 2025", "January 1, 2026"))
        posts = all_posts(self.site_dir)
        self.assertEqual([p["slug"] for p in posts], ["newer", "older"])

    def test_all_posts_on_missing_posts_dir(self):
        empty_site = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(empty_site))
        self.assertEqual(all_posts(empty_site), [])


if __name__ == "__main__":
    unittest.main()
