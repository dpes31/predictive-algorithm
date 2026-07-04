from __future__ import annotations
import unittest
from research_ensemble.registry import RegistryValidationError, seal_physical_adapter, seal_registry
from research_ensemble.runner_core import run_integrated_prediction
from research_ensemble.scoring import build_score_bundle
from research_ensemble.vector import normalize_vector
from a2_fixtures import hypothesis_registry, synthetic_records, user_registry


class A2NegativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = synthetic_records()
        self.target = len(self.records) + 1

    def test_invalid_vector_shapes_and_values(self) -> None:
        with self.assertRaises(ValueError):
            normalize_vector({number: 0.0 for number in range(1, 45)})
        with self.assertRaises(ValueError):
            normalize_vector({number: 0.0 for number in range(1, 47)})
        with self.assertRaises(ValueError):
            normalize_vector({number: (float("nan") if number == 1 else 0.0) for number in range(1, 46)})

    def test_number_mapping_outside_range_fails(self) -> None:
        values = {str(number): float(number) for number in range(1, 46)}
        values["46"] = 1.0
        with self.assertRaises(RegistryValidationError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=user_registry(values))

    def test_hypothesis_aggregate_cap_fails(self) -> None:
        base = hypothesis_registry()["entries"][0]
        entries = []
        for index in range(3):
            item = {key: value for key, value in base.items() if key != "hypothesis_hash"}
            item["hypothesis_id"] = f"HYP-{index}"
            entries.append(item)
        registry = seal_registry({"registry_type": "hypothesis", "contract_version": "hypothesis-registry-1.0.0", "registry_version": "overflow", "status": "APPROVED", "approved_by": "user", "approved_at": "2026-07-03T00:00:00+09:00", "entries": entries})
        with self.assertRaisesRegex(RegistryValidationError, "aggregate"):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", hypothesis_registry=registry)

    def test_physical_aggregate_cap_and_unknown_reference_fail(self) -> None:
        fields = [{"field_id": f"PHY-{index}", "input_entry_id": "UPI-SYNTHETIC", "hypothesis_id": "HYP-SYNTHETIC", "normalization": "CROSS_SECTIONAL_Z_CLIP_3", "direction_source": "HYPOTHESIS_ONLY", "field_cap": 0.05} for index in range(4)]
        adapter = seal_physical_adapter({"registry_type": "physical_adapter", "contract_version": "user-physical-adapter-1.0.0", "adapter_version": "overflow", "status": "APPROVED", "approved_by": "user", "approved_at": "2026-07-03T00:00:00+09:00", "fields": fields})
        with self.assertRaisesRegex(RegistryValidationError, "aggregate"):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", physical_adapter=adapter)
        adapter = seal_physical_adapter({"registry_type": "physical_adapter", "contract_version": "user-physical-adapter-1.0.0", "adapter_version": "unknown", "status": "APPROVED", "approved_by": "user", "approved_at": "2026-07-03T00:00:00+09:00", "fields": [{**fields[0], "field_id": "PHY-UNKNOWN", "input_entry_id": "MISSING"}]})
        with self.assertRaises(RegistryValidationError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=user_registry(), hypothesis_registry=hypothesis_registry(), physical_adapter=adapter)

    def test_unknown_ablation_and_mode_fail(self) -> None:
        with self.assertRaises(ValueError):
            build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", ablation_id="UNKNOWN")
        with self.assertRaises(ValueError):
            run_integrated_prediction(target_draw_no=1231, dataset_path="data/draws.json", generated_at="2026-07-03T00:00:00Z", mode="UNKNOWN")


if __name__ == "__main__":
    unittest.main()
