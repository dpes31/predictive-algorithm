"""Abstention and hysteresis state for M4 correction engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AbstentionStatus(str, Enum):
    INVALID_METADATA = "INVALID_METADATA"
    ABSTAIN = "ABSTAIN"
    SHADOW_ACTIVE = "SHADOW_ACTIVE"
    CANDIDATE_ELIGIBLE = "CANDIDATE_ELIGIBLE"
    FORCED_RETURN = "FORCED_RETURN"


@dataclass(frozen=True)
class AbstentionInput:
    evidence: float
    invalid_metadata: bool = False
    latest_block_delta_log_loss: float | None = None
    latest_block_delta_brier: float | None = None
    prior_active: bool = False
    forced_return_remaining: int = 0
    research_only: bool = True


@dataclass(frozen=True)
class AbstentionDecision:
    status: AbstentionStatus
    active_for_shadow: bool
    deployable_weight: float
    forced_return_remaining: int
    reasons: tuple[str, ...]


def decide_abstention(
    value: AbstentionInput,
    *,
    activation: float = 1000.0,
    deactivation: float = 100.0,
    hard_return_draws: int = 52,
    candidate_weight_cap: float = 0.10,
) -> AbstentionDecision:
    if value.invalid_metadata:
        return AbstentionDecision(
            AbstentionStatus.INVALID_METADATA, False, 0.0, 0, ("metadata_global_veto",)
        )
    if value.forced_return_remaining > 0:
        return AbstentionDecision(
            AbstentionStatus.FORCED_RETURN,
            True,
            0.0,
            value.forced_return_remaining - 1,
            ("hard_return_active",),
        )
    if (
        value.latest_block_delta_log_loss is not None
        and value.latest_block_delta_brier is not None
        and value.latest_block_delta_log_loss <= 0.0
        and value.latest_block_delta_brier < 0.0
    ):
        return AbstentionDecision(
            AbstentionStatus.FORCED_RETURN,
            True,
            0.0,
            hard_return_draws,
            ("recent_block_harm",),
        )
    threshold = deactivation if value.prior_active else activation
    evidence_active = value.evidence >= threshold
    metrics_positive = (
        value.latest_block_delta_log_loss is not None
        and value.latest_block_delta_brier is not None
        and value.latest_block_delta_log_loss > 0.0
        and value.latest_block_delta_brier >= 0.0
    )
    if not evidence_active or not metrics_positive:
        return AbstentionDecision(
            AbstentionStatus.ABSTAIN,
            False,
            0.0,
            0,
            ("insufficient_evidence_or_block_metrics",),
        )
    if value.research_only:
        return AbstentionDecision(
            AbstentionStatus.SHADOW_ACTIVE,
            True,
            0.0,
            0,
            ("research_distribution_forced_to_m0",),
        )
    return AbstentionDecision(
        AbstentionStatus.CANDIDATE_ELIGIBLE,
        True,
        candidate_weight_cap,
        0,
        (),
    )
