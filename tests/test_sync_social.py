import pathlib
import tempfile
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
    def test_jsonld_block_uses_site_fields(self):
        block = sync_social.build_jsonld_block(context.FAKE_SITE)
        self.assertIn('"name": "Test Person"', block)
        self.assertIn('"url": "https://example.com"', block)
        self.assertIn('"email": "mailto:test@example.com"', block)
        self.assertIn('"https://github.com/testperson"', block)
        self.assertIn('"https://x.com/testperson"', block)
        self.assertIn('"https://linkedin.com/in/testperson"', block)

    def test_links_block_uses_site_fields(self):
        block = sync_social.build_links_block(context.FAKE_SITE)
        self.assertIn('href="https://x.com/testperson"', block)
        self.assertIn('href="https://linkedin.com/in/testperson"', block)
        self.assertIn('href="https://github.com/testperson"', block)
        self.assertIn('href="mailto:test@example.com"', block)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = pathlib.Path(self.tmp.name)
        self.site_dir = self.repo_root / "site"
        self.site_dir.mkdir()
        context.write_fake_site_json(self.repo_root)

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
