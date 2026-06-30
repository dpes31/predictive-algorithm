"""Sequential loss-based weight updates with bounded one-step influence."""

from __future__ import annotations

import math
from collections.abc import Mapping

from .config import EngineConfig


def uniform_weights(names: list[str] | tuple[str, ...]) -> dict[str, float]:
    if not names:
        raise ValueError("names must not be empty")
    value = 1.0 / len(names)
    return {name: value for name in names}


def update_weights(
    previous: Mapping[str, float],
    losses: Mapping[str, float],
    *,
    baseline_loss: float,
    config: EngineConfig,
) -> dict[str, float]:
    if set(previous) != set(losses):
        raise ValueError("previous weights and losses must have identical keys")
    raw: dict[str, float] = {}
    for name, previous_weight in previous.items():
        if previous_weight <= 0 or not math.isfinite(previous_weight):
            raise ValueError("previous weights must be finite and positive")
        loss = losses[name]
        if not math.isfinite(loss):
            raise ValueError("losses must be finite")
        difference = max(
            -config.loss_difference_clip,
            min(config.loss_difference_clip, loss - baseline_loss),
        )
        value = (previous_weight ** config.weight_decay) * math.exp(-config.learning_rate * difference)
        raw[name] = max(config.minimum_weight, value)
    total = sum(raw.values())
    return {name: value / total for name, value in raw.items()}
