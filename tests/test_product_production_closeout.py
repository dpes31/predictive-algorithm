from __future__ import annotations

import hashlib
import json
import math
import pathlib
import unittest

from product.config import EXPECTED_DATA_HASH, PRODUCT_WEIGHTS
from product.dynamic_prediction import run_dynamic_prediction


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "draws.json"


class ProductionCloseoutContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DATA.read_text(encoding="utf-8"))
        cls.overlay = [
            {
                "draw_no": 1231,
                "draw_date": "2026-07-04",
                "numbers": [1, 7, 18, 24, 33, 41],
                "bonus_number": 12,
            }
        ]

    def test_locked_archive_is_complete(self) -> None:
        records = self.payload["records"]
        self.assertEqual(hashlib.sha256(DATA.read_bytes()).hexdigest(), EXPECTED_DATA_HASH)
        self.assertEqual(len(records), 1230)
        self.assertEqual([record["draw_no"] for record in records], list(range(1, 1231)))

    def test_control_m0_runtime_contract(self) -> None:
        result = run_dynamic_prediction(overlay=[], generated_at="2026-07-04T00:00:00Z")
        expected = 1.0 / math.comb(45, 6)
        self.assertEqual(result["target_draw_no"], 1231)
        self.assertEqual(result["final_distribution"], "M0_ONLY")
        self.assertEqual(result["product_weights"], PRODUCT_WEIGHTS)
        self.assertEqual(len(result["candidate_sets"]), 5)
        self.assertEqual(len({tuple(item["numbers"]) for item in result["candidate_sets"]}), 5)
        for item in result["candidate_sets"]:
            self.assertEqual(len(item["numbers"]), 6)
            self.assertEqual(item["joint_probability"], expected)
            self.assertEqual(item["lift_vs_uniform"], 1.0)
        self.assertRegex(result["seed"], r"^[0-9a-f]{64}$")
        self.assertRegex(result["hashes"]["effective_data_hash"], r"^[0-9a-f]{64}$")
        self.assertRegex(result["hashes"]["prediction_hash"], r"^[0-9a-f]{64}$")

    def test_manual_overlay_advances_target_and_identity(self) -> None:
        baseline = run_dynamic_prediction(overlay=[], generated_at="2026-07-04T00:00:00Z")
        first = run_dynamic_prediction(overlay=self.overlay, generated_at="2026-07-04T01:00:00Z")
        second = run_dynamic_prediction(overlay=self.overlay, generated_at="2026-07-04T02:00:00Z")
        self.assertEqual(first["input_last_draw"], 1231)
        self.assertEqual(first["target_draw_no"], 1232)
        self.assertEqual(first["seed"], second["seed"])
        self.assertEqual(first["candidate_sets"], second["candidate_sets"])
        self.assertEqual(first["hashes"]["prediction_hash"], second["hashes"]["prediction_hash"])
        self.assertNotEqual(baseline["seed"], first["seed"])
        self.assertNotEqual(
            baseline["hashes"]["effective_data_hash"],
            first["hashes"]["effective_data_hash"],
        )
        self.assertNotEqual(
            baseline["hashes"]["prediction_hash"],
            first["hashes"]["prediction_hash"],
        )

    def test_production_pages_use_dynamic_endpoints(self) -> None:
        home = (ROOT / "public/index.html").read_text(encoding="utf-8")
        archive = (ROOT / "public/archive.html").read_text(encoding="utf-8")
        update = (ROOT / "public/update.html").read_text(encoding="utf-8")
        home_js = (ROOT / "public/assets/js/home.js").read_text(encoding="utf-8")
        archive_js = (ROOT / "public/assets/js/archive.js").read_text(encoding="utf-8")
        data_js = (ROOT / "public/assets/js/data-store.js").read_text(encoding="utf-8")
        for marker in ("예측하기", "과거 데이터", "당첨번호 입력"):
            self.assertIn(marker, home)
        self.assertIn("회차 검색", archive)
        self.assertIn("당첨번호 6개", update)
        self.assertIn('fetch("/api/predict"', home_js)
        self.assertIn('fetch("/api/archive"', data_js)
        self.assertIn("state.canonical.records", archive_js)
        self.assertNotIn("product-prediction.json", home_js)


if __name__ == "__main__":
    unittest.main()
