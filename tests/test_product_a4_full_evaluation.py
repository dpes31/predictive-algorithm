from __future__ import annotations

import json
import os
import pathlib
import unittest

from engine.hashing import canonical_json
from research_ensemble.compare_evaluation import compare_results
from research_ensemble.evaluation import evaluate_dataset, write_result


class A4FullEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact_dir = pathlib.Path(os.environ.get("A4_ARTIFACT_DIR", "artifacts/a4-local"))
        cls.artifact_dir.mkdir(parents=True, exist_ok=True)
        cls.run1_path = cls.artifact_dir / "run1.json"
        cls.run2_path = cls.artifact_dir / "run2.json"
        cls.rows_path = cls.artifact_dir / "target-rows.jsonl"
        cls.within_path = cls.artifact_dir / "runtime-verification.json"

        cls.run1 = evaluate_dataset(dataset_path="data/draws.json", rows_output=cls.rows_path)
        write_result(cls.run1, cls.run1_path)
        cls.run2 = evaluate_dataset(dataset_path="data/draws.json")
        write_result(cls.run2, cls.run2_path)
        cls.within = compare_results([cls.run1_path, cls.run2_path], cross_runtime=False)
        cls.within_path.write_text(canonical_json(cls.within) + "\n", encoding="utf-8")

        canonical = cls.run1["canonical_result"]
        summary = {
            "runtime": cls.run1["runtime"],
            "status": canonical["status"],
            "decision_reasons": canonical.get("decision_reasons", []),
            "canonical_result_hash": cls.run1["canonical_result_hash"],
            "primary": canonical.get("primary"),
            "secondary": {
                "mean_brier_gain": canonical.get("secondary", {}).get("mean_brier_gain"),
                "quarter_means": canonical.get("secondary", {}).get("quarter_means"),
                "positive_quarter_count": canonical.get("secondary", {}).get("positive_quarter_count"),
                "final_cumulative_delta": canonical.get("secondary", {}).get("final_cumulative_delta"),
                "calibration_ece": canonical.get("secondary", {}).get("calibration", {}).get("weighted_ece"),
            },
            "integrity": {
                name: value.get("pass")
                for name, value in canonical.get("integrity", {}).items()
            },
            "equivalence": canonical.get("equivalence", {}).get("checks"),
            "hashes": canonical.get("hashes"),
            "within_runtime": cls.within,
            "target_rows_file_sha256": canonical.get("integrity", {}).get("E13_hash_recomputation", {}).get("rows_file_sha256"),
        }
        print("A4_RUNTIME_SUMMARY_JSON=" + canonical_json(summary))

    def test_evaluation_completed(self) -> None:
        self.assertIn(
            self.run1["canonical_result"]["status"],
            {"A4_EVALUATION_PASS_CANDIDATE", "A4_EVALUATION_FAIL"},
        )
        self.assertEqual(self.run1["canonical_result"]["target_sequence"]["target_count"], 879)

    def test_two_repeats_are_identical(self) -> None:
        self.assertEqual(self.run1["canonical_result_hash"], self.run2["canonical_result_hash"])
        self.assertTrue(self.within["E11_reproducibility"]["pass"])

    def test_target_rows_are_persisted(self) -> None:
        self.assertTrue(self.rows_path.is_file())
        with self.rows_path.open("r", encoding="utf-8") as handle:
            row_count = sum(1 for _ in handle)
        self.assertEqual(row_count, 8790)

    def test_runtime_artifacts_are_valid_json(self) -> None:
        for path in (self.run1_path, self.run2_path, self.within_path):
            json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
