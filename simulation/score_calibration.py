"""Score calibration for synthetic validation."""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ScoreCalibration:
    calibration_series: int
    sorted_scores: tuple[float, ...]
    alpha: float = 0.001

    @classmethod
    def fit(
        cls,
        summaries: Sequence[Mapping[str, Mapping[str, float | int]]],
        *,
        alpha: float = 0.001,
    ) -> "ScoreCalibration":
        scores = [
            max(float(summary[name]["mean_delta_log_loss"]) for name in ("M1", "M2", "M3", "SHADOW"))
            for summary in summaries
        ]
        if not scores:
            raise ValueError("at least one summary is required")
        return cls(len(scores), tuple(sorted(scores)), alpha)

    def tail_probability(self, observed: float) -> float:
        index = bisect.bisect_left(self.sorted_scores, observed)
        return (len(self.sorted_scores) - index + 1.0) / (len(self.sorted_scores) + 1.0)

    def threshold(self) -> float:
        index = min(
            len(self.sorted_scores) - 1,
            max(0, math.ceil((1.0 - self.alpha) * len(self.sorted_scores)) - 1),
        )
        return self.sorted_scores[index]


def proxy_decision(
    summaries: Mapping[str, Mapping[str, float | int]],
    calibration: ScoreCalibration,
    *,
    m3_significant_origins: int,
) -> dict[str, object]:
    winner = max(
        ("M1", "M2", "M3", "SHADOW"),
        key=lambda name: float(summaries[name]["mean_delta_log_loss"]),
    )
    summary = summaries[winner]
    score = float(summary["mean_delta_log_loss"])
    tail = calibration.tail_probability(score)
    structural_ok = winner != "M3" or m3_significant_origins > 0
    decision = (
        score > 0
        and tail <= calibration.alpha
        and float(summary["mean_delta_brier"]) >= 0
        and int(summary["positive_macro_blocks"]) >= 2
        and structural_ok
    )
    return {
        "decision": decision,
        "winning_model": winner,
        "mean_delta_log_loss": score,
        "tail_probability": tail,
        "brier_not_worse": float(summary["mean_delta_brier"]) >= 0,
        "supporting_macro_blocks": int(summary["positive_macro_blocks"]),
        "structural_requirement": structural_ok,
    }
