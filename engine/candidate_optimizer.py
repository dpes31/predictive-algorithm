"""Deterministic five-set candidate selection."""

from __future__ import annotations

import hashlib
import random
from collections.abc import Sequence

from .config import EngineConfig
from .contracts import CandidateSet
from .distributions import CombinationDistribution


def _random_combination(rng: random.Random, number_count: int, pick_count: int) -> tuple[int, ...]:
    return tuple(sorted(rng.sample(range(1, number_count + 1), pick_count)))


def _diversity_score(candidate: tuple[int, ...], selected: Sequence[tuple[int, ...]]) -> tuple[int, int]:
    if not selected:
        return (len(candidate), 0)
    selected_union = set().union(*(set(values) for values in selected))
    union_gain = len(set(candidate) - selected_union)
    total_overlap = sum(len(set(candidate) & set(values)) for values in selected)
    return (union_gain, -total_overlap)


def _uniform_candidates(seed: str, config: EngineConfig) -> list[tuple[int, ...]]:
    rng = random.Random(int(seed[:16], 16))
    pool: set[tuple[int, ...]] = set()
    while len(pool) < config.uniform_candidate_pool:
        pool.add(_random_combination(rng, config.number_count, config.pick_count))
    ranked = sorted(
        pool,
        key=lambda combination: hashlib.sha256(f"{seed}:{combination}".encode("utf-8")).hexdigest(),
    )
    selected = [ranked[0]]
    while len(selected) < config.candidate_count:
        remaining = [candidate for candidate in ranked if candidate not in selected]
        best = max(remaining, key=lambda candidate: (_diversity_score(candidate, selected), tuple(-n for n in candidate)))
        selected.append(best)
    return selected


def _nonuniform_candidates(
    distribution: CombinationDistribution,
    config: EngineConfig,
) -> list[tuple[int, ...]]:
    universe = distribution.top_combinations(config.candidate_universe_per_component)
    if len(universe) < config.candidate_count:
        raise RuntimeError("candidate universe is too small")
    ranked = sorted(universe, key=lambda combination: (-distribution.joint_probability(combination), combination))
    fifth_probability = distribution.joint_probability(ranked[config.candidate_count - 1])
    eligible = [
        combination
        for combination in ranked
        if distribution.joint_probability(combination) >= config.near_tie_ratio * fifth_probability
    ]
    selected = [ranked[0]]
    while len(selected) < config.candidate_count:
        remaining = [candidate for candidate in eligible if candidate not in selected]
        if not remaining:
            remaining = [candidate for candidate in ranked if candidate not in selected]
        best = max(
            remaining,
            key=lambda candidate: (
                _diversity_score(candidate, selected),
                distribution.joint_probability(candidate),
                tuple(-number for number in candidate),
            ),
        )
        selected.append(best)
    return selected


def optimize_candidates(
    distribution: CombinationDistribution,
    *,
    seed: str,
    uniform_probability: float,
    config: EngineConfig,
) -> list[CandidateSet]:
    combinations = (
        _uniform_candidates(seed, config)
        if getattr(distribution, "is_uniform", False)
        else _nonuniform_candidates(distribution, config)
    )
    candidates: list[CandidateSet] = []
    for rank, numbers in enumerate(combinations, start=1):
        probability = distribution.joint_probability(numbers)
        candidates.append(
            CandidateSet(
                rank=rank,
                numbers=numbers,
                joint_probability=probability,
                lift_vs_uniform=probability / uniform_probability,
                credible_interval_95=None,
                crowd_avoidance_score=0.0,
            )
        )
    return candidates
