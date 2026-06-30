"""Leakage-safe Gate 2 feature generation."""

from __future__ import annotations

import math
from collections.abc import Sequence

from .config import EngineConfig
from .contracts import DrawRecord, FeatureSnapshot
from .hashing import sha256_value


def _clip(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def _cross_sectional_z(values: dict[int, float], limit: float) -> dict[int, float]:
    mean = sum(values.values()) / len(values)
    variance = sum((value - mean) ** 2 for value in values.values()) / len(values)
    standard_deviation = math.sqrt(variance)
    if standard_deviation <= 0:
        return {number: 0.0 for number in values}
    return {number: _clip((value - mean) / standard_deviation, limit) for number, value in values.items()}


def _entropy(records: Sequence[DrawRecord], number_count: int, pick_count: int) -> float:
    if not records:
        return 1.0
    counts = {number: 0 for number in range(1, number_count + 1)}
    for record in records:
        for number in record.numbers:
            counts[number] += 1
    denominator = pick_count * len(records)
    probabilities = [count / denominator for count in counts.values() if count]
    return -sum(probability * math.log(probability) for probability in probabilities) / math.log(number_count)


def build_feature_snapshot(
    records: Sequence[DrawRecord],
    *,
    target_draw_no: int,
    data_version: str,
    config: EngineConfig,
) -> FeatureSnapshot:
    if not records:
        raise ValueError("records must not be empty")
    if records[-1].draw_no != target_draw_no - 1:
        raise ValueError("feature snapshot requires input_last_draw == target_draw_no - 1")
    if len(records) < config.min_history:
        raise ValueError(f"at least {config.min_history} draws are required")

    number_sets = [set(record.numbers) for record in records]
    p0 = config.uniform_number_probability
    alpha0 = config.prior_concentration * p0
    beta0 = config.prior_concentration * (1.0 - p0)
    limit = config.winsor_limit
    number_features: dict[int, dict[str, float]] = {
        number: {} for number in range(1, config.number_count + 1)
    }

    long_count = {
        number: sum(number in values for values in number_sets)
        for number in range(1, config.number_count + 1)
    }
    long_se = math.sqrt(p0 * (1 - p0) / (config.prior_concentration + len(records)))
    for number in number_features:
        long_rate = (alpha0 + long_count[number]) / (alpha0 + beta0 + len(records))
        number_features[number]["z_long"] = _clip((long_rate - p0) / long_se, limit)

    for window in config.recent_windows:
        recent = number_sets[-window:]
        standard_error = math.sqrt(p0 * (1 - p0) / window)
        for number in number_features:
            rate = sum(number in values for values in recent) / window
            number_features[number][f"z_recent_{window}"] = _clip((rate - p0) / standard_error, limit)

    for number in number_features:
        number_features[number]["z_trend_10_52"] = _clip(
            (number_features[number]["z_recent_10"] - number_features[number]["z_recent_52"]) / math.sqrt(2),
            limit,
        )
        number_features[number]["z_trend_30_104"] = _clip(
            (number_features[number]["z_recent_30"] - number_features[number]["z_recent_104"]) / math.sqrt(2),
            limit,
        )

    mean_gap = (1 - p0) / p0
    standard_gap = math.sqrt(1 - p0) / p0
    for number in number_features:
        gap = 0
        for values in reversed(number_sets):
            if number in values:
                break
            gap += 1
        number_features[number]["z_gap"] = _clip((gap - mean_gap) / standard_gap, limit)

    for window in (52, 104):
        if len(records) < 2 * window:
            for number in number_features:
                number_features[number][f"z_shift_{window}"] = 0.0
            continue
        recent = number_sets[-window:]
        previous = number_sets[-2 * window : -window]
        standard_error = math.sqrt(2 * p0 * (1 - p0) / window)
        for number in number_features:
            recent_rate = sum(number in values for values in recent) / window
            previous_rate = sum(number in values for values in previous) / window
            number_features[number][f"z_shift_{window}"] = _clip(
                (recent_rate - previous_rate) / standard_error,
                limit,
            )

    ewma_alpha = 1.0 - math.exp(-math.log(2.0) / config.ewma_half_life)
    ewma_values: dict[int, float] = {number: p0 for number in number_features}
    for values in number_sets:
        for number in number_features:
            observed = 1.0 if number in values else 0.0
            ewma_values[number] = ewma_alpha * observed + (1 - ewma_alpha) * ewma_values[number]
    ewma_difference = {
        number: ewma_values[number]
        - (alpha0 + long_count[number]) / (alpha0 + beta0 + len(records))
        for number in number_features
    }
    ewma_z = _cross_sectional_z(ewma_difference, limit)

    drift_allowance = 0.25 * math.sqrt(p0 * (1 - p0))
    cplus = {number: 0.0 for number in number_features}
    cminus = {number: 0.0 for number in number_features}
    for values in number_sets:
        for number in number_features:
            centered = (1.0 if number in values else 0.0) - p0
            cplus[number] = max(0.0, cplus[number] + centered - drift_allowance)
            cminus[number] = min(0.0, cminus[number] + centered + drift_allowance)
    cusum_z = _cross_sectional_z(
        {number: cplus[number] + cminus[number] for number in number_features},
        limit,
    )
    for number in number_features:
        number_features[number]["z_ewma_minus_long"] = ewma_z[number]
        number_features[number]["signed_cusum_score"] = cusum_z[number]

    global_features: dict[str, float | bool | str] = {
        "entropy_52": _entropy(records[-52:], config.number_count, config.pick_count),
        "entropy_104": _entropy(records[-104:], config.number_count, config.pick_count),
        "max_abs_shift_52": max(abs(features["z_shift_52"]) for features in number_features.values()),
        "max_abs_shift_104": max(abs(features["z_shift_104"]) for features in number_features.values()),
        "max_abs_cusum": max(abs(features["signed_cusum_score"]) for features in number_features.values()),
        "change_gate": 0.0,
        "change_gate_calibrated": False,
        "change_gate_status": "pending_gate2_3_null_calibration",
    }
    payload = {
        "target_draw_no": target_draw_no,
        "input_last_draw": records[-1].draw_no,
        "data_version": data_version,
        "feature_contract_version": config.feature_contract_version,
        "number_features": {str(number): number_features[number] for number in sorted(number_features)},
        "global_features": global_features,
    }
    return FeatureSnapshot(
        target_draw_no=target_draw_no,
        input_last_draw=records[-1].draw_no,
        data_version=data_version,
        feature_contract_version=config.feature_contract_version,
        number_features=number_features,
        global_features=global_features,
        snapshot_hash=sha256_value(payload),
    )
