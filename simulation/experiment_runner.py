"""Top-level Gate 2-3 synthetic experiment runner."""

from __future__ import annotations

from typing import Callable

from engine.config import DEFAULT_CONFIG, EngineConfig
from engine.hashing import sha256_value
from .experiment_config import ExperimentConfig
from .null_experiment import run_null_experiment
from .positive_experiment import minimum_detectable_effect, run_positive_experiments


def run_gate2_3_experiment(
    experiment: ExperimentConfig,
    *,
    config: EngineConfig = DEFAULT_CONFIG,
    progress: Callable[[str], None] | None = None,
) -> dict[str, object]:
    experiment.validate()
    null_result = run_null_experiment(experiment, config=config, progress=progress)
    positive_results = run_positive_experiments(
        experiment,
        null_result.calibration,
        null_result.score_calibration,
        config=config,
        progress=progress,
    )
    payload: dict[str, object] = {
        "experiment": experiment.to_dict(),
        "model_version": config.model_version,
        "feature_contract_version": config.feature_contract_version,
        "research_only": True,
        "public_release_allowed": False,
        "null_calibration": null_result.calibration.to_dict(),
        "score_calibration": {
            "calibration_series": null_result.score_calibration.calibration_series,
            "alpha": null_result.score_calibration.alpha,
            "familywise_score_threshold": null_result.score_calibration.threshold(),
        },
        "null_validation": null_result.validation_report,
        "positive_controls": positive_results,
        "minimum_detectable_effect": minimum_detectable_effect(positive_results),
        "interpretation_limits": [
            "Synthetic detectability does not establish real lottery predictability.",
            "One thousand validation series can estimate a 0.1 percent event rate but cannot prove a 0.1 percent upper confidence bound when zero events are observed.",
            "Historical real-data walk-forward remains reserved for Gate 2-4.",
        ],
    }
    payload["report_hash"] = sha256_value(payload)
    return payload
