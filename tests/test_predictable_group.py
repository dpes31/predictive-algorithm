from __future__ import annotations

import unittest

import engine.experts.predictable_group as predictable_group
from engine.experts.predictable_group import (
    OccurrenceIndex,
    numbers_to_mask,
    rank_numbers,
    score_numbers,
    select_predictable_group,
)


class PredictableGroupTests(unittest.TestCase):
    @staticmethod
    def history(count: int = 600):
        mask = numbers_to_mask((1, 2, 3, 4, 5, 6))
        return tuple(mask for _ in range(count))

    def test_mask_validation(self):
        self.assertEqual(numbers_to_mask((1, 2, 3, 4, 5, 6)).bit_count(), 6)
        with self.assertRaises(ValueError):
            numbers_to_mask((1, 2, 3))

    def test_score_and_tie_rules(self):
        index = OccurrenceIndex.build(self.history(520))
        scores = score_numbers(index, start=1, end=520)
        self.assertGreater(scores[1], scores[45])
        tied = {number: 0.0 for number in range(1, 46)}
        self.assertEqual(rank_numbers(tied), tuple(range(1, 46)))

    def test_incomplete_window_rejected(self):
        index = OccurrenceIndex.build(self.history(519))
        with self.assertRaises(ValueError):
            select_predictable_group(index, block_start=520)

    def test_no_eligible_size_abstains(self):
        index = OccurrenceIndex.build(self.history())
        original = predictable_group._validation_log_lr
        predictable_group._validation_log_lr = lambda *args, **kwargs: -1.0
        try:
            decision = select_predictable_group(index, block_start=521)
        finally:
            predictable_group._validation_log_lr = original
        self.assertTrue(decision.abstain)
        self.assertIsNone(decision.selected_size)

    def test_size_tie_prefers_six(self):
        index = OccurrenceIndex.build(self.history())
        original = predictable_group._validation_log_lr
        predictable_group._validation_log_lr = lambda *args, **kwargs: 1.0
        try:
            decision = select_predictable_group(index, block_start=521)
        finally:
            predictable_group._validation_log_lr = original
        self.assertFalse(decision.abstain)
        self.assertEqual(decision.selected_size, 6)

    def test_decision_is_deterministic(self):
        index = OccurrenceIndex.build(self.history())
        first = select_predictable_group(index, block_start=521)
        second = select_predictable_group(index, block_start=521)
        self.assertEqual(first, second)
        if not first.abstain:
            self.assertIn(first.selected_size, (6, 10, 15))
            self.assertEqual(len(first.group), first.selected_size)


if __name__ == "__main__":
    unittest.main()
