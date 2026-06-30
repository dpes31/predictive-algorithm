"""Revised null calibration for Gate 2-3R."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from engine.config import DEFAULT_CONFIG, EngineConfig
from .calibration import NullCalibration
from .diagnostics import build_origin_snapshots
from .experiment_config import ExperimentConfig
from .probe import run_blockwise_probe
from .reporting_r1 import model_summary_dict, rate_summary
from .score_calibration import ScoreCalibration, proxy_decision
from .uniform_lottery import generate_uniform_draws


@dataclass(frozen=True)
class NullExperimentResult:
    calibration: NullCalibration
    score_calibration: ScoreCalibration
    validation_report: dict[str, object]


def run_null_experiment(
    experiment: ExperimentConfig,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
    progress: Callable[[str], None] | None = None,
) -> NullExperimentResult:
    notify = progress or (lambda message: None)
    maxima_shift_52: list[float] = []
    maxima_shift_104: list[float] = []
    minima_entropy_52: list[float] = []
    maxima_cusum: list[float] = []
    maxima_all_pair: list[float] = []
    maxima_planted_pair: list[float] = []

    notify("null diagnostic calibration")
    for index in range(experiment.null_calibration_series):
        records = generate_uniform_draws(experiment.draw_count, seed=experiment.seed_base + index)
        snapshots = build_origin_snapshots(records, config=config)
        maxima_shift_52.append(max(x.diagnostics["raw_max_abs_shift_52"] for x in snapshots))
        maxima_shift_104.append(max(x.diagnostics["raw_max_abs_shift_104"] for x in snapshots))
        minima_entropy_52.append(min(x.diagnostics["entropy_52"] for x in snapshots))
        maxima_cusum.append(max(x.diagnostics["raw_max_abs_cusum"] for x in snapshots))
        maxima_all_pair.append(max(x.diagnostics["max_abs_pair_104"] for x in snapshots))
        maxima_planted_pair.append(max(x.diagnostics["target_pair_z_104"] for x in snapshots))

    calibration = NullCalibration(
        calibration_series=experiment.null_calibration_series,
        maxima_raw_shift_52=tuple(sorted(maxima_shift_52)),
        maxima_raw_shift_104=tuple(sorted(maxima_shift_104)),
        minima_entropy_52=tuple(sorted(minima_entropy_52)),
        maxima_raw_cusum=tuple(sorted(maxima_cusum)),
        maxima_pair_104=tuple(sorted(maxima_all_pair)),
        maxima_target_pair_104=tuple(sorted(maxima_planted_pair)),
        alpha=experiment.alpha,
    )

    notify("null score calibration")
    score_inputs = []
    for index in range(experiment.null_calibration_series):
        records = generate_uniform_draws(experiment.draw_count, seed=experiment.seed_base + index)
        snapshots = build_origin_snapshots(records, config=config)
        probe = run_blockwise_probe(records, snapshots, calibration, config=config)
        score_inputs.append(model_summary_dict(probe))
    score_calibration = ScoreCalibration.fit(score_inputs, alpha=experiment.alpha)

    notify("independent null validation")
    counts = {"proxy": 0, "m3": 0, "all_pair": 0, "planted_pair": 0}
    for index in range(experiment.null_validation_series):
        records = generate_uniform_draws(experiment.draw_count, seed=experiment.seed_base + 1_000_000 + index)
        snapshots = build_origin_snapshots(records, config=config)
        probe = run_blockwise_probe(records, snapshots, calibration, config=config)
        decision = proxy_decision(model_summary_dict(probe), score_calibration, m3_significant_origins=probe.m3_significant_origins)
        counts["proxy"] += int(bool(decision["decision"]))
        counts["m3"] += int(probe.m3_significant_origins > 0)
        counts["all_pair"] += int(probe.exploratory_pair_significant_origins > 0)
        counts["planted_pair"] += int(probe.target_pair_significant_origins > 0)

    trials = experiment.null_validation_series
    exploratory = rate_summary(counts["all_pair"], trials)
    report = {
        "proxy_false_activation": rate_summary(counts["proxy"], trials),
        "m3_diagnostic_false_activation": rate_summary(counts["m3"], trials),
        "exploratory_pair_false_activation": exploratory,
        "pair_diagnostic_false_activation": exploratory,
        "target_pair_false_activation": rate_summary(counts["planted_pair"], trials),
    }
    return NullExperimentResult(calibration, score_calibration, report)
