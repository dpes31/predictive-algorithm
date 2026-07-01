"""Gate 2-3P-R3 DEV-only grid evaluation utilities.

The first evaluation is deliberately constraint-first. The frozen R1 contract
requires the P4 regime-reversal path to activate M3 and then satisfy the
lift-1.25 direction constraint. M3 detector parameters are fixed and independent
of the 27 M4 hyperparameter combinations. Therefore, if no registered k_m3 value
can become eligible on the P4 DEV cell, every combined configuration is
ineligible and the M4 grid must not be searched merely to select a cosmetic
winner.

CAL and SEALED namespaces are rejected by construction.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, replace
from statistics import fmean
from typing import Any, Mapping, Sequence

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.contracts import DrawRecord
from engine.distributions import FixedSizeDistribution
from engine.experts.change_eprocess import ChangeEProcessDetector, ChangeEProcessResult
from engine.experts.post_change import build_post_change_model
from simulation.physical_validation import ScenarioSpec, generate_fast_series

DEV_NAMESPACE = "DEV"
M4_GRID = tuple(
    (k_global, k_context, effect_clip)
    for k_global in (260.0, 520.0, 1040.0)
    for k_context in (90.0, 260.0, 520.0)
    for effect_clip in (0.10, 0.20, 0.35)
)
M3_GRID = (90.0, 260.0, 520.0)
P4_LIFT_125 = ScenarioSpec("p4_regime_reversal", "regime_reversal", lift=1.25)


def development_seed(
    category: str,
    scenario: str,
    effect: float,
    replicate: int,
    *,
    namespace: str = DEV_NAMESPACE,
) -> int:
    if namespace != DEV_NAMESPACE:
        raise ValueError("Gate 2-3P-R3 accepts DEV namespace only")
    material = (
        f"Gate2-3P-R3|{DEFAULT_CONFIG.model_version}|{namespace}|"
        f"{category}|{scenario}|{effect:.8f}|{replicate}"
    )
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _record(draw_no: int, numbers: Sequence[int]) -> DrawRecord:
    return DrawRecord(
        draw_no=draw_no,
        draw_date=f"2026-01-{((draw_no - 1) % 28) + 1:02d}",
        numbers=tuple(numbers),
        verification_status="synthetic",
        source="gate2-r3-dev",
    )


def _brier(marginals: Mapping[int, float], numbers: Sequence[int]) -> float:
    selected = set(numbers)
    return sum(
        (marginals[number] - (1.0 if number in selected else 0.0)) ** 2
        for number in range(1, 46)
    ) / 45.0


def _direction_hit(
    marginals: Mapping[int, float],
    favored: Sequence[int],
) -> bool:
    favored_set = set(favored)
    if not favored_set or len(favored_set) >= 45:
        return False
    favored_mean = fmean(marginals[number] for number in favored_set)
    other_mean = fmean(
        marginals[number]
        for number in range(1, 46)
        if number not in favored_set
    )
    return favored_mean > other_mean


@dataclass(frozen=True)
class M3SeriesResult:
    seed: int
    activated: bool
    first_trigger_draw: int | None
    max_e_value: float
    direction_hits: Mapping[str, int]
    direction_trials: Mapping[str, int]
    delta_log_loss: Mapping[str, float]
    delta_brier: Mapping[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_m3_series(
    *,
    seed: int,
    draw_count: int = 1230,
    config: EngineConfig = DEFAULT_CONFIG,
) -> M3SeriesResult:
    fast_series = generate_fast_series(P4_LIFT_125, draw_count=draw_count, seed=seed)
    records = tuple(
        _record(draw_no, draw.numbers)
        for draw_no, draw in enumerate(fast_series, start=1)
    )
    detector = ChangeEProcessDetector(config)
    origin_set = set(range(config.min_history, draw_count, 52))
    origin_results: dict[int, ChangeEProcessResult] = {}
    first_trigger: int | None = None
    max_e_value = 1.0

    for record in records:
        result = detector.update(record)
        max_e_value = max(max_e_value, result.e_value)
        if result.active and first_trigger is None:
            first_trigger = result.trigger_draw_no
        if record.draw_no in origin_set:
            origin_results[record.draw_no] = result

    uniform = FixedSizeDistribution(tuple(0.0 for _ in range(45)), 6)
    uniform_log_probability = -math.log(math.comb(45, 6))
    uniform_marginals = uniform.marginal_probabilities()
    direction_hits = {str(int(value)): 0 for value in M3_GRID}
    direction_trials = {str(int(value)): 0 for value in M3_GRID}
    log_loss_values = {str(int(value)): [] for value in M3_GRID}
    brier_values = {str(int(value)): [] for value in M3_GRID}

    for origin in sorted(origin_results):
        result = origin_results[origin]
        if not result.active:
            continue
        block_end = min(draw_count, origin + 52)
        for k_m3 in M3_GRID:
            key = str(int(k_m3))
            candidate_config = replace(config, correction_k_m3=k_m3)
            model = build_post_change_model(records[:origin], result, candidate_config)
            if not model.diagnostics.active:
                continue
            marginals = model.distribution.marginal_probabilities()
            for target_index in range(origin, block_end):
                target = fast_series[target_index]
                target_record = records[target_index]
                log_loss_values[key].append(
                    model.distribution.joint_log_probability(target_record.numbers)
                    - uniform_log_probability
                )
                brier_values[key].append(
                    _brier(uniform_marginals, target_record.numbers)
                    - _brier(marginals, target_record.numbers)
                )
                if target.signal_active and target.favored:
                    direction_trials[key] += 1
                    direction_hits[key] += int(_direction_hit(marginals, target.favored))

    return M3SeriesResult(
        seed=seed,
        activated=first_trigger is not None,
        first_trigger_draw=first_trigger,
        max_e_value=max_e_value,
        direction_hits=direction_hits,
        direction_trials=direction_trials,
        delta_log_loss={
            key: fmean(values) if values else 0.0
            for key, values in log_loss_values.items()
        },
        delta_brier={
            key: fmean(values) if values else 0.0
            for key, values in brier_values.items()
        },
    )


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(probability * len(ordered)) - 1))
    return ordered[index]


def run_m3_preflight(
    *,
    replicates: int = 200,
    draw_count: int = 1230,
) -> dict[str, Any]:
    if replicates < 1:
        raise ValueError("replicates must be positive")
    rows = []
    for replicate in range(replicates):
        seed = development_seed(
            "positive_control",
            P4_LIFT_125.name,
            P4_LIFT_125.lift,
            replicate,
        )
        rows.append(evaluate_m3_series(seed=seed, draw_count=draw_count))

    activated_count = sum(row.activated for row in rows)
    max_values = [row.max_e_value for row in rows]
    m3_configs: list[dict[str, Any]] = []
    eligible_k_m3: list[float] = []
    for k_m3 in M3_GRID:
        key = str(int(k_m3))
        hits = sum(row.direction_hits[key] for row in rows)
        trials = sum(row.direction_trials[key] for row in rows)
        direction_accuracy = hits / trials if trials else None
        ll_values = [row.delta_log_loss[key] for row in rows if row.direction_trials[key] > 0]
        brier_values = [row.delta_brier[key] for row in rows if row.direction_trials[key] > 0]
        eligible = (
            trials > 0
            and direction_accuracy is not None
            and direction_accuracy >= 0.80
            and fmean(ll_values) > 0.0
            and fmean(brier_values) >= 0.0
        )
        if eligible:
            eligible_k_m3.append(k_m3)
        m3_configs.append(
            {
                "k_m3": k_m3,
                "direction_hits": hits,
                "direction_trials": trials,
                "direction_accuracy": direction_accuracy,
                "mean_delta_log_loss": fmean(ll_values) if ll_values else 0.0,
                "mean_delta_brier": fmean(brier_values) if brier_values else 0.0,
                "eligible": eligible,
            }
        )

    combined_grid_count = len(M4_GRID) * len(M3_GRID)
    if eligible_k_m3:
        preflight_status = "M3_ELIGIBLE_CONTINUE_M4_GRID"
        pruned_combinations = combined_grid_count - len(M4_GRID) * len(eligible_k_m3)
    else:
        preflight_status = "NO_ELIGIBLE_CONFIG"
        pruned_combinations = combined_grid_count

    payload: dict[str, Any] = {
        "gate": "Gate 2-3P-R3",
        "namespace": DEV_NAMESPACE,
        "model_version": DEFAULT_CONFIG.model_version,
        "feature_contract_version": DEFAULT_CONFIG.feature_contract_version,
        "scenario": P4_LIFT_125.name,
        "effect_size": P4_LIFT_125.lift,
        "replicates": replicates,
        "draw_count": draw_count,
        "activation_threshold": DEFAULT_CONFIG.correction_activation_e,
        "activated_series": activated_count,
        "activation_rate": activated_count / replicates,
        "max_e_value": max(max_values),
        "max_e_q50": _quantile(max_values, 0.50),
        "max_e_q95": _quantile(max_values, 0.95),
        "max_e_q99": _quantile(max_values, 0.99),
        "m3_configs": m3_configs,
        "registered_m4_grid_count": len(M4_GRID),
        "registered_m3_grid_count": len(M3_GRID),
        "combined_grid_count": combined_grid_count,
        "pruned_combined_configurations": pruned_combinations,
        "eligible_k_m3": eligible_k_m3,
        "status": preflight_status,
        "selected_config": None,
        "calibration_executed": False,
        "sealed_validation_executed": False,
        "research_only": True,
        "public_release_allowed": False,
        "rows": [row.to_dict() for row in rows],
    }
    payload["report_hash"] = hashlib.sha256(
        repr({key: value for key, value in payload.items() if key != "report_hash"}).encode("utf-8")
    ).hexdigest()
    return payload
