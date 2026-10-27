"""Every text and background pair in data/theme.json meets WCAG AA (4.5:1), in light and dark mode."""
import unittest

import context
from lib_site import load_theme

MINIMUM = 4.5
PAIRS = (
    ("foreground", "background"),
    ("foreground", "card"),
    ("foreground", "secondary"),
    ("muted-foreground", "background"),
    ("muted-foreground", "card"),
    ("primary", "background"),
    ("primary", "card"),
    ("primary-foreground", "primary"),
)


def channel(value: int) -> float:
    srgb = value / 255
    return srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4


def luminance(color: str) -> float:
    red, green, blue = (channel(int(color[index : index + 2], 16)) for index in (1, 3, 5))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class TestContrastMath(unittest.TestCase):
    def test_black_on_white_is_twenty_one(self):
        self.assertAlmostEqual(contrast("#000000", "#ffffff"), 21.0, places=1)

    def test_the_order_of_the_colors_does_not_matter(self):
        self.assertEqual(contrast("#c2410c", "#ffffff"), contrast("#ffffff", "#c2410c"))


class TestThemeContrast(unittest.TestCase):
    def test_every_pair_meets_the_minimum_in_both_modes(self):
        theme = load_theme(context.REPO_ROOT)
        failures = [
            f"{mode} {text} on {surface}: {contrast(theme[mode][text], theme[mode][surface]):.2f}"
            for mode in ("light", "dark")
            for text, surface in PAIRS
            if contrast(theme[mode][text], theme[mode][surface]) < MINIMUM
        ]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
