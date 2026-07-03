from __future__ import annotations
import json
import pathlib
import tempfile
import unittest
from product.run_prediction import run_product_prediction
from research_ensemble.runner_core import run_integrated_prediction
from a2_fixtures import synthetic_records

ROOT = pathlib.Path(__file__).resolve().parents[1]


class A2RunnerTests(unittest.TestCase):
    def test_default_control_is_existing_product_output(self) -> None:
        integrated = run_integrated_prediction(target_draw_no=1231, dataset_path=ROOT / "data/draws.json", generated_at="2026-07-03T00:00:00Z")
        control = run_product_prediction(target_draw_no=1231, dataset_path=ROOT / "data/draws.json", generated_at="2026-07-03T00:00:00Z")
        self.assertEqual(integrated, control)

    def test_research_output_is_deterministic_and_research_only(self) -> None:
        records = synthetic_records()
        payload = {"data_version": "synthetic-a2", "records": [{"draw_no": item.draw_no, "draw_date": item.draw_date, "numbers": list(item.numbers), "bonus_number": None, "verification_status": "auto_checked", "locked": False, "source": "synthetic_fixture"} for item in records]}
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "draws.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            first = run_integrated_prediction(target_draw_no=len(records) + 1, dataset_path=path, generated_at="2026-07-03T00:00:00Z", mode="RESEARCH_ENSEMBLE")
            second = run_integrated_prediction(target_draw_no=len(records) + 1, dataset_path=path, generated_at="2026-07-03T01:00:00Z", mode="RESEARCH_ENSEMBLE")
        self.assertEqual(first["mode_effective"], "RESEARCH_ENSEMBLE")
        self.assertEqual(len(first["candidate_sets"]), 5)
        self.assertEqual(first["candidate_sets"], second["candidate_sets"])
        self.assertEqual(first["hashes"]["prediction_hash"], second["hashes"]["prediction_hash"])
        self.assertTrue(first["research_only"])
        self.assertFalse(first["public_release_allowed"])
        self.assertFalse(first["statistical_edge"])


if __name__ == "__main__":
    unittest.main()
