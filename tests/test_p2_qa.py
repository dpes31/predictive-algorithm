from __future__ import annotations

import json
import pathlib
import unittest

from product.run_prediction import run_product_prediction
from qa.p2_common import (
    CANONICAL_GENERATED_AT,
    CANONICAL_TARGET_DRAW,
    canonical_core,
    generate_core_snapshot,
    negative_payload_mutations,
    semantic_contract_errors,
    validate_payload,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "draws.json"


class ProductP2UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = run_product_prediction(
            target_draw_no=CANONICAL_TARGET_DRAW,
            dataset_path=DATASET,
            generated_at=CANONICAL_GENERATED_AT,
        )
        cls.schema = json.loads((ROOT / "schemas" / "product_prediction.schema.json").read_text(encoding="utf-8"))

    def test_canonical_payload_passes_schema_and_semantics(self) -> None:
        self.assertEqual(validate_payload(self.payload, self.schema), [])

    def test_all_registered_negative_mutations_are_rejected(self) -> None:
        for name, mutation in negative_payload_mutations(self.payload).items():
            with self.subTest(name=name):
                self.assertTrue(validate_payload(mutation, self.schema))

    def test_shadow_and_generated_at_do_not_change_product_core(self) -> None:
        baseline = canonical_core(self.payload)
        shadow = run_product_prediction(
            target_draw_no=CANONICAL_TARGET_DRAW,
            dataset_path=DATASET,
            generated_at="2026-07-03T02:00:00Z",
            shadow_diagnostics={"M4": {"score": 999}, "M1": [1, 2, 3]},
        )
        self.assertEqual(canonical_core(shadow), baseline)

    def test_core_snapshot_contract(self) -> None:
        snapshot = generate_core_snapshot(ROOT, DATASET)
        self.assertTrue(snapshot["repeats_equal"])
        self.assertTrue(snapshot["generated_at_invariant"])
        self.assertTrue(snapshot["shadow_isolation"])
        self.assertTrue(snapshot["target_change_invalidates_seed"])

    def test_false_cutoff_hash_is_semantically_rejected(self) -> None:
        mutation = dict(self.payload)
        mutation["diagnostics"] = dict(self.payload["diagnostics"])
        mutation["diagnostics"]["cutoff"] = dict(self.payload["diagnostics"]["cutoff"])
        mutation["diagnostics"]["cutoff"]["cutoff_hash"] = "0" * 64
        self.assertTrue(semantic_contract_errors(mutation))


if __name__ == "__main__":
    unittest.main()
