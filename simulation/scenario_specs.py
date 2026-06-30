"""Preregistered Gate 2-3 scenario definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    family: str
    expected_model: str
    effect_size: float
    target_numbers: tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    change_points: tuple[int, ...] = ()
    active_range: tuple[int, int] | None = None
    target_pair: tuple[int, int] | None = None


FIXED_BIAS_SCENARIOS = tuple(
    ScenarioSpec(
        name=f"fixed_bias_{int(round((lift - 1) * 100))}pct",
        family="fixed_bias",
        expected_model="M1",
        effect_size=lift,
    )
    for lift in (1.02, 1.05, 1.10)
)

PERSISTENCE_SCENARIO = ScenarioSpec(
    name="persistence_recent52",
    family="persistence",
    expected_model="M1",
    effect_size=0.20,
)

REVERSAL_SCENARIO = ScenarioSpec(
    name="reversal_recent52",
    family="reversal",
    expected_model="M2",
    effect_size=0.20,
)

REGIME_SHIFT_SCENARIO = ScenarioSpec(
    name="regime_shift_400_800",
    family="regime_shift",
    expected_model="M3",
    effect_size=1.10,
    change_points=(400, 800),
)

TEMPORARY_ANOMALY_SCENARIO = ScenarioSpec(
    name="temporary_52_draw_bias",
    family="temporary_anomaly",
    expected_model="M3",
    effect_size=1.10,
    active_range=(600, 651),
)

PAIR_SCENARIOS = tuple(
    ScenarioSpec(
        name=f"pair_factor_{str(factor).replace('.', '_')}",
        family="pair_interaction",
        expected_model="PAIR_DIAGNOSTIC",
        effect_size=factor,
        target_pair=(7, 38),
    )
    for factor in (1.25, 1.50, 2.00, 3.00)
)

ALL_POSITIVE_SCENARIOS = (
    *FIXED_BIAS_SCENARIOS,
    PERSISTENCE_SCENARIO,
    REVERSAL_SCENARIO,
    REGIME_SHIFT_SCENARIO,
    TEMPORARY_ANOMALY_SCENARIO,
    *PAIR_SCENARIOS,
)
