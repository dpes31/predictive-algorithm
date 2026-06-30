from __future__ import annotations

import unittest

from engine.config import EngineConfig
from engine.maxt_gate import MaxTCalibration


class MaxTGateTests(unittest.TestCase):
    def test_smoke_calibration_is_not_full_contract_ready(self):
        calibration = MaxTCalibration.fit(
            [
                [{"shift_52": 1.0, "cusum": 0.5}],
                [{"shift_52": 1.5, "cusum": 1.2}],
            ]
        )
        self.assertFalse(calibration.full_contract_ready)
        result = calibration.evaluate(
            {"shift_52": 100.0, "cusum": 100.0},
            require_full_contract=False,
        )
        self.assertFalse(result.active)
        self.assertAlmostEqual(result.empirical_p_value, 1 / 3)

    def test_full_contract_can_activate_without_holm_double_penalty(self):
        config = EngineConfig(
            maxt_alpha=0.30,
            maxt_min_calibration_series=3,
        )
        calibration = MaxTCalibration.fit(
            [
                [{"shift_52": 1.0, "cusum": 0.5}],
                [{"shift_52": 1.5, "cusum": 1.2}],
                [{"shift_52": 2.0, "cusum": 1.8}],
            ],
            config=config,
            require_full_contract=True,
        )
        result = calibration.evaluate({"shift_52": 10.0, "cusum": 2.0})
        self.assertTrue(calibration.full_contract_ready)
        self.assertTrue(result.active)
        self.assertAlmostEqual(result.empirical_p_value, 1 / 4)

    def test_series_max_controls_all_origins_and_diagnostics(self):
        calibration = MaxTCalibration.fit(
            [
                [
                    {"shift_52": 1.0, "cusum": 0.2},
                    {"shift_52": 0.4, "cusum": 3.0},
                ],
                [
                    {"shift_52": 2.0, "cusum": 0.1},
                ],
            ]
        )
        self.assertEqual(calibration.null_maxima, (2.0, 3.0))
        self.assertEqual(
            calibration.to_dict()["multiple_testing"],
            "single_familywise_maxT_no_additional_Holm",
        )


if __name__ == "__main__":
    unittest.main()
