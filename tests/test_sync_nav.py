import pathlib
import unittest

import context
import sync_nav

NAV_TEMPLATE = '<nav><a href="{root}index.html">{name}</a>\n{page_links}\n{menu_links}\n</nav>'

PAGE_WITH_MARKERS = """<html><body>
<!-- NAV:START -->
<nav>OLD NAV</nav>
<!-- NAV:END -->
<main>content</main>
</body></html>
"""

class TestPageLinks(unittest.TestCase):
    def test_lists_menu_pages_in_page_order(self):
        links = sync_nav.page_links(context.FAKE_PAGES, "../../")
        self.assertEqual(
            links,
            '      <a class="nav-link" href="../../about.html">About</a>\n'
            '      <a class="nav-link" href="../../resume.html" target="_blank" rel="noopener">Resume</a>',
        )

    def test_marks_the_current_page(self):
        links = sync_nav.page_links(context.FAKE_PAGES, "", ("about.html", "page"))
        self.assertIn('<a class="nav-link" href="about.html" aria-current="page">About</a>', links)
        self.assertNotIn('resume.html" aria-current', links)

    def test_menu_style_uses_the_menu_link_class(self):
        links = sync_nav.page_links(context.FAKE_PAGES, "", style="menu")
        self.assertIn('<a class="menu-link" href="about.html">About</a>', links)


class TestPlace(unittest.TestCase):
    def test_a_top_level_page_is_marked_page(self):
        self.assertEqual(sync_nav.current_page(pathlib.Path("about.html")), ("about.html", "page"))

    def test_a_post_marks_the_home_link(self):
        self.assertEqual(sync_nav.current_page(pathlib.Path("posts/x/index.html")), ("index.html", "true"))

    def test_root_prefix_counts_directories(self):
        self.assertEqual(sync_nav.page_root(pathlib.Path("posts/x/index.html"), context.FAKE_PAGES), "../../")
        self.assertEqual(sync_nav.page_root(pathlib.Path("about.html"), context.FAKE_PAGES), "")

    def test_an_absolute_page_uses_a_root_slash(self):
        pages = [{**context.FAKE_PAGES[0], "file": "404.html", "absolute": True}]
        self.assertEqual(sync_nav.page_root(pathlib.Path("404.html"), pages), "/")


class TestRenderAndBuildBlock(unittest.TestCase):
    def test_render_nav_fills_in_root(self):
        self.assertEqual(
            sync_nav.render_nav(NAV_TEMPLATE, root="../../", name="N", page_links="x", menu_links="y"),
            '<nav><a href="../../index.html">N</a>\nx\ny\n</nav>',
        )

    def test_build_block_wraps_in_markers(self):
        block = sync_nav.build_block(NAV_TEMPLATE, root="", name="", page_links="", menu_links="")
        self.assertTrue(block.startswith("<!-- NAV:START -->"))
        self.assertTrue(block.endswith("<!-- NAV:END -->"))


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        (self.repo_root / "templates").mkdir()
        (self.repo_root / "templates" / "nav.html").write_text(NAV_TEMPLATE)
        self.site_dir = self.repo_root / "site"

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
        self.assertIn('<a class="nav-link" href="../../about.html">About</a>', post_text)

    def test_page_without_markers_is_left_alone(self):
        (self.site_dir / "about.html").write_text("<html><body><main>no nav here</main></body></html>")
        self.assertEqual(sync_nav.sync(self.repo_root), [])

    def test_page_with_nav_off_is_skipped(self):
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
