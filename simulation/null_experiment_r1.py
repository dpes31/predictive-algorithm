"""Revised null calibration for Gate 2-3R."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from engine.config import DEFAULT_CONFIG, EngineConfig
from .calibration import NullCalibration
from .diagnostics import build_origin_snapshots
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


def run_null_experiment(
    experiment: ExperimentConfig,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
    progress: Callable[[str], None] | None = None,
) -> NullExperimentResult:
    notify = progress or (lambda message: None)
    calibration_sets = []
    notify("null diagnostic calibration")
    for index in range(experiment.null_calibration_series):
        records = generate_uniform_draws(experiment.draw_count, seed=experiment.seed_base + index)
        calibration_sets.append(build_origin_snapshots(records, config=config))
    calibration = NullCalibration.fit(calibration_sets, alpha=experiment.alpha)

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
    report = {
        "proxy_false_activation": rate_summary(counts["proxy"], trials),
        "m3_diagnostic_false_activation": rate_summary(counts["m3"], trials),
        "exploratory_pair_false_activation": rate_summary(counts["all_pair"], trials),
        "target_pair_false_activation": rate_summary(counts["planted_pair"], trials),
    }
    return NullExperimentResult(calibration, score_calibration, report)
