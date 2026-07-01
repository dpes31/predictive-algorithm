from __future__ import annotations

import unittest

from simulation.correction_development import (
    M3_GRID,
    M4_GRID,
    development_seed,
    run_m3_preflight,
)


class CorrectionDevelopmentTests(unittest.TestCase):
    def test_seed_is_deterministic_and_dev_only(self):
        first = development_seed("positive", "p4", 1.25, 3)
        second = development_seed("positive", "p4", 1.25, 3)
        self.assertEqual(first, second)
        with self.assertRaises(ValueError):
            development_seed("positive", "p4", 1.25, 3, namespace="CAL")

    def test_registered_grid_sizes(self):
        self.assertEqual(len(M4_GRID), 27)
        self.assertEqual(len(M3_GRID), 3)
        self.assertEqual(len(M4_GRID) * len(M3_GRID), 81)

    def test_small_preflight_is_reproducible_and_research_only(self):
        first = run_m3_preflight(replicates=2, draw_count=360)
        second = run_m3_preflight(replicates=2, draw_count=360)
        self.assertEqual(first, second)
        self.assertEqual(first["namespace"], "DEV")
        self.assertFalse(first["calibration_executed"])
        self.assertFalse(first["sealed_validation_executed"])
        self.assertTrue(first["research_only"])
        self.assertFalse(first["public_release_allowed"])
        self.assertEqual(first["combined_grid_count"], 81)


if __name__ == "__main__":
    unittest.main()
