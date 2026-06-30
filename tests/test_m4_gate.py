from __future__ import annotations

import unittest

from engine.randomness_gate import GateState, effective_weights


class M4GateTests(unittest.TestCase):
    def test_candidate_state_caps_m4_at_ten_percent(self):
        weights = effective_weights(
            GateState.CANDIDATE,
            {"M0": 0.05, "M1": 0.05, "M2": 0.05, "M3": 0.05, "M4": 0.80},
            physical_weight_cap=0.10,
        )
        self.assertGreaterEqual(weights["M0"], 0.70)
        self.assertLessEqual(weights["M4"], 0.10)
        self.assertAlmostEqual(sum(weights.values()), 1.0)

    def test_research_state_is_m0_only_with_m4_present(self):
        weights = effective_weights(
            GateState.RESEARCH,
            {"M0": 0.2, "M1": 0.2, "M2": 0.2, "M3": 0.2, "M4": 0.2},
        )
        self.assertEqual(
            weights,
            {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0},
        )

    def test_legacy_m0_to_m3_contract_remains_supported(self):
        weights = effective_weights(
            GateState.RESEARCH,
            {"M0": 0.25, "M1": 0.25, "M2": 0.25, "M3": 0.25},
        )
        self.assertEqual(weights, {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0})


if __name__ == "__main__":
    unittest.main()
