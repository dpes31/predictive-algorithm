from __future__ import annotations

import math
import unittest

from simulation.calibration import NullCalibration
from simulation.diagnostics import build_origin_snapshots
from simulation.experiment_config import ExperimentConfig
from simulation.experiment_runner import run_gate2_3_experiment
from simulation.probe import run_blockwise_probe
from simulation.uniform_lottery import generate_uniform_draws


class SyntheticProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = [build_origin_snapshots(generate_uniform_draws(360, seed=seed)) for seed in range(6)]
        cls.calibration = NullCalibration.fit(cls.series)

    def test_probe_returns_finite_metrics(self):
        records = generate_uniform_draws(360, seed=99)
        snapshots = build_origin_snapshots(records)
        result = run_blockwise_probe(records, snapshots, self.calibration)
        self.assertIn(result.winning_model, {None, "M1", "M2", "M3"})
        self.assertEqual(set(result.model_summaries), {"M1", "M2", "M3", "SHADOW"})
        for summary in result.model_summaries.values():
            self.assertTrue(math.isfinite(summary.mean_delta_log_loss))
            self.assertTrue(math.isfinite(summary.mean_delta_brier))
        self.assertAlmostEqual(sum(result.final_shadow_weights.values()), 1.0)
        self.assertEqual(len(result.final_subexpert_weights["M1"]), 35)
        self.assertEqual(len(result.final_subexpert_weights["M2"]), 35)
        self.assertEqual(len(result.final_subexpert_weights["M3"]), 4)

    def test_small_experiment_is_reproducible_and_research_only(self):
        config = ExperimentConfig(
            draw_count=360,
            null_calibration_series=3,
            null_validation_series=2,
            positive_series_per_scenario=1,
            seed_base=55,
            alpha=0.20,
        )
        first = run_gate2_3_experiment(config)
        second = run_gate2_3_experiment(config)
        self.assertEqual(first, second)
        self.assertTrue(first["research_only"])
        self.assertFalse(first["public_release_allowed"])
        self.assertEqual(first["model_version"], "2.1.0-research")
        self.assertEqual(first["gate_revision"], "2-3R")
        self.assertEqual(first["experiment"]["draw_count"], 360)
        self.assertIn("fixed_bias_2pct", first["positive_controls"])
        self.assertIn("strict_detection_rate", first["positive_controls"]["fixed_bias_2pct"])


if __name__ == "__main__":
    unittest.main()
