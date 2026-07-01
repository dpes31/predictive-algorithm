from __future__ import annotations

import unittest

from simulation.predictable_group_feasibility import (
    bootstrap_seed,
    group_marginals,
    run_predictable_group_gate,
    seed_for,
)


class PredictableGroupFeasibilityTests(unittest.TestCase):
    def test_seed_namespaces_are_deterministic_and_isolated(self):
        self.assertEqual(seed_for("positive", 3), seed_for("positive", 3))
        self.assertNotEqual(seed_for("positive", 3), seed_for("null", 3))
        with self.assertRaises(ValueError):
            seed_for("positive", 3, namespace="CAL")
        with self.assertRaises(ValueError):
            seed_for("positive", 3, namespace="SEALED")
        self.assertEqual(
            bootstrap_seed("delta_log_loss", "abc"),
            bootstrap_seed("delta_log_loss", "abc"),
        )

    def test_group_marginals_sum_to_six(self):
        for size in (6, 10, 15):
            inside, outside = group_marginals(size)
            self.assertAlmostEqual(size * inside + (45 - size) * outside, 6.0)
            self.assertGreater(inside, outside)

    def test_small_gate_is_reproducible_and_scope_locked(self):
        first = run_predictable_group_gate(
            positive_replicates=2,
            null_replicates=3,
            bootstrap_resamples=20,
            implementation_commit="test-commit",
        )
        second = run_predictable_group_gate(
            positive_replicates=2,
            null_replicates=3,
            bootstrap_resamples=20,
            implementation_commit="test-commit",
        )
        self.assertEqual(first, second)
        self.assertEqual(first["namespace"], "DEV-PG")
        self.assertEqual(first["bootstrap_namespace"], "DEV-PG-CI")
        self.assertEqual(first["final_distribution"], "M0_ONLY")
        self.assertFalse(first["full_m3_dev_executed"])
        self.assertFalse(first["calibration_executed"])
        self.assertFalse(first["sealed_validation_executed"])
        self.assertFalse(first["real_data_executed"])
        self.assertFalse(first["mobile_work_executed"])
        self.assertFalse(first["main_merge_performed"])
        self.assertFalse(first["public_release_allowed"])


if __name__ == "__main__":
    unittest.main()
