import json
import unittest

import context
from lib_schema import SchemaError
from lib_site import REPO_ROOT, load_pages, load_site, load_theme, page_url, profile, profile_links


class TestProfiles(unittest.TestCase):
    def test_lists_label_and_url_in_the_order_of_the_data(self):
        self.assertEqual(
            profile_links(context.FAKE_SITE),
            [
                ("GitHub", "https://github.com/testperson"),
                ("X", "https://x.com/testperson"),
                ("LinkedIn", "https://linkedin.com/in/testperson"),
            ],
        )

    def test_finds_one_profile_by_its_key(self):
        self.assertEqual(profile(context.FAKE_SITE, "x"), ("X", "https://x.com/testperson"))


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

    def test_rejects_a_base_url_with_a_trailing_slash(self):
        site = {**context.FAKE_SITE, "base_url": "https://example.com/"}
        (self.repo_root / "data" / "site.json").write_text(json.dumps(site))
        with self.assertRaises(SchemaError):
            load_site(self.repo_root)

    def test_the_real_site_data_is_valid(self):
        self.assertTrue(load_site(REPO_ROOT))


class TestLoadTheme(unittest.TestCase):
    def test_loads_both_color_modes_and_the_fixed_tokens(self):
        theme = load_theme(context.temp_repo(self))
        self.assertEqual(theme["light"]["primary"], "#aa3300")
        self.assertEqual(theme["fixed"]["radius"], "0.5rem")

    def test_rejects_a_color_that_is_not_six_digit_hex(self):
        repo_root = context.temp_repo(self)
        theme = {**context.FAKE_THEME, "light": {**context.FAKE_THEME["light"], "primary": "red"}}
        (repo_root / "data" / "theme.json").write_text(json.dumps(theme))
        with self.assertRaises(SchemaError):
            load_theme(repo_root)

    def test_the_real_theme_is_valid(self):
        self.assertTrue(load_theme(REPO_ROOT))


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
