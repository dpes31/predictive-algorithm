"""User-approved hypothesis and physical score components."""
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from .config import ResearchEnsembleConfig
from .registry import RegistryValidationError, number_mapping
from .vector import normalize_vector, zero_vector


def direction(entry: Mapping[str, Any]) -> float:
    value = entry.get("expected_direction")
    if value == "POSITIVE":
        return 1.0
    if value == "NEGATIVE":
        return -1.0
    signed = float(entry.get("parameters", {}).get("direction", 0.0))
    if signed not in {-1.0, 1.0}:
        raise RegistryValidationError("invalid user-defined direction")
    return signed


def full_vector(entry: Mapping[str, Any], config: ResearchEnsembleConfig) -> dict[int, float] | None:
    if entry.get("classification") != "NUMBER_LEVEL":
        return None
    values = number_mapping(entry)
    return values if set(values) == set(range(1, config.number_count + 1)) else None


def hypothesis_component(users: Mapping[str, Any], registry: Mapping[str, Any], excluded: set[str], config: ResearchEnsembleConfig) -> dict[str, Any]:
    by_id = {str(item["entry_id"]): item for item in users.get("entries", [])}
    active = [item for item in registry.get("entries", []) if item.get("status") == "ACTIVE" and str(item["hypothesis_id"]) not in excluded]
    total = zero_vector(config.number_count)
    details: dict[str, dict[int, float]] = {}
    reasons: list[str] = []
    run_reasons: list[str] = []
    fulfilled = 0
    component_abstain = False
    for item in active:
        hypothesis_id = str(item["hypothesis_id"])
        input_ids = [str(value) for value in item.get("input_entry_ids", [])]
        source = by_id.get(input_ids[0]) if len(input_ids) == 1 else None
        values = None if source is None else full_vector(source, config)
        if values is None:
            reasons.append(f"{hypothesis_id}:missing_or_non_discriminative_input")
            policy = str(item.get("missing_policy"))
            if item.get("required") or policy == "ABSTAIN_RUN":
                run_reasons.append(f"required_hypothesis_missing:{hypothesis_id}")
            elif policy == "ABSTAIN_COMPONENT":
                component_abstain = True
            continue
        normalized = normalize_vector(values, number_count=config.number_count)
        cap = float(item.get("single_hypothesis_cap", 0.0))
        scored = {number: cap * direction(item) * normalized[number] for number in normalized}
        details[hypothesis_id] = scored
        fulfilled += 1
        for number in total:
            total[number] += scored[number]
    if component_abstain:
        total, details = zero_vector(config.number_count), {}
        reasons.append("hypothesis_component_abstained")
    if not active:
        reasons.append("no_active_hypotheses")
    return {"contribution": total, "by_hypothesis": details, "support": fulfilled / len(active) if active else 0.0, "reasons": reasons, "run_abstention_reasons": run_reasons, "active_count": len(active)}


def physical_component(users: Mapping[str, Any], registry: Mapping[str, Any], adapter: Mapping[str, Any], config: ResearchEnsembleConfig) -> dict[str, Any]:
    user_by_id = {str(item["entry_id"]): item for item in users.get("entries", [])}
    hypothesis_by_id = {str(item["hypothesis_id"]): item for item in registry.get("entries", [])}
    total = zero_vector(config.number_count)
    details: dict[str, dict[int, float]] = {}
    used: set[str] = set()
    reasons: list[str] = []
    for field in adapter.get("fields", []):
        field_id = str(field["field_id"])
        hypothesis_id = str(field.get("hypothesis_id", ""))
        hypothesis = hypothesis_by_id.get(hypothesis_id)
        source = user_by_id.get(str(field.get("input_entry_id", "")))
        if hypothesis is None or source is None:
            raise RegistryValidationError("physical field has unknown reference")
        if hypothesis.get("status") != "ACTIVE":
            reasons.append(f"{field_id}:hypothesis_not_active")
            continue
        values = full_vector(source, config)
        if values is None:
            reasons.append(f"{field_id}:input_not_number_discriminative")
            continue
        normalized = normalize_vector(values, number_count=config.number_count)
        if max(abs(value) for value in normalized.values()) <= 1e-15:
            reasons.append(f"{field_id}:zero_reference")
            continue
        cap = float(field.get("field_cap", 0.0))
        scored = {number: cap * direction(hypothesis) * normalized[number] for number in normalized}
        details[field_id] = scored
        used.add(hypothesis_id)
        for number in total:
            total[number] += scored[number]
    if not adapter.get("fields"):
        reasons.append("no_physical_adapter_fields")
    count = len(adapter.get("fields", []))
    return {"contribution": total, "by_field": details, "support": len(details) / count if count else 0.0, "reasons": reasons, "used_hypothesis_ids": used, "active_fields": len(details)}
