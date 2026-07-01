"""Anytime-valid restart-mixture e-process detector for M3."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord
from ..eprocess import e_value_from_log, logmeanexp


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
        }


@dataclass
class ChangeEProcessDetector:
    config: EngineConfig = DEFAULT_CONFIG
    _processes: dict[tuple[int, int, float], float] = field(default_factory=dict)
    _active: bool = False
    _last_draw_no: int = 0

    def _start_restart(self, draw_no: int) -> None:
        for number_index in range(self.config.number_count):
            for betting_fraction in self.config.correction_m3_lambda_grid:
                self._processes[(draw_no, number_index, betting_fraction)] = 0.0

    def _drop_expired(self, draw_no: int) -> None:
        maximum_age = self.config.correction_change_max_life
        self._processes = {
            key: value for key, value in self._processes.items()
            if draw_no - key[0] < maximum_age
        }
        restart_values = sorted({key[0] for key in self._processes}, reverse=True)
        keep = set(restart_values[: self.config.correction_m3_max_restarts])
        self._processes = {key: value for key, value in self._processes.items() if key[0] in keep}

    def update(self, record: DrawRecord) -> ChangeEProcessResult:
        if record.draw_no <= self._last_draw_no:
            raise ValueError("change e-process records must be strictly increasing")
        if not self._processes or (record.draw_no - 1) % self.config.correction_m3_restart_interval == 0:
            self._start_restart(record.draw_no)
        selected = {number - 1 for number in record.numbers}
        p0 = self.config.uniform_number_probability
        updated: dict[tuple[int, int, float], float] = {}
        for key, log_value in self._processes.items():
            _, number_index, betting_fraction = key
            centered = (1.0 if number_index in selected else 0.0) - p0
            factor = 1.0 + betting_fraction * centered
            if factor <= 0.0:
                raise ValueError("M3 betting factor must remain positive")
            updated[key] = log_value + math.log(factor)
        self._processes = updated
        self._last_draw_no = record.draw_no
        self._drop_expired(record.draw_no)
        log_values = tuple(self._processes.values())
        global_log_e = logmeanexp(log_values) if log_values else 0.0
        global_e = e_value_from_log(global_log_e)
        if self._active:
            if global_e < self.config.correction_deactivation_e:
                self._active = False
        elif global_e >= self.config.correction_activation_e:
            self._active = True

        direction_scores: list[float] = []
        for number_index in range(self.config.number_count):
            signed_logs = [
                (log_value, betting_fraction)
                for (_, index, betting_fraction), log_value in self._processes.items()
                if index == number_index
            ]
            if not signed_logs:
                direction_scores.append(0.0)
                continue
            maximum = max(log_value for log_value, _ in signed_logs)
            weights = [math.exp(log_value - maximum) for log_value, _ in signed_logs]
            denominator = sum(weights)
            direction_scores.append(
                sum(
                    weight * (1.0 if betting_fraction > 0 else -1.0)
                    for weight, (_, betting_fraction) in zip(weights, signed_logs, strict=True)
                ) / denominator
            )
        return ChangeEProcessResult(
            draw_no=record.draw_no,
            e_value=global_e,
            log_e_value=global_log_e,
            active=self._active,
            status="ACTIVE" if self._active else "ABSTAIN",
            restart_count=len({key[0] for key in self._processes}),
            direction_scores=tuple(direction_scores),
            trigger=self.config.correction_activation_e,
            deactivation=self.config.correction_deactivation_e,
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
