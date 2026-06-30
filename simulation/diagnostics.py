"""Incremental feature and diagnostic snapshots for Gate 2-3."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from itertools import combinations
from statistics import fmean
from typing import Mapping, Sequence

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.contracts import DrawRecord


@dataclass(frozen=True)
class OriginSnapshot:
    origin_draw_no: int
    forecast_start: int
    forecast_end: int
    number_features: Mapping[str, tuple[float, ...]]
    diagnostics: Mapping[str, float]


def forecast_origins(draw_count: int, *, minimum_history: int = 299, block_size: int = 52) -> tuple[int, ...]:
    if draw_count <= minimum_history:
        return ()
    origins: list[int] = []
    origin = minimum_history
    while origin < draw_count:
        origins.append(origin)
        origin += block_size
    return tuple(origins)


def _clip(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def _cross_sectional_z(values: Sequence[float], limit: float) -> tuple[float, ...]:
    mean = fmean(values)
    variance = fmean((value - mean) ** 2 for value in values)
    standard_deviation = math.sqrt(variance)
    if standard_deviation <= 0:
        return tuple(0.0 for _ in values)
    return tuple(_clip((value - mean) / standard_deviation, limit) for value in values)


def _entropy(counts: Sequence[int], total_mass: int, number_count: int) -> float:
    if total_mass <= 0:
        return 1.0
    probabilities = [count / total_mass for count in counts if count > 0]
    return -sum(probability * math.log(probability) for probability in probabilities) / math.log(number_count)


def _pair_index(number_count: int) -> tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], int]]:
    pairs = tuple(combinations(range(1, number_count + 1), 2))
    return pairs, {pair: index for index, pair in enumerate(pairs)}


def build_origin_snapshots(
    records: Sequence[DrawRecord],
    *,
    block_size: int = 52,
    config: EngineConfig = DEFAULT_CONFIG,
    target_pair: tuple[int, int] = (7, 38),
) -> list[OriginSnapshot]:
    if len(records) < config.min_history:
        raise ValueError("insufficient records")
    draw_count = len(records)
    origins = set(forecast_origins(draw_count, minimum_history=config.min_history, block_size=block_size))
    p0 = config.uniform_number_probability
    alpha0 = config.prior_concentration * p0
    beta0 = config.prior_concentration * (1.0 - p0)
    ewma_alpha = 1.0 - math.exp(-math.log(2.0) / config.ewma_half_life)
    drift_allowance = 0.25 * math.sqrt(p0 * (1.0 - p0))
    pair_probability = 1.0 / 66.0

    cumulative: list[list[int]] = [[0] * config.number_count]
    last_seen = [0] * config.number_count
    ewma = [p0] * config.number_count
    cplus = [0.0] * config.number_count
    cminus = [0.0] * config.number_count

    pairs, pair_lookup = _pair_index(config.number_count)
    pair_counts = [0] * len(pairs)
    pair_window: deque[tuple[int, ...]] = deque(maxlen=104)
    snapshots: list[OriginSnapshot] = []

    for record in records:
        draw_no = record.draw_no
        present = {number - 1 for number in record.numbers}
        current_counts = cumulative[-1].copy()
        for index in present:
            current_counts[index] += 1
            last_seen[index] = draw_no
        cumulative.append(current_counts)

        for index in range(config.number_count):
            observed = 1.0 if index in present else 0.0
            ewma[index] = ewma_alpha * observed + (1.0 - ewma_alpha) * ewma[index]
            centered = observed - p0
            cplus[index] = max(0.0, cplus[index] + centered - drift_allowance)
            cminus[index] = min(0.0, cminus[index] + centered + drift_allowance)

        if len(pair_window) == pair_window.maxlen:
            expired = pair_window[0]
            for left, right in combinations(expired, 2):
                pair_counts[pair_lookup[(left, right)]] -= 1
        pair_window.append(record.numbers)
        for left, right in combinations(record.numbers, 2):
            pair_counts[pair_lookup[(left, right)]] += 1

        if draw_no not in origins:
            continue

        features: dict[str, tuple[float, ...]] = {}
        long_standard_error = math.sqrt(p0 * (1.0 - p0) / (config.prior_concentration + draw_no))
        long_values = []
        long_rates = []
        for count in current_counts:
            long_rate = (alpha0 + count) / (alpha0 + beta0 + draw_no)
            long_rates.append(long_rate)
            long_values.append(_clip((long_rate - p0) / long_standard_error, config.winsor_limit))
        features["z_long"] = tuple(long_values)

        recent_features: dict[int, tuple[float, ...]] = {}
        for window in config.recent_windows:
            start = max(0, draw_no - window)
            counts = [current_counts[index] - cumulative[start][index] for index in range(config.number_count)]
            standard_error = math.sqrt(p0 * (1.0 - p0) / window)
            values = tuple(
                _clip((count / window - p0) / standard_error, config.winsor_limit)
                for count in counts
            )
            recent_features[window] = values
            features[f"z_recent_{window}"] = values

        features["z_trend_10_52"] = tuple(
            _clip((recent_features[10][index] - recent_features[52][index]) / math.sqrt(2.0), config.winsor_limit)
            for index in range(config.number_count)
        )
        features["z_trend_30_104"] = tuple(
            _clip((recent_features[30][index] - recent_features[104][index]) / math.sqrt(2.0), config.winsor_limit)
            for index in range(config.number_count)
        )

        mean_gap = (1.0 - p0) / p0
        standard_gap = math.sqrt(1.0 - p0) / p0
        features["z_gap"] = tuple(
            _clip(((draw_no - last_seen[index]) - mean_gap) / standard_gap, config.winsor_limit)
            for index in range(config.number_count)
        )

        for window in (52, 104):
            recent_start = draw_no - window
            prior_start = draw_no - 2 * window
            recent_counts = [current_counts[index] - cumulative[recent_start][index] for index in range(config.number_count)]
            prior_counts = [cumulative[recent_start][index] - cumulative[prior_start][index] for index in range(config.number_count)]
            standard_error = math.sqrt(2.0 * p0 * (1.0 - p0) / window)
            features[f"z_shift_{window}"] = tuple(
                _clip(((recent_counts[index] - prior_counts[index]) / window) / standard_error, config.winsor_limit)
                for index in range(config.number_count)
            )

        features["z_ewma_minus_long"] = _cross_sectional_z(
            [ewma[index] - long_rates[index] for index in range(config.number_count)],
            config.winsor_limit,
        )
        features["signed_cusum_score"] = _cross_sectional_z(
            [cplus[index] + cminus[index] for index in range(config.number_count)],
            config.winsor_limit,
        )

        counts52 = [current_counts[index] - cumulative[draw_no - 52][index] for index in range(config.number_count)]
        counts104 = [current_counts[index] - cumulative[draw_no - 104][index] for index in range(config.number_count)]
        pair_standard_error = math.sqrt(pair_probability * (1.0 - pair_probability) / 104.0)
        pair_zscores = [
            (count / 104.0 - pair_probability) / pair_standard_error
            for count in pair_counts
        ]
        normalized_pair = tuple(sorted(target_pair))
        diagnostics = {
            "max_abs_shift_52": max(abs(value) for value in features["z_shift_52"]),
            "max_abs_shift_104": max(abs(value) for value in features["z_shift_104"]),
            "entropy_52": _entropy(counts52, config.pick_count * 52, config.number_count),
            "entropy_104": _entropy(counts104, config.pick_count * 104, config.number_count),
            "max_abs_cusum": max(abs(value) for value in features["signed_cusum_score"]),
            "max_abs_pair_104": max(abs(value) for value in pair_zscores),
            "target_pair_z_104": pair_zscores[pair_lookup[normalized_pair]],
        }
        snapshots.append(
            OriginSnapshot(
                origin_draw_no=draw_no,
                forecast_start=draw_no + 1,
                forecast_end=min(draw_count, draw_no + block_size),
                number_features=features,
                diagnostics=diagnostics,
            )
        )
    return snapshots
