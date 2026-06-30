from __future__ import annotations

import unittest

from simulation.calibration import NullCalibration, holm_adjust, one_sided_binomial_upper
from simulation.diagnostics import build_origin_snapshots, forecast_origins
from simulation.uniform_lottery import generate_uniform_draws


class SyntheticDiagnosticTests(unittest.TestCase):
    def test_forecast_origins_are_block_aligned(self):
        self.assertEqual(forecast_origins(360), (299, 351))
        self.assertEqual(forecast_origins(299), ())

    def test_snapshots_are_deterministic_and_bounded(self):
        records = generate_uniform_draws(360, seed=123)
        first = build_origin_snapshots(records)
        second = build_origin_snapshots(records)
        self.assertEqual(first, second)
        self.assertEqual([item.origin_draw_no for item in first], [299, 351])
        for snapshot in first:
            for values in snapshot.number_features.values():
                self.assertTrue(all(-3.0 <= value <= 3.0 for value in values))
            self.assertGreaterEqual(snapshot.diagnostics["entropy_52"], 0.0)
            self.assertLessEqual(snapshot.diagnostics["entropy_52"], 1.0)

    def test_holm_adjustment_is_monotone(self):
        adjusted = holm_adjust({"a": 0.001, "b": 0.02, "c": 0.04})
        self.assertLessEqual(adjusted["a"], adjusted["b"])
        self.assertLessEqual(adjusted["b"], adjusted["c"])

    def test_zero_event_upper_bound_exceeds_point_one_percent_for_1000(self):
        upper = one_sided_binomial_upper(0, 1000)
        self.assertGreater(upper, 0.001)
        self.assertLess(upper, 0.004)

    def test_calibration_evaluates_without_nan(self):
        series = [build_origin_snapshots(generate_uniform_draws(360, seed=seed)) for seed in range(5)]
        calibration = NullCalibration.fit(series)
        result = calibration.evaluate(series[0][0])
        self.assertGreaterEqual(result.change_gate, 0.0)
        self.assertLessEqual(result.change_gate, 1.0)
        self.assertGreater(result.pair_tail_probability, 0.0)


if __name__ == "__main__":
    unittest.main()
