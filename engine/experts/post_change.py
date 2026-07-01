"""Post-change M3 prediction expert required by the 4.0 correction contract."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord
from ..distributions import FixedSizeDistribution
from .change_eprocess import ChangeEProcessResult


def _uniform(config: EngineConfig) -> FixedSizeDistribution:
    return FixedSizeDistribution(tuple(0.0 for _ in range(config.number_count)), config.pick_count)


def _logit(probability: float) -> float:
    clipped = min(1.0 - 1e-12, max(1e-12, probability))
    return math.log(clipped / (1.0 - clipped))


def _center_clip(values: Sequence[float], limit: float) -> tuple[float, ...]:
    if not values:
        return ()
    center = sum(values) / len(values)
    return tuple(max(-limit, min(limit, value - center)) for value in values)


@dataclass(frozen=True)
class PostChangeDiagnostics:
    active: bool
    trigger_draw_no: int | None
    support: int
    prior_concentration: float
    effect_clip: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "trigger_draw_no": self.trigger_draw_no,
            "support": self.support,
            "prior_concentration": self.prior_concentration,
            "effect_clip": self.effect_clip,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class PostChangeModel:
    distribution: FixedSizeDistribution
    diagnostics: PostChangeDiagnostics


def build_post_change_model(
    records: Sequence[DrawRecord],
    change_result: ChangeEProcessResult | None,
    config: EngineConfig = DEFAULT_CONFIG,
) -> PostChangeModel:
    """Return the shrunk post-trigger M3 distribution, or exact M0 when ineligible."""
    reasons: list[str] = []
    trigger = None if change_result is None else change_result.trigger_draw_no
    if change_result is None:
        reasons.append("change_result_not_provided")
    elif not change_result.active:
        reasons.append("change_detector_inactive")
    elif trigger is None:
        reasons.append("trigger_draw_not_recorded")

    if reasons:
        return PostChangeModel(
            _uniform(config),
            PostChangeDiagnostics(
                False,
                trigger,
                0,
                config.correction_k_m3,
                config.correction_m3_effect_clip,
                tuple(reasons),
            ),
        )

    post_change = tuple(record for record in records if record.draw_no >= int(trigger))
    support = len(post_change)
    if support < config.correction_m3_min_support:
        return PostChangeModel(
            _uniform(config),
            PostChangeDiagnostics(
                False,
                trigger,
                support,
                config.correction_k_m3,
                config.correction_m3_effect_clip,
                ("insufficient_post_change_support",),
            ),
        )

    counts = [0] * config.number_count
    for record in post_change:
        for number in record.numbers:
            counts[number - 1] += 1

    p0 = config.uniform_number_probability
    prior = config.correction_k_m3
    baseline = _logit(p0)
    logits = _center_clip(
        [
            _logit((prior * p0 + counts[index]) / (prior + support)) - baseline
            for index in range(config.number_count)
        ],
        config.correction_m3_effect_clip,
    )
    return PostChangeModel(
        FixedSizeDistribution(logits, config.pick_count),
        PostChangeDiagnostics(
            True,
            trigger,
            support,
            prior,
            config.correction_m3_effect_clip,
            (),
        ),
    )
