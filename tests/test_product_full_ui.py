from __future__ import annotations

import hashlib
import json
import pathlib
import unittest

from product.config import EXPECTED_DATA_HASH, PRODUCT_WEIGHTS
from product.dynamic_prediction import run_dynamic_prediction, validate_overlay


class FullProductUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = pathlib.Path(__file__).resolve().parents[1]
        cls.canonical = json.loads((cls.root / "data/draws.json").read_text(encoding="utf-8"))
        cls.valid_overlay = [
            {
                "draw_no": 1231,
                "draw_date": "2026-07-04",
                "numbers": [1, 7, 18, 24, 33, 41],
                "bonus_number": 12,
            }
        ]

    def test_canonical_dataset_is_unchanged(self) -> None:
        digest = hashlib.sha256((self.root / "data/draws.json").read_bytes()).hexdigest()
        self.assertEqual(digest, EXPECTED_DATA_HASH)
        self.assertEqual(self.canonical["records"][0]["draw_no"], 1)
        self.assertEqual(self.canonical["records"][-1]["draw_no"], 1230)

    def test_no_overlay_targets_1231_with_m0_only(self) -> None:
        result = run_dynamic_prediction(overlay=[], generated_at="2026-07-04T00:00:00Z")
        self.assertEqual(result["input_last_draw"], 1230)
        self.assertEqual(result["target_draw_no"], 1231)
        self.assertEqual(result["final_distribution"], "M0_ONLY")
        self.assertEqual(result["product_weights"], PRODUCT_WEIGHTS)
        self.assertFalse(result["statistical_edge"])
        self.assertEqual(result["reason"], "no_validated_nonuniform_signal")
        self.assertEqual(len(result["candidate_sets"]), 5)
        self.assertTrue(all(len(item["numbers"]) == 6 for item in result["candidate_sets"]))
        self.assertEqual(len({tuple(item["numbers"]) for item in result["candidate_sets"]}), 5)

    def test_overlay_advances_latest_and_target(self) -> None:
        first = run_dynamic_prediction(overlay=self.valid_overlay, generated_at="2026-07-04T01:00:00Z")
        second = run_dynamic_prediction(overlay=self.valid_overlay, generated_at="2026-07-04T02:00:00Z")
        self.assertEqual(first["input_last_draw"], 1231)
        self.assertEqual(first["target_draw_no"], 1232)
        self.assertEqual(first["data"]["overlay_record_count"], 1)
        self.assertEqual(first["seed"], second["seed"])
        self.assertEqual(first["hashes"]["prediction_hash"], second["hashes"]["prediction_hash"])
        self.assertEqual(first["candidate_sets"], second["candidate_sets"])
        self.assertNotEqual(first["generated_at"], second["generated_at"])

    def test_overlay_validation_blocks_invalid_records(self) -> None:
        records = self.canonical["records"]
        bad_cases = [
            [{**self.valid_overlay[0], "draw_no": 1232}],
            [{**self.valid_overlay[0], "draw_date": records[-1]["draw_date"]}],
            [{**self.valid_overlay[0], "numbers": [1, 1, 2, 3, 4, 5]}],
            [{**self.valid_overlay[0], "bonus_number": 1}],
            [{**self.valid_overlay[0], "numbers": [0, 2, 3, 4, 5, 6]}],
        ]
        for case in bad_cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    validate_overlay(case, records)

    def test_locked_1231_fixture_remains_regression_only(self) -> None:
        fixture = json.loads((self.root / "public/product-prediction.json").read_text(encoding="utf-8"))
        self.assertEqual(fixture["target_draw_no"], 1231)
        self.assertEqual(fixture["input_last_draw"], 1230)
        self.assertEqual(
            fixture["hashes"]["prediction_hash"],
            "119f28875355952fa5c80e2095e70c096aee081ee56c750fa4caf2e373c5fe32",
        )

    def test_full_ui_pages_and_click_contract(self) -> None:
        home = (self.root / "public/index.html").read_text(encoding="utf-8")
        archive = (self.root / "public/archive.html").read_text(encoding="utf-8")
        update = (self.root / "public/update.html").read_text(encoding="utf-8")
        home_js = (self.root / "public/assets/js/home.js").read_text(encoding="utf-8")
        data_js = (self.root / "public/assets/js/data-store.js").read_text(encoding="utf-8")

        for marker in ("예측하기", "과거 데이터", "당첨번호 입력", "통계적 우위 없음"):
            self.assertIn(marker, home)
        for marker in ("회차 검색", "번호별 출현", "사용자 입력"):
            self.assertIn(marker, archive)
        for marker in ("당첨번호 6개", "보너스번호", "사용자 overlay에 저장"):
            self.assertIn(marker, update)
        self.assertIn('addEventListener("click", predict)', home_js)
        self.assertIn('fetch("/api/predict"', home_js)
        self.assertIn("localStorage", data_js)
        self.assertNotIn("product-prediction.json", home_js)

    def test_vercel_static_and_function_configuration(self) -> None:
        config = json.loads((self.root / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["outputDirectory"], "public")
        self.assertIn("api/archive.py", config["functions"])
        self.assertIn("api/predict.py", config["functions"])
        self.assertTrue((self.root / "api/archive.py").is_file())
        self.assertTrue((self.root / "api/predict.py").is_file())


if __name__ == "__main__":
    unittest.main()
