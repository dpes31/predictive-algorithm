from __future__ import annotations

import unittest

from engine.physical_metadata import PhysicalDrawMetadata, validate_metadata_sequence


def evidence(value, *, observed_at="2026-07-04T19:00:00+09:00", status="verified"):
    return {
        "value": value,
        "status": status,
        "source_type": "official_document",
        "source_url": "https://example.invalid/source",
        "observed_at": observed_at,
        "available_before_draw": status not in {"unknown", "inferred"},
        "confidence": 0.95 if status not in {"unknown", "inferred"} else 0.0,
    }


def valid_mapping(draw_no=1231):
    return {
        "draw_no": draw_no,
        "draw_datetime": "2026-07-04T20:35:00+09:00",
        "metadata_version": "1.0.0",
        "machine": {
            "machine_id": evidence("M1"),
            "machine_generation": evidence("MG1"),
        },
        "ball_set": {
            "ball_set_id": evidence("B3"),
            "ball_generation": evidence("BG1"),
        },
        "regime": {
            "machine_regime_id": evidence("MR1"),
            "ball_regime_id": evidence("BR1"),
            "operating_procedure_regime_id": evidence("OR1"),
        },
    }


class PhysicalMetadataTests(unittest.TestCase):
    def test_valid_metadata_is_active_and_traceable(self):
        metadata = PhysicalDrawMetadata.from_mapping(valid_mapping())
        quality = metadata.quality()
        self.assertTrue(quality.active)
        self.assertEqual(quality.required_field_completeness, 1.0)
        self.assertEqual(quality.pre_draw_availability_rate, 1.0)
        self.assertEqual(quality.source_traceability_rate, 1.0)
        self.assertEqual(set(metadata.context_values()), {
            "machine.machine_id",
            "machine.machine_generation",
            "ball_set.ball_set_id",
            "ball_set.ball_generation",
            "regime.machine_regime_id",
            "regime.ball_regime_id",
            "regime.operating_procedure_regime_id",
        })

    def test_post_draw_evidence_cannot_be_marked_pre_draw(self):
        mapping = valid_mapping()
        mapping["machine"]["machine_id"] = evidence(
            "M1",
            observed_at="2026-07-04T21:00:00+09:00",
        )
        with self.assertRaisesRegex(ValueError, "observed after the draw"):
            PhysicalDrawMetadata.from_mapping(mapping)

    def test_current_result_fields_are_forbidden(self):
        mapping = valid_mapping()
        mapping["ordered_numbers"] = evidence([1, 2, 3, 4, 5, 6])
        with self.assertRaisesRegex(ValueError, "result field is forbidden"):
            PhysicalDrawMetadata.from_mapping(mapping)

    def test_inferred_evidence_is_not_prediction_eligible(self):
        mapping = valid_mapping()
        inferred = evidence("B3", status="inferred")
        inferred["available_before_draw"] = False
        mapping["ball_set"]["ball_set_id"] = inferred
        metadata = PhysicalDrawMetadata.from_mapping(mapping)
        self.assertNotIn("ball_set.ball_set_id", metadata.eligible_fields())
        self.assertFalse(metadata.quality().active)

    def test_duplicate_draw_numbers_are_rejected(self):
        one = PhysicalDrawMetadata.from_mapping(valid_mapping(1230))
        two = PhysicalDrawMetadata.from_mapping(valid_mapping(1230))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_metadata_sequence([one, two])


if __name__ == "__main__":
    unittest.main()
