from __future__ import annotations

import itertools
import random
import unittest

from simulation.sampling import sample_weighted_combination, sample_with_pair_factor


class SyntheticSamplingTests(unittest.TestCase):
    def test_fixed_size_and_labels(self):
        rng = random.Random(7)
        for _ in range(100):
            sample = sample_weighted_combination([1.0, 2.0, 3.0, 4.0], pick_count=2, rng=rng)
            self.assertEqual(len(sample), 2)
            self.assertEqual(tuple(sorted(sample)), sample)
            self.assertEqual(len(set(sample)), 2)

    def test_weighted_sampler_matches_small_exact_distribution(self):
        rng = random.Random(11)
        weights = [1.0, 2.0, 3.0, 4.0]
        samples = 30000
        counts = {combo: 0 for combo in itertools.combinations(range(1, 5), 2)}
        for _ in range(samples):
            counts[sample_weighted_combination(weights, pick_count=2, rng=rng)] += 1
        normalizer = sum(weights[a - 1] * weights[b - 1] for a, b in counts)
        for combo, count in counts.items():
            expected = weights[combo[0] - 1] * weights[combo[1] - 1] / normalizer
            self.assertLess(abs(count / samples - expected), 0.015)

    def test_pair_factor_increases_pair_frequency(self):
        rng = random.Random(19)
        hits = 0
        trials = 5000
        for _ in range(trials):
            sample = sample_with_pair_factor(
                number_count=10,
                pick_count=3,
                selected_pair=(2, 7),
                factor=3.0,
                rng=rng,
            )
            hits += int(2 in sample and 7 in sample)
        uniform_pair_probability = 3 * 2 / (10 * 9)
        self.assertGreater(hits / trials, uniform_pair_probability)


if __name__ == "__main__":
    unittest.main()
