"""Empirical null calibration utilities for Gate 2-3."""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from statistics import median
from typing import Mapping, Sequence

from .diagnostics import OriginSnapshot


@dataclass(frozen=True)
class GateCalibrationResult:
    change_gate: float
    raw_p_values: Mapping[str, float]
    holm_adjusted_p_values: Mapping[str, float]
    significant: bool
    pair_tail_probability: float


def holm_adjust(p_values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    count = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (name, value) in enumerate(ordered):
        candidate = min(1.0, (count - rank) * value)
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def _upper_tail(sorted_values: Sequence[float], observed: float) -> float:
    index = bisect.bisect_left(sorted_values, observed)
    count = len(sorted_values) - index
    return (count + 1.0) / (len(sorted_values) + 1.0)


def _lower_tail(sorted_values: Sequence[float], observed: float) -> float:
    index = bisect.bisect_right(sorted_values, observed)
    return (index + 1.0) / (len(sorted_values) + 1.0)


def _series_extrema(snapshots: Sequence[OriginSnapshot]) -> dict[str, float]:
    if not snapshots:
        raise ValueError("snapshots must not be empty")
    return {
        "max_abs_shift_52": max(snapshot.diagnostics["max_abs_shift_52"] for snapshot in snapshots),
        "max_abs_shift_104": max(snapshot.diagnostics["max_abs_shift_104"] for snapshot in snapshots),
        "min_entropy_52": min(snapshot.diagnostics["entropy_52"] for snapshot in snapshots),
        "max_abs_cusum": max(snapshot.diagnostics["max_abs_cusum"] for snapshot in snapshots),
        "max_abs_pair_104": max(snapshot.diagnostics["max_abs_pair_104"] for snapshot in snapshots),
    }


@dataclass(frozen=True)
class NullCalibration:
    calibration_series: int
    maxima_shift_52: tuple[float, ...]
    maxima_shift_104: tuple[float, ...]
    minima_entropy_52: tuple[float, ...]
    maxima_cusum: tuple[float, ...]
    maxima_pair_104: tuple[float, ...]
    alpha: float = 0.001

    @classmethod
    def fit(cls, series_snapshots: Sequence[Sequence[OriginSnapshot]], *, alpha: float = 0.001) -> "NullCalibration":
        extrema = [_series_extrema(snapshots) for snapshots in series_snapshots]
        if not extrema:
            raise ValueError("at least one calibration series is required")
        return cls(
            calibration_series=len(extrema),
            maxima_shift_52=tuple(sorted(item["max_abs_shift_52"] for item in extrema)),
            maxima_shift_104=tuple(sorted(item["max_abs_shift_104"] for item in extrema)),
            minima_entropy_52=tuple(sorted(item["min_entropy_52"] for item in extrema)),
            maxima_cusum=tuple(sorted(item["max_abs_cusum"] for item in extrema)),
            maxima_pair_104=tuple(sorted(item["max_abs_pair_104"] for item in extrema)),
            alpha=alpha,
        )

    def evaluate(self, snapshot: OriginSnapshot) -> GateCalibrationResult:
        raw = {
            "shift_52": _upper_tail(self.maxima_shift_52, snapshot.diagnostics["max_abs_shift_52"]),
            "shift_104": _upper_tail(self.maxima_shift_104, snapshot.diagnostics["max_abs_shift_104"]),
            "entropy_52": _lower_tail(self.minima_entropy_52, snapshot.diagnostics["entropy_52"]),
            "cusum": _upper_tail(self.maxima_cusum, snapshot.diagnostics["max_abs_cusum"]),
        }
        adjusted = holm_adjust(raw)
        significant = min(adjusted.values()) <= self.alpha
        evidence = [max(0.0, 1.0 - 2.0 * value) for value in raw.values()]
        change_gate = median(evidence) if significant else 0.0
        pair_tail = _upper_tail(self.maxima_pair_104, snapshot.diagnostics["max_abs_pair_104"])
        return GateCalibrationResult(
            change_gate=change_gate,
            raw_p_values=raw,
            holm_adjusted_p_values=adjusted,
            significant=significant,
            pair_tail_probability=pair_tail,
        )

    def to_dict(self) -> dict[str, object]:
        def quantile(values: Sequence[float], probability: float) -> float:
            index = min(len(values) - 1, max(0, math.ceil(probability * len(values)) - 1))
            return values[index]

        return {
            "calibration_series": self.calibration_series,
            "alpha": self.alpha,
            "familywise_over_origins": True,
            "quantiles": {
                "max_abs_shift_52_q999": quantile(self.maxima_shift_52, 0.999),
                "max_abs_shift_104_q999": quantile(self.maxima_shift_104, 0.999),
                "min_entropy_52_q001": quantile(self.minima_entropy_52, 0.001),
                "max_abs_cusum_q999": quantile(self.maxima_cusum, 0.999),
                "max_abs_pair_104_q999": quantile(self.maxima_pair_104, 0.999),
            },
        }


def one_sided_binomial_upper(successes: int, trials: int, *, confidence: float = 0.95) -> float:
    """Exact Clopper-Pearson one-sided upper confidence limit."""
    if not 0 <= successes <= trials or trials <= 0:
        raise ValueError("invalid binomial counts")
    if successes == trials:
        return 1.0
    alpha = 1.0 - confidence

    def cumulative(probability: float) -> float:
        return sum(
            math.comb(trials, index)
            * (probability**index)
            * ((1.0 - probability) ** (trials - index))
            for index in range(successes + 1)
        )

    lower, upper = 0.0, 1.0
    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        if cumulative(midpoint) > alpha:
            lower = midpoint
        else:
            upper = midpoint
    return upper
