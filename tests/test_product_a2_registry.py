from __future__ import annotations
import unittest
from research_ensemble.registry import RegistryValidationError, empty_user_registry
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import hypothesis_registry, physical_adapter, synthetic_records, user_registry


class A2RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = synthetic_records()
        self.target = len(self.records) + 1

    def test_empty_and_draft_registries_do_not_activate(self) -> None:
        empty = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2")
        self.assertEqual(empty["hypothesis"]["active_count"], 0)
        self.assertEqual(empty["physical"]["active_fields"], 0)
        draft = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=user_registry(), hypothesis_registry=hypothesis_registry(status="DRAFT"))
        self.assertEqual(draft["hypothesis"]["active_count"], 0)

    def test_hash_source_and_cap_violations_fail(self) -> None:
        tampered = user_registry()
        tampered["registry_hash"] = "0" * 64
        with self.assertRaises(RegistryValidationError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=tampered)
        with self.assertRaises(RegistryValidationError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=user_registry(source="EXTERNAL"))
        with self.assertRaises(RegistryValidationError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", hypothesis_registry=hypothesis_registry(cap=0.11))
        with self.assertRaises(RegistryValidationError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", physical_adapter=physical_adapter(cap=0.06))

    def test_required_missing_input_abstains(self) -> None:
        bundle = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=empty_user_registry(), hypothesis_registry=hypothesis_registry(required=True), ablation_id="HYPOTHESIS_ONLY")
        self.assertTrue(bundle["selected"]["run_abstained"])


if __name__ == "__main__":
    unittest.main()
