from __future__ import annotations

import unittest

from engine.data_loader import records_for_target
from simulation.uniform_lottery import generate_uniform_draws


class DataCutoffTests(unittest.TestCase):
    def test_research_accepts_auto_checked(self):
        records = generate_uniform_draws(299, seed=1)
        usable = records_for_target(records, target_draw_no=300, research_only=True, minimum_history=299)
        self.assertEqual(usable[-1].draw_no, 299)

    def test_public_rejects_unlocked_auto_checked(self):
        records = generate_uniform_draws(299, seed=1)
        with self.assertRaises(ValueError):
            records_for_target(records, target_draw_no=300, research_only=False, minimum_history=299)

    def test_future_draw_is_rejected(self):
        records = generate_uniform_draws(300, seed=1)
        with self.assertRaisesRegex(ValueError, "future-data cutoff"):
            records_for_target(records, target_draw_no=300, research_only=True, minimum_history=299)


if __name__ == "__main__":
    unittest.main()
