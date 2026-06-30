"""Gate 2-3P-R2 corrected M4 physical and operational evidence expert."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..abstention import AbstentionController, AbstentionDecision, MacroPerformance
from ..config import DEFAULT_CONFIG, EngineConfig
from ..contracts import DrawRecord
from ..distributions import FixedSizeDistribution
from ..eprocess import e_value_from_log, logmeanexp
from ..metadata_veto import MetadataVetoResult, evaluate_metadata_global_veto
from ..physical_metadata import MetadataQuality, PhysicalDrawMetadata, validate_metadata_sequence
from .physical_stable import StablePhysicalFamily
from .physical_transient import TransientPhysicalFamily


def _uniform_distribution(config: EngineConfig) -> FixedSizeDistribution:
    return FixedSizeDistribution(tuple(0.0 for _ in range(config.number_count)), config.pick_count)


def _center_clip(values: Sequence[float], limit: float) -> tuple[float, ...]:
    if not values:
        return ()
    mean = sum(values) / len(values)
    return tuple(max(-limit, min(limit, value - mean)) for value in values)


def _capped_normalize(raw: Mapping[str, float], caps: Mapping[str, float]) -> dict[str, float]:
    positive = {key: max(0.0, float(value)) for key, value in raw.items() if value > 0.0}
    if not positive:
        return {}
    remaining = set(positive)
    result = {key: 0.0 for key in positive}
    remaining_mass = 1.0
    while remaining and remaining_mass > 1e-15:
        denominator = sum(positive[key] for key in remaining)
        if denominator <= 0.0:
            break
        newly_capped: set[str] = set()
        for key in tuple(remaining):
            proposed = remaining_mass * positive[key] / denominator
            cap = caps.get(key, 1.0)
            if proposed > cap + 1e-15:
                result[key] = cap
                remaining_mass -= cap
                newly_capped.add(key)
        if not newly_capped:
            for key in remaining:
                result[key] = remaining_mass * positive[key] / denominator
            remaining_mass = 0.0
            break
        remaining -= newly_capped
    correction = 1.0 - sum(result.values())
    if abs(correction) > 1e-12 and result:
        result[max(result, key=result.get)] += correction
    return result


@dataclass(frozen=True)
class PhysicalEvidenceDiagnostics:
    active: bool
    status: str
    quality: MetadataQuality
    metadata_veto: MetadataVetoResult
    matched_contexts: int
    weighted_context_support: float
    context_support: Mapping[str, float]
    number_logits: tuple[float, ...]
    reasons: tuple[str, ...]
    stable_family_e_value: float
    transient_family_e_value: float
    combined_e_value: float
    field_e_values: Mapping[str, float]
    field_weights: Mapping[str, float]
    family_weights: Mapping[str, float]
    abstention: AbstentionDecision
    stable_diagnostics: Mapping[str, Mapping[str, Any]]
    transient_diagnostics: Mapping[str, Mapping[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "status": self.status,
            "quality": self.quality.to_dict(),
            "metadata_veto": self.metadata_veto.to_dict(),
            "matched_contexts": self.matched_contexts,
            "weighted_context_support": self.weighted_context_support,
            "context_support": dict(self.context_support),
            "number_logits": list(self.number_logits),
            "reasons": list(self.reasons),
            "stable_family_e_value": self.stable_family_e_value,
            "transient_family_e_value": self.transient_family_e_value,
            "combined_e_value": self.combined_e_value,
            "field_e_values": dict(self.field_e_values),
            "field_weights": dict(self.field_weights),
            "family_weights": dict(self.family_weights),
            "abstention": self.abstention.to_dict(),
            "stable_diagnostics": {key: dict(value) for key, value in self.stable_diagnostics.items()},
            "transient_diagnostics": {key: dict(value) for key, value in self.transient_diagnostics.items()},
        }


@dataclass(frozen=True)
class PhysicalEvidenceModel:
    distribution: FixedSizeDistribution
    diagnostics: PhysicalEvidenceDiagnostics


def _family_e_value(values: Mapping[str, float]) -> float:
    if any(math.isinf(value) and value > 0.0 for value in values.values()):
        return math.inf
    logs = [math.log(value) for value in values.values() if value > 0.0 and math.isfinite(value)]
    return e_value_from_log(logmeanexp(logs)) if logs else 1.0


def build_physical_evidence_model(
    records: Sequence[DrawRecord],
    metadata_records: Sequence[PhysicalDrawMetadata],
    target_metadata: PhysicalDrawMetadata,
    config: EngineConfig = DEFAULT_CONFIG,
    *,
    recent_macro_performance: Sequence[MacroPerformance] = (),
    research_only: bool = True,
    abstention_controller: AbstentionController | None = None,
) -> PhysicalEvidenceModel:
    """Replay corrected M4 prequentially and predict one target draw."""
    if not records:
        raise ValueError("records must not be empty")
    ordered_records = tuple(sorted(records, key=lambda record: record.draw_no))
    if ordered_records[-1].draw_no >= target_metadata.draw_no:
        raise ValueError("M4 records must end before the target draw")
    history_metadata = validate_metadata_sequence(metadata_records, target_draw_no=target_metadata.draw_no - 1)
    metadata_by_draw = {item.draw_no: item for item in history_metadata}
    uniform = _uniform_distribution(config)
    stable = StablePhysicalFamily(config)
    transient = TransientPhysicalFamily(config)

    for record in ordered_records:
        metadata = metadata_by_draw.get(record.draw_no)
        if metadata is None:
            fields: Mapping[str, Any] = {}
        else:
            veto = evaluate_metadata_global_veto(metadata, target_draw_no=record.draw_no, config=config)
            fields = {} if veto.vetoed else metadata.eligible_fields()
        stable.score_and_observe(fields, record, uniform)
        transient.score_and_observe(fields, record, uniform)

    target_veto = evaluate_metadata_global_veto(target_metadata, target_draw_no=target_metadata.draw_no, config=config)
    quality = target_metadata.quality(config)
    reasons = list(target_veto.reasons) + list(quality.reasons)
    target_fields = {} if target_veto.vetoed else target_metadata.eligible_fields()
    stable_snapshot = stable.predict(target_fields)
    transient_snapshot = transient.predict(target_fields, target_draw_no=target_metadata.draw_no)
    stable_e = _family_e_value(stable_snapshot.e_values)
    transient_e = _family_e_value(transient_snapshot.e_values)
    stable_log = math.log(stable_e) if stable_e > 0.0 and math.isfinite(stable_e) else 709.0
    transient_log = math.log(transient_e) if transient_e > 0.0 and math.isfinite(transient_e) else 709.0
    combined_e = e_value_from_log(logmeanexp((stable_log, transient_log)))

    controller = abstention_controller or AbstentionController(config)
    decision = controller.evaluate(
        draw_no=target_metadata.draw_no,
        e_value=combined_e,
        recent_performance=recent_macro_performance,
        metadata_vetoed=target_veto.vetoed or not quality.active,
        research_only=research_only,
    )
    all_distributions = {**stable_snapshot.distributions, **transient_snapshot.distributions}
    all_e_values = {**stable_snapshot.e_values, **transient_snapshot.e_values}
    raw_field_weights = {
        name: max(0.0, math.log(value))
        for name, value in all_e_values.items()
        if value > 1.0 and math.isfinite(value)
    }
    stable_raw = {name: raw_field_weights[name] for name in stable_snapshot.distributions if name in raw_field_weights}
    transient_raw = {name: raw_field_weights[name] for name in transient_snapshot.distributions if name in raw_field_weights}
    stable_caps = {
        name: (config.correction_interaction_field_weight_cap if name == "interaction.machine_ball_set_id" else config.correction_single_field_weight_cap)
        for name in stable_raw
    }
    transient_caps = {name: config.correction_single_field_weight_cap for name in transient_raw}
    stable_weights = _capped_normalize(stable_raw, stable_caps)
    transient_weights = _capped_normalize(transient_raw, transient_caps)
    stable_strength = max(0.0, math.log(stable_e)) if stable_e > 0.0 and math.isfinite(stable_e) else 709.0
    transient_strength = max(0.0, math.log(transient_e)) if transient_e > 0.0 and math.isfinite(transient_e) else 709.0
    total_strength = stable_strength + transient_strength
    if total_strength > 0.0:
        transient_family_weight = min(config.correction_transient_family_weight_cap, transient_strength / total_strength)
        stable_family_weight = 1.0 - transient_family_weight
    else:
        stable_family_weight = transient_family_weight = 0.0
    field_weights = {
        **{name: stable_family_weight * weight for name, weight in stable_weights.items()},
        **{name: transient_family_weight * weight for name, weight in transient_weights.items()},
    }

    if decision.active and field_weights:
        raw_logits = [
            sum(field_weights[name] * all_distributions[name].logits[index] for name in field_weights)
            for index in range(config.number_count)
        ]
        logits = _center_clip(raw_logits, config.correction_effect_clip)
        distribution = FixedSizeDistribution(logits, config.pick_count)
    else:
        logits = tuple(0.0 for _ in range(config.number_count))
        distribution = uniform
        if not field_weights:
            reasons.append("no_positive_field_evidence")

    combined_diagnostics = {**stable_snapshot.diagnostics, **transient_snapshot.diagnostics}
    context_support = {name: float(value.get("context_support", 0.0)) for name, value in combined_diagnostics.items()}
    matched_contexts = sum(value > 0.0 for value in context_support.values())
    weighted_context_support = sum(context_support.get(name, 0.0) * field_weights.get(name, 0.0) for name in context_support)
    reasons.extend(decision.reasons)
    diagnostics = PhysicalEvidenceDiagnostics(
        active=decision.active,
        status=decision.status.value,
        quality=quality,
        metadata_veto=target_veto,
        matched_contexts=matched_contexts,
        weighted_context_support=weighted_context_support,
        context_support=context_support,
        number_logits=logits,
        reasons=tuple(dict.fromkeys(reasons)),
        stable_family_e_value=stable_e,
        transient_family_e_value=transient_e,
        combined_e_value=combined_e,
        field_e_values=all_e_values,
        field_weights=field_weights,
        family_weights={"stable": stable_family_weight, "transient": transient_family_weight},
        abstention=decision,
        stable_diagnostics=stable_snapshot.diagnostics,
        transient_diagnostics=transient_snapshot.diagnostics,
    )
    return PhysicalEvidenceModel(distribution=distribution, diagnostics=diagnostics)
