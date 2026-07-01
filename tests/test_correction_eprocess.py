from __future__ import annotations

import math
import unittest

from engine.eprocess import LogEProcess, WindowMixtureEProcess, logmeanexp


class CorrectionEProcessTests(unittest.TestCase):
    def test_logmeanexp_matches_arithmetic_mean(self):
        self.assertAlmostEqual(math.exp(logmeanexp((math.log(2.0), math.log(8.0)))), 5.0, places=12)

    def test_single_process_neutral_and_positive_updates(self):
        process = LogEProcess()
        self.assertEqual(process.e_value, 1.0)
        process.neutral_update()
        process.update_ratio(2.0)
        process.update_log_ratio(math.log(0.5))
        self.assertAlmostEqual(process.e_value, 1.0, places=12)

    def test_window_mixture_uses_registered_horizons(self):
        process = WindowMixtureEProcess((2, 4))
        for ratio in (2.0, 2.0, 0.5, 0.5, 2.0):
            process.update_ratio(ratio)
        self.assertEqual(process.observations, 4)
        expected = (0.5 * 2.0 + 2.0 * 0.5 * 0.5 * 2.0) / 2.0
        self.assertAlmostEqual(process.e_value, expected, places=12)
        process.expire()
        self.assertEqual(process.e_value, 1.0)

    def test_invalid_ratio_is_rejected(self):
        with self.assertRaises(ValueError):
            LogEProcess().update_ratio(0.0)


if __name__ == "__main__":
    unittest.main()
