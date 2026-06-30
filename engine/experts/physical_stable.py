"""Stable-family physical evidence with prequential e-process scoring."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping

from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord
from ..distributions import FixedSizeDistribution
from ..eprocess import LogEProcess, mean_e_value
from ..physical_metadata import EvidenceValue
from .physical_hierarchy import HierarchicalPhysicalEstimator


@dataclass(frozen=True)
class StableFamilySnapshot:
    distributions: Mapping[str, FixedSizeDistribution]
    e_values: Mapping[str, float]
    diagnostics: Mapping[str, Mapping[str, Any]]
    family_e_value: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "e_values": dict(self.e_values),
            "diagnostics": {key: dict(value) for key, value in self.diagnostics.items()},
            "family_e_value": self.family_e_value,
        }


@dataclass
class StablePhysicalFamily:
    config: EngineConfig = DEFAULT_CONFIG
    estimator: HierarchicalPhysicalEstimator = field(init=False)
    processes: dict[str, LogEProcess] = field(default_factory=dict)
    current_regime_signature: tuple[object, object] | None = None

    def __post_init__(self) -> None:
        self.estimator = HierarchicalPhysicalEstimator(self.config)
        for name in self.config.correction_stable_fields:
            self.processes.setdefault(name, LogEProcess())
        self.processes.setdefault("interaction.machine_ball_set_id", LogEProcess())

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(self.config.correction_stable_fields)

    def _regime_signature(self, fields: Mapping[str, EvidenceValue]) -> tuple[object, object] | None:
        machine = fields.get("regime.machine_regime_id")
        ball = fields.get("regime.ball_regime_id")
        if machine is None or ball is None or machine.value is None or ball.value is None:
            return None
        return machine.value, ball.value

    def _maybe_reset_contexts(self, fields: Mapping[str, EvidenceValue]) -> None:
        signature = self._regime_signature(fields)
        if signature is None:
            return
        if self.current_regime_signature is None:
            self.current_regime_signature = signature
            return
        if signature != self.current_regime_signature:
            self.current_regime_signature = signature
            self.estimator.reset_contexts((*self.field_names, "interaction.machine_ball_set_id"))

    def predict(self, fields: Mapping[str, EvidenceValue]) -> StableFamilySnapshot:
        distributions: dict[str, FixedSizeDistribution] = {}
        diagnostics: dict[str, Mapping[str, Any]] = {}
        for name in self.field_names:
            result = self.estimator.distribution(name, fields.get(name))
            distributions[name] = result.distribution
            diagnostics[name] = result.diagnostics.to_dict()
        interaction = self.estimator.interaction_distribution(fields)
        distributions["interaction.machine_ball_set_id"] = interaction.distribution
        diagnostics["interaction.machine_ball_set_id"] = interaction.diagnostics.to_dict()
        e_values = {name: process.e_value for name, process in self.processes.items()}
        return StableFamilySnapshot(distributions, e_values, diagnostics, mean_e_value(self.processes.values()))

    @staticmethod
    def _interaction_evidence(fields: Mapping[str, EvidenceValue]) -> EvidenceValue | None:
        machine = fields.get("machine.machine_id")
        ball = fields.get("ball_set.ball_set_id")
        if machine is None or ball is None or machine.value is None or ball.value is None:
            return None
        return EvidenceValue(
            value=(machine.value, ball.value),
            status="observed",
            source_type="official_document",
            source_url=machine.source_url or ball.source_url,
            observed_at=machine.observed_at or ball.observed_at,
            available_before_draw=True,
            confidence=min(machine.confidence, ball.confidence),
        )

    def score_and_observe(
        self,
        fields: Mapping[str, EvidenceValue],
        record: DrawRecord,
        uniform: FixedSizeDistribution,
    ) -> None:
        self._maybe_reset_contexts(fields)
        snapshot = self.predict(fields)
        uniform_log_probability = uniform.joint_log_probability(record.numbers)
        for name, distribution in snapshot.distributions.items():
            evidence = self._interaction_evidence(fields) if name == "interaction.machine_ball_set_id" else fields.get(name)
            process = self.processes[name]
            if evidence is None or evidence.value is None or evidence.confidence <= 0.0:
                process.neutral_update()
                continue
            log_lr = distribution.joint_log_probability(record.numbers) - uniform_log_probability
            if not math.isfinite(log_lr):
                raise ValueError("stable field produced non-finite log likelihood ratio")
            process.update_log_ratio(log_lr)
        self.estimator.update(fields, record.numbers, field_names=self.field_names)
