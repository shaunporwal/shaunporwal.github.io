import pathlib
import tempfile
import unittest

import context  # noqa: F401
import sync_seo

PAGE_TEMPLATE = """<!doctype html>
<html><head>
<meta charset="utf-8">
<title>{title}</title>
</head><body>
<main class="page">
  <h1 class="page-title">{h1}</h1>
  <p class="page-meta">March 5, 2025</p>
<p>{excerpt}</p>
</main>
</body></html>
"""


class TestBuildBlockAndInject(unittest.TestCase):
    def test_build_block_contains_expected_tags(self):
        block = sync_seo.build_block(
            "https://example.com/", "A Title", 'A "quoted" description', "website", "https://example.com/img.png"
        )
        self.assertIn('<meta name="description" content="A &quot;quoted&quot; description">', block)
        self.assertIn('<link rel="canonical" href="https://example.com/">', block)
        self.assertIn('<meta property="og:type" content="website">', block)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', block)

    def test_inject_into_page_without_markers(self):
        text = PAGE_TEMPLATE.format(title="Home", h1="Home", excerpt="hi")
        block = sync_seo.build_block("u", "t", "d", "website", "i")
        result = sync_seo.inject(text, block)
        self.assertIsNotNone(result)
        self.assertIn("<!-- SEO:START -->", result)

    def test_inject_replaces_existing_markers(self):
        text = PAGE_TEMPLATE.format(title="Home", h1="Home", excerpt="hi")
        first = sync_seo.inject(text, sync_seo.build_block("u", "old-title", "d", "website", "i"))
        second = sync_seo.inject(first, sync_seo.build_block("u", "new-title", "d", "website", "i"))
        self.assertIn("new-title", second)
        self.assertNotIn("old-title", second)

    def test_inject_returns_none_when_unchanged(self):
        text = PAGE_TEMPLATE.format(title="Home", h1="Home", excerpt="hi")
        block = sync_seo.build_block("u", "t", "d", "website", "i")
        once = sync_seo.inject(text, block)
        self.assertIsNone(sync_seo.inject(once, block))


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site_dir = pathlib.Path(self.tmp.name)

    def test_top_level_pages_get_seo_tags(self):
        (self.site_dir / "index.html").write_text(
            PAGE_TEMPLATE.format(title="Shaun Porwal", h1="Home", excerpt="hi")
        )
        changed = sync_seo.sync(self.site_dir)
        self.assertIn("index.html", changed)
        text = (self.site_dir / "index.html").read_text()
        self.assertIn('property="og:url" content="https://shaunporwal.com/"', text)

    def test_posts_get_auto_derived_seo_tags(self):
        post_dir = self.site_dir / "posts" / "hello-world"
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(
            PAGE_TEMPLATE.format(title="Hello — Shaun Porwal", h1="Hello World", excerpt="An intro paragraph.")
        )
        changed = sync_seo.sync(self.site_dir)
        self.assertIn("posts/hello-world/index.html", changed)
        text = (post_dir / "index.html").read_text()
        self.assertIn("An intro paragraph.", text)
        self.assertIn("https://shaunporwal.com/posts/hello-world/", text)

    def test_missing_top_level_page_is_skipped_without_error(self):
        # No index.html/about.html/etc present at all.
        changed = sync_seo.sync(self.site_dir)
        self.assertEqual(changed, [])


if __name__ == "__main__":
    unittest.main()
