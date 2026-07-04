from __future__ import annotations

import unittest
from dataclasses import replace

from engine.experts.change_eprocess import ChangeEProcessDetector
from engine.prediction_run import run_research_prediction
from simulation.physical_scenarios import BALL_SET_LIFT_125, generate_physical_series, holdout_target


class PhysicalPredictionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records, metadata = generate_physical_series(BALL_SET_LIFT_125, draw_count=321, seed=777)
        history, cls.metadata_history, cls.target_result, cls.target_metadata = holdout_target(records, metadata)
        cls.history = tuple(replace(record, verification_status="auto_checked") for record in history)
        cls.change_result = ChangeEProcessDetector().replay(cls.history)

    def _run(self):
        return run_research_prediction(
            self.history,
            target_draw_no=self.target_result.draw_no,
            data_version="synthetic-physical-320",
            generated_at="2026-06-30T00:00:00Z",
            physical_metadata_records=self.metadata_history,
            target_physical_metadata=self.target_metadata,
            change_eprocess_result=self.change_result,
        )

    def test_m4_is_evaluated_but_abstains_without_macro_contract(self):
        result = self._run()
        self.assertEqual(result.gate_state, "RESEARCH")
        self.assertEqual(result.model_weights["M0"], 1.0)
        self.assertEqual(result.model_weights["M4"], 0.0)
        self.assertEqual(result.metadata["physical_evidence"]["status"], "ABSTAIN")
        self.assertFalse(result.public_release_allowed)
        self.assertEqual(len(result.candidate_sets), 5)
        self.assertEqual(result.model_version, "4.0.0-research")

    def test_physical_prediction_is_deterministic(self):
        first = self._run()
        second = self._run()
        self.assertEqual(first.prediction_hash, second.prediction_hash)
        self.assertEqual([candidate.numbers for candidate in first.candidate_sets], [candidate.numbers for candidate in second.candidate_sets])


if __name__ == "__main__":
    unittest.main()
