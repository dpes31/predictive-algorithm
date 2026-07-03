from __future__ import annotations
import math
import unittest
from research_ensemble.config import DEFAULT_INTEGRATION_CONFIG
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import synthetic_records


class A2ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = synthetic_records()
        cls.target = len(cls.records) + 1
        cls.bundle = build_score_bundle(cls.records, target_draw_no=cls.target, data_version="synthetic-a2")

    def test_contract_and_shape(self) -> None:
        config = DEFAULT_INTEGRATION_CONFIG
        self.assertEqual(config.implementation_contract_version, "research-ensemble-implementation-1.0.0")
        rows = self.bundle["selected"]["score_vector"]
        self.assertEqual([row["number"] for row in rows], list(range(1, 46)))
        logits = [row["final_logit"] for row in rows]
        self.assertTrue(all(math.isfinite(value) for value in logits))
        self.assertLessEqual(abs(sum(logits)), 1e-11)
        self.assertLessEqual(max(abs(value) for value in logits), 0.35 + 1e-15)

    def test_five_repeats_match(self) -> None:
        hashes = {build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2")["selected"]["score_vector_hash"] for _ in range(5)}
        self.assertEqual(len(hashes), 1)

    def test_contributions_recalculate(self) -> None:
        for row in self.bundle["selected"]["score_vector"]:
            raw = row["historical_contribution"] + row["hypothesis_contribution"] + row["physical_contribution"]
            self.assertAlmostEqual(raw * (1.0 - row["uncertainty_rate"]), row["pre_center_logit"], places=10)


if __name__ == "__main__":
    unittest.main()
