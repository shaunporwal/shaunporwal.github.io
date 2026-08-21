import pathlib
import tempfile
import unittest

import context  # noqa: F401
import gen_blog_index

POST_HTML = """<main class="page">
  <h1 class="page-title">{title}</h1>
  <p class="page-meta">{date} &middot; <span class="cat">{cat}</span></p>
<p>Excerpt.</p>
</main>
"""

INDEX_TEMPLATE = """<html><body>
<main class="page">
  <ul class="post-list">
<!-- POSTLIST:START -->
OLD CONTENT
<!-- POSTLIST:END -->
  </ul>
</main>
</body></html>
"""

INDEX_WITHOUT_MARKERS = "<html><body><main>no listing here</main></body></html>"


class TestRenderItem(unittest.TestCase):
    def test_includes_title_date_and_categories(self):
        post = {
            "slug": "hello-world",
            "title": "Hello World",
            "date": __import__("datetime").date(2025, 3, 5),
            "categories": ["A", "B"],
        }
        item = gen_blog_index.render_item(post)
        self.assertIn('href="posts/hello-world/index.html"', item)
        self.assertIn("Hello World", item)
        self.assertIn("March 5, 2025", item)
        self.assertIn('<span class="cat">A</span><span class="cat">B</span>', item)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site_dir = pathlib.Path(self.tmp.name)

    def make_post(self, slug, date, draft=False):
        post_dir = self.site_dir / "posts" / slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(
            POST_HTML.format(title=slug, date=date, cat="Test")
        )
        if draft:
            (post_dir / ".draft").touch()

    def test_replaces_marker_block_with_published_posts(self):
        (self.site_dir / "index.html").write_text(INDEX_TEMPLATE)
        self.make_post("post-a", "January 1, 2025")
        self.make_post("draft-post", "January 2, 2025", draft=True)

        changed = gen_blog_index.sync(self.site_dir)

        self.assertTrue(changed)
        text = (self.site_dir / "index.html").read_text()
        self.assertIn("post-a", text)
        self.assertNotIn("draft-post", text)
        self.assertNotIn("OLD CONTENT", text)

    def test_no_markers_returns_false(self):
        (self.site_dir / "index.html").write_text(INDEX_WITHOUT_MARKERS)
        self.assertFalse(gen_blog_index.sync(self.site_dir))

    def test_idempotent_second_run(self):
        (self.site_dir / "index.html").write_text(INDEX_TEMPLATE)
        self.make_post("post-a", "January 1, 2025")
        gen_blog_index.sync(self.site_dir)
        self.assertFalse(gen_blog_index.sync(self.site_dir))


if __name__ == "__main__":
    unittest.main()
