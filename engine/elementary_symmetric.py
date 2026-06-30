"""Elementary symmetric polynomial utilities for fixed-size sampling."""

from __future__ import annotations

from collections.abc import Sequence


def elementary_symmetric_coefficients(weights: Sequence[float], degree: int) -> list[float]:
    if degree < 0:
        raise ValueError("degree must be non-negative")
    coefficients = [0.0] * (degree + 1)
    coefficients[0] = 1.0
    for weight in weights:
        if weight < 0:
            raise ValueError("weights must be non-negative")
        for current_degree in range(degree, 0, -1):
            coefficients[current_degree] += weight * coefficients[current_degree - 1]
    return coefficients


def elementary_symmetric(weights: Sequence[float], degree: int) -> float:
    if degree > len(weights):
        return 0.0
    return elementary_symmetric_coefficients(weights, degree)[degree]


def inclusion_probabilities(weights: Sequence[float], pick_count: int) -> list[float]:
    """Return exact inclusion marginals for fixed-size product weights."""
    count = len(weights)
    if not 0 <= pick_count <= count:
        raise ValueError("pick_count outside valid range")
    coefficients = elementary_symmetric_coefficients(weights, pick_count)
    normalizer = coefficients[pick_count]
    if normalizer <= 0:
        raise ValueError("distribution normalizer must be positive")
    if pick_count == 0:
        return [0.0] * count

    probabilities: list[float] = []
    for weight in weights:
        excluded = 1.0
        for degree in range(1, pick_count):
            excluded = coefficients[degree] - weight * excluded
            if excluded < 0 and abs(excluded) < 1e-12:
                excluded = 0.0
        probability = weight * excluded / normalizer
        probabilities.append(max(0.0, min(1.0, probability)))
    return probabilities
