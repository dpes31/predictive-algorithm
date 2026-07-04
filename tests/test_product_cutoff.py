from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from product.run_prediction import run_product_prediction


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "draws.json"
GENERATED_AT = "2026-07-01T00:00:00Z"


class ProductCutoffTests(unittest.TestCase):
    def test_next_target_cutoff(self) -> None:
        result = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at=GENERATED_AT,
        )
        self.assertEqual(result["input_last_draw"], 1230)
        cutoff = result["diagnostics"]["cutoff"]
        self.assertEqual(cutoff["input_first_draw"], 1)
        self.assertEqual(cutoff["input_last_draw"], 1230)
        self.assertEqual(cutoff["input_record_count"], 1230)
        self.assertEqual(cutoff["excluded_draws_at_or_after_target"], 0)
        self.assertRegex(cutoff["cutoff_hash"], r"^[a-f0-9]{64}$")

    def test_target_or_later_draw_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "future-data cutoff violation"):
            run_product_prediction(
                target_draw_no=1230,
                dataset_path=DATASET,
                generated_at=GENERATED_AT,
            )

    def test_missing_target_minus_one_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "input_last_draw must equal target_draw_no - 1"):
            run_product_prediction(
                target_draw_no=1232,
                dataset_path=DATASET,
                generated_at=GENERATED_AT,
            )

    def test_tampered_dataset_hash_is_rejected(self) -> None:
        payload = json.loads(DATASET.read_text(encoding="utf-8"))
        payload["records"][0]["numbers"] = [1, 2, 3, 4, 5, 6]
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "tampered.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dataset hash mismatch"):
                run_product_prediction(
                    target_draw_no=1231,
                    dataset_path=path,
                    generated_at=GENERATED_AT,
                )

    def test_generated_at_requires_timezone(self) -> None:
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            run_product_prediction(
                target_draw_no=1231,
                dataset_path=DATASET,
                generated_at="2026-07-01T00:00:00",
            )


if __name__ == "__main__":
    unittest.main()
