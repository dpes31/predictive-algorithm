from __future__ import annotations

import unittest

from engine.config import DEFAULT_CONFIG
from engine.randomness_gate import GateEvidence, GateState, effective_weights, evaluate_gate
from engine.weights import update_weights


class WeightAndGateTests(unittest.TestCase):
    def test_single_draw_cannot_explode_weight(self):
        previous = {"a": 0.5, "b": 0.5}
        updated = update_weights(
            previous,
            {"a": 0.0, "b": 100.0},
            baseline_loss=10.0,
            config=DEFAULT_CONFIG,
        )
        self.assertAlmostEqual(sum(updated.values()), 1.0)
        self.assertLess(updated["a"], 0.75)
        self.assertGreater(updated["b"], 0.25)

    def test_default_evidence_is_research(self):
        self.assertEqual(evaluate_gate(GateEvidence()), GateState.RESEARCH)

    def test_candidate_caps_nonuniform_weight(self):
        shadow = {"M0": 0.1, "M1": 0.4, "M2": 0.3, "M3": 0.2}
        effective = effective_weights(GateState.CANDIDATE, shadow)
        self.assertGreaterEqual(effective["M0"], 0.70)
        self.assertLessEqual(effective["M1"] + effective["M2"] + effective["M3"], 0.30 + 1e-12)

    def test_research_uses_uniform_final_weights(self):
        shadow = {"M0": 0.1, "M1": 0.4, "M2": 0.3, "M3": 0.2}
        self.assertEqual(
            effective_weights(GateState.RESEARCH, shadow),
            {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0},
        )


if __name__ == "__main__":
    unittest.main()
