from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from scripts.build_c3_html_mvp import build


class ProductCloseoutC3HtmlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = pathlib.Path(__file__).resolve().parents[1]
        self.html = (self.root / "public/index.html").read_text(encoding="utf-8")

    def test_required_display_contract_is_present(self) -> None:
        required = (
            "통계적 우위 없음",
            "no_validated_nonuniform_signal",
            "auto_checked",
            "officially_locked=false",
            "Prediction Hash",
            "당첨확률 향상을 보장하지 않습니다",
            "product-prediction.json",
            "M0_ONLY",
            "public_release_allowed",
        )
        for marker in required:
            self.assertIn(marker, self.html)

    def test_no_external_runtime_or_research_visualization(self) -> None:
        prohibited = (
            "https://",
            "http://",
            "research_ensemble",
            "hot/cold",
            "Supabase",
        )
        for marker in prohibited:
            self.assertNotIn(marker, self.html)

    def test_build_generates_valid_static_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = pathlib.Path(temporary)
            first = build(output)
            prediction = json.loads((output / "product-prediction.json").read_text(encoding="utf-8"))
            index = (output / "index.html").read_text(encoding="utf-8")
            manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(prediction["target_draw_no"], 1231)
            self.assertEqual(prediction["input_last_draw"], 1230)
            self.assertEqual(prediction["final_distribution"], "M0_ONLY")
            self.assertFalse(prediction["statistical_edge"])
            self.assertEqual(prediction["reason"], "no_validated_nonuniform_signal")
            self.assertEqual(len(prediction["candidate_sets"]), 5)
            self.assertTrue(all(len(item["numbers"]) == 6 for item in prediction["candidate_sets"]))
            self.assertEqual(first, manifest)
            self.assertEqual(index, self.html)
            self.assertEqual(manifest["prediction_hash"], prediction["hashes"]["prediction_hash"])
            self.assertFalse(manifest["public_release_allowed"])

    def test_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = pathlib.Path(first_dir)
            second = pathlib.Path(second_dir)
            self.assertEqual(build(first), build(second))
            for filename in ("index.html", "product-prediction.json", "build-manifest.json"):
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())


if __name__ == "__main__":
    unittest.main()
