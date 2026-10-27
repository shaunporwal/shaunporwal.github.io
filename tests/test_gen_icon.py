"""Tests for scripts/gen_icon.py."""
import unittest

import context
import gen_icon


class TestGenIcon(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        gen_icon.sync(self.repo_root)
        self.svg = (self.repo_root / "site" / "media" / "favicon.svg").read_text()

    def test_fills_the_square_with_the_primary_color_and_strokes_the_letter_in_its_foreground(self):
        self.assertIn('fill="#aa3300"', self.svg)
        self.assertIn('stroke="#ffffff"', self.svg)

    def test_is_a_valid_svg_root(self):
        self.assertTrue(self.svg.startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'))

    def test_second_run_changes_nothing(self):
        self.assertFalse(gen_icon.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
