from __future__ import annotations

import unittest

from engine.config import DEFAULT_CONFIG
from engine.randomness_gate import GateState


class EngineContractTests(unittest.TestCase):
    def test_frozen_versions_and_dimensions(self):
        self.assertEqual(DEFAULT_CONFIG.model_version, "2.1.0-research")
        self.assertEqual(DEFAULT_CONFIG.feature_contract_version, "1.1.0")
        self.assertEqual(DEFAULT_CONFIG.number_count, 45)
        self.assertEqual(DEFAULT_CONFIG.pick_count, 6)
        self.assertEqual(DEFAULT_CONFIG.candidate_count, 5)
        self.assertEqual(DEFAULT_CONFIG.temperature_grid, (0.05, 0.10, 0.20, 0.50, 1.00))

    def test_gate_states_are_not_collapsed(self):
        self.assertEqual(
            {state.value for state in GateState},
            {"CLOSED", "RESEARCH", "CANDIDATE", "PROMOTED"},
        )

    def test_crowd_avoidance_cap_is_five_percent(self):
        self.assertEqual(DEFAULT_CONFIG.crowd_avoidance_max_share, 0.05)


if __name__ == "__main__":
    unittest.main()
