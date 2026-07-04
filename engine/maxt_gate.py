"""Single-test maxT calibration for the M3 structural-change gate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .config import DEFAULT_CONFIG, EngineConfig


@dataclass(frozen=True)
class MaxTResult:
    observed_max_t: float
    empirical_p_value: float
    active: bool
    calibrated_series: int
    full_contract_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "observed_max_t": self.observed_max_t,
            "empirical_p_value": self.empirical_p_value,
            "active": self.active,
            "calibrated_series": self.calibrated_series,
            "full_contract_ready": self.full_contract_ready,
        }


@dataclass(frozen=True)
class MaxTCalibration:
    null_maxima: tuple[float, ...]
    alpha: float = 0.001
    minimum_series: int = 10_000

    def __post_init__(self) -> None:
        if not self.null_maxima:
            raise ValueError("maxT calibration requires at least one null series")
        if any(value < 0 for value in self.null_maxima):
            raise ValueError("maxT null maxima must be non-negative")
        if tuple(sorted(self.null_maxima)) != self.null_maxima:
            raise ValueError("maxT null maxima must be sorted")
        if not 0.0 < self.alpha < 1.0:
            raise ValueError("alpha must be in (0, 1)")
        if self.minimum_series < 1:
            raise ValueError("minimum_series must be positive")

    @staticmethod
    def statistic(values: Mapping[str, float]) -> float:
        if not values:
            raise ValueError("maxT statistic requires at least one diagnostic")
        return max(abs(float(value)) for value in values.values())

    @classmethod
    def fit(
        cls,
        null_series: Sequence[Sequence[Mapping[str, float]]],
        *,
        config: EngineConfig = DEFAULT_CONFIG,
        require_full_contract: bool = False,
    ) -> "MaxTCalibration":
        maxima: list[float] = []
        for series in null_series:
            if not series:
                raise ValueError("every null series must contain at least one forecast origin")
            maxima.append(max(cls.statistic(origin) for origin in series))
        calibration = cls(
            null_maxima=tuple(sorted(maxima)),
            alpha=config.maxt_alpha,
            minimum_series=config.maxt_min_calibration_series,
        )
        if require_full_contract and not calibration.full_contract_ready:
            raise ValueError(
                f"maxT full contract requires at least {calibration.minimum_series} null series"
            )
        return calibration

    @property
    def full_contract_ready(self) -> bool:
        return len(self.null_maxima) >= self.minimum_series

    def empirical_p_value(self, observed_max_t: float) -> float:
        exceedances = sum(value >= observed_max_t for value in self.null_maxima)
        return (1.0 + exceedances) / (len(self.null_maxima) + 1.0)

    def evaluate(
        self,
        observed_diagnostics: Mapping[str, float],
        *,
        require_full_contract: bool = True,
    ) -> MaxTResult:
        if require_full_contract and not self.full_contract_ready:
            raise ValueError(
                f"maxT calibration has {len(self.null_maxima)} series; "
                f"{self.minimum_series} required"
            )
        observed = self.statistic(observed_diagnostics)
        p_value = self.empirical_p_value(observed)
        return MaxTResult(
            observed_max_t=observed,
            empirical_p_value=p_value,
            active=self.full_contract_ready and p_value <= self.alpha,
            calibrated_series=len(self.null_maxima),
            full_contract_ready=self.full_contract_ready,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "calibrated_series": len(self.null_maxima),
            "alpha": self.alpha,
            "minimum_series": self.minimum_series,
            "full_contract_ready": self.full_contract_ready,
            "minimum_empirical_p": 1.0 / (len(self.null_maxima) + 1.0),
            "multiple_testing": "single_familywise_maxT_no_additional_Holm",
        }
