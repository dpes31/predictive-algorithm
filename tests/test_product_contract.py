from __future__ import annotations

import json
import math
import pathlib
import unittest

from product.run_prediction import run_product_prediction


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "draws.json"
GENERATED_AT = "2026-07-01T00:00:00Z"


class ProductContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_product_prediction(
            target_draw_no=1231,
            dataset_path=DATASET,
            generated_at=GENERATED_AT,
        )

    def test_m0_only_and_disclosures(self) -> None:
        self.assertEqual(
            self.result["product_weights"],
            {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0},
        )
        self.assertEqual(self.result["final_distribution"], "M0_ONLY")
        self.assertFalse(self.result["statistical_edge"])
        self.assertEqual(self.result["reason"], "no_validated_nonuniform_signal")
        self.assertEqual(self.result["advantage_status"], "통계적 우위 없음")
        self.assertTrue(self.result["research_only"])
        self.assertFalse(self.result["public_release_allowed"])

    def test_exactly_five_distinct_six_number_sets(self) -> None:
        candidates = self.result["candidate_sets"]
        self.assertEqual(len(candidates), 5)
        self.assertEqual([candidate["rank"] for candidate in candidates], [1, 2, 3, 4, 5])
        combinations = []
        for candidate in candidates:
            numbers = candidate["numbers"]
            self.assertEqual(len(numbers), 6)
            self.assertEqual(len(set(numbers)), 6)
            self.assertEqual(numbers, sorted(numbers))
            self.assertTrue(all(1 <= number <= 45 for number in numbers))
            combinations.append(tuple(numbers))
        self.assertEqual(len(set(combinations)), 5)

    def test_uniform_probability_and_lift(self) -> None:
        expected = 1.0 / math.comb(45, 6)
        for candidate in self.result["candidate_sets"]:
            self.assertEqual(candidate["joint_probability"], expected)
            self.assertEqual(candidate["lift_vs_uniform"], 1.0)

    def test_versions_hashes_and_dataset_identity(self) -> None:
        self.assertEqual(self.result["versions"]["data_version"], "draws-2026.06.27-r1")
        self.assertEqual(
            self.result["hashes"]["data_hash"],
            "57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1",
        )
        for value in self.result["hashes"].values():
            self.assertRegex(value, r"^[a-f0-9]{64}$")
        self.assertRegex(self.result["seed"], r"^[a-f0-9]{64}$")

    def test_json_schema_constants(self) -> None:
        schema = json.loads((ROOT / "schemas" / "product_prediction.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["statistical_edge"]["const"], False)
        self.assertEqual(
            schema["properties"]["reason"]["const"],
            "no_validated_nonuniform_signal",
        )
        candidates = schema["properties"]["candidate_sets"]
        self.assertEqual(candidates["minItems"], 5)
        self.assertEqual(candidates["maxItems"], 5)
        self.assertEqual(candidates["items"]["properties"]["numbers"]["minItems"], 6)
        self.assertEqual(candidates["items"]["properties"]["numbers"]["maxItems"], 6)

    def test_assembly_and_rollback_manifests(self) -> None:
        assembly = json.loads((ROOT / "release" / "assembly_manifest.json").read_text(encoding="utf-8"))
        rollback = json.loads((ROOT / "release" / "rollback_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(assembly["final_distribution"], "M0_ONLY")
        self.assertEqual(assembly["product_weights"], self.result["product_weights"])
        self.assertEqual(rollback["implementation_branch"], "feature/product-p1-release-candidate")
        self.assertRegex(rollback["pre_assembly_commit"], r"^[a-f0-9]{40}$")
        self.assertRegex(rollback["assembled_commit"], r"^[a-f0-9]{40}$")
        self.assertFalse(rollback["main_affected"])


if __name__ == "__main__":
    unittest.main()
