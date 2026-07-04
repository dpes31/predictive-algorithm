from __future__ import annotations

import json
import pathlib
import unittest


class ProductVercelDeploymentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = pathlib.Path(__file__).resolve().parents[1]

    def test_vercel_serves_public_directory(self) -> None:
        config = json.loads((self.root / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["$schema"], "https://openapi.vercel.sh/vercel.json")
        self.assertEqual(config["outputDirectory"], "public")
        self.assertNotIn("redirects", config)
        self.assertNotIn("rewrites", config)

    def test_required_static_files_exist(self) -> None:
        self.assertTrue((self.root / "public/index.html").is_file())
        self.assertTrue((self.root / "public/product-prediction.json").is_file())

    def test_static_prediction_contract_is_locked(self) -> None:
        payload = json.loads(
            (self.root / "public/product-prediction.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["target_draw_no"], 1231)
        self.assertEqual(payload["input_last_draw"], 1230)
        self.assertEqual(payload["final_distribution"], "M0_ONLY")
        self.assertFalse(payload["statistical_edge"])
        self.assertEqual(payload["reason"], "no_validated_nonuniform_signal")
        self.assertFalse(payload["public_release_allowed"])
        self.assertEqual(
            payload["hashes"]["prediction_hash"],
            "119f28875355952fa5c80e2095e70c096aee081ee56c750fa4caf2e373c5fe32",
        )
        self.assertEqual(len(payload["candidate_sets"]), 5)
        self.assertTrue(all(len(item["numbers"]) == 6 for item in payload["candidate_sets"]))

    def test_html_loads_local_prediction_only(self) -> None:
        html = (self.root / "public/index.html").read_text(encoding="utf-8")
        self.assertIn('fetch("./product-prediction.json"', html)
        self.assertNotIn("https://", html)
        self.assertNotIn("http://", html)


if __name__ == "__main__":
    unittest.main()
