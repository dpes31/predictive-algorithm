from __future__ import annotations

import unittest

from engine.config import DEFAULT_CONFIG
from engine.randomness_gate import GateState


class EngineContractTests(unittest.TestCase):
    def test_frozen_versions_and_dimensions(self):
        self.assertEqual(DEFAULT_CONFIG.model_version, "3.0.0-research")
        self.assertEqual(DEFAULT_CONFIG.feature_contract_version, "2.0.0")
        self.assertEqual(DEFAULT_CONFIG.physical_data_schema_version, "1.0.0")
        self.assertEqual(DEFAULT_CONFIG.number_count, 45)
        self.assertEqual(DEFAULT_CONFIG.pick_count, 6)
        self.assertEqual(DEFAULT_CONFIG.candidate_count, 5)
        self.assertEqual(DEFAULT_CONFIG.temperature_grid, (0.05, 0.10, 0.20, 0.50, 1.00))

    def test_gate_states_are_not_collapsed(self):
        self.assertEqual(
            {state.value for state in GateState},
            {"CLOSED", "RESEARCH", "CANDIDATE", "PROMOTED"},
        )

    def test_safety_caps_are_frozen(self):
        self.assertEqual(DEFAULT_CONFIG.crowd_avoidance_max_share, 0.05)
        self.assertEqual(DEFAULT_CONFIG.physical_candidate_weight_cap, 0.10)
        self.assertEqual(DEFAULT_CONFIG.maxt_alpha, 0.001)
        self.assertEqual(DEFAULT_CONFIG.maxt_min_calibration_series, 10_000)


if __name__ == "__main__":
    unittest.main()
