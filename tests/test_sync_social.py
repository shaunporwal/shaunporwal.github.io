import unittest

import context
import sync_social

ABOUT_TEMPLATE = """<!doctype html>
<html><head>
<!-- SOCIAL_JSONLD:START -->
<script type="application/ld+json">
OLD JSONLD
</script>
<!-- SOCIAL_JSONLD:END -->
</head><body>
<div class="about-links">
  <!-- SOCIAL_LINKS:START -->
  OLD LINKS
  <!-- SOCIAL_LINKS:END -->
</div>
</body></html>
"""

ABOUT_WITHOUT_MARKERS = "<html><body>no social markers here</body></html>"


class TestBuildBlocks(unittest.TestCase):
    def test_jsonld_block_is_a_profile_page_with_the_profile_links(self):
        block = sync_social.build_jsonld_block(context.FAKE_SITE, context.SAMPLE_RECORD)
        self.assertIn('"@type": "ProfilePage"', block)
        self.assertIn('"name": "Test Person"', block)
        self.assertIn('"https://github.com/testperson"', block)
        self.assertIn('"https://x.com/testperson"', block)
        self.assertIn('"https://linkedin.com/in/testperson"', block)

    def test_no_block_holds_the_email_address(self):
        text = sync_social.build_jsonld_block(context.FAKE_SITE, context.SAMPLE_RECORD)
        text += sync_social.build_links_block(context.FAKE_SITE)
        self.assertNotIn("test@example.com", text)
        self.assertNotIn("mailto", text)

    def test_links_block_has_a_button_for_each_profile_and_the_booking_page(self):
        block = sync_social.build_links_block(context.FAKE_SITE)
        self.assertIn('class="btn btn-outline" href="https://x.com/testperson"', block)
        self.assertIn('rel="me noopener">X</a>', block)
        self.assertIn('href="https://linkedin.com/in/testperson"', block)
        self.assertIn('href="https://github.com/testperson"', block)
        self.assertIn('href="https://cal.com/testperson" target="_blank" rel="noopener">Book a call</a>', block)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        context.write_record_fixture(self.repo_root, context.SAMPLE_RECORD)
        self.site_dir = self.repo_root / "site"

    def test_replaces_both_marker_blocks(self):
        (self.site_dir / "about.html").write_text(ABOUT_TEMPLATE)
        changed = sync_social.sync(self.repo_root)
        self.assertTrue(changed)
        text = (self.site_dir / "about.html").read_text()
        self.assertNotIn("OLD JSONLD", text)
        self.assertNotIn("OLD LINKS", text)
        self.assertIn("https://github.com/testperson", text)

    def test_missing_about_html_returns_false(self):
        self.assertFalse(sync_social.sync(self.repo_root))

    def test_no_markers_returns_false(self):
        (self.site_dir / "about.html").write_text(ABOUT_WITHOUT_MARKERS)
        self.assertFalse(sync_social.sync(self.repo_root))

    def test_idempotent_second_run(self):
        (self.site_dir / "about.html").write_text(ABOUT_TEMPLATE)
        sync_social.sync(self.repo_root)
        self.assertFalse(sync_social.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
