from __future__ import annotations

import unittest

from engine.prediction_run import run_research_prediction
from simulation.uniform_lottery import generate_uniform_draws


class PredictionRunTests(unittest.TestCase):
    def setUp(self):
        self.records = generate_uniform_draws(320, seed=2026)

    def _run(self):
        return run_research_prediction(
            self.records,
            target_draw_no=321,
            data_version="synthetic-2026-320",
            generated_at="2026-06-30T00:00:00Z",
        )

    def test_research_run_is_uniform_publicly_and_reproducible(self):
        first = self._run()
        second = self._run()
        self.assertEqual(first.gate_state, "RESEARCH")
        self.assertEqual(first.model_weights, {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0})
        self.assertEqual(first.advantage_status, "통계적 우위 없음")
        self.assertTrue(first.research_only)
        self.assertFalse(first.public_release_allowed)
        self.assertEqual(first.prediction_hash, second.prediction_hash)
        self.assertEqual([c.numbers for c in first.candidate_sets], [c.numbers for c in second.candidate_sets])
        self.assertFalse(first.metadata["physical_evidence"]["active"])
        self.assertEqual(first.uncertainty_status, "pending_gate2_3p_r")
        self.assertEqual(first.model_version, "4.0.0-research")

    def test_outputs_five_unique_sets_with_unit_lift(self):
        result = self._run()
        combinations = [candidate.numbers for candidate in result.candidate_sets]
        self.assertEqual(len(combinations), 5)
        self.assertEqual(len(set(combinations)), 5)
        for candidate in result.candidate_sets:
            self.assertEqual(len(candidate.numbers), 6)
            self.assertAlmostEqual(candidate.lift_vs_uniform, 1.0, places=12)
            self.assertIsNone(candidate.credible_interval_95)

    def test_uniform_portfolio_has_meaningful_coverage(self):
        result = self._run()
        union = set().union(*(set(candidate.numbers) for candidate in result.candidate_sets))
        self.assertGreaterEqual(len(union), 20)


if __name__ == "__main__":
    unittest.main()
