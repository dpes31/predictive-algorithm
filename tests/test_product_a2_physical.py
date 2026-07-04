from __future__ import annotations
import unittest
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import hypothesis_registry, physical_adapter, synthetic_records, user_registry


class A2PhysicalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = synthetic_records()
        self.target = len(self.records) + 1

    def test_common_value_has_exact_zero_contribution(self) -> None:
        constant = {str(number): 4.0 for number in range(1, 46)}
        bundle = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=user_registry(constant), hypothesis_registry=hypothesis_registry(), physical_adapter=physical_adapter())
        self.assertTrue(all(value == 0.0 for value in bundle["physical"]["contribution"].values()))
        self.assertIn("PHY-SYNTHETIC:zero_reference", bundle["physical"]["reasons"])

    def test_number_level_fixture_is_capped_and_not_double_counted(self) -> None:
        bundle = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", user_input_registry=user_registry(), hypothesis_registry=hypothesis_registry(), physical_adapter=physical_adapter())
        self.assertLessEqual(max(abs(value) for value in bundle["physical"]["contribution"].values()), 0.05 + 1e-15)
        self.assertEqual(bundle["hypothesis"]["active_count"], 0)


if __name__ == "__main__":
    unittest.main()
