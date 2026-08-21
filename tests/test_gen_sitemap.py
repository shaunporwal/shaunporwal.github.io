import datetime
import pathlib
import tempfile
import unittest

import context
import gen_sitemap

POST_HTML = """<main class="page">
  <h1 class="page-title">A Post</h1>
  <p class="page-meta">March 5, 2025</p>
<p>Excerpt.</p>
</main>
"""


class TestRenderSitemap(unittest.TestCase):
    def test_renders_loc_and_lastmod(self):
        urls = [("https://x.com/", None), ("https://x.com/posts/a/", datetime.date(2025, 1, 2))]
        xml = gen_sitemap.render_sitemap(urls)
        self.assertIn("<loc>https://x.com/</loc>", xml)
        self.assertIn("<loc>https://x.com/posts/a/</loc>", xml)
        self.assertIn("<lastmod>2025-01-02</lastmod>", xml)
        self.assertTrue(xml.startswith('<?xml version="1.0"'))


class TestCollectUrls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = pathlib.Path(self.tmp.name)
        self.site_dir = self.repo_root / "site"
        self.site_dir.mkdir()
        context.write_fake_site_json(self.repo_root)

    def make_post(self, slug, draft=False):
        post_dir = self.site_dir / "posts" / slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(POST_HTML)
        if draft:
            (post_dir / ".draft").touch()

    def test_includes_top_level_pages(self):
        urls = gen_sitemap.collect_urls(self.site_dir)
        locs = [u for u, _ in urls]
        self.assertIn("https://example.com/", locs)
        self.assertIn("https://example.com/about.html", locs)

    def test_excludes_draft_posts(self):
        self.make_post("published")
        self.make_post("draft-one", draft=True)
        urls = gen_sitemap.collect_urls(self.site_dir)
        locs = [u for u, _ in urls]
        self.assertIn("https://example.com/posts/published/", locs)
        self.assertNotIn("https://example.com/posts/draft-one/", locs)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = pathlib.Path(self.tmp.name)
        self.site_dir = self.repo_root / "site"
        self.site_dir.mkdir()
        context.write_fake_site_json(self.repo_root)

    def test_writes_file_on_first_run(self):
        self.assertTrue(gen_sitemap.sync(self.site_dir))
        self.assertTrue((self.site_dir / "sitemap.xml").exists())

    def test_second_run_with_no_changes_returns_false(self):
        gen_sitemap.sync(self.site_dir)
        self.assertFalse(gen_sitemap.sync(self.site_dir))

    def test_new_post_triggers_a_change(self):
        gen_sitemap.sync(self.site_dir)
        post_dir = self.site_dir / "posts" / "new-post"
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(POST_HTML)
        self.assertTrue(gen_sitemap.sync(self.site_dir))


if __name__ == "__main__":
    unittest.main()
