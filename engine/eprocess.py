"""Log-domain evidence-process primitives for Gate 2-3P-R2."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceState:
    log_e: float = 0.0
    observations: int = 0

    @property
    def e_value(self) -> float:
        return math.exp(min(self.log_e, 700.0))

    def update(self, likelihood_ratio: float) -> "EvidenceState":
        if likelihood_ratio <= 0.0 or not math.isfinite(likelihood_ratio):
            raise ValueError("likelihood_ratio must be finite and positive")
        return EvidenceState(self.log_e + math.log(likelihood_ratio), self.observations + 1)

    def neutral(self) -> "EvidenceState":
        return EvidenceState(self.log_e, self.observations + 1)


@dataclass(frozen=True)
class RestartMixture:
    states: tuple[EvidenceState, ...] = ()
    max_states: int = 104

    def update(self, likelihood_ratio: float, start_new: bool = False) -> "RestartMixture":
        updated = [state.update(likelihood_ratio) for state in self.states]
        if start_new or not updated:
            updated.append(EvidenceState().update(likelihood_ratio))
        return RestartMixture(tuple(updated[-self.max_states:]), self.max_states)

    @property
    def e_value(self) -> float:
        if not self.states:
            return 1.0
        return sum(state.e_value for state in self.states) / len(self.states)


def exact_likelihood_ratio(q_probability: float, p0_probability: float) -> float:
    if q_probability <= 0.0 or p0_probability <= 0.0:
        raise ValueError("joint probabilities must be positive")
    return q_probability / p0_probability


def betting_factor(observation: float, baseline: float, fraction: float) -> float:
    factor = 1.0 + fraction * (observation - baseline)
    if factor <= 0.0:
        raise ValueError("betting factor must be positive")
    return factor
