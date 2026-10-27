import json
import pathlib
import re
import struct
import unittest

import context
import sync_seo
from lib_images import PNG_SIGNATURE

PNG_8X8 = PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 8, 8) + b"\x08\x06\x00\x00\x00"

PAGE_TEMPLATE = """<!doctype html>
<html><head>
<meta charset="utf-8">
<title>{title}</title>
</head><body>
<main id="main" class="page">
  <h1 class="page-title">{h1}</h1>
  <p class="page-meta">March 5, 2025</p>
<p>{excerpt}</p>
</main>
</body></html>
"""


class TestBuildBlockAndInject(unittest.TestCase):
    def test_build_block_escapes_an_ampersand_and_angle_bracket_once(self):
        meta = sync_seo.SeoMeta("https://example.com/", "Cats & Dogs", "R&D <draft>", "website", "https://example.com/i.png")
        block = sync_seo.build_block(meta)
        self.assertIn('content="Cats &amp; Dogs"', block)
        self.assertIn('content="R&amp;D &lt;draft&gt;"', block)
        self.assertNotIn("&amp;amp;", block)

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

    def test_build_block_adds_the_common_head_lines_before_the_extra_lines(self):
        meta = sync_seo.SeoMeta("u", "t", "d", "website", "i", ("<extra>",))
        block = sync_seo.build_block(meta, ("<common>",))
        self.assertLess(block.index("<common>"), block.index("<extra>"))


class TestCommonHead(unittest.TestCase):
    def setUp(self):
        self.head = "\n".join(sync_seo.common_head(context.FAKE_SITE, context.FAKE_THEME))

    def test_has_a_theme_color_for_each_color_scheme(self):
        self.assertIn('<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">', self.head)
        self.assertIn('<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">', self.head)

    def test_has_the_icons_the_manifest_and_the_feed_with_absolute_urls(self):
        self.assertIn('<link rel="icon" href="https://example.com/media/favicon.svg" type="image/svg+xml">', self.head)
        self.assertIn('<link rel="apple-touch-icon" href="https://example.com/media/apple-touch-icon.png">', self.head)
        self.assertIn('<link rel="manifest" href="https://example.com/manifest.webmanifest">', self.head)
        self.assertIn('href="https://example.com/feed.xml"', self.head)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        context.write_record_fixture(self.repo_root, context.SAMPLE_RECORD)
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

    def test_the_home_page_gets_the_website_and_person_data_and_no_email(self):
        (self.site_dir / "index.html").write_text(PAGE_TEMPLATE.format(title="x", h1="Home", excerpt="hi"))
        sync_seo.sync(self.repo_root)
        text = (self.site_dir / "index.html").read_text()
        self.assertIn('"@type": "WebSite"', text)
        self.assertIn('"@type": "Person"', text)
        self.assertNotIn("test@example.com", text)

    def test_every_page_gets_the_common_head_lines(self):
        (self.site_dir / "about.html").write_text(PAGE_TEMPLATE.format(title="x", h1="About", excerpt="hi"))
        sync_seo.sync(self.repo_root)
        self.assertIn('<link rel="manifest"', (self.site_dir / "about.html").read_text())

    def test_a_page_with_the_noindex_switch_gets_a_noindex_tag(self):
        pages = [{**context.FAKE_PAGES[1], "file": "404.html", "noindex": True}]
        (self.repo_root / "data" / "pages.json").write_text(json.dumps(pages))
        (self.site_dir / "404.html").write_text(PAGE_TEMPLATE.format(title="x", h1="Missing", excerpt="hi"))
        sync_seo.sync(self.repo_root)
        self.assertIn('<meta name="robots" content="noindex">', (self.site_dir / "404.html").read_text())

    def test_the_social_image_gets_its_size_when_the_file_exists(self):
        (self.site_dir / "media").mkdir()
        (self.site_dir / "media" / "avatar.jpg").write_bytes(PNG_8X8)
        (self.site_dir / "about.html").write_text(PAGE_TEMPLATE.format(title="x", h1="About", excerpt="hi"))
        sync_seo.sync(self.repo_root)
        text = (self.site_dir / "about.html").read_text()
        self.assertIn('<meta property="og:image:width" content="8">', text)
        self.assertIn('<meta property="og:image:height" content="8">', text)

    def test_published_post_gets_breadcrumb_data(self):
        path = self.make_post("hello", "Hello World")
        sync_seo.sync(self.repo_root)
        self.assertIn('"@type": "BreadcrumbList"', path.read_text())

    def test_page_title_tag_comes_from_page_data(self):
        (self.site_dir / "about.html").write_text(PAGE_TEMPLATE.format(title="Old title", h1="About", excerpt="hi"))
        sync_seo.sync(self.repo_root)
        self.assertIn("<title>About — Test Person</title>", (self.site_dir / "about.html").read_text())

    def test_post_title_tag_comes_from_its_heading(self):
        path = self.make_post("hello", "Hello & World")
        path.write_text(path.read_text().replace("<title>Hello & World</title>", "<title>Stale</title>"))
        sync_seo.sync(self.repo_root)
        self.assertIn("<title>Hello &amp; World — Test Person</title>", path.read_text())

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
