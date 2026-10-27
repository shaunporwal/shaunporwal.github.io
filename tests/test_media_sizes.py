"""The rendered icons and the social image have the sizes that data/site.json and the card formats
declare. No generator makes these files, so this test catches a file that someone swapped for a
wrong size. The card pictures stay small, because every visitor downloads them."""
import json
import pathlib
import unittest

import context
from lib_images import image_size

MEDIA_DIR = context.REPO_ROOT / "site" / "media"
APPLE_TOUCH_SIZE = 180
FAVICON_SIZE = 48
SOCIAL_SIZE = (1200, 630)
PROJECTS_DIR = MEDIA_DIR / "projects"
CARD_RATIO = (16, 10)
BUDGET_BYTES = {".mp4": 450_000, ".webm": 450_000, ".webp": 100_000}


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


def over_budget(directory: pathlib.Path) -> list[str]:
    return [
        f"{path.name}: {path.stat().st_size} bytes is over {BUDGET_BYTES[path.suffix]}"
        for path in sorted(directory.iterdir())
        if path.stat().st_size > BUDGET_BYTES[path.suffix]
    ]


def clip_stills() -> list[pathlib.Path]:
    projects = json.loads((context.REPO_ROOT / "data" / "site.json").read_text())["projects"]
    clips = [project["picture"] for project in projects if project["picture"]["kind"] == "clip"]
    return [context.REPO_ROOT / "site" / clip["still"].lstrip("/") for clip in clips]


def not_card_shaped(stills: list[pathlib.Path]) -> list[str]:
    wide, high = CARD_RATIO
    sizes = {path.name: image_size(path) for path in stills}
    return [f"{name}: {size} is not 16:10" for name, size in sizes.items() if size[0] * high != size[1] * wide]


class TestProjectMedia(unittest.TestCase):
    def test_reports_a_file_over_its_budget(self):
        directory = context.temp_repo(self) / "projects"
        directory.mkdir()
        (directory / "big.webp").write_bytes(b"x" * (BUDGET_BYTES[".webp"] + 1))
        self.assertEqual(len(over_budget(directory)), 1)

    def test_every_card_picture_is_within_its_budget(self):
        self.assertEqual(over_budget(PROJECTS_DIR), [])

    def test_reports_a_still_that_is_not_card_shaped(self):
        self.assertEqual(len(not_card_shaped([MEDIA_DIR / "favicon-48.png"])), 1)

    def test_every_clip_still_has_the_card_ratio(self):
        self.assertTrue(clip_stills())
        self.assertEqual(not_card_shaped(clip_stills()), [])

    def test_the_folder_holds_only_the_file_types_that_have_a_budget(self):
        suffixes = {path.suffix for path in PROJECTS_DIR.iterdir()}
        self.assertLessEqual(suffixes, set(BUDGET_BYTES))


if __name__ == "__main__":
    unittest.main()
