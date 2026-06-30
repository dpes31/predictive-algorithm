"""Anytime-valid log-domain e-process utilities for Gate 2-3P-R2."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Iterable, Sequence

_LOG_MAX = math.log(float.fromhex("0x1.fffffffffffffp+1023"))


def logmeanexp(values: Sequence[float]) -> float:
    """Return log(mean(exp(values))) without overflow."""
    if not values:
        return 0.0
    maximum = max(values)
    if maximum == -math.inf:
        return -math.inf
    return maximum + math.log(sum(math.exp(value - maximum) for value in values) / len(values))


def e_value_from_log(log_value: float) -> float:
    if log_value >= _LOG_MAX:
        return math.inf
    return math.exp(log_value)


def validate_likelihood_ratio(value: float) -> float:
    ratio = float(value)
    if ratio <= 0.0 or not math.isfinite(ratio):
        raise ValueError("likelihood ratio must be finite and positive")
    return ratio


@dataclass
class LogEProcess:
    """Single non-negative likelihood-ratio e-process."""

    log_e_value: float = 0.0
    observations: int = 0

    @property
    def e_value(self) -> float:
        return e_value_from_log(self.log_e_value)

    def update_ratio(self, likelihood_ratio: float) -> float:
        ratio = validate_likelihood_ratio(likelihood_ratio)
        self.log_e_value += math.log(ratio)
        self.observations += 1
        return self.e_value

    def update_log_ratio(self, log_likelihood_ratio: float) -> float:
        value = float(log_likelihood_ratio)
        if not math.isfinite(value):
            raise ValueError("log likelihood ratio must be finite")
        self.log_e_value += value
        self.observations += 1
        return self.e_value

    def neutral_update(self) -> float:
        self.observations += 1
        return self.e_value

    def reset(self) -> None:
        self.log_e_value = 0.0
        self.observations = 0


@dataclass
class WindowMixtureEProcess:
    """Mixture of rolling-window e-processes for transient evidence."""

    horizons: tuple[int, ...] = (13, 26, 52, 104)
    _log_ratios: deque[float] = field(default_factory=deque)

    def __post_init__(self) -> None:
        if not self.horizons or any(horizon < 1 for horizon in self.horizons):
            raise ValueError("horizons must contain positive integers")
        if tuple(sorted(set(self.horizons))) != self.horizons:
            raise ValueError("horizons must be sorted and unique")

    @property
    def observations(self) -> int:
        return len(self._log_ratios)

    @property
    def component_log_values(self) -> tuple[float, ...]:
        values = tuple(self._log_ratios)
        return tuple(sum(values[-horizon:]) for horizon in self.horizons)

    @property
    def log_e_value(self) -> float:
        if not self._log_ratios:
            return 0.0
        return logmeanexp(self.component_log_values)

    @property
    def e_value(self) -> float:
        return e_value_from_log(self.log_e_value)

    def update_ratio(self, likelihood_ratio: float) -> float:
        ratio = validate_likelihood_ratio(likelihood_ratio)
        return self.update_log_ratio(math.log(ratio))

    def update_log_ratio(self, log_likelihood_ratio: float) -> float:
        value = float(log_likelihood_ratio)
        if not math.isfinite(value):
            raise ValueError("log likelihood ratio must be finite")
        self._log_ratios.append(value)
        while len(self._log_ratios) > max(self.horizons):
            self._log_ratios.popleft()
        return self.e_value

    def neutral_update(self) -> float:
        self._log_ratios.append(0.0)
        while len(self._log_ratios) > max(self.horizons):
            self._log_ratios.popleft()
        return self.e_value

    def expire(self) -> None:
        self._log_ratios.clear()


def mean_e_value(processes: Iterable[LogEProcess | WindowMixtureEProcess]) -> float:
    log_values = [process.log_e_value for process in processes]
    return e_value_from_log(logmeanexp(log_values)) if log_values else 1.0
