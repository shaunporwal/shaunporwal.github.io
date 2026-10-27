"""The card pictures in site/js/motion.js play only while they can be seen, and stay still for a visitor who asks
for less motion or less data. The script has no test runner, so this test reads its text. The browser walk in the PR
doc checks the behavior."""
import re
import unittest

import context

SOURCE = (context.REPO_ROOT / "site" / "js" / "motion.js").read_text()
NAMED_FUNCTIONS = ("canPlayPictures", "startClip", "setPlaying", "syncPlayback", "onPictureIntersect", "armPictures")


def function_text(name: str) -> str:
    match = re.search(rf"^function {name}\(.*?^}}", SOURCE, re.DOTALL | re.MULTILINE)
    return match.group(0) if match else ""


class TestPictureScript(unittest.TestCase):
    def test_each_step_is_a_small_named_function(self):
        for name in NAMED_FUNCTIONS:
            self.assertTrue(function_text(name), name)

    def test_start_arms_the_pictures(self):
        self.assertIn("armPictures()", function_text("start"))

    def test_reduced_motion_and_save_data_keep_the_still(self):
        body = function_text("canPlayPictures")
        self.assertIn("prefersReducedMotion()", body)
        self.assertIn("saveData", body)

    def test_pictures_play_only_while_on_screen_and_while_the_tab_is_visible(self):
        self.assertIn("IntersectionObserver", function_text("armPictures"))
        self.assertIn("visibilitychange", function_text("armPictures"))
        self.assertIn("document.hidden", SOURCE)

    def test_a_clip_that_cannot_start_does_not_raise(self):
        self.assertIn(".catch(", function_text("startClip"))

    def test_the_script_marks_playing_pictures_for_the_stylesheet(self):
        self.assertIn("dataset.playing", function_text("setPlaying"))


if __name__ == "__main__":
    unittest.main()
