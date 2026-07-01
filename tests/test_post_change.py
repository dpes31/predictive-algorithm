from __future__ import annotations

import math
import unittest
from dataclasses import replace

from engine.config import DEFAULT_CONFIG
from engine.contracts import DrawRecord
from engine.experts.change_eprocess import ChangeEProcessDetector, ChangeEProcessResult
from engine.experts.post_change import build_post_change_model


def record(draw_no: int, numbers=(1, 2, 3, 4, 5, 6)) -> DrawRecord:
    return DrawRecord(
        draw_no=draw_no,
        draw_date=f"2026-01-{((draw_no - 1) % 28) + 1:02d}",
        numbers=tuple(numbers),
        source="synthetic",
    )


class PostChangeModelTests(unittest.TestCase):
    def test_inactive_detector_returns_exact_uniform(self):
        result = ChangeEProcessResult(
            draw_no=60,
            e_value=1.0,
            log_e_value=0.0,
            active=False,
            status="ABSTAIN",
            restart_count=1,
            direction_scores=tuple(0.0 for _ in range(45)),
            trigger=1000.0,
            deactivation=100.0,
        )
        model = build_post_change_model(tuple(record(i) for i in range(1, 61)), result)
        self.assertTrue(model.distribution.is_uniform)
        self.assertFalse(model.diagnostics.active)

    def test_active_detector_uses_only_post_trigger_records(self):
        records = tuple(
            record(i, (1, 2, 3, 4, 5, 6) if i >= 20 else (40, 41, 42, 43, 44, 45))
            for i in range(1, 61)
        )
        result = ChangeEProcessResult(
            draw_no=60,
            e_value=2000.0,
            log_e_value=math.log(2000.0),
            active=True,
            status="ACTIVE",
            restart_count=4,
            direction_scores=tuple(0.0 for _ in range(45)),
            trigger=1000.0,
            deactivation=100.0,
            trigger_draw_no=20,
            active_age=40,
        )
        config = replace(DEFAULT_CONFIG, correction_k_m3=90.0)
        model = build_post_change_model(records, result, config)
        self.assertTrue(model.diagnostics.active)
        self.assertEqual(model.diagnostics.support, 41)
        marginals = model.distribution.marginal_probabilities()
        self.assertGreater(marginals[1], marginals[45])

    def test_detector_records_trigger_and_expires(self):
        config = replace(
            DEFAULT_CONFIG,
            correction_activation_e=1.01,
            correction_deactivation_e=0.0001,
            correction_m3_restart_interval=1,
            correction_change_max_life=5,
        )
        detector = ChangeEProcessDetector(config)
        saw_active = False
        saw_expired = False
        for draw_no in range(1, 80):
            result = detector.update(record(draw_no))
            if result.active:
                saw_active = True
                self.assertIsNotNone(result.trigger_draw_no)
            if result.expired:
                saw_expired = True
                self.assertEqual(result.status, "EXPIRED")
        self.assertTrue(saw_active)
        self.assertTrue(saw_expired)


if __name__ == "__main__":
    unittest.main()
