import json
import unittest

import context
import gen_manifest


class TestGenManifest(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        gen_manifest.sync(self.repo_root)
        path = self.repo_root / "site" / "manifest.webmanifest"
        self.manifest = json.loads(path.read_text())

    def test_names_the_site_and_uses_the_light_background_for_both_colors(self):
        self.assertEqual(self.manifest["name"], "Test Person")
        self.assertEqual(self.manifest["theme_color"], "#ffffff")
        self.assertEqual(self.manifest["background_color"], "#ffffff")

    def test_lists_each_png_icon_and_the_svg(self):
        icons = self.manifest["icons"]
        self.assertEqual(icons[0], {"src": "/media/icon-192.png", "sizes": "192x192", "type": "image/png"})
        self.assertEqual(icons[-1], {"src": "/media/favicon.svg", "sizes": "any", "type": "image/svg+xml"})

    def test_second_run_changes_nothing(self):
        self.assertFalse(gen_manifest.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
