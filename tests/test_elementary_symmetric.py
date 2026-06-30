from __future__ import annotations

import itertools
import math
import unittest

from engine.distributions import FixedSizeDistribution
from engine.elementary_symmetric import elementary_symmetric


class ElementarySymmetricTests(unittest.TestCase):
    def test_matches_bruteforce(self):
        weights = [1.0, 2.0, 3.0, 4.0]
        expected = sum(math.prod(combo) for combo in itertools.combinations(weights, 2))
        self.assertAlmostEqual(elementary_symmetric(weights, 2), expected)

    def test_uniform_distribution_normalizes(self):
        distribution = FixedSizeDistribution((0.0, 0.0, 0.0, 0.0), pick_count=2)
        total = sum(distribution.joint_probability(combo) for combo in itertools.combinations(range(1, 5), 2))
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_marginals_sum_to_pick_count(self):
        distribution = FixedSizeDistribution((0.0, 0.2, -0.3, 0.8, 0.1), pick_count=2)
        marginals = distribution.marginal_probabilities()
        self.assertAlmostEqual(sum(marginals.values()), 2.0, places=12)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in marginals.values()))

    def test_top_combinations_are_probability_sorted(self):
        distribution = FixedSizeDistribution((3.0, 2.0, 1.0, 0.0), pick_count=2)
        top = distribution.top_combinations(3)
        probabilities = [distribution.joint_probability(combo) for combo in top]
        self.assertEqual(top[0], (1, 2))
        self.assertEqual(probabilities, sorted(probabilities, reverse=True))


if __name__ == "__main__":
    unittest.main()
