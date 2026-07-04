from __future__ import annotations
import unittest
from engine.contracts import DrawRecord
from research_ensemble.historical import M1_FEATURES, M2_FEATURES, M3_FEATURES
from research_ensemble.scoring import build_score_bundle
from a2_fixtures import synthetic_records


class A2HistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = synthetic_records()
        self.target = len(self.records) + 1

    def test_feature_contract_and_prequential_weights(self) -> None:
        self.assertEqual(len(M1_FEATURES), 7)
        self.assertEqual(M2_FEATURES[-1], ("z_gap", 1.0))
        self.assertEqual(len(M3_FEATURES), 4)
        historical = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2")["historical"]
        self.assertAlmostEqual(sum(historical["weights"].values()), 1.0)
        self.assertLess(historical["loss_sequence"][-1]["draw_no"], self.target)

    def test_m3_abstains_and_can_use_registered_fixture(self) -> None:
        inactive = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2")["historical"]
        self.assertFalse(inactive["m3_eligible"])
        self.assertEqual(inactive["weights"]["M3"], 0.0)
        active = build_score_bundle(self.records, target_draw_no=self.target, data_version="synthetic-a2", m3_evidence={"pre_target_only": True, "calibrated": True, "active": True, "post_draw_fields_present": False})["historical"]
        self.assertTrue(active["m3_eligible"])

    def test_future_missing_and_duplicate_rejected(self) -> None:
        future = self.records + [DrawRecord(draw_no=self.target, draw_date="2020-01-01", numbers=(1, 2, 3, 4, 5, 6), verification_status="auto_checked")]
        with self.assertRaises(ValueError):
            build_score_bundle(future, target_draw_no=self.target, data_version="synthetic-a2")
        with self.assertRaises(ValueError):
            build_score_bundle(self.records[:-1], target_draw_no=self.target, data_version="synthetic-a2")
        with self.assertRaises(ValueError):
            build_score_bundle(self.records + [self.records[-1]], target_draw_no=self.target, data_version="synthetic-a2")


if __name__ == "__main__":
    unittest.main()
