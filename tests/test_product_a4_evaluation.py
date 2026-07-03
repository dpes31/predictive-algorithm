from __future__ import annotations

import unittest

from research_ensemble.config import ABLATION_IDS
from research_ensemble.evaluation import (
    BOOTSTRAP_BLOCK_LENGTH,
    EVALUATION_CONTRACT_VERSION,
    SPEC_CONTRACT_VERSION,
    _block_starts,
    bootstrap_summary,
    holm_adjust,
)
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import synthetic_records


class A4EvaluationContractTests(unittest.TestCase):
    def test_contract_versions_are_frozen(self) -> None:
        self.assertEqual(EVALUATION_CONTRACT_VERSION, "research-ensemble-evaluation-implementation-1.0.0")
        self.assertEqual(SPEC_CONTRACT_VERSION, "research-ensemble-evaluation-spec-1.0.0")
        self.assertEqual(len(ABLATION_IDS), 10)

    def test_empty_registry_equivalence_hashes(self) -> None:
        records = synthetic_records()
        bundle = build_score_bundle(records, target_draw_no=304, data_version="synthetic-a4")
        hashes = {name: value["score_vector_hash"] for name, value in bundle["ablations"].items()}
        self.assertEqual(hashes["ENSEMBLE_FULL"], hashes["HISTORICAL_ONLY"])
        self.assertEqual(hashes["ENSEMBLE_FULL"], hashes["ENSEMBLE_MINUS_M3"])
        self.assertEqual(hashes["ENSEMBLE_FULL"], hashes["ENSEMBLE_MINUS_HYPOTHESES"])
        self.assertEqual(hashes["ENSEMBLE_FULL"], hashes["ENSEMBLE_MINUS_PHYSICAL"])
        self.assertEqual(hashes["HYPOTHESIS_ONLY"], hashes["CONTROL_M0"])
        self.assertEqual(hashes["PHYSICAL_ONLY"], hashes["CONTROL_M0"])

    def test_bootstrap_is_deterministic(self) -> None:
        values = [float((index % 7) - 3) for index in range(879)]
        starts = _block_starts("fixture-seed", len(values), BOOTSTRAP_BLOCK_LENGTH, 100)
        first = bootstrap_summary(values, starts=starts, block_length=BOOTSTRAP_BLOCK_LENGTH)
        second = bootstrap_summary(values, starts=starts, block_length=BOOTSTRAP_BLOCK_LENGTH)
        self.assertEqual(first, second)

    def test_holm_adjustment_is_monotone(self) -> None:
        adjusted = holm_adjust({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(adjusted["a"], 0.03)
        self.assertAlmostEqual(adjusted["c"], 0.06)
        self.assertAlmostEqual(adjusted["b"], 0.06)


if __name__ == "__main__":
    unittest.main()
