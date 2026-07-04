from __future__ import annotations

import math
import unittest

from simulation.physical_validation import (
    ScenarioSpec,
    _m3_diagnostic_maxima,
    evaluate_series,
    generate_fast_series,
)


class PhysicalValidationHarnessTests(unittest.TestCase):
    def test_fast_series_is_deterministic_and_fixed_size(self):
        spec = ScenarioSpec("test_ball", "ball_set", lift=1.25)
        first = generate_fast_series(spec, draw_count=320, seed=123)
        second = generate_fast_series(spec, draw_count=320, seed=123)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 320)
        for draw in first:
            self.assertEqual(len(draw.numbers), 6)
            self.assertEqual(len(set(draw.numbers)), 6)
            self.assertTrue(all(1 <= number <= 45 for number in draw.numbers))

    def test_null_without_metadata_is_safe_and_finite(self):
        summary = evaluate_series(
            ScenarioSpec("test_null", "null_no_metadata"),
            category="test",
            draw_count=360,
            seed=321,
            include_m3_diagnostics=False,
        )
        self.assertIsNone(summary.direction_accuracy)
        self.assertEqual(summary.effect_size, 1.0)
        for value in summary.mean_delta_log_loss.values():
            self.assertTrue(math.isfinite(value))
        for value in summary.mean_delta_brier.values():
            self.assertTrue(math.isfinite(value))

    def test_contextual_signal_produces_direction_trials(self):
        summary = evaluate_series(
            ScenarioSpec("test_machine", "machine", lift=1.50),
            category="test",
            draw_count=360,
            seed=456,
            include_m3_diagnostics=False,
        )
        self.assertIsNotNone(summary.direction_accuracy)
        self.assertGreaterEqual(summary.direction_accuracy or 0.0, 0.0)
        self.assertLessEqual(summary.direction_accuracy or 0.0, 1.0)
        self.assertGreater(len(summary.m4_strength_by_origin), 0)

    def test_m3_diagnostics_are_nonnegative_and_finite(self):
        series = generate_fast_series(
            ScenarioSpec("test_regime", "regime_reversal", lift=1.25),
            draw_count=360,
            seed=789,
        )
        values = _m3_diagnostic_maxima(series, __import__("engine.config", fromlist=["DEFAULT_CONFIG"]).DEFAULT_CONFIG)
        self.assertEqual(len(values), 4)
        self.assertTrue(all(math.isfinite(value) and value >= 0.0 for value in values))


if __name__ == "__main__":
    unittest.main()
