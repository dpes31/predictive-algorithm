from __future__ import annotations

import unittest

from engine.metadata_veto import evaluate_metadata_global_veto


def evidence(value, observed_at="2026-07-01T10:00:00+09:00"):
    return {
        "value": value,
        "status": "verified",
        "source_type": "official_document",
        "source_url": "https://synthetic.invalid/source",
        "observed_at": observed_at,
        "available_before_draw": True,
        "confidence": 0.95,
    }


class MetadataVetoTests(unittest.TestCase):
    def valid_payload(self):
        return {
            "draw_no": 1231,
            "draw_datetime": "2026-07-04T20:35:00+09:00",
            "metadata_version": "1.0.0",
            "machine": {"machine_id": evidence("M1")},
            "ball_set": {"ball_set_id": evidence("B1")},
        }

    def test_valid_metadata_is_not_vetoed(self):
        result = evaluate_metadata_global_veto(self.valid_payload(), target_draw_no=1231)
        self.assertFalse(result.vetoed)
        self.assertEqual(result.status, "VALID_METADATA")

    def test_post_draw_timestamp_vetoes_all_m4(self):
        payload = self.valid_payload()
        payload["machine"]["machine_id"] = evidence("M1", "2026-07-04T21:00:00+09:00")
        result = evaluate_metadata_global_veto(payload, target_draw_no=1231)
        self.assertTrue(any(reason.startswith("post_draw_timestamp") for reason in result.reasons))

    def test_current_result_field_is_forbidden(self):
        payload = self.valid_payload()
        payload["winning_numbers"] = [1, 2, 3, 4, 5, 6]
        result = evaluate_metadata_global_veto(payload, target_draw_no=1231)
        self.assertIn("result_field:winning_numbers", result.reasons)

    def test_schema_mismatch_is_vetoed(self):
        payload = self.valid_payload()
        payload["metadata_version"] = "0.9.0"
        result = evaluate_metadata_global_veto(payload, target_draw_no=1231)
        self.assertIn("schema_version_mismatch", result.reasons)


if __name__ == "__main__":
    unittest.main()
