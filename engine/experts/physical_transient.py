"""Transient-family physical evidence with rolling hierarchy and restart mixtures."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Mapping

from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord
from ..distributions import FixedSizeDistribution
from ..eprocess import WindowMixtureEProcess, mean_e_value
from ..physical_metadata import EvidenceValue
from .physical_hierarchy import HierarchicalPhysicalEstimator


@dataclass(frozen=True)
class TransientFamilySnapshot:
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
class TransientPhysicalFamily:
    config: EngineConfig = DEFAULT_CONFIG
    history: deque[tuple[Mapping[str, EvidenceValue], DrawRecord]] = field(init=False)
    processes: dict[str, WindowMixtureEProcess] = field(default_factory=dict)
    last_observed_draw: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.history = deque(maxlen=max(self.config.correction_transient_windows))
        for name in self.config.correction_transient_fields:
            self.processes.setdefault(name, WindowMixtureEProcess(self.config.correction_transient_windows))

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(self.config.correction_transient_fields)

    def _estimator(self) -> HierarchicalPhysicalEstimator:
        estimator = HierarchicalPhysicalEstimator(self.config)
        for fields, record in self.history:
            estimator.update(fields, record.numbers, field_names=self.field_names)
        return estimator

    def predict(self, fields: Mapping[str, EvidenceValue], *, target_draw_no: int) -> TransientFamilySnapshot:
        estimator = self._estimator()
        distributions: dict[str, FixedSizeDistribution] = {}
        diagnostics: dict[str, Mapping[str, Any]] = {}
        e_values: dict[str, float] = {}
        for name in self.field_names:
            last = self.last_observed_draw.get(name)
            process = self.processes[name]
            if last is not None and target_draw_no - last > max(self.config.correction_transient_windows):
                process.expire()
            result = estimator.distribution(name, fields.get(name))
            distributions[name] = result.distribution
            diagnostics[name] = result.diagnostics.to_dict()
            e_values[name] = process.e_value
        return TransientFamilySnapshot(distributions, e_values, diagnostics, mean_e_value(self.processes.values()))

    def score_and_observe(
        self,
        fields: Mapping[str, EvidenceValue],
        record: DrawRecord,
        uniform: FixedSizeDistribution,
    ) -> None:
        snapshot = self.predict(fields, target_draw_no=record.draw_no)
        uniform_log_probability = uniform.joint_log_probability(record.numbers)
        for name, distribution in snapshot.distributions.items():
            evidence = fields.get(name)
            process = self.processes[name]
            if evidence is None or evidence.value is None or evidence.confidence <= 0.0:
                process.neutral_update()
                continue
            log_lr = distribution.joint_log_probability(record.numbers) - uniform_log_probability
            if not math.isfinite(log_lr):
                raise ValueError("transient field produced non-finite log likelihood ratio")
            process.update_log_ratio(log_lr)
            self.last_observed_draw[name] = record.draw_no
        self.history.append((dict(fields), record))
