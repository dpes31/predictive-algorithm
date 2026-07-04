from __future__ import annotations

import unittest

from simulation.oracle_feasibility import (
    one_sided_binomial_upper,
    oracle_seed,
    run_oracle_gate,
)


class OracleFeasibilityTests(unittest.TestCase):
    def test_seed_is_dev_only_and_deterministic(self):
        first = oracle_seed("positive", 3)
        second = oracle_seed("positive", 3)
        self.assertEqual(first, second)
        with self.assertRaises(ValueError):
            oracle_seed("positive", 3, namespace="CAL")
        with self.assertRaises(ValueError):
            oracle_seed("positive", 3, namespace="SEALED")

    def test_exact_one_sided_upper_for_zero_successes(self):
        value = one_sided_binomial_upper(0, 1000)
        self.assertAlmostEqual(value, 1.0 - 0.05 ** (1.0 / 1000.0), places=10)

    def test_small_gate_is_reproducible_and_scope_locked(self):
        first = run_oracle_gate(
            positive_replicates=20,
            null_replicates=100,
            implementation_commit="test-commit",
        )
        second = run_oracle_gate(
            positive_replicates=20,
            null_replicates=100,
            implementation_commit="test-commit",
        )
        self.assertEqual(first, second)
        self.assertEqual(first["namespace"], "DEV")
        self.assertEqual(first["model_version"], "5.0.0-research")
        self.assertEqual(first["detection_horizon"], 520)
        self.assertEqual(first["post_activation_active_life"], 208)
        self.assertEqual(first["activation_threshold"], 1000.0)
        self.assertFalse(first["predictable_group_executed"])
        self.assertFalse(first["full_m3_dev_executed"])
        self.assertFalse(first["calibration_executed"])
        self.assertFalse(first["sealed_validation_executed"])
        self.assertFalse(first["real_data_executed"])
        self.assertFalse(first["mobile_work_executed"])
        self.assertFalse(first["public_release_allowed"])


if __name__ == "__main__":
    unittest.main()
