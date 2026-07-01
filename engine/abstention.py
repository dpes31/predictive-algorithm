"""M4 abstention state machine for Gate 2-3P-R2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

from .config import DEFAULT_CONFIG, EngineConfig


class AbstentionStatus(str, Enum):
    INVALID_METADATA = "INVALID_METADATA"
    ABSTAIN = "ABSTAIN"
    SHADOW_ACTIVE = "SHADOW_ACTIVE"
    CANDIDATE_ELIGIBLE = "CANDIDATE_ELIGIBLE"
    FORCED_RETURN = "FORCED_RETURN"


@dataclass(frozen=True)
class MacroPerformance:
    delta_log_loss: float
    delta_brier: float

    def to_dict(self) -> dict[str, float]:
        return {
            "delta_log_loss": self.delta_log_loss,
            "delta_brier": self.delta_brier,
        }


@dataclass(frozen=True)
class AbstentionDecision:
    status: AbstentionStatus
    active: bool
    deployable: bool
    exact_m0: bool
    forced_until_draw: int | None
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "active": self.active,
            "deployable": self.deployable,
            "exact_m0": self.exact_m0,
            "forced_until_draw": self.forced_until_draw,
            "reasons": list(self.reasons),
        }


@dataclass
class AbstentionController:
    config: EngineConfig = DEFAULT_CONFIG
    active: bool = False
    forced_until_draw: int | None = None

    def evaluate(
        self,
        *,
        draw_no: int,
        e_value: float,
        recent_performance: Sequence[MacroPerformance] = (),
        metadata_vetoed: bool = False,
        research_only: bool = True,
    ) -> AbstentionDecision:
        reasons: list[str] = []
        if metadata_vetoed:
            self.active = False
            return AbstentionDecision(
                AbstentionStatus.INVALID_METADATA,
                False,
                False,
                True,
                self.forced_until_draw,
                ("metadata_global_veto",),
            )

        latest = recent_performance[-1] if recent_performance else None
        if latest is not None and latest.delta_log_loss <= 0.0 and latest.delta_brier < 0.0:
            self.active = False
            self.forced_until_draw = max(
                self.forced_until_draw or 0,
                draw_no + self.config.correction_forced_return_draws - 1,
            )
            reasons.append("negative_log_loss_and_brier")

        if self.forced_until_draw is not None and draw_no <= self.forced_until_draw:
            return AbstentionDecision(
                AbstentionStatus.FORCED_RETURN,
                False,
                False,
                True,
                self.forced_until_draw,
                tuple(reasons or ("forced_return_window",)),
            )
        if self.forced_until_draw is not None and draw_no > self.forced_until_draw:
            self.forced_until_draw = None

        if self.active:
            if e_value < self.config.correction_deactivation_e:
                self.active = False
                reasons.append("evidence_below_deactivation")
            elif any(item.delta_log_loss <= 0.0 for item in recent_performance[-2:]):
                self.active = False
                reasons.append("recent_block_log_loss_not_positive")
        else:
            eligible = (
                latest is not None
                and latest.delta_log_loss > 0.0
                and latest.delta_brier >= 0.0
            )
            if e_value >= self.config.correction_activation_e and eligible:
                self.active = True
                reasons.append("activation_contract_met")
            elif e_value < self.config.correction_activation_e:
                reasons.append("evidence_below_activation")
            else:
                reasons.append("macro_performance_not_eligible")

        if not self.active:
            return AbstentionDecision(
                AbstentionStatus.ABSTAIN,
                False,
                False,
                True,
                self.forced_until_draw,
                tuple(reasons),
            )
        if research_only:
            return AbstentionDecision(
                AbstentionStatus.SHADOW_ACTIVE,
                True,
                False,
                False,
                self.forced_until_draw,
                tuple(reasons),
            )
        return AbstentionDecision(
            AbstentionStatus.CANDIDATE_ELIGIBLE,
            True,
            True,
            False,
            self.forced_until_draw,
            tuple(reasons),
        )
