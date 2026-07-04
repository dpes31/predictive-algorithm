from __future__ import annotations

import math
import unittest

from engine.experts.oracle_group_eprocess import (
    ExactGroupAlternative,
    OracleGroupEProcess,
)


class ExactGroupAlternativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alternative = ExactGroupAlternative(tuple(range(36, 46)), 1.25)

    def test_null_expectation_of_likelihood_ratio_is_one(self):
        probabilities = self.alternative.count_probabilities(alternative=False)
        expectation = sum(
            probability
            * math.exp(
                self.alternative.log_likelihood_ratio_from_count(selected_favored)
            )
            for probability, selected_favored in zip(
                probabilities, self.alternative.support, strict=True
            )
        )
        self.assertAlmostEqual(expectation, 1.0, places=12)

    def test_exact_formula_matches_selected_group_count(self):
        numbers = (1, 2, 36, 37, 38, 39)
        expected = 4 * math.log(1.25) + self.alternative.log_lr_constant
        self.assertAlmostEqual(
            self.alternative.log_likelihood_ratio(numbers), expected, places=12
        )

    def test_invalid_fixed_size_draw_is_rejected(self):
        with self.assertRaises(ValueError):
            self.alternative.log_likelihood_ratio((1, 2, 3))
        with self.assertRaises(ValueError):
            self.alternative.log_likelihood_ratio((1, 2, 3, 4, 5, 5))


class OracleGroupEProcessTests(unittest.TestCase):
    def test_repeated_favored_counts_activate(self):
        alternative = ExactGroupAlternative(tuple(range(36, 46)), 2.0)
        process = OracleGroupEProcess(
            alternative,
            activation_threshold=2.0,
            detection_horizon=20,
            active_life=208,
        )
        result = None
        for _ in range(20):
            result = process.update_count(max(alternative.support))
            if result.active:
                break
        self.assertIsNotNone(result)
        self.assertTrue(result.ever_activated)
        self.assertIsNotNone(result.trigger_draw_index)

    def test_horizon_prevents_late_activation(self):
        alternative = ExactGroupAlternative(tuple(range(36, 46)), 1.25)
        process = OracleGroupEProcess(
            alternative,
            activation_threshold=1000.0,
            detection_horizon=3,
            active_life=208,
        )
        for _ in range(10):
            result = process.update_count(max(alternative.support))
        self.assertFalse(result.ever_activated)
        self.assertEqual(result.status, "HORIZON_EXHAUSTED")

    def test_post_activation_life_is_208_draws(self):
        alternative = ExactGroupAlternative(tuple(range(36, 46)), 2.0)
        process = OracleGroupEProcess(
            alternative,
            activation_threshold=1.01,
            detection_horizon=520,
            active_life=208,
        )
        result = process.update_count(max(alternative.support))
        self.assertTrue(result.active)
        for _ in range(208):
            result = process.update_count(max(alternative.support))
        self.assertFalse(result.active)
        self.assertTrue(result.expired)
        self.assertEqual(result.status, "EXPIRED")


if __name__ == "__main__":
    unittest.main()
