"""Anytime-valid restart-mixture e-process detector for M3."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord


@dataclass(frozen=True)
class ChangeEProcessResult:
    draw_no: int
    e_value: float
    log_e_value: float
    active: bool
    status: str
    restart_count: int
    direction_scores: tuple[float, ...]
    trigger: float
    deactivation: float
    trigger_draw_no: int | None = None
    active_age: int = 0
    expired: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "draw_no": self.draw_no,
            "e_value": self.e_value,
            "log_e_value": self.log_e_value,
            "active": self.active,
            "status": self.status,
            "restart_count": self.restart_count,
            "direction_scores": list(self.direction_scores),
            "trigger": self.trigger,
            "deactivation": self.deactivation,
            "trigger_draw_no": self.trigger_draw_no,
            "active_age": self.active_age,
            "expired": self.expired,
        }


@dataclass
class _RestartState:
    start_draw: int
    scales: list[float]
    totals: list[float]
    relatives: list[list[float]]

    @classmethod
    def create(cls, start_draw: int, lambda_count: int, number_count: int) -> "_RestartState":
        return cls(
            start_draw=start_draw,
            scales=[1.0] * lambda_count,
            totals=[float(number_count)] * lambda_count,
            relatives=[[1.0] * number_count for _ in range(lambda_count)],
        )


@dataclass
class ChangeEProcessDetector:
    """Registered M3 detector with algebraically exact scaled process state.

    For each restart and betting fraction, all unselected number processes share
    a common scale. Selected-number processes are stored as relative values.
    This is exactly the same arithmetic mixture of e-processes as the previous
    log-dictionary implementation, but is substantially cheaper for DEV runs.
    """

    config: EngineConfig = DEFAULT_CONFIG
    _restarts: list[_RestartState] = field(default_factory=list)
    _active: bool = False
    _last_draw_no: int = 0
    _trigger_draw_no: int | None = None

    def __post_init__(self) -> None:
        p0 = self.config.uniform_number_probability
        selected_factors = tuple(
            1.0 + value * (1.0 - p0)
            for value in self.config.correction_m3_lambda_grid
        )
        self._unselected_factors = tuple(
            1.0 - value * p0
            for value in self.config.correction_m3_lambda_grid
        )
        if any(value <= 0.0 for value in self._unselected_factors + selected_factors):
            raise ValueError("M3 betting factors must remain positive")
        self._relative_ratios = tuple(
            selected / unselected
            for selected, unselected in zip(
                selected_factors,
                self._unselected_factors,
                strict=True,
            )
        )

    def _start_restart(self, draw_no: int) -> None:
        self._restarts.append(
            _RestartState.create(
                draw_no,
                len(self.config.correction_m3_lambda_grid),
                self.config.number_count,
            )
        )

    def _drop_expired(self, draw_no: int) -> None:
        self._restarts = [
            restart
            for restart in self._restarts
            if draw_no - restart.start_draw < self.config.correction_change_max_life
        ]
        if len(self._restarts) > self.config.correction_m3_max_restarts:
            self._restarts = self._restarts[-self.config.correction_m3_max_restarts :]

    def _global_e_value(self) -> float:
        process_count = (
            len(self._restarts)
            * self.config.number_count
            * len(self.config.correction_m3_lambda_grid)
        )
        if process_count == 0:
            return 1.0
        process_sum = sum(
            scale * total
            for restart in self._restarts
            for scale, total in zip(restart.scales, restart.totals, strict=True)
        )
        return process_sum / process_count

    def _direction_scores(self) -> tuple[float, ...]:
        if not self._restarts:
            return tuple(0.0 for _ in range(self.config.number_count))
        scores: list[float] = []
        lambdas = self.config.correction_m3_lambda_grid
        for number_index in range(self.config.number_count):
            numerator = 0.0
            denominator = 0.0
            for restart in self._restarts:
                for slot, betting_fraction in enumerate(lambdas):
                    value = restart.scales[slot] * restart.relatives[slot][number_index]
                    denominator += value
                    numerator += value * (1.0 if betting_fraction > 0.0 else -1.0)
            scores.append(numerator / denominator if denominator > 0.0 else 0.0)
        return tuple(scores)

    def update(self, record: DrawRecord) -> ChangeEProcessResult:
        if record.draw_no <= self._last_draw_no:
            raise ValueError("change e-process records must be strictly increasing")
        if (
            not self._restarts
            or (record.draw_no - 1) % self.config.correction_m3_restart_interval == 0
        ):
            self._start_restart(record.draw_no)

        selected_indexes = tuple(number - 1 for number in record.numbers)
        for restart in self._restarts:
            for slot, unselected_factor in enumerate(self._unselected_factors):
                restart.scales[slot] *= unselected_factor
                relatives = restart.relatives[slot]
                total = restart.totals[slot]
                ratio = self._relative_ratios[slot]
                for number_index in selected_indexes:
                    previous = relatives[number_index]
                    current = previous * ratio
                    relatives[number_index] = current
                    total += current - previous
                restart.totals[slot] = total

        self._last_draw_no = record.draw_no
        self._drop_expired(record.draw_no)
        global_e = self._global_e_value()
        global_log_e = math.log(global_e) if global_e > 0.0 else float("-inf")
        expired_now = False

        if self._active:
            active_age = (
                0
                if self._trigger_draw_no is None
                else record.draw_no - self._trigger_draw_no
            )
            if global_e < self.config.correction_deactivation_e:
                self._active = False
                self._trigger_draw_no = None
            elif active_age >= self.config.correction_change_max_life:
                self._active = False
                self._trigger_draw_no = None
                self._restarts.clear()
                self._start_restart(record.draw_no)
                expired_now = True
        elif global_e >= self.config.correction_activation_e:
            self._active = True
            self._trigger_draw_no = record.draw_no

        active_age = (
            record.draw_no - self._trigger_draw_no
            if self._active and self._trigger_draw_no is not None
            else 0
        )
        status = "EXPIRED" if expired_now else ("ACTIVE" if self._active else "ABSTAIN")
        direction_scores = (
            self._direction_scores()
            if self._active or expired_now
            else tuple(0.0 for _ in range(self.config.number_count))
        )
        return ChangeEProcessResult(
            draw_no=record.draw_no,
            e_value=global_e,
            log_e_value=global_log_e,
            active=self._active,
            status=status,
            restart_count=len(self._restarts),
            direction_scores=direction_scores,
            trigger=self.config.correction_activation_e,
            deactivation=self.config.correction_deactivation_e,
            trigger_draw_no=self._trigger_draw_no,
            active_age=active_age,
            expired=expired_now,
        )

    def replay(self, records: Sequence[DrawRecord]) -> ChangeEProcessResult:
        result: ChangeEProcessResult | None = None
        for record in records:
            result = self.update(record)
        if result is not None:
            return result
        return ChangeEProcessResult(
            0,
            1.0,
            0.0,
            False,
            "ABSTAIN",
            0,
            tuple(0.0 for _ in range(self.config.number_count)),
            self.config.correction_activation_e,
            self.config.correction_deactivation_e,
        )
