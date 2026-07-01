"""Exact fixed-size group likelihood-ratio and oracle e-process for M3 5.0.

This module is intentionally limited to the Gate 2-3P-R3M-2 oracle contract.
It does not learn groups, search hypotheses, or expose a deployable M3 model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class ExactGroupAlternative:
    """Exact 6-of-45 alternative that upweights a prespecified number group."""

    favored_numbers: tuple[int, ...]
    lift: float
    number_count: int = 45
    pick_count: int = 6

    def __post_init__(self) -> None:
        favored = tuple(sorted(set(self.favored_numbers)))
        if favored != self.favored_numbers:
            object.__setattr__(self, "favored_numbers", favored)
        if self.number_count < 2:
            raise ValueError("number_count must be at least 2")
        if not 1 <= self.pick_count < self.number_count:
            raise ValueError("pick_count must be between 1 and number_count - 1")
        if not self.favored_numbers or len(self.favored_numbers) >= self.number_count:
            raise ValueError("favored group must be non-empty and smaller than the universe")
        if any(number < 1 or number > self.number_count for number in self.favored_numbers):
            raise ValueError("favored numbers must be inside the number universe")
        if not math.isfinite(self.lift) or self.lift <= 0.0:
            raise ValueError("lift must be finite and positive")

    @property
    def favored_count(self) -> int:
        return len(self.favored_numbers)

    @property
    def support(self) -> tuple[int, ...]:
        lower = max(0, self.pick_count - (self.number_count - self.favored_count))
        upper = min(self.pick_count, self.favored_count)
        return tuple(range(lower, upper + 1))

    @property
    def uniform_combination_count(self) -> int:
        return math.comb(self.number_count, self.pick_count)

    @property
    def normalizer(self) -> float:
        return sum(
            math.comb(self.favored_count, selected_favored)
            * math.comb(
                self.number_count - self.favored_count,
                self.pick_count - selected_favored,
            )
            * (self.lift**selected_favored)
            for selected_favored in self.support
        )

    @property
    def log_lr_constant(self) -> float:
        return math.log(self.uniform_combination_count) - math.log(self.normalizer)

    def validate_numbers(self, numbers: Sequence[int]) -> tuple[int, ...]:
        canonical = tuple(sorted(numbers))
        if len(canonical) != self.pick_count or len(set(canonical)) != self.pick_count:
            raise ValueError("numbers must contain exactly pick_count unique values")
        if any(number < 1 or number > self.number_count for number in canonical):
            raise ValueError("numbers must be inside the number universe")
        return canonical

    def favored_selected(self, numbers: Sequence[int]) -> int:
        canonical = self.validate_numbers(numbers)
        favored = set(self.favored_numbers)
        return sum(number in favored for number in canonical)

    def log_likelihood_ratio_from_count(self, selected_favored: int) -> float:
        if selected_favored not in self.support:
            raise ValueError("selected_favored is outside the feasible support")
        return selected_favored * math.log(self.lift) + self.log_lr_constant

    def log_likelihood_ratio(self, numbers: Sequence[int]) -> float:
        return self.log_likelihood_ratio_from_count(self.favored_selected(numbers))

    def likelihood_ratio(self, numbers: Sequence[int]) -> float:
        return math.exp(self.log_likelihood_ratio(numbers))

    def count_probabilities(self, *, alternative: bool) -> tuple[float, ...]:
        weights = []
        for selected_favored in self.support:
            value = math.comb(self.favored_count, selected_favored) * math.comb(
                self.number_count - self.favored_count,
                self.pick_count - selected_favored,
            )
            if alternative:
                value *= self.lift**selected_favored
            weights.append(float(value))
        total = sum(weights)
        return tuple(value / total for value in weights)

    def to_dict(self) -> dict[str, Any]:
        return {
            "favored_numbers": list(self.favored_numbers),
            "favored_count": self.favored_count,
            "lift": self.lift,
            "number_count": self.number_count,
            "pick_count": self.pick_count,
            "normalizer": self.normalizer,
            "uniform_combination_count": self.uniform_combination_count,
        }


@dataclass(frozen=True)
class OracleGroupEProcessResult:
    draw_index: int
    e_value: float
    log_e_value: float
    active: bool
    ever_activated: bool
    trigger_draw_index: int | None
    active_age: int
    expired: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "draw_index": self.draw_index,
            "e_value": self.e_value,
            "log_e_value": self.log_e_value,
            "active": self.active,
            "ever_activated": self.ever_activated,
            "trigger_draw_index": self.trigger_draw_index,
            "active_age": self.active_age,
            "expired": self.expired,
            "status": self.status,
        }


@dataclass
class OracleGroupEProcess:
    """Oracle-only e-process with separate detection and active-life contracts."""

    alternative: ExactGroupAlternative
    activation_threshold: float = 1000.0
    detection_horizon: int = 520
    active_life: int = 208
    _draw_index: int = 0
    _log_e_value: float = 0.0
    _max_log_e_value: float = 0.0
    _active: bool = False
    _ever_activated: bool = False
    _trigger_draw_index: int | None = None
    _expired: bool = False

    def __post_init__(self) -> None:
        if not math.isfinite(self.activation_threshold) or self.activation_threshold <= 1.0:
            raise ValueError("activation_threshold must be finite and greater than 1")
        if self.detection_horizon < 1:
            raise ValueError("detection_horizon must be positive")
        if self.active_life < 1:
            raise ValueError("active_life must be positive")

    @property
    def max_e_value(self) -> float:
        return math.exp(self._max_log_e_value)

    def update(self, numbers: Sequence[int]) -> OracleGroupEProcessResult:
        selected_favored = self.alternative.favored_selected(numbers)
        return self.update_count(selected_favored)

    def update_count(self, selected_favored: int) -> OracleGroupEProcessResult:
        self._draw_index += 1

        if not self._ever_activated and self._draw_index <= self.detection_horizon:
            self._log_e_value += self.alternative.log_likelihood_ratio_from_count(
                selected_favored
            )
            self._max_log_e_value = max(self._max_log_e_value, self._log_e_value)
            if self._log_e_value >= math.log(self.activation_threshold):
                self._active = True
                self._ever_activated = True
                self._trigger_draw_index = self._draw_index

        if self._active and self._trigger_draw_index is not None:
            active_age = self._draw_index - self._trigger_draw_index
            if active_age >= self.active_life:
                self._active = False
                self._expired = True
        else:
            active_age = 0

        if self._expired:
            status = "EXPIRED"
        elif self._active:
            status = "ACTIVE"
        elif not self._ever_activated and self._draw_index >= self.detection_horizon:
            status = "HORIZON_EXHAUSTED"
        else:
            status = "ABSTAIN"

        return OracleGroupEProcessResult(
            draw_index=self._draw_index,
            e_value=math.exp(self._log_e_value),
            log_e_value=self._log_e_value,
            active=self._active,
            ever_activated=self._ever_activated,
            trigger_draw_index=self._trigger_draw_index,
            active_age=active_age,
            expired=self._expired,
            status=status,
        )
