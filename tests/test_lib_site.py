import json
import unittest

import context
from lib_schema import SchemaError
from lib_site import REPO_ROOT, load_pages, load_site, page_url


class TestLoadSite(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)

    def test_loads_fields_from_site_json(self):
        site = load_site(self.repo_root)
        self.assertEqual(site["name"], "Test Person")
        self.assertEqual(site["base_url"], "https://example.com")
        self.assertEqual(site["github"], "https://github.com/testperson")

    def test_computes_default_og_image_from_base_url_and_path(self):
        site = load_site(self.repo_root)
        self.assertEqual(site["default_og_image"], "https://example.com/media/avatar.jpg")


class TestLoadPages(unittest.TestCase):
    def test_loads_the_page_list(self):
        pages = load_pages(context.temp_repo(self))
        self.assertEqual([p["file"] for p in pages], [p["file"] for p in context.FAKE_PAGES])

    def test_rejects_a_page_with_no_nav_setting(self):
        repo_root = context.temp_repo(self)
        pages = [{k: v for k, v in context.FAKE_PAGES[0].items() if k != "nav"}]
        (repo_root / "data" / "pages.json").write_text(json.dumps(pages))
        with self.assertRaises(SchemaError):
            load_pages(repo_root)

    def test_the_real_page_list_is_valid(self):
        self.assertTrue(load_pages(REPO_ROOT))


class TestPageUrl(unittest.TestCase):
    def test_index_is_the_site_root(self):
        self.assertEqual(page_url("https://x.com", "index.html"), "https://x.com/")

    def test_other_pages_keep_their_file_name(self):
        self.assertEqual(page_url("https://x.com", "about.html"), "https://x.com/about.html")


class TestRepoRoot(unittest.TestCase):
    def test_points_at_this_repo(self):
        self.assertEqual(REPO_ROOT, context.REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
