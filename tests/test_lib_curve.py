"""Tests for scripts/lib_curve.py: the decision curve maths and the plot geometry."""
import unittest

import context  # noqa: F401  (puts scripts/ on sys.path)
import lib_curve
from lib_curve import Curve

CURVE = Curve(prevalence=0.2, separation=1.5)


class TestNormalCdf(unittest.TestCase):
    def test_is_one_half_at_zero(self):
        self.assertAlmostEqual(lib_curve.normal_cdf(0), 0.5)

    def test_matches_a_known_value(self):
        self.assertAlmostEqual(lib_curve.normal_cdf(1.96), 0.975, places=3)


class TestBenefit(unittest.TestCase):
    def test_every_line_with_a_benefit_starts_at_the_prevalence(self):
        self.assertAlmostEqual(lib_curve.benefit_model(CURVE, 0), 0.2)
        self.assertAlmostEqual(lib_curve.benefit_all(CURVE, 0), 0.2)

    def test_treat_all_is_zero_when_the_threshold_equals_the_prevalence(self):
        self.assertAlmostEqual(lib_curve.benefit_all(CURVE, 0.2), 0.0)

    def test_treat_all_falls_below_zero_after_the_prevalence(self):
        self.assertLess(lib_curve.benefit_all(CURVE, 0.3), 0)

    def test_treat_none_is_always_zero(self):
        self.assertEqual(lib_curve.benefit_none(CURVE, 0.3), 0)

    def test_the_model_beats_both_references_across_the_range(self):
        for step in range(1, 51):
            t = step / 100
            self.assertGreaterEqual(lib_curve.benefit_model(CURVE, t), max(0, lib_curve.benefit_all(CURVE, t)) - 1e-9)

    def test_the_threshold_for_a_treat_all_benefit_reverses_the_benefit(self):
        threshold = lib_curve.threshold_for_benefit_all(CURVE, 0.04)
        self.assertAlmostEqual(lib_curve.benefit_all(CURVE, threshold), 0.04)

    def test_the_model_matches_the_hub_script(self):
        # Values from assets/js/decision-curve.js in the Junto hub, for the same prevalence and separation.
        for threshold, hub_value in {0.1: 0.143243, 0.2: 0.109349, 0.5: 0.048534}.items():
            self.assertAlmostEqual(lib_curve.benefit_model(CURVE, threshold), hub_value, places=5)


class TestGeometry(unittest.TestCase):
    def test_the_plot_box_sits_inside_the_view_box(self):
        box = lib_curve.BOX
        self.assertGreater(box["left"], 0)
        self.assertLess(box["right"], lib_curve.WIDTH)
        self.assertGreater(box["top"], 0)
        self.assertLess(box["bottom"], lib_curve.HEIGHT)

    def test_the_view_box_has_the_card_picture_ratio(self):
        self.assertEqual(lib_curve.WIDTH * 10, lib_curve.HEIGHT * 16)

    def test_threshold_zero_is_the_left_edge_and_the_top_threshold_the_right_edge(self):
        self.assertEqual(lib_curve.x_at(0), lib_curve.BOX["left"])
        self.assertEqual(lib_curve.x_at(lib_curve.T_MAX), lib_curve.BOX["right"])

    def test_the_lowest_benefit_is_the_bottom_edge(self):
        self.assertAlmostEqual(lib_curve.y_at(lib_curve.NB_MIN), lib_curve.BOX["bottom"])

    def test_a_higher_benefit_is_higher_on_the_page(self):
        self.assertLess(lib_curve.y_at(0.1), lib_curve.y_at(0.0))


class TestPaths(unittest.TestCase):
    def test_a_line_path_starts_with_a_move_and_samples_the_whole_range(self):
        path = lib_curve.line_path(CURVE, "model")
        self.assertTrue(path.startswith("M20 "))
        self.assertEqual(path.count("L"), 100)

    def test_numbers_have_one_decimal_and_no_trailing_zero(self):
        self.assertEqual(lib_curve.number(23.30001), "23.3")
        self.assertEqual(lib_curve.number(32.0), "32")

    def test_the_area_closes_along_the_zero_line(self):
        path = lib_curve.area_path(CURVE)
        zero = lib_curve.number(lib_curve.y_at(0))
        self.assertTrue(path.endswith(f"L{lib_curve.number(lib_curve.x_at(0))} {zero}Z"))

    def test_the_same_curve_gives_the_same_path(self):
        self.assertEqual(lib_curve.line_path(CURVE, "all"), lib_curve.line_path(CURVE, "all"))

    def test_the_marker_sits_on_the_model_line(self):
        x, y = lib_curve.marker_at(CURVE, 0.2)
        self.assertEqual(x, lib_curve.x_at(0.2))
        self.assertEqual(y, lib_curve.y_at(lib_curve.benefit_model(CURVE, 0.2)))


if __name__ == "__main__":
    unittest.main()
