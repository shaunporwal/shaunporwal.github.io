import datetime
import struct
import unittest

import context
import gen_blog_index
from lib_images import PNG_SIGNATURE

PNG_640X480 = PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 640, 480) + b"\x08\x06\x00\x00\x00"

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
    def setUp(self):
        self.site_dir = context.temp_repo(self) / "site"
        self.post = {
            "slug": "hello-world",
            "title": "Hello World",
            "date": datetime.date(2025, 3, 5),
            "categories": ["A", "B"],
            "image": None,
        }

    def test_includes_title_link_date_and_categories(self):
        item = gen_blog_index.render_item(self.post, self.site_dir)
        self.assertIn('<a class="post-title" href="posts/hello-world/index.html">Hello World</a>', item)
        self.assertIn('<time class="post-date" datetime="2025-03-05">March 5, 2025</time>', item)
        self.assertIn('<p class="post-cats"><span class="cat">A</span><span class="cat">B</span></p>', item)

    def test_the_row_reveals_on_scroll(self):
        item = gen_blog_index.render_item(self.post, self.site_dir)
        self.assertIn('<li class="post-row" data-reveal-item>', item)

    def test_no_date_or_categories_leave_those_parts_out(self):
        item = gen_blog_index.render_item({**self.post, "date": None, "categories": []}, self.site_dir)
        self.assertNotIn("<time", item)
        self.assertNotIn("post-cats", item)

    def test_thumbnail_has_a_lazy_decorative_image_with_its_size(self):
        (self.site_dir / "posts" / "hello-world").mkdir(parents=True)
        (self.site_dir / "posts" / "hello-world" / "cover.png").write_bytes(PNG_640X480)
        item = gen_blog_index.render_item({**self.post, "image": "cover.png"}, self.site_dir)
        self.assertIn(
            '<img class="post-thumb" src="posts/hello-world/cover.png" alt="" width="640" height="480" '
            'loading="lazy" decoding="async">',
            item,
        )

    def test_no_thumbnail_when_post_has_no_image(self):
        self.assertNotIn("post-thumb", gen_blog_index.render_item(self.post, self.site_dir))


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.site_dir = self.repo_root / "site"

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

        changed = gen_blog_index.sync(self.repo_root)

        self.assertTrue(changed)
        text = (self.site_dir / "index.html").read_text()
        self.assertIn("post-a", text)
        self.assertNotIn("draft-post", text)
        self.assertNotIn("OLD CONTENT", text)

    def test_no_markers_returns_false(self):
        (self.site_dir / "index.html").write_text(INDEX_WITHOUT_MARKERS)
        self.assertFalse(gen_blog_index.sync(self.repo_root))

    def test_idempotent_second_run(self):
        (self.site_dir / "index.html").write_text(INDEX_TEMPLATE)
        self.make_post("post-a", "January 1, 2025")
        gen_blog_index.sync(self.repo_root)
        self.assertFalse(gen_blog_index.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
