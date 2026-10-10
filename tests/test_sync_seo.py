import json
import pathlib
import re
import unittest

import context
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
            sync_seo.SeoMeta("https://example.com/", "A Title", 'A "quoted" description', "website", "https://example.com/img.png")
        )
        self.assertIn('<meta name="description" content="A &quot;quoted&quot; description">', block)
        self.assertIn('<link rel="canonical" href="https://example.com/">', block)
        self.assertIn('<meta property="og:type" content="website">', block)
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', block)

    def test_inject_into_page_without_markers(self):
        text = PAGE_TEMPLATE.format(title="Home", h1="Home", excerpt="hi")
        block = sync_seo.build_block(sync_seo.SeoMeta("u", "t", "d", "website", "i"))
        result = sync_seo.inject(text, block)
        self.assertIsNotNone(result)
        self.assertIn("<!-- SEO:START -->", result)

    def test_inject_replaces_existing_markers(self):
        text = PAGE_TEMPLATE.format(title="Home", h1="Home", excerpt="hi")
        first = sync_seo.inject(text, sync_seo.build_block(sync_seo.SeoMeta("u", "old-title", "d", "website", "i")))
        second = sync_seo.inject(first, sync_seo.build_block(sync_seo.SeoMeta("u", "new-title", "d", "website", "i")))
        self.assertIn("new-title", second)
        self.assertNotIn("old-title", second)

    def test_inject_twice_gives_the_same_text(self):
        text = PAGE_TEMPLATE.format(title="Home", h1="Home", excerpt="hi")
        block = sync_seo.build_block(sync_seo.SeoMeta("u", "t", "d", "website", "i"))
        once = sync_seo.inject(text, block)
        self.assertEqual(sync_seo.inject(once, block), once)

    def test_inject_into_a_page_with_no_title_returns_none(self):
        block = sync_seo.build_block(sync_seo.SeoMeta("u", "t", "d", "website", "i"))
        self.assertIsNone(sync_seo.inject("<html></html>", block))

    def test_json_ld_cannot_close_its_script_tag(self):
        tag = sync_seo.json_ld({"headline": "A </script> title"})
        self.assertIn("A <\\/script> title", tag)
        self.assertEqual(tag.count("</script>"), 1)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.site_dir = self.repo_root / "site"

    def test_top_level_pages_get_seo_tags(self):
        (self.site_dir / "index.html").write_text(
            PAGE_TEMPLATE.format(title="Test Person", h1="Home", excerpt="hi")
        )
        changed = sync_seo.sync(self.repo_root)
        self.assertIn("index.html", changed)
        text = (self.site_dir / "index.html").read_text()
        self.assertIn('property="og:url" content="https://example.com/"', text)
        self.assertIn("Test Person", text)

    def test_posts_get_auto_derived_seo_tags(self):
        post_dir = self.site_dir / "posts" / "hello-world"
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(
            PAGE_TEMPLATE.format(title="Hello — Test Person", h1="Hello World", excerpt="An intro paragraph.")
        )
        changed = sync_seo.sync(self.repo_root)
        self.assertIn("posts/hello-world/index.html", changed)
        text = (post_dir / "index.html").read_text()
        self.assertIn("An intro paragraph.", text)
        self.assertIn("https://example.com/posts/hello-world/", text)

    def make_post(self, slug: str, title: str, draft: bool = False) -> pathlib.Path:
        post_dir = self.site_dir / "posts" / slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(PAGE_TEMPLATE.format(title=title, h1=title, excerpt="An intro."))
        if draft:
            (post_dir / ".draft").touch()
        return post_dir / "index.html"

    def test_draft_post_gets_noindex_and_no_structured_data(self):
        path = self.make_post("draft-post", "Draft", draft=True)
        sync_seo.sync(self.repo_root)
        text = path.read_text()
        self.assertIn('<meta name="robots" content="noindex">', text)
        self.assertNotIn("BlogPosting", text)

    def test_published_post_gets_blog_posting_data(self):
        path = self.make_post("hello", "Hello World")
        sync_seo.sync(self.repo_root)
        text = path.read_text()
        self.assertNotIn("noindex", text)
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.DOTALL).group(1))
        self.assertEqual(data["@type"], "BlogPosting")
        self.assertEqual(data["headline"], "Hello World")
        self.assertEqual(data["datePublished"], "2025-03-05")
        self.assertEqual(data["author"], {"@type": "Person", "name": "Test Person", "url": "https://example.com/"})

    def test_top_level_pages_have_no_noindex(self):
        (self.site_dir / "about.html").write_text(PAGE_TEMPLATE.format(title="About", h1="About", excerpt="hi"))
        sync_seo.sync(self.repo_root)
        self.assertNotIn("noindex", (self.site_dir / "about.html").read_text())

    def test_missing_top_level_page_is_skipped_without_error(self):
        # No index.html/about.html/etc present at all.
        changed = sync_seo.sync(self.repo_root)
        self.assertEqual(changed, [])


if __name__ == "__main__":
    unittest.main()
