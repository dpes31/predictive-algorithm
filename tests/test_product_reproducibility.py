from __future__ import annotations

import pathlib
import unittest

from product.run_prediction import run_product_prediction


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "draws.json"


class ProductReproducibilityTests(unittest.TestCase):
    def test_same_input_is_identical(self) -> None:
        first = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at="2026-07-01T00:00:00Z",
        )
        second = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at="2026-07-01T00:00:00Z",
        )
        self.assertEqual(first, second)

    def test_generated_at_does_not_change_candidates_or_hash(self) -> None:
        first = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at="2026-07-01T00:00:00Z",
        )
        second = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at="2026-07-01T01:00:00Z",
        )
        self.assertNotEqual(first["generated_at"], second["generated_at"])
        self.assertEqual(first["candidate_sets"], second["candidate_sets"])
        self.assertEqual(first["seed"], second["seed"])
        self.assertEqual(first["hashes"]["prediction_hash"], second["hashes"]["prediction_hash"])

    def test_shadow_diagnostics_cannot_change_product_output(self) -> None:
        baseline = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at="2026-07-01T00:00:00Z",
        )
        shadowed = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at="2026-07-01T00:00:00Z",
            shadow_diagnostics={
                "M1": {"weight": 0.99},
                "M2": {"weight": 0.99},
                "M3": {"weight": 0.99},
                "M4": {"weight": 0.99},
            },
        )
        self.assertFalse(baseline["diagnostics"]["shadow_enabled"])
        self.assertTrue(shadowed["diagnostics"]["shadow_enabled"])
        self.assertEqual(baseline["product_weights"], shadowed["product_weights"])
        self.assertEqual(baseline["candidate_sets"], shadowed["candidate_sets"])
        self.assertEqual(baseline["seed"], shadowed["seed"])
        self.assertEqual(
            baseline["hashes"]["prediction_hash"],
            shadowed["hashes"]["prediction_hash"],
        )


if __name__ == "__main__":
    unittest.main()
