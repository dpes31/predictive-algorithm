from __future__ import annotations

import unittest
from dataclasses import replace

from engine.config import DEFAULT_CONFIG
from engine.experts.physical_hierarchy import HierarchicalPhysicalEstimator
from engine.physical_metadata import EvidenceValue


def ev(value, confidence=1.0):
    return EvidenceValue(
        value=value,
        status="observed",
        source_type="official_document",
        source_url="https://synthetic.invalid/source",
        observed_at="2026-01-01T00:00:00+09:00",
        available_before_draw=True,
        confidence=confidence,
    )


class PhysicalHierarchyTests(unittest.TestCase):
    def test_unseen_context_uses_parent_fallback(self):
        config = replace(DEFAULT_CONFIG, correction_k_global=20.0, correction_k_context=10.0, correction_effect_clip=0.35)
        estimator = HierarchicalPhysicalEstimator(config)
        for _ in range(40):
            estimator.update_field("machine.machine_id", ev("M1"), (1, 2, 3, 4, 5, 6))
        result = estimator.distribution("machine.machine_id", ev("M2"))
        self.assertTrue(result.diagnostics.used_parent_fallback)
        self.assertGreater(result.diagnostics.parent_support, 0.0)
        self.assertAlmostEqual(sum(result.distribution.logits), 0.0, places=10)
        self.assertGreater(result.distribution.logits[0], result.distribution.logits[-1])

    def test_context_child_moves_away_from_parent(self):
        config = replace(DEFAULT_CONFIG, correction_k_global=20.0, correction_k_context=5.0, correction_effect_clip=0.35)
        estimator = HierarchicalPhysicalEstimator(config)
        for _ in range(20):
            estimator.update_field("ball_set.ball_set_id", ev("B1"), (1, 2, 3, 4, 5, 6))
            estimator.update_field("ball_set.ball_set_id", ev("B2"), (40, 41, 42, 43, 44, 45))
        b1 = estimator.distribution("ball_set.ball_set_id", ev("B1"))
        b2 = estimator.distribution("ball_set.ball_set_id", ev("B2"))
        self.assertGreater(b1.distribution.logits[0], b1.distribution.logits[-1])
        self.assertLess(b2.distribution.logits[0], b2.distribution.logits[-1])

    def test_regime_reset_preserves_parent_and_clears_children(self):
        estimator = HierarchicalPhysicalEstimator(DEFAULT_CONFIG)
        estimator.update_field("machine.machine_id", ev("M1"), (1, 2, 3, 4, 5, 6))
        estimator.reset_contexts(("machine.machine_id",))
        parent, child = estimator.support("machine.machine_id", ev("M1"))
        self.assertGreater(parent, 0.0)
        self.assertEqual(child, 0.0)


if __name__ == "__main__":
    unittest.main()
