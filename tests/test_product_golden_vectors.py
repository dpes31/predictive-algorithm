"""Golden-vector regression tests freezing CONTROL_M0 deterministic outputs.

Why this file exists
---------------------
`product/dynamic_prediction.run_dynamic_prediction` and the underlying
`engine/candidate_optimizer.optimize_candidates` build candidate sets using
`random.Random(int(seed[:16], 16))` followed by `rng.sample(...)`. CPython
only guarantees cross-version stability for `random.Random.random()` (the
core PRNG stream); it does NOT make a public compatibility promise about the
exact sequence produced by `random.sample()` across Python versions. That
means the product's "identical input -> identical output" behavior is an
*empirically observed* property of the current CPython implementations, not
an officially documented guarantee.

These tests exist to FREEZE the exact values currently produced, so that any
future change in behavior -- whether from a Python upgrade, a stdlib change,
or an accidental code change -- is caught immediately as a test failure
instead of silently shipping a different prediction for the same input.

Verification performed for this freeze
---------------------------------------
The constants below were captured by running the exact same code path under
all four available CPython interpreters (3.10, 3.11, 3.12, 3.13) and
confirming the outputs were byte-for-byte identical across all of them, on
2026-07-04. See docs/DETERMINISM_GOLDEN_VECTORS.md for the full policy.

IMPORTANT -- if these tests fail on a future Python version:
Do NOT regenerate/update these constants to make the tests pass. A failure
here means the deterministic reproduction contract described above may be
broken for that Python version. This requires an explicit, human-approved
decision about how to respond (see docs/DETERMINISM_GOLDEN_VECTORS.md),
not a silent constant refresh.
"""

from __future__ import annotations

import hashlib
import math
import pathlib
import unittest

from engine.candidate_optimizer import optimize_candidates
from engine.config import EngineConfig
from engine.distributions import FixedSizeDistribution
from product.dynamic_prediction import run_dynamic_prediction

ROOT = pathlib.Path(__file__).resolve().parents[1]


class GoldenVectorCanonicalOnlyTests(unittest.TestCase):
    """Golden A: run_dynamic_prediction with an empty overlay."""

    def test_canonical_only_matches_golden_vector(self) -> None:
        result = run_dynamic_prediction(overlay=[], generated_at="2026-01-01T00:00:00Z")

        self.assertEqual(result["target_draw_no"], 1231)
        self.assertEqual(
            result["seed"],
            "536db9f14b495720ecb5f54a07e4148e0089219cf25bc92fbdea315c46b0fa8d",
        )
        self.assertEqual(
            result["hashes"]["effective_data_hash"],
            "3d7adfa271bd9646009ad9dfa3d969ef62db90fddc6be0f9c3a4cee92fcfa535",
        )
        self.assertEqual(
            result["hashes"]["prediction_hash"],
            "bbf8b4756d84a7a069aa120f31ff75c9171f62b8367833bb46ab19772134a8ca",
        )
        self.assertEqual(
            [candidate["numbers"] for candidate in result["candidate_sets"]],
            [
                [6, 15, 26, 27, 28, 35],
                [1, 2, 3, 12, 17, 32],
                [4, 5, 7, 16, 34, 42],
                [8, 9, 11, 22, 25, 29],
                [10, 13, 14, 23, 31, 44],
            ],
        )
        self.assertEqual(
            result["product_weights"],
            {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0},
        )
        self.assertFalse(result["statistical_edge"])


class GoldenVectorFixedOverlayTests(unittest.TestCase):
    """Golden B: run_dynamic_prediction with one fixed overlay record.

    The overlay's draw_date (2026-07-04) is the canonical last draw_date
    (2026-06-27, draw 1230) plus 7 days, computed once and hardcoded here as
    a literal string.
    """

    def test_fixed_overlay_matches_golden_vector(self) -> None:
        overlay = [
            {
                "draw_no": 1231,
                "draw_date": "2026-07-04",
                "numbers": [3, 11, 19, 27, 35, 43],
                "bonus_number": 7,
            }
        ]
        result = run_dynamic_prediction(overlay=overlay, generated_at="2026-01-01T00:00:00Z")

        self.assertEqual(result["target_draw_no"], 1232)
        self.assertEqual(
            result["seed"],
            "900ec89466b713b8e68015fc0e6b92e81621f8b2801ea97d0e7a538886d03c63",
        )
        self.assertEqual(
            result["hashes"]["effective_data_hash"],
            "851377198a753242d6937e6911bd5e00920576a33da7d50cf538c38a286f0184",
        )
        self.assertEqual(
            result["hashes"]["prediction_hash"],
            "397d6cb696fdfdcd7226a42d33610838d5d9ed55737fa5ee5c70ed4f428a4882",
        )
        self.assertEqual(
            [candidate["numbers"] for candidate in result["candidate_sets"]],
            [
                [4, 9, 21, 27, 32, 42],
                [1, 2, 3, 31, 36, 39],
                [5, 6, 7, 11, 26, 43],
                [8, 10, 14, 19, 29, 41],
                [12, 15, 23, 37, 44, 45],
            ],
        )


class GoldenVectorEngineIsolationTests(unittest.TestCase):
    """Golden C: engine-level optimize_candidates with a fixed synthetic seed.

    This isolates the candidate optimizer from the product wrapper entirely,
    so a regression can be localized to engine/candidate_optimizer.py versus
    product/dynamic_prediction.py.
    """

    def test_engine_isolation_matches_golden_vector(self) -> None:
        distribution = FixedSizeDistribution(logits=(0.0,) * 45, pick_count=6)
        engine_config = EngineConfig(
            number_count=45,
            pick_count=6,
            candidate_count=5,
            uniform_candidate_pool=3000,
        )
        fixed_seed = hashlib.sha256(b"golden-vector-fixed-seed").hexdigest()
        uniform_probability = 1.0 / math.comb(45, 6)

        candidates = optimize_candidates(
            distribution,
            seed=fixed_seed,
            uniform_probability=uniform_probability,
            config=engine_config,
        )

        self.assertEqual(
            [tuple(candidate.numbers) for candidate in candidates],
            [
                (1, 2, 3, 20, 33, 45),
                (4, 5, 6, 22, 25, 42),
                (7, 8, 9, 17, 35, 38),
                (10, 11, 12, 16, 26, 39),
                (13, 18, 19, 24, 30, 34),
            ],
        )


if __name__ == "__main__":
    unittest.main()
