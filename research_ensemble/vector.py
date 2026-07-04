"""Deterministic helpers for 45-number score vectors."""

from __future__ import annotations

import math
from collections.abc import Mapping


def stable_float(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("non-finite value")
    return float(format(value, ".15g"))


def validate_vector(values: Mapping[int, float], *, number_count: int = 45) -> None:
    if set(values) != set(range(1, number_count + 1)):
        raise ValueError("score vector must contain numbers 1..45 exactly once")
    if not all(math.isfinite(float(value)) for value in values.values()):
        raise ValueError("score vector values must be finite")


def zero_vector(number_count: int = 45) -> dict[int, float]:
    return {number: 0.0 for number in range(1, number_count + 1)}


def normalize_vector(values: Mapping[int, float], *, number_count: int = 45) -> dict[int, float]:
    validate_vector(values, number_count=number_count)
    mean = sum(float(values[number]) for number in range(1, number_count + 1)) / number_count
    centered = {number: float(values[number]) - mean for number in range(1, number_count + 1)}
    maximum = max(abs(value) for value in centered.values())
    if maximum <= 1e-15:
        return zero_vector(number_count)
    return {number: centered[number] / maximum for number in centered}


def center_and_cap(values: Mapping[int, float], cap: float, *, number_count: int = 45) -> dict[int, float]:
    validate_vector(values, number_count=number_count)
    mean = sum(float(values[number]) for number in range(1, number_count + 1)) / number_count
    centered = {number: float(values[number]) - mean for number in range(1, number_count + 1)}
    maximum = max(abs(value) for value in centered.values())
    if maximum <= cap + 1e-15:
        return centered
    scale = cap / maximum
    return {number: centered[number] * scale for number in centered}
