from __future__ import annotations

import unittest

from engine.experts.physical_evidence import build_physical_evidence_model
from simulation.physical_scenarios import (
    BALL_SET_LIFT_125,
    BALL_SET_LIFT_125_MISSING_30,
    NULL_UNRELATED,
    generate_physical_series,
    holdout_target,
)


class PhysicalEvidenceTests(unittest.TestCase):
    def test_ball_set_signal_produces_active_centered_distribution(self):
        records, metadata = generate_physical_series(
            BALL_SET_LIFT_125,
            draw_count=420,
            seed=101,
        )
        history, metadata_history, _, target_metadata = holdout_target(records, metadata)
        model = build_physical_evidence_model(
            history,
            metadata_history,
            target_metadata,
        )
        self.assertTrue(model.diagnostics.active)
        self.assertGreaterEqual(model.diagnostics.matched_contexts, 1)
        self.assertAlmostEqual(sum(model.diagnostics.number_logits), 0.0, places=10)
        self.assertGreater(
            max(model.diagnostics.number_logits) - min(model.diagnostics.number_logits),
            0.0,
        )
        marginals = model.distribution.marginal_probabilities()
        self.assertAlmostEqual(sum(marginals.values()), 6.0, places=10)

    def test_same_seed_is_deterministic(self):
        first = generate_physical_series(NULL_UNRELATED, draw_count=320, seed=2026)
        second = generate_physical_series(NULL_UNRELATED, draw_count=320, seed=2026)
        self.assertEqual(first, second)

    def test_low_quality_target_falls_back_to_uniform(self):
        records, metadata = generate_physical_series(
            BALL_SET_LIFT_125_MISSING_30,
            draw_count=320,
            seed=303,
        )
        history, metadata_history, _, target_metadata = holdout_target(records, metadata)
        # The random target may or may not pass 30% missingness, so force all required
        # fields to unknown while preserving the original draw identity.
        fields = dict(target_metadata.fields)
        for path in (
            "machine.machine_id",
            "ball_set.ball_set_id",
            "regime.machine_regime_id",
            "regime.ball_regime_id",
        ):
            fields[path] = type(fields[path])()
        low_quality = type(target_metadata)(
            draw_no=target_metadata.draw_no,
            draw_datetime=target_metadata.draw_datetime,
            metadata_version=target_metadata.metadata_version,
            fields=fields,
        )
        model = build_physical_evidence_model(
            history,
            metadata_history,
            low_quality,
        )
        self.assertFalse(model.diagnostics.active)
        self.assertIn("required_field_completeness_below_threshold", model.diagnostics.reasons)
        marginals = model.distribution.marginal_probabilities()
        for probability in marginals.values():
            self.assertAlmostEqual(probability, 6 / 45, places=12)


if __name__ == "__main__":
    unittest.main()
