"""The rendered icons and the social image have the sizes that data/site.json and the card formats
declare. No generator makes these files, so this test catches a file that someone swapped for a
wrong size."""
import json
import pathlib
import unittest

import context
from lib_images import image_size

MEDIA_DIR = context.REPO_ROOT / "site" / "media"
APPLE_TOUCH_SIZE = 180
FAVICON_SIZE = 48
SOCIAL_SIZE = (1200, 630)


def declared_icons() -> dict:
    return json.loads((context.REPO_ROOT / "data" / "site.json").read_text())["icons"]


def size_of(public_path: str) -> tuple[int, int] | None:
    return image_size(MEDIA_DIR / pathlib.PurePosixPath(public_path).name)


def wrong_sizes(expected: dict[str, tuple[int, int]]) -> list[str]:
    return [f"{path}: {size_of(path)} is not {want}" for path, want in expected.items() if size_of(path) != want]


class TestMediaSizes(unittest.TestCase):
    def test_reports_a_size_that_differs(self):
        self.assertEqual(len(wrong_sizes({"/media/favicon-48.png": (1, 1)})), 1)

    def test_manifest_icons_match_their_declared_sizes(self):
        expected = {item["path"]: (item["size"], item["size"]) for item in declared_icons()["manifest"]}
        self.assertEqual(wrong_sizes(expected), [])

    def test_favicon_and_touch_icon_have_the_standard_sizes(self):
        icons = declared_icons()
        expected = {
            icons["png"]: (FAVICON_SIZE, FAVICON_SIZE),
            icons["apple"]: (APPLE_TOUCH_SIZE, APPLE_TOUCH_SIZE),
        }
        self.assertEqual(wrong_sizes(expected), [])

    def test_social_image_is_1200_by_630(self):
        path = json.loads((context.REPO_ROOT / "data" / "site.json").read_text())["og_image_path"]
        self.assertEqual(wrong_sizes({path: SOCIAL_SIZE}), [])


if __name__ == "__main__":
    unittest.main()
