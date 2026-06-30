"""Exact synthetic 6-of-45 samplers for Gate 2-3."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence


def _suffix_polynomials(weights: Sequence[float], pick_count: int) -> list[list[float]]:
    size = len(weights)
    suffix = [[0.0] * (pick_count + 1) for _ in range(size + 1)]
    suffix[size][0] = 1.0
    for index in range(size - 1, -1, -1):
        suffix[index][0] = 1.0
        weight = weights[index]
        for degree in range(1, pick_count + 1):
            suffix[index][degree] = suffix[index + 1][degree] + weight * suffix[index + 1][degree - 1]
    return suffix


def sample_weighted_combination(
    weights: Sequence[float],
    *,
    pick_count: int,
    rng: random.Random,
    labels: Sequence[int] | None = None,
) -> tuple[int, ...]:
    """Sample a fixed-size set with probability proportional to its weight product."""
    if not 0 < pick_count <= len(weights):
        raise ValueError("invalid pick_count")
    if any(weight <= 0 or not math.isfinite(weight) for weight in weights):
        raise ValueError("all weights must be finite and positive")
    resolved_labels = tuple(labels or range(1, len(weights) + 1))
    if len(resolved_labels) != len(weights) or len(set(resolved_labels)) != len(weights):
        raise ValueError("labels must be unique and aligned")

    suffix = _suffix_polynomials(weights, pick_count)
    remaining = pick_count
    selected: list[int] = []
    for index, weight in enumerate(weights):
        if remaining == 0:
            break
        items_left = len(weights) - index
        if items_left == remaining:
            selected.extend(resolved_labels[index:])
            break
        denominator = suffix[index][remaining]
        inclusion_probability = weight * suffix[index + 1][remaining - 1] / denominator
        if rng.random() < inclusion_probability:
            selected.append(resolved_labels[index])
            remaining -= 1
    if len(selected) != pick_count:
        raise RuntimeError("fixed-size sampler did not return the requested count")
    return tuple(sorted(selected))


def sample_with_pair_factor(
    *,
    number_count: int,
    pick_count: int,
    selected_pair: tuple[int, int],
    factor: float,
    rng: random.Random,
) -> tuple[int, ...]:
    """Sample a uniform combination with an exact multiplicative factor on one pair."""
    if factor < 1 or not math.isfinite(factor):
        raise ValueError("factor must be finite and at least one")
    if len(set(selected_pair)) != 2 or not all(1 <= number <= number_count for number in selected_pair):
        raise ValueError("invalid selected_pair")
    while True:
        candidate = tuple(sorted(rng.sample(range(1, number_count + 1), pick_count)))
        has_pair = selected_pair[0] in candidate and selected_pair[1] in candidate
        acceptance_probability = 1.0 if has_pair else 1.0 / factor
        if rng.random() <= acceptance_probability:
            return candidate
