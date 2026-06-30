"""Report helpers for synthetic validation."""

from __future__ import annotations

from .calibration import one_sided_binomial_upper
from .probe import ProbeResult


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
