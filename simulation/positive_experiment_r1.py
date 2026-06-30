"""Strict planted-signal validation for Gate 2-3R."""

from __future__ import annotations

from statistics import median
from typing import Callable

from engine.config import DEFAULT_CONFIG, EngineConfig
from .calibration import NullCalibration
from .diagnostics import build_origin_snapshots
from .experiment_config import ExperimentConfig
from .probe import ProbeResult, run_blockwise_probe
from .reporting_r1 import model_summary_dict, scenario_summary
from .scenario_generators import generate_scenario_draws
from .scenario_specs import ALL_POSITIVE_SCENARIOS, ScenarioSpec
from .score_calibration import ScoreCalibration, proxy_decision


_PERSISTENT_FAMILIES = {"fixed_bias", "persistence", "reversal"}


def _signal_start(spec: ScenarioSpec, config: EngineConfig) -> int:
    if spec.family == "regime_shift":
        return spec.change_points[0]
    if spec.family == "temporary_anomaly":
        assert spec.active_range is not None
        return spec.active_range[0]
    return config.min_history


def _return_delay(spec: ScenarioSpec, snapshots, calibration: NullCalibration) -> int | None:
    if spec.family != "temporary_anomaly" or spec.active_range is None:
        return None
    end_draw = spec.active_range[1]
    for snapshot in snapshots:
        if snapshot.origin_draw_no > end_draw and calibration.evaluate(snapshot).change_gate == 0.0:
            return snapshot.origin_draw_no - end_draw
    return None


def _strict_model_success(spec: ScenarioSpec, probe: ProbeResult) -> bool:
    expected = spec.expected_model
    if expected not in {"M1", "M2", "M3"}:
        return False
    summary = probe.model_summaries[expected]
    competitor_scores = [
        probe.model_summaries[name].mean_delta_log_loss
        for name in ("M1", "M2", "M3")
        if name != expected
    ]
    if summary.mean_delta_log_loss <= 0:
        return False
    if summary.mean_delta_log_loss <= max(competitor_scores) + 1e-15:
        return False
    if summary.mean_delta_brier < 0:
        return False
    if spec.family in _PERSISTENT_FAMILIES and summary.positive_macro_blocks < 2:
        return False
    if expected == "M3" and probe.m3_significant_origins < 1:
        return False
    return probe.winning_model == expected


def _pair_summary(
    spec: ScenarioSpec,
    *,
    experiment: ExperimentConfig,
    calibration: NullCalibration,
    config: EngineConfig,
    scenario_index: int,
) -> dict[str, object]:
    target_activations = 0
    exploratory_activations = 0
    first_delays: list[int] = []
    for repetition in range(experiment.positive_series_per_scenario):
        seed = experiment.seed_base + 2_000_000 + scenario_index * 100_000 + repetition
        records = generate_scenario_draws(spec, draw_count=experiment.draw_count, seed=seed, config=config)
        snapshots = build_origin_snapshots(records, config=config, target_pair=spec.target_pair or (7, 38))
        target_origins = []
        exploratory_found = False
        for snapshot in snapshots:
            result = calibration.evaluate(snapshot)
            if result.target_pair_tail_probability <= calibration.alpha:
                target_origins.append(snapshot.origin_draw_no)
            if result.exploratory_pair_tail_probability <= calibration.alpha:
                exploratory_found = True
        if target_origins:
            target_activations += 1
            first_delays.append(max(0, target_origins[0] - config.min_history))
        exploratory_activations += int(exploratory_found)

    repetitions = experiment.positive_series_per_scenario
    target_rate = target_activations / repetitions
    return {
        "family": spec.family,
        "expected_model": spec.expected_model,
        "effect_size": spec.effect_size,
        "repetitions": repetitions,
        "matched_model_win_rate": None,
        "matched_model_positive_score_rate": None,
        "strict_detection_rate": target_rate,
        "direction_miss_rate": None,
        "proxy_detection_rate": None,
        "m3_activation_rate": None,
        "exploratory_pair_activation_rate": exploratory_activations / repetitions,
        "target_pair_activation_rate": target_rate,
        "mean_matched_delta_log_loss": None,
        "mean_matched_delta_brier": None,
        "median_detection_delay_draws": median(first_delays) if first_delays else None,
        "median_return_to_zero_gate_draws": None,
    }


def run_positive_experiments(
    experiment: ExperimentConfig,
    calibration: NullCalibration,
    score_calibration: ScoreCalibration,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
    progress: Callable[[str], None] | None = None,
) -> dict[str, object]:
    notify = progress or (lambda message: None)
    results: dict[str, object] = {}

    for scenario_index, spec in enumerate(ALL_POSITIVE_SCENARIOS):
        notify(f"positive control: {spec.name}")
        if spec.family == "pair_interaction":
            results[spec.name] = _pair_summary(
                spec,
                experiment=experiment,
                calibration=calibration,
                config=config,
                scenario_index=scenario_index,
            )
            continue

        probes: list[ProbeResult] = []
        proxy_decisions: list[dict[str, object]] = []
        strict_successes: list[bool] = []
        delays: list[int] = []
        return_delays: list[int] = []
        for repetition in range(experiment.positive_series_per_scenario):
            seed = experiment.seed_base + 2_000_000 + scenario_index * 100_000 + repetition
            records = generate_scenario_draws(spec, draw_count=experiment.draw_count, seed=seed, config=config)
            snapshots = build_origin_snapshots(records, config=config)
            probe = run_blockwise_probe(records, snapshots, calibration, config=config)
            decision = proxy_decision(
                model_summary_dict(probe),
                score_calibration,
                m3_significant_origins=probe.m3_significant_origins,
            )
            probes.append(probe)
            proxy_decisions.append(decision)
            strict_successes.append(_strict_model_success(spec, probe))

            origin = probe.first_positive_origin.get(spec.expected_model)
            if origin is not None:
                delays.append(max(0, origin - _signal_start(spec, config)))
            delay = _return_delay(spec, snapshots, calibration)
            if delay is not None:
                return_delays.append(delay)

        results[spec.name] = scenario_summary(
            spec,
            probes,
            proxy_decisions,
            strict_successes,
            delays,
            return_delays,
        )
    return results


def minimum_detectable_effect(results: dict[str, object]) -> dict[str, float | None]:
    fixed = [
        float(value["effect_size"])
        for name, value in results.items()
        if name.startswith("fixed_bias_") and float(value["strict_detection_rate"] or 0.0) >= 0.80
    ]
    pairs = [
        float(value["effect_size"])
        for name, value in results.items()
        if name.startswith("pair_factor_") and float(value["target_pair_activation_rate"] or 0.0) >= 0.80
    ]
    return {
        "fixed_number_relative_lift_at_80pct_power": min(fixed) if fixed else None,
        "pair_factor_at_80pct_power": min(pairs) if pairs else None,
    }
