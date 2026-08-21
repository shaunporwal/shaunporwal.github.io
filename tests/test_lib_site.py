import pathlib
import tempfile
import unittest

import context
from lib_site import load_site


class TestLoadSite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = pathlib.Path(self.tmp.name)
        context.write_fake_site_json(self.repo_root)

    def test_loads_fields_from_site_json(self):
        site = load_site(self.repo_root)
        self.assertEqual(site["name"], "Test Person")
        self.assertEqual(site["base_url"], "https://example.com")
        self.assertEqual(site["github"], "https://github.com/testperson")

    def test_computes_default_og_image_from_base_url_and_path(self):
        site = load_site(self.repo_root)
        self.assertEqual(site["default_og_image"], "https://example.com/media/avatar.jpg")


if __name__ == "__main__":
    unittest.main()
