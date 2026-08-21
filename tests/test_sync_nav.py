import pathlib
import tempfile
import unittest

import context  # noqa: F401
import sync_nav

NAV_TEMPLATE = '<nav><a href="{root}index.html">Home</a></nav>'

PAGE_WITH_MARKERS = """<html><body>
<!-- NAV:START -->
<nav>OLD NAV</nav>
<!-- NAV:END -->
<main>content</main>
</body></html>
"""

PAGE_WITHOUT_MARKERS = "<html><body><main>no nav here</main></body></html>"


class TestRenderAndBuildBlock(unittest.TestCase):
    def test_render_nav_fills_in_root(self):
        self.assertEqual(
            sync_nav.render_nav(NAV_TEMPLATE, "../../"),
            '<nav><a href="../../index.html">Home</a></nav>',
        )

    def test_build_block_wraps_in_markers(self):
        block = sync_nav.build_block(NAV_TEMPLATE, "")
        self.assertTrue(block.startswith("<!-- NAV:START -->"))
        self.assertTrue(block.endswith("<!-- NAV:END -->"))


class TestInject(unittest.TestCase):
    def test_replaces_existing_markers(self):
        block = sync_nav.build_block(NAV_TEMPLATE, "")
        result = sync_nav.inject(PAGE_WITH_MARKERS, block)
        self.assertIsNotNone(result)
        self.assertIn('<a href="index.html">Home</a>', result)
        self.assertNotIn("OLD NAV", result)

    def test_no_markers_returns_none(self):
        block = sync_nav.build_block(NAV_TEMPLATE, "")
        self.assertIsNone(sync_nav.inject(PAGE_WITHOUT_MARKERS, block))

    def test_identical_content_returns_none(self):
        block = sync_nav.build_block(NAV_TEMPLATE, "")
        already_synced = PAGE_WITH_MARKERS.replace(
            "<!-- NAV:START -->\n<nav>OLD NAV</nav>\n<!-- NAV:END -->", block
        )
        self.assertIsNone(sync_nav.inject(already_synced, block))


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = pathlib.Path(self.tmp.name)
        (self.repo_root / "templates").mkdir()
        (self.repo_root / "templates" / "nav.html").write_text(NAV_TEMPLATE)
        self.site_dir = self.repo_root / "site"
        self.site_dir.mkdir()

    def test_updates_root_and_nested_pages_with_correct_depth(self):
        (self.site_dir / "about.html").write_text(PAGE_WITH_MARKERS)
        post_dir = self.site_dir / "posts" / "my-post"
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(PAGE_WITH_MARKERS)

        changed = sync_nav.sync(self.repo_root)

        self.assertEqual(len(changed), 2)
        about_text = (self.site_dir / "about.html").read_text()
        self.assertIn('href="index.html"', about_text)
        post_text = (post_dir / "index.html").read_text()
        self.assertIn('href="../../index.html"', post_text)

    def test_resume_html_is_skipped(self):
        (self.site_dir / "resume.html").write_text(PAGE_WITH_MARKERS)
        changed = sync_nav.sync(self.repo_root)
        self.assertEqual(changed, [])
        self.assertIn("OLD NAV", (self.site_dir / "resume.html").read_text())

    def test_idempotent_second_run_reports_no_changes(self):
        (self.site_dir / "about.html").write_text(PAGE_WITH_MARKERS)
        sync_nav.sync(self.repo_root)
        second_run_changed = sync_nav.sync(self.repo_root)
        self.assertEqual(second_run_changed, [])


if __name__ == "__main__":
    unittest.main()
