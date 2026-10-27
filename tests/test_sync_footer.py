"""Tests for scripts/sync_footer.py."""
import unittest

import context
import sync_footer

FOOTER_TEMPLATE = '<footer><a href="{root}index.html">{name}</a></footer>'

PAGE = "<html><body>\n<main>content</main>\n</body></html>\n"
PAGE_WITH_FOOTER = PAGE.replace("</body>", "<!-- FOOTER:START -->\nOLD\n<!-- FOOTER:END -->\n</body>")


class TestInject(unittest.TestCase):
    def test_adds_the_block_before_the_end_of_the_body(self):
        block = sync_footer.build_block(FOOTER_TEMPLATE, root="", name="N")
        self.assertEqual(
            sync_footer.inject(PAGE, block),
            "<html><body>\n<main>content</main>\n"
            "<!-- FOOTER:START -->\n<footer><a href=\"index.html\">N</a></footer>\n<!-- FOOTER:END -->\n"
            "</body></html>\n",
        )

    def test_replaces_an_existing_block(self):
        block = sync_footer.build_block(FOOTER_TEMPLATE, root="", name="N")
        self.assertNotIn("OLD", sync_footer.inject(PAGE_WITH_FOOTER, block))

    def test_a_page_with_no_body_returns_none(self):
        self.assertIsNone(sync_footer.inject("<p>fragment</p>", "<!-- FOOTER:START -->x<!-- FOOTER:END -->"))


class TestProfileAnchors(unittest.TestCase):
    def test_one_anchor_per_profile_in_order_that_opens_a_new_tab_as_me(self):
        anchors = sync_footer.profile_anchors(context.FAKE_SITE).splitlines()
        self.assertEqual(len(anchors), 3)
        self.assertIn('href="https://github.com/testperson" target="_blank" rel="me noopener">GitHub</a>', anchors[0])
        self.assertTrue(anchors[2].endswith(">LinkedIn</a>"))


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        (self.repo_root / "templates").mkdir()
        (self.repo_root / "templates" / "footer.html").write_text(FOOTER_TEMPLATE)
        self.site_dir = self.repo_root / "site"

    def test_stamps_pages_and_posts_with_the_right_root(self):
        (self.site_dir / "about.html").write_text(PAGE)
        post_dir = self.site_dir / "posts" / "p"
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(PAGE)
        self.assertEqual(len(sync_footer.sync(self.repo_root)), 2)
        self.assertIn('href="index.html"', (self.site_dir / "about.html").read_text())
        self.assertIn('href="../../index.html"', (post_dir / "index.html").read_text())

    def test_a_page_with_nav_off_gets_no_footer(self):
        (self.site_dir / "resume.html").write_text(PAGE)
        self.assertEqual(sync_footer.sync(self.repo_root), [])

    def test_second_run_changes_nothing(self):
        (self.site_dir / "about.html").write_text(PAGE)
        sync_footer.sync(self.repo_root)
        self.assertEqual(sync_footer.sync(self.repo_root), [])


if __name__ == "__main__":
    unittest.main()
