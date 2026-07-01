from __future__ import annotations

import unittest
from dataclasses import replace

from engine.config import DEFAULT_CONFIG
from engine.contracts import DrawRecord
from engine.experts.change_eprocess import ChangeEProcessDetector


def record(draw_no: int, numbers=(1, 2, 3, 4, 5, 6)):
    return DrawRecord(
        draw_no=draw_no,
        draw_date=f"2026-01-{((draw_no - 1) % 28) + 1:02d}",
        numbers=tuple(numbers),
        source="synthetic",
    )


class ChangeEProcessTests(unittest.TestCase):
    def test_replay_is_deterministic(self):
        records = tuple(record(index) for index in range(1, 40))
        first = ChangeEProcessDetector().replay(records)
        second = ChangeEProcessDetector().replay(records)
        self.assertEqual(first, second)
        self.assertGreater(first.restart_count, 0)
        self.assertEqual(len(first.direction_scores), 45)

    def test_low_trigger_can_activate_on_repeated_direction(self):
        config = replace(
            DEFAULT_CONFIG,
            correction_activation_e=1.01,
            correction_deactivation_e=1.0,
            correction_m3_restart_interval=1,
            correction_change_max_life=30,
        )
        detector = ChangeEProcessDetector(config)
        result = None
        for draw_no in range(1, 80):
            result = detector.update(record(draw_no))
        self.assertIsNotNone(result)
        self.assertTrue(result.active)
        self.assertGreater(result.direction_scores[0], 0.0)

    def test_non_increasing_draws_are_rejected(self):
        detector = ChangeEProcessDetector()
        detector.update(record(1))
        with self.assertRaises(ValueError):
            detector.update(record(1))


if __name__ == "__main__":
    unittest.main()
