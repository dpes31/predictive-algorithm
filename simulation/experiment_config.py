"""Configuration contract for Gate 2-3 experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    draw_count: int = 1230
    null_calibration_series: int = 1000
    null_validation_series: int = 1000
    positive_series_per_scenario: int = 100
    seed_base: int = 20260630
    alpha: float = 0.001

    def validate(self) -> None:
        if self.draw_count < 300:
            raise ValueError("draw_count must be at least 300")
        if self.null_calibration_series < 1:
            raise ValueError("null_calibration_series must be positive")
        if self.null_validation_series < 1:
            raise ValueError("null_validation_series must be positive")
        if self.positive_series_per_scenario < 1:
            raise ValueError("positive_series_per_scenario must be positive")
        if not 0 < self.alpha < 1:
            raise ValueError("alpha must be between zero and one")

    def to_dict(self) -> dict[str, int | float]:
        return {
            "draw_count": self.draw_count,
            "null_calibration_series": self.null_calibration_series,
            "null_validation_series": self.null_validation_series,
            "positive_series_per_scenario": self.positive_series_per_scenario,
            "seed_base": self.seed_base,
            "alpha": self.alpha,
        }
