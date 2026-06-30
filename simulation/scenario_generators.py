"""Synthetic draw generators for preregistered Gate 2-3 scenarios."""

from __future__ import annotations

import datetime as dt
import math
import random
from collections import deque

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.contracts import DrawRecord
from .sampling import sample_weighted_combination, sample_with_pair_factor
from .scenario_specs import ScenarioSpec


def _recent_zscores(history: deque[tuple[int, ...]], config: EngineConfig) -> list[float]:
    window = len(history)
    if window == 0:
        return [0.0] * config.number_count
    counts = [0] * config.number_count
    for combination in history:
        for number in combination:
            counts[number - 1] += 1
    p0 = config.uniform_number_probability
    standard_error = math.sqrt(p0 * (1.0 - p0) / window)
    return [
        max(-config.winsor_limit, min(config.winsor_limit, (count / window - p0) / standard_error))
        for count in counts
    ]


def _weights_for_draw(
    spec: ScenarioSpec,
    draw_no: int,
    recent_history: deque[tuple[int, ...]],
    config: EngineConfig,
) -> list[float]:
    weights = [1.0] * config.number_count
    if spec.family == "fixed_bias":
        for number in spec.target_numbers:
            weights[number - 1] = spec.effect_size
    elif spec.family in {"persistence", "reversal"} and len(recent_history) == recent_history.maxlen:
        sign = 1.0 if spec.family == "persistence" else -1.0
        zscores = _recent_zscores(recent_history, config)
        weights = [math.exp(sign * spec.effect_size * zscore) for zscore in zscores]
    elif spec.family == "regime_shift":
        if spec.change_points[0] <= draw_no < spec.change_points[1]:
            for number in (1, 2, 3, 4, 5, 6):
                weights[number - 1] = spec.effect_size
        elif draw_no >= spec.change_points[1]:
            for number in (40, 41, 42, 43, 44, 45):
                weights[number - 1] = spec.effect_size
    elif spec.family == "temporary_anomaly":
        assert spec.active_range is not None
        if spec.active_range[0] <= draw_no <= spec.active_range[1]:
            for number in spec.target_numbers:
                weights[number - 1] = spec.effect_size
    return weights


def generate_scenario_draws(
    spec: ScenarioSpec,
    *,
    draw_count: int = 1230,
    seed: int,
    config: EngineConfig = DEFAULT_CONFIG,
) -> list[DrawRecord]:
    if draw_count < 1:
        raise ValueError("draw_count must be positive")
    rng = random.Random(seed)
    start = dt.date(2002, 12, 7)
    recent_history: deque[tuple[int, ...]] = deque(maxlen=52)
    records: list[DrawRecord] = []

    for draw_no in range(1, draw_count + 1):
        if spec.family == "pair_interaction":
            assert spec.target_pair is not None
            numbers = sample_with_pair_factor(
                number_count=config.number_count,
                pick_count=config.pick_count,
                selected_pair=spec.target_pair,
                factor=spec.effect_size,
                rng=rng,
            )
        else:
            numbers = sample_weighted_combination(
                _weights_for_draw(spec, draw_no, recent_history, config),
                pick_count=config.pick_count,
                rng=rng,
            )
        remaining = [number for number in range(1, config.number_count + 1) if number not in numbers]
        bonus = rng.choice(remaining)
        records.append(
            DrawRecord(
                draw_no=draw_no,
                draw_date=(start + dt.timedelta(days=7 * (draw_no - 1))).isoformat(),
                numbers=numbers,
                bonus_number=bonus,
                verification_status="auto_checked",
                locked=False,
                source=f"synthetic_{spec.name}",
            )
        )
        recent_history.append(numbers)
    return records
