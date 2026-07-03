from __future__ import annotations
import unittest
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import synthetic_records


class A2CrossRuntimeTests(unittest.TestCase):
    def test_frozen_synthetic_score_hash(self) -> None:
        records = synthetic_records()
        result = build_score_bundle(records, target_draw_no=len(records) + 1, data_version="synthetic-a2")
        self.assertEqual(result["selected"]["score_vector_hash"], "1eb1ec7904478e36cc4b92d549428f5791f0a93b88e61ae7838a96bca2006ed0")


if __name__ == "__main__":
    unittest.main()
