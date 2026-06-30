"""Hierarchical partial pooling for physical-context number distributions."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..config import DEFAULT_CONFIG, EngineConfig
from ..distributions import FixedSizeDistribution
from ..physical_metadata import EvidenceValue


def _logit(probability: float) -> float:
    clipped = min(1.0 - 1e-12, max(1e-12, probability))
    return math.log(clipped / (1.0 - clipped))


def _center_clip(values: Sequence[float], limit: float) -> tuple[float, ...]:
    if not values:
        return ()
    mean = sum(values) / len(values)
    return tuple(max(-limit, min(limit, value - mean)) for value in values)


@dataclass
class WeightedCounts:
    exposure: float
    hits: list[float]

    @classmethod
    def empty(cls, number_count: int) -> "WeightedCounts":
        return cls(0.0, [0.0] * number_count)

    def update(self, numbers: Sequence[int], weight: float) -> None:
        if weight <= 0.0:
            return
        self.exposure += weight
        for number in numbers:
            self.hits[int(number) - 1] += weight


@dataclass(frozen=True)
class HierarchyDiagnostics:
    field: str
    context: str | None
    parent_support: float
    context_support: float
    used_parent_fallback: bool
    prediction_eligible: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "context": self.context,
            "parent_support": self.parent_support,
            "context_support": self.context_support,
            "used_parent_fallback": self.used_parent_fallback,
            "prediction_eligible": self.prediction_eligible,
        }


@dataclass(frozen=True)
class HierarchicalDistribution:
    distribution: FixedSizeDistribution
    diagnostics: HierarchyDiagnostics


@dataclass
class HierarchicalPhysicalEstimator:
    """Two-level empirical-Bayes estimator with exact 6-of-45 output."""

    config: EngineConfig = DEFAULT_CONFIG
    parent_counts: dict[str, WeightedCounts] = field(default_factory=dict)
    context_counts: dict[tuple[str, str], WeightedCounts] = field(default_factory=dict)

    def _parent(self, field_name: str) -> WeightedCounts:
        return self.parent_counts.setdefault(field_name, WeightedCounts.empty(self.config.number_count))

    def _context(self, field_name: str, context: str) -> WeightedCounts:
        return self.context_counts.setdefault((field_name, context), WeightedCounts.empty(self.config.number_count))

    @staticmethod
    def context_key(value: object) -> str:
        return repr(value)

    def update_field(self, field_name: str, evidence: EvidenceValue | None, numbers: Sequence[int]) -> None:
        if evidence is None or evidence.value is None or evidence.confidence <= 0.0:
            return
        weight = float(evidence.confidence)
        context = self.context_key(evidence.value)
        self._parent(field_name).update(numbers, weight)
        self._context(field_name, context).update(numbers, weight)

    def update(
        self,
        fields: Mapping[str, EvidenceValue],
        numbers: Sequence[int],
        *,
        field_names: Sequence[str],
    ) -> None:
        for field_name in field_names:
            self.update_field(field_name, fields.get(field_name), numbers)
        self._update_interaction(fields, numbers)

    def _update_interaction(self, fields: Mapping[str, EvidenceValue], numbers: Sequence[int]) -> None:
        machine = fields.get("machine.machine_id")
        ball = fields.get("ball_set.ball_set_id")
        if machine is None or ball is None or machine.value is None or ball.value is None:
            return
        interaction = EvidenceValue(
            value=(machine.value, ball.value),
            status="observed",
            source_type="official_document",
            source_url=machine.source_url or ball.source_url,
            observed_at=machine.observed_at or ball.observed_at,
            available_before_draw=True,
            confidence=min(machine.confidence, ball.confidence),
        )
        self.update_field("interaction.machine_ball_set_id", interaction, numbers)

    def reset_contexts(self, field_names: Sequence[str]) -> None:
        names = set(field_names)
        self.context_counts = {key: value for key, value in self.context_counts.items() if key[0] not in names}

    def support(self, field_name: str, evidence: EvidenceValue | None) -> tuple[float, float]:
        parent = self.parent_counts.get(field_name)
        parent_support = 0.0 if parent is None else parent.exposure
        if evidence is None or evidence.value is None:
            return parent_support, 0.0
        context = self.context_counts.get((field_name, self.context_key(evidence.value)))
        return parent_support, 0.0 if context is None else context.exposure

    def distribution(
        self,
        field_name: str,
        evidence: EvidenceValue | None,
        *,
        effect_clip: float | None = None,
        context_prior: float | None = None,
    ) -> HierarchicalDistribution:
        config = self.config
        p0 = config.uniform_number_probability
        clip = config.correction_effect_clip if effect_clip is None else float(effect_clip)
        k_global = config.correction_k_global
        k_context = config.correction_k_context if context_prior is None else float(context_prior)
        parent = self.parent_counts.get(field_name)
        parent_exposure = 0.0 if parent is None else parent.exposure
        parent_hits = [0.0] * config.number_count if parent is None else parent.hits
        parent_probabilities = [
            (k_global * p0 + parent_hits[index]) / (k_global + parent_exposure)
            for index in range(config.number_count)
        ]
        eligible = evidence is not None and evidence.value is not None and evidence.confidence > 0.0
        context_name = None if evidence is None else self.context_key(evidence.value)
        child = None if not eligible or context_name is None else self.context_counts.get((field_name, context_name))
        child_exposure = 0.0 if child is None else child.exposure
        child_hits = [0.0] * config.number_count if child is None else child.hits
        probabilities = [
            (k_context * parent_probabilities[index] + child_hits[index]) / (k_context + child_exposure)
            for index in range(config.number_count)
        ]
        baseline = _logit(p0)
        logits = _center_clip([_logit(probability) - baseline for probability in probabilities], clip)
        return HierarchicalDistribution(
            FixedSizeDistribution(logits, config.pick_count),
            HierarchyDiagnostics(
                field_name,
                context_name,
                parent_exposure,
                child_exposure,
                child_exposure <= 0.0,
                eligible,
            ),
        )

    def interaction_distribution(self, fields: Mapping[str, EvidenceValue]) -> HierarchicalDistribution:
        machine = fields.get("machine.machine_id")
        ball = fields.get("ball_set.ball_set_id")
        if machine is None or ball is None or machine.value is None or ball.value is None:
            uniform = FixedSizeDistribution(tuple(0.0 for _ in range(self.config.number_count)), self.config.pick_count)
            return HierarchicalDistribution(
                uniform,
                HierarchyDiagnostics("interaction.machine_ball_set_id", None, 0.0, 0.0, True, False),
            )
        synthetic = EvidenceValue(
            value=(machine.value, ball.value),
            status="observed",
            source_type="official_document",
            source_url=machine.source_url or ball.source_url,
            observed_at=machine.observed_at or ball.observed_at,
            available_before_draw=True,
            confidence=min(machine.confidence, ball.confidence),
        )
        machine_result = self.distribution("machine.machine_id", machine)
        ball_result = self.distribution("ball_set.ball_set_id", ball)
        interaction_result = self.distribution(
            "interaction.machine_ball_set_id",
            synthetic,
            effect_clip=self.config.correction_interaction_effect_clip,
            context_prior=self.config.correction_interaction_prior,
        )
        support = interaction_result.diagnostics.context_support
        if support < self.config.correction_interaction_min_support:
            residual = tuple(0.0 for _ in range(self.config.number_count))
        else:
            residual = _center_clip(
                [
                    interaction_result.distribution.logits[index]
                    - machine_result.distribution.logits[index]
                    - ball_result.distribution.logits[index]
                    for index in range(self.config.number_count)
                ],
                self.config.correction_interaction_effect_clip,
            )
        combined = _center_clip(
            [
                machine_result.distribution.logits[index]
                + ball_result.distribution.logits[index]
                + residual[index]
                for index in range(self.config.number_count)
            ],
            self.config.correction_effect_clip,
        )
        return HierarchicalDistribution(FixedSizeDistribution(combined, self.config.pick_count), interaction_result.diagnostics)
