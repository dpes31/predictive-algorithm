"""Uniform null calibration and independent validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from engine.config import DEFAULT_CONFIG, EngineConfig
from .calibration import NullCalibration
from .diagnostics import OriginSnapshot, build_origin_snapshots
from .experiment_config import ExperimentConfig
from .probe import run_blockwise_probe
from .reporting import model_summary_dict, rate_summary
from .score_calibration import ScoreCalibration, proxy_decision
from .uniform_lottery import generate_uniform_draws


@dataclass(frozen=True)
class NullExperimentResult:
    calibration: NullCalibration
    score_calibration: ScoreCalibration
    validation_report: dict[str, object]


def _extrema(snapshots: list[OriginSnapshot]) -> dict[str, float]:
    return {
        "max_abs_shift_52": max(item.diagnostics["max_abs_shift_52"] for item in snapshots),
        "max_abs_shift_104": max(item.diagnostics["max_abs_shift_104"] for item in snapshots),
        "min_entropy_52": min(item.diagnostics["entropy_52"] for item in snapshots),
        "max_abs_cusum": max(item.diagnostics["max_abs_cusum"] for item in snapshots),
        "max_abs_pair_104": max(item.diagnostics["max_abs_pair_104"] for item in snapshots),
    }


def _build_calibration(extrema: list[dict[str, float]], alpha: float) -> NullCalibration:
    return NullCalibration(
        calibration_series=len(extrema),
        maxima_shift_52=tuple(sorted(item["max_abs_shift_52"] for item in extrema)),
        maxima_shift_104=tuple(sorted(item["max_abs_shift_104"] for item in extrema)),
        minima_entropy_52=tuple(sorted(item["min_entropy_52"] for item in extrema)),
        maxima_cusum=tuple(sorted(item["max_abs_cusum"] for item in extrema)),
        maxima_pair_104=tuple(sorted(item["max_abs_pair_104"] for item in extrema)),
        alpha=alpha,
    )


def run_null_experiment(
    experiment: ExperimentConfig,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
    progress: Callable[[str], None] | None = None,
) -> NullExperimentResult:
    notify = progress or (lambda message: None)
    extrema: list[dict[str, float]] = []
    notify("null diagnostic calibration")
    for index in range(experiment.null_calibration_series):
        records = generate_uniform_draws(experiment.draw_count, seed=experiment.seed_base + index)
        extrema.append(_extrema(build_origin_snapshots(records, config=config)))
    calibration = _build_calibration(extrema, experiment.alpha)

    notify("null score calibration")
    score_inputs: list[dict[str, dict[str, float | int]]] = []
    for index in range(experiment.null_calibration_series):
        records = generate_uniform_draws(experiment.draw_count, seed=experiment.seed_base + index)
        snapshots = build_origin_snapshots(records, config=config)
        probe = run_blockwise_probe(records, snapshots, calibration, config=config)
        score_inputs.append(model_summary_dict(probe))
    score_calibration = ScoreCalibration.fit(score_inputs, alpha=experiment.alpha)

    notify("independent null validation")
    proxy_events = 0
    m3_events = 0
    pair_events = 0
    for index in range(experiment.null_validation_series):
        records = generate_uniform_draws(
            experiment.draw_count,
            seed=experiment.seed_base + 1_000_000 + index,
        )
        snapshots = build_origin_snapshots(records, config=config)
        probe = run_blockwise_probe(records, snapshots, calibration, config=config)
        decision = proxy_decision(
            model_summary_dict(probe),
            score_calibration,
            m3_significant_origins=probe.m3_significant_origins,
        )
        proxy_events += int(bool(decision["decision"]))
        m3_events += int(probe.m3_significant_origins > 0)
        pair_events += int(probe.target_pair_significant_origins > 0)

    report = {
        "proxy_false_activation": rate_summary(proxy_events, experiment.null_validation_series),
        "m3_diagnostic_false_activation": rate_summary(m3_events, experiment.null_validation_series),
        "pair_diagnostic_false_activation": rate_summary(pair_events, experiment.null_validation_series),
    }
    return NullExperimentResult(calibration, score_calibration, report)
