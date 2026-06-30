"""Elementary symmetric polynomial utilities for fixed-size sampling."""

from __future__ import annotations

from collections.abc import Sequence


def elementary_symmetric(weights: Sequence[float], degree: int) -> float:
    if degree < 0:
        raise ValueError("degree must be non-negative")
    if degree > len(weights):
        return 0.0
    coefficients = [0.0] * (degree + 1)
    coefficients[0] = 1.0
    for weight in weights:
        if weight < 0:
            raise ValueError("weights must be non-negative")
        for current_degree in range(degree, 0, -1):
            coefficients[current_degree] += weight * coefficients[current_degree - 1]
    return coefficients[degree]


def inclusion_probabilities(weights: Sequence[float], pick_count: int) -> list[float]:
    """Return exact inclusion marginals for product weights conditioned on fixed size."""
    n = len(weights)
    if not 0 <= pick_count <= n:
        raise ValueError("pick_count outside valid range")
    normalizer = elementary_symmetric(weights, pick_count)
    if normalizer <= 0:
        raise ValueError("distribution normalizer must be positive")

    prefix = [[0.0] * (pick_count + 1) for _ in range(n + 1)]
    suffix = [[0.0] * (pick_count + 1) for _ in range(n + 1)]
    prefix[0][0] = 1.0
    suffix[n][0] = 1.0

    for index, weight in enumerate(weights):
        prefix[index + 1] = prefix[index].copy()
        for degree in range(1, pick_count + 1):
            prefix[index + 1][degree] += weight * prefix[index][degree - 1]

    for index in range(n - 1, -1, -1):
        weight = weights[index]
        suffix[index] = suffix[index + 1].copy()
        for degree in range(1, pick_count + 1):
            suffix[index][degree] += weight * suffix[index + 1][degree - 1]

    probabilities: list[float] = []
    for index, weight in enumerate(weights):
        excluded = 0.0
        for left_degree in range(pick_count):
            right_degree = pick_count - 1 - left_degree
            excluded += prefix[index][left_degree] * suffix[index + 1][right_degree]
        probabilities.append(weight * excluded / normalizer)
    return probabilities
