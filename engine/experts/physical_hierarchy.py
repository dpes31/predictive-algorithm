"""Hierarchical partial pooling for physical-context number effects."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from ..config import DEFAULT_CONFIG, EngineConfig


def _logit(probability: float) -> float:
    probability = min(1.0 - 1e-12, max(1e-12, probability))
    return math.log(probability / (1.0 - probability))


def _center_clip(values: Sequence[float], limit: float) -> tuple[float, ...]:
    mean = sum(values) / len(values)
    return tuple(max(-limit, min(limit, value - mean)) for value in values)


@dataclass(frozen=True)
class HierarchicalEstimate:
    logits: tuple[float, ...]
    support: float
    used_parent_only: bool


def estimate_context_logits(
    *,
    field_hits: Sequence[float],
    field_exposure: float,
    context_hits: Sequence[float],
    context_exposure: float,
    config: EngineConfig = DEFAULT_CONFIG,
) -> HierarchicalEstimate:
    if len(field_hits) != config.number_count or len(context_hits) != config.number_count:
        raise ValueError("hit vectors must match number_count")
    if field_exposure < 0.0 or context_exposure < 0.0:
        raise ValueError("exposure must be non-negative")

    p0 = config.uniform_number_probability
    field_rates = [
        (config.physical_k_global * p0 + field_hits[index])
        / (config.physical_k_global + field_exposure)
        for index in range(config.number_count)
    ]
    if context_exposure < config.physical_min_context_support:
        context_rates = field_rates
        parent_only = True
    else:
        context_rates = [
            (config.physical_k_context * field_rates[index] + context_hits[index])
            / (config.physical_k_context + context_exposure)
            for index in range(config.number_count)
        ]
        parent_only = False

    baseline = _logit(p0)
    raw = [_logit(rate) - baseline for rate in context_rates]
    return HierarchicalEstimate(
        logits=_center_clip(raw, config.physical_effect_clip),
        support=context_exposure,
        used_parent_only=parent_only,
    )


def estimate_interaction_logits(
    machine_logits: Sequence[float],
    ball_logits: Sequence[float],
    residual_hits: Sequence[float],
    residual_exposure: float,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
) -> HierarchicalEstimate:
    if not (
        len(machine_logits)
        == len(ball_logits)
        == len(residual_hits)
        == config.number_count
    ):
        raise ValueError("interaction vectors must match number_count")
    base = [machine_logits[index] + ball_logits[index] for index in range(config.number_count)]
    if residual_exposure < config.physical_min_interaction_support:
        return HierarchicalEstimate(
            logits=_center_clip(base, config.physical_effect_clip),
            support=residual_exposure,
            used_parent_only=True,
        )
    p0 = config.uniform_number_probability
    residual = [
        (residual_hits[index] - residual_exposure * p0)
        / (config.physical_k_context + residual_exposure)
        for index in range(config.number_count)
    ]
    strongly_shrunk = [value * 0.25 for value in residual]
    combined = [base[index] + strongly_shrunk[index] for index in range(config.number_count)]
    return HierarchicalEstimate(
        logits=_center_clip(combined, config.physical_effect_clip),
        support=residual_exposure,
        used_parent_only=False,
    )


def weighted_hits(
    outcomes: Sequence[Sequence[int]],
    weights: Sequence[float],
    *,
    number_count: int = 45,
) -> tuple[tuple[float, ...], float]:
    if len(outcomes) != len(weights):
        raise ValueError("outcomes and weights length mismatch")
    hits = [0.0] * number_count
    exposure = 0.0
    for numbers, weight in zip(outcomes, weights):
        if weight <= 0.0:
            continue
        exposure += weight
        for number in numbers:
            if not 1 <= number <= number_count:
                raise ValueError("number out of range")
            hits[number - 1] += weight
    return tuple(hits), exposure
