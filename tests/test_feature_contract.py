from __future__ import annotations

import math
import unittest

from engine.config import DEFAULT_CONFIG
from engine.feature_engineering import build_feature_snapshot
from simulation.uniform_lottery import generate_uniform_draws


class FeatureContractTests(unittest.TestCase):
    def setUp(self):
        self.records = generate_uniform_draws(320, seed=9)

    def test_snapshot_is_deterministic_and_finite(self):
        first = build_feature_snapshot(
            self.records,
            target_draw_no=321,
            data_version="synthetic",
            config=DEFAULT_CONFIG,
        )
        second = build_feature_snapshot(
            self.records,
            target_draw_no=321,
            data_version="synthetic",
            config=DEFAULT_CONFIG,
        )
        self.assertEqual(first.snapshot_hash, second.snapshot_hash)
        self.assertEqual(first.to_dict(), second.to_dict())
        for features in first.number_features.values():
            self.assertTrue(all(math.isfinite(value) for value in features.values()))
        self.assertEqual(first.global_features["change_gate"], 0.0)
        self.assertFalse(first.global_features["change_gate_calibrated"])

    def test_feature_bounds(self):
        snapshot = build_feature_snapshot(
            self.records,
            target_draw_no=321,
            data_version="synthetic",
            config=DEFAULT_CONFIG,
        )
        for features in snapshot.number_features.values():
            self.assertTrue(all(-3.0 <= value <= 3.0 for value in features.values()))


if __name__ == "__main__":
    unittest.main()
