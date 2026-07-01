"""Exact low-overhead evaluator for the registered M3 mixture e-process."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.contracts import DrawRecord
from engine.experts.change_eprocess import ChangeEProcessResult


@dataclass
class _Restart:
    start_draw: int
    scales: list[float]
    totals: list[float]
    relatives: list[list[float]]

    @classmethod
    def create(cls, start_draw: int, lambda_count: int, number_count: int) -> "_Restart":
        return cls(
            start_draw,
            [1.0] * lambda_count,
            [float(number_count)] * lambda_count,
            [[1.0] * number_count for _ in range(lambda_count)],
        )


@dataclass
class FastChangeDetector:
    """Same process mean and state transitions as ChangeEProcessDetector.

    A common unselected scale plus per-number relative values replaces the
    dictionary of every restart-number-lambda process.
    """

    config: EngineConfig = DEFAULT_CONFIG
    _restarts: list[_Restart] = field(default_factory=list)
    _active: bool = False
    _trigger_draw_no: int | None = None
    _last_draw_no: int = 0

    def __post_init__(self) -> None:
        p0 = self.config.uniform_number_probability
        selected = tuple(
            1.0 + value * (1.0 - p0)
            for value in self.config.correction_m3_lambda_grid
        )
        unselected = tuple(
            1.0 - value * p0
            for value in self.config.correction_m3_lambda_grid
        )
        self._unselected = unselected
        self._ratios = tuple(
            left / right for left, right in zip(selected, unselected, strict=True)
        )

    def _start(self, draw_no: int) -> None:
        self._restarts.append(
            _Restart.create(
                draw_no,
                len(self.config.correction_m3_lambda_grid),
                self.config.number_count,
            )
        )

    def update(self, record: DrawRecord) -> ChangeEProcessResult:
        if record.draw_no <= self._last_draw_no:
            raise ValueError("change e-process records must be strictly increasing")
        if (
            not self._restarts
            or (record.draw_no - 1) % self.config.correction_m3_restart_interval == 0
        ):
            self._start(record.draw_no)

        selected_indexes = tuple(number - 1 for number in record.numbers)
        for restart in self._restarts:
            for slot, base_factor in enumerate(self._unselected):
                restart.scales[slot] *= base_factor
                relative = restart.relatives[slot]
                total = restart.totals[slot]
                ratio = self._ratios[slot]
                for number_index in selected_indexes:
                    previous = relative[number_index]
                    current = previous * ratio
                    relative[number_index] = current
                    total += current - previous
                restart.totals[slot] = total

        self._last_draw_no = record.draw_no
        self._restarts = [
            restart
            for restart in self._restarts
            if record.draw_no - restart.start_draw < self.config.correction_change_max_life
        ]
        if len(self._restarts) > self.config.correction_m3_max_restarts:
            self._restarts = self._restarts[-self.config.correction_m3_max_restarts :]

        process_sum = sum(
            scale * total
            for restart in self._restarts
            for scale, total in zip(restart.scales, restart.totals, strict=True)
        )
        process_count = (
            len(self._restarts)
            * self.config.number_count
            * len(self.config.correction_m3_lambda_grid)
        )
        e_value = process_sum / process_count if process_count else 1.0
        log_e_value = math.log(e_value) if e_value > 0.0 else float("-inf")
        expired = False

        if self._active:
            age = record.draw_no - (self._trigger_draw_no or record.draw_no)
            if e_value < self.config.correction_deactivation_e:
                self._active = False
                self._trigger_draw_no = None
            elif age >= self.config.correction_change_max_life:
                self._active = False
                self._trigger_draw_no = None
                self._restarts.clear()
                expired = True
        elif e_value >= self.config.correction_activation_e:
            self._active = True
            self._trigger_draw_no = record.draw_no

        active_age = (
            record.draw_no - self._trigger_draw_no
            if self._active and self._trigger_draw_no is not None
            else 0
        )
        return ChangeEProcessResult(
            draw_no=record.draw_no,
            e_value=e_value,
            log_e_value=log_e_value,
            active=self._active,
            status="EXPIRED" if expired else ("ACTIVE" if self._active else "ABSTAIN"),
            restart_count=len(self._restarts),
            direction_scores=tuple(0.0 for _ in range(self.config.number_count)),
            trigger=self.config.correction_activation_e,
            deactivation=self.config.correction_deactivation_e,
            trigger_draw_no=self._trigger_draw_no,
            active_age=active_age,
            expired=expired,
        )
