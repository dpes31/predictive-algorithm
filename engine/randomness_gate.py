"""Conservative Gate 2 model activation state machine."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class GateState(StrEnum):
    CLOSED = "CLOSED"
    RESEARCH = "RESEARCH"
    CANDIDATE = "CANDIDATE"
    PROMOTED = "PROMOTED"


@dataclass(frozen=True)
class GateEvidence:
    probability_improvement: float = 0.0
    adjusted_p_value: float = 1.0
    brier_not_worse: bool = False
    supporting_blocks: int = 0
    null_false_activation_rate: float = 1.0
    prospective_draws: int = 0
    anytime_e_value: float = 1.0
    calibration_not_worse: bool = False
    official_data_locked: bool = False


def evaluate_gate(evidence: GateEvidence) -> GateState:
    candidate = (
        evidence.probability_improvement >= 0.999
        and evidence.adjusted_p_value <= 0.001
        and evidence.brier_not_worse
        and evidence.supporting_blocks >= 2
        and evidence.null_false_activation_rate <= 0.001
    )
    if not candidate:
        return GateState.RESEARCH
    promoted = (
        evidence.prospective_draws >= 52
        and evidence.anytime_e_value >= 1000
        and evidence.calibration_not_worse
        and evidence.official_data_locked
    )
    return GateState.PROMOTED if promoted else GateState.CANDIDATE


def effective_weights(state: GateState, shadow: Mapping[str, float]) -> dict[str, float]:
    required = {"M0", "M1", "M2", "M3"}
    if set(shadow) != required:
        raise ValueError("shadow weights must contain M0, M1, M2, and M3")
    if any(value < 0 or not math.isfinite(value) for value in shadow.values()):
        raise ValueError("shadow weights must be finite and non-negative")
    total = sum(shadow.values())
    if total <= 0:
        raise ValueError("shadow weights must have positive total")
    normalized = {name: value / total for name, value in shadow.items()}

    if state in {GateState.CLOSED, GateState.RESEARCH}:
        return {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0}

    minimum_m0 = 0.70 if state == GateState.CANDIDATE else 0.25
    m0 = max(minimum_m0, normalized["M0"])
    available = 1.0 - m0
    nonuniform_total = sum(normalized[name] for name in ("M1", "M2", "M3"))
    if nonuniform_total <= 0:
        return {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0}
    output = {"M0": m0}
    for name in ("M1", "M2", "M3"):
        output[name] = available * normalized[name] / nonuniform_total
    return output
