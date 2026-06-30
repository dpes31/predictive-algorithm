"""Report helpers for synthetic validation."""

from __future__ import annotations

from statistics import fmean, median
from typing import Mapping, Sequence

from .calibration import one_sided_binomial_upper
from .probe import ProbeResult
from .scenario_specs import ScenarioSpec


def model_summary_dict(probe: ProbeResult) -> dict[str, dict[str, float | int]]:
    return {
        name: {
            "mean_delta_log_loss": summary.mean_delta_log_loss,
            "mean_delta_brier": summary.mean_delta_brier,
            "positive_macro_blocks": summary.positive_macro_blocks,
        }
        for name, summary in probe.model_summaries.items()
    }


def rate_summary(events: int, trials: int) -> dict[str, float | int | bool]:
    rate = events / trials if trials else 0.0
    upper = one_sided_binomial_upper(events, trials) if trials else 1.0
    return {
        "events": events,
        "trials": trials,
        "rate": rate,
        "one_sided_95_upper": upper,
        "point_estimate_le_0_001": rate <= 0.001,
        "upper_bound_le_0_001": upper <= 0.001,
    }


def scenario_summary(
    spec: ScenarioSpec,
    probes: Sequence[ProbeResult],
    decisions: Sequence[Mapping[str, object]],
    delays: Sequence[int],
    return_delays: Sequence[int],
) -> dict[str, object]:
    repetitions = len(probes)
    expected = spec.expected_model
    is_model = expected in {"M1", "M2", "M3"}
    wins = sum(probe.winning_model == expected for probe in probes) if is_model else 0
    positive_scores = (
        sum(probe.model_summaries[expected].mean_delta_log_loss > 0 for probe in probes)
        if is_model
        else 0
    )
    decisions_count = sum(bool(item["decision"]) for item in decisions)
    m3_count = sum(probe.m3_significant_origins > 0 for probe in probes)
    pair_count = sum(probe.target_pair_significant_origins > 0 for probe in probes)
    mean_ll = fmean(probe.model_summaries[expected].mean_delta_log_loss for probe in probes) if is_model else None
    mean_brier = fmean(probe.model_summaries[expected].mean_delta_brier for probe in probes) if is_model else None
    return {
        "family": spec.family,
        "expected_model": expected,
        "effect_size": spec.effect_size,
        "repetitions": repetitions,
        "matched_model_win_rate": wins / repetitions if repetitions else None,
        "matched_model_positive_score_rate": positive_scores / repetitions if repetitions else None,
        "direction_miss_rate": (repetitions - wins) / repetitions if repetitions and is_model else None,
        "proxy_detection_rate": decisions_count / repetitions if repetitions else None,
        "m3_activation_rate": m3_count / repetitions if repetitions else None,
        "pair_activation_rate": pair_count / repetitions if repetitions else None,
        "mean_matched_delta_log_loss": mean_ll,
        "mean_matched_delta_brier": mean_brier,
        "median_detection_delay_draws": median(delays) if delays else None,
        "median_return_to_zero_gate_draws": median(return_delays) if return_delays else None,
    }
