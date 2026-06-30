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


def effective_weights(
    state: GateState,
    shadow: Mapping[str, float],
    *,
    physical_weight_cap: float = 0.10,
) -> dict[str, float]:
    """Return deployable model weights while preserving the M0 safety floor.

    M4 is optional for backward compatibility. When present it is capped at ten
    percent until a later, explicitly approved promotion contract changes it.
    """

    required = {"M0", "M1", "M2", "M3"}
    allowed = required | {"M4"}
    if not required.issubset(shadow) or not set(shadow).issubset(allowed):
        raise ValueError("shadow weights must contain M0-M3 and may optionally contain M4")
    if any(value < 0 or not math.isfinite(value) for value in shadow.values()):
        raise ValueError("shadow weights must be finite and non-negative")
    if not 0.0 <= physical_weight_cap <= 1.0:
        raise ValueError("physical_weight_cap must be in [0, 1]")
    total = sum(shadow.values())
    if total <= 0:
        raise ValueError("shadow weights must have positive total")
    normalized = {name: value / total for name, value in shadow.items()}
    names = tuple(name for name in ("M0", "M1", "M2", "M3", "M4") if name in normalized)

    if state in {GateState.CLOSED, GateState.RESEARCH}:
        return {name: (1.0 if name == "M0" else 0.0) for name in names}

    minimum_m0 = 0.70 if state == GateState.CANDIDATE else 0.25
    m0 = max(minimum_m0, normalized["M0"])
    available = 1.0 - m0
    nonuniform_names = tuple(name for name in names if name != "M0")
    nonuniform_total = sum(normalized[name] for name in nonuniform_names)
    if nonuniform_total <= 0:
        return {name: (1.0 if name == "M0" else 0.0) for name in names}

    output = {"M0": m0}
    for name in nonuniform_names:
        output[name] = available * normalized[name] / nonuniform_total

    if "M4" in output and output["M4"] > physical_weight_cap:
        excess = output["M4"] - physical_weight_cap
        output["M4"] = physical_weight_cap
        legacy_names = tuple(name for name in ("M1", "M2", "M3") if name in output)
        legacy_total = sum(output[name] for name in legacy_names)
        if legacy_total > 0:
            for name in legacy_names:
                output[name] += excess * output[name] / legacy_total
        else:
            output["M0"] += excess

    correction = 1.0 - sum(output.values())
    output["M0"] += correction
    return output
