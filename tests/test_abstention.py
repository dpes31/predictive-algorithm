from __future__ import annotations

import unittest
from dataclasses import replace

from engine.abstention import AbstentionController, AbstentionStatus, MacroPerformance
from engine.config import DEFAULT_CONFIG


class AbstentionTests(unittest.TestCase):
    def config(self):
        return replace(DEFAULT_CONFIG, correction_activation_e=10.0, correction_deactivation_e=2.0, correction_forced_return_draws=3)

    def test_activation_is_shadow_only_in_research(self):
        controller = AbstentionController(self.config())
        decision = controller.evaluate(
            draw_no=100,
            e_value=12.0,
            recent_performance=(MacroPerformance(0.1, 0.0),),
            research_only=True,
        )
        self.assertEqual(decision.status, AbstentionStatus.SHADOW_ACTIVE)
        self.assertTrue(decision.active)
        self.assertFalse(decision.deployable)

    def test_deactivation_hysteresis(self):
        controller = AbstentionController(self.config(), active=True)
        decision = controller.evaluate(
            draw_no=101,
            e_value=1.5,
            recent_performance=(MacroPerformance(0.1, 0.0),),
        )
        self.assertEqual(decision.status, AbstentionStatus.ABSTAIN)
        self.assertFalse(decision.active)

    def test_negative_block_forces_m0_return(self):
        controller = AbstentionController(self.config(), active=True)
        decision = controller.evaluate(
            draw_no=200,
            e_value=100.0,
            recent_performance=(MacroPerformance(0.0, -0.1),),
        )
        self.assertEqual(decision.status, AbstentionStatus.FORCED_RETURN)
        self.assertTrue(decision.exact_m0)
        self.assertEqual(decision.forced_until_draw, 202)

    def test_metadata_veto_has_priority(self):
        controller = AbstentionController(self.config(), active=True)
        decision = controller.evaluate(
            draw_no=200,
            e_value=1000.0,
            recent_performance=(MacroPerformance(1.0, 1.0),),
            metadata_vetoed=True,
        )
        self.assertEqual(decision.status, AbstentionStatus.INVALID_METADATA)
        self.assertFalse(decision.active)


if __name__ == "__main__":
    unittest.main()
