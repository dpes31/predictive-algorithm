from __future__ import annotations

import unittest

from engine.config import DEFAULT_CONFIG
from engine.experts import build_persistence_model, build_regime_change_model, build_reversal_model
from engine.feature_engineering import build_feature_snapshot
from simulation.uniform_lottery import generate_uniform_draws


class ExpertTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records = generate_uniform_draws(320, seed=77)
        cls.snapshot = build_feature_snapshot(
            records,
            target_draw_no=321,
            data_version="synthetic",
            config=DEFAULT_CONFIG,
        )

    def test_expert_marginals_sum_to_six(self):
        for model in (
            build_persistence_model(self.snapshot, DEFAULT_CONFIG),
            build_reversal_model(self.snapshot, DEFAULT_CONFIG),
            build_regime_change_model(self.snapshot, DEFAULT_CONFIG),
        ):
            self.assertAlmostEqual(sum(model.marginal_probabilities().values()), 6.0, places=10)

    def test_regime_model_is_uniform_until_calibrated(self):
        model = build_regime_change_model(self.snapshot, DEFAULT_CONFIG)
        expected = 6 / 45
        self.assertTrue(all(abs(value - expected) < 1e-12 for value in model.marginal_probabilities().values()))


if __name__ == "__main__":
    unittest.main()
