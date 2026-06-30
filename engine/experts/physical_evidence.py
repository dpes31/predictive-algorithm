"""M4 physical and operational evidence expert.

The expert is deliberately conservative: only pre-draw, traceable metadata is
eligible; unsupported or low-quality context collapses to the uniform model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord
from ..distributions import FixedSizeDistribution
from ..physical_metadata import MetadataQuality, PhysicalDrawMetadata, validate_metadata_sequence


def _logit(probability: float) -> float:
    clipped = min(1.0 - 1e-12, max(1e-12, probability))
    return math.log(clipped / (1.0 - clipped))


def _uniform_distribution(config: EngineConfig) -> FixedSizeDistribution:
    return FixedSizeDistribution(tuple(0.0 for _ in range(config.number_count)), config.pick_count)


@dataclass(frozen=True)
class PhysicalEvidenceDiagnostics:
    active: bool
    quality: MetadataQuality
    matched_contexts: int
    weighted_context_support: float
    context_support: Mapping[str, float]
    number_logits: tuple[float, ...]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "quality": self.quality.to_dict(),
            "matched_contexts": self.matched_contexts,
            "weighted_context_support": self.weighted_context_support,
            "context_support": dict(self.context_support),
            "number_logits": list(self.number_logits),
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class PhysicalEvidenceModel:
    distribution: FixedSizeDistribution
    diagnostics: PhysicalEvidenceDiagnostics


def build_physical_evidence_model(
    records: Sequence[DrawRecord],
    metadata_records: Sequence[PhysicalDrawMetadata],
    target_metadata: PhysicalDrawMetadata,
    config: EngineConfig = DEFAULT_CONFIG,
) -> PhysicalEvidenceModel:
    """Build a leakage-safe contextual M4 distribution.

    Historical results are used only for draws earlier than target_metadata.draw_no.
    Each matching context receives a strongly shrunk inclusion-rate estimate. The
    target evidence confidence scales its contribution and contributions are
    averaged so adding more metadata fields cannot mechanically increase certainty.
    """

    if not records:
        raise ValueError("records must not be empty")
    target_draw_no = target_metadata.draw_no
    if records[-1].draw_no >= target_draw_no:
        raise ValueError("M4 records must end before the target draw")
    if target_metadata.metadata_version != config.physical_data_schema_version:
        raise ValueError(
            "physical metadata version mismatch: "
            f"expected {config.physical_data_schema_version}, got {target_metadata.metadata_version}"
        )

    history_metadata = validate_metadata_sequence(metadata_records, target_draw_no=target_draw_no - 1)
    result_by_draw = {record.draw_no: record for record in records if record.draw_no < target_draw_no}
    quality = target_metadata.quality(config)
    target_context = target_metadata.context_values(config)
    reasons = list(quality.reasons)

    if not quality.active:
        logits = tuple(0.0 for _ in range(config.number_count))
        return PhysicalEvidenceModel(
            _uniform_distribution(config),
            PhysicalEvidenceDiagnostics(
                active=False,
                quality=quality,
                matched_contexts=0,
                weighted_context_support=0.0,
                context_support={},
                number_logits=logits,
                reasons=tuple(reasons),
            ),
        )
    if not target_context:
        reasons.append("no_eligible_context_fields")
        logits = tuple(0.0 for _ in range(config.number_count))
        return PhysicalEvidenceModel(
            _uniform_distribution(config),
            PhysicalEvidenceDiagnostics(False, quality, 0, 0.0, {}, logits, tuple(reasons)),
        )

    p0 = config.uniform_number_probability
    prior = config.physical_prior_concentration
    baseline_logit = _logit(p0)
    context_contributions: dict[str, tuple[float, ...]] = {}
    context_support: dict[str, float] = {}
    context_weights: dict[str, float] = {}

    for path, target_evidence in target_context.items():
        weighted_exposure = 0.0
        weighted_hits = [0.0] * config.number_count
        target_value = target_evidence.value

        for metadata in history_metadata:
            historical_evidence = metadata.eligible_fields().get(path)
            record = result_by_draw.get(metadata.draw_no)
            if historical_evidence is None or record is None:
                continue
            if historical_evidence.value != target_value:
                continue
            reliability = min(target_evidence.confidence, historical_evidence.confidence)
            if reliability <= 0.0:
                continue
            weighted_exposure += reliability
            for number in record.numbers:
                weighted_hits[number - 1] += reliability

        context_support[path] = weighted_exposure
        if weighted_exposure < config.physical_min_context_support:
            continue

        contributions: list[float] = []
        for index in range(config.number_count):
            rate = (prior * p0 + weighted_hits[index]) / (prior + weighted_exposure)
            delta = _logit(rate) - baseline_logit
            contributions.append(
                max(-config.physical_effect_clip, min(config.physical_effect_clip, delta))
            )
        context_contributions[path] = tuple(contributions)
        context_weights[path] = target_evidence.confidence

    matched_contexts = len(context_contributions)
    total_context_weight = sum(context_weights.values())
    weighted_support = sum(context_support[path] * context_weights[path] for path in context_contributions)

    if matched_contexts == 0 or total_context_weight <= 0.0:
        reasons.append("insufficient_matching_context_support")
        logits = tuple(0.0 for _ in range(config.number_count))
        return PhysicalEvidenceModel(
            _uniform_distribution(config),
            PhysicalEvidenceDiagnostics(
                active=False,
                quality=quality,
                matched_contexts=0,
                weighted_context_support=0.0,
                context_support=context_support,
                number_logits=logits,
                reasons=tuple(reasons),
            ),
        )

    raw_logits = [
        sum(
            context_weights[path] * context_contributions[path][index]
            for path in context_contributions
        )
        / total_context_weight
        for index in range(config.number_count)
    ]
    mean_logit = sum(raw_logits) / len(raw_logits)
    centered_logits = tuple(
        max(
            -config.physical_effect_clip,
            min(config.physical_effect_clip, value - mean_logit),
        )
        for value in raw_logits
    )

    return PhysicalEvidenceModel(
        distribution=FixedSizeDistribution(centered_logits, config.pick_count),
        diagnostics=PhysicalEvidenceDiagnostics(
            active=True,
            quality=quality,
            matched_contexts=matched_contexts,
            weighted_context_support=weighted_support,
            context_support=context_support,
            number_logits=centered_logits,
            reasons=tuple(reasons),
        ),
    )
