"""Score-45 assembly, uncertainty, abstention, and ablation."""
from __future__ import annotations
from collections.abc import Mapping, Sequence
from typing import Any
from engine.contracts import DrawRecord
from engine.hashing import sha256_value
from .components import hypothesis_component, physical_component
from .config import ABLATION_IDS, DEFAULT_INTEGRATION_CONFIG, ResearchEnsembleConfig
from .historical import build_historical_component, historical_contribution_for_ablation
from .registry import empty_hypothesis_registry, empty_physical_adapter, empty_user_registry, validate_hypothesis_registry, validate_physical_adapter, validate_user_registry
from .vector import center_and_cap, stable_float, zero_vector


def selected_components(ablation_id: str) -> tuple[bool, bool, bool]:
    historical = ablation_id not in {"CONTROL_M0", "HYPOTHESIS_ONLY", "PHYSICAL_ONLY"}
    hypothesis = ablation_id not in {"CONTROL_M0", "HISTORICAL_ONLY", "PHYSICAL_ONLY", "ENSEMBLE_MINUS_HYPOTHESES"}
    physical = ablation_id not in {"CONTROL_M0", "HISTORICAL_ONLY", "HYPOTHESIS_ONLY", "ENSEMBLE_MINUS_PHYSICAL"}
    return historical, hypothesis, physical


def disagreement(values: Sequence[float], raw: float) -> float:
    denominator = sum(abs(value) for value in values)
    if denominator <= 1e-15:
        return 0.0
    if abs(raw) <= 1e-15:
        return 1.0
    sign = 1.0 if raw > 0.0 else -1.0
    return min(1.0, sum(abs(value) for value in values if value * sign < 0.0) / denominator)


def assemble_ablation(ablation_id: str, historical: Mapping[str, Any], hypotheses: Mapping[str, Any], physical: Mapping[str, Any], config: ResearchEnsembleConfig) -> dict[str, Any]:
    use_historical, use_hypothesis, use_physical = selected_components(ablation_id)
    historical_values = historical_contribution_for_ablation(historical, ablation_id=ablation_id, config=config) if use_historical else zero_vector(config.number_count)
    hypothesis_values = dict(hypotheses["contribution"]) if use_hypothesis else zero_vector(config.number_count)
    physical_values = dict(physical["contribution"]) if use_physical else zero_vector(config.number_count)
    supports: list[float] = []
    if use_historical:
        supports.append(float(historical["support"]))
    if use_hypothesis and int(hypotheses["active_count"]) > 0:
        supports.append(float(hypotheses["support"]))
    if use_physical and physical["by_field"]:
        supports.append(float(physical["support"]))
    support = sum(supports) / len(supports) if supports else 0.0
    provisional, raw_values, rates = {}, {}, {}
    for number in range(1, config.number_count + 1):
        components = [historical_values[number], hypothesis_values[number], physical_values[number]]
        raw = sum(components)
        rate = min(config.uncertainty_abs_cap, 0.35 * (1.0 - support) + 0.40 * disagreement(components, raw))
        raw_values[number], rates[number] = raw, rate
        provisional[number] = raw * (1.0 - rate)
    final_logits = center_and_cap(provisional, config.final_logit_abs_cap, number_count=config.number_count)
    reasons = list(hypotheses["run_abstention_reasons"])
    if max(abs(value) for value in final_logits.values()) <= 1e-12:
        reasons.append("all_nonuniform_components_abstained")
    rows = []
    common_reasons = list(historical["m3_reasons"]) + list(hypotheses["reasons"]) + list(physical["reasons"])
    for number in range(1, config.number_count + 1):
        rows.append({
            "number": number,
            "m1_raw": stable_float(historical["raw"]["M1"][number]),
            "m1_normalized": stable_float(historical["normalized"]["M1"][number]),
            "m2_raw": stable_float(historical["raw"]["M2"][number]),
            "m2_normalized": stable_float(historical["normalized"]["M2"][number]),
            "m3_raw": stable_float(historical["raw"]["M3"][number]),
            "m3_normalized": stable_float(historical["normalized"]["M3"][number]),
            "m3_eligible": bool(historical["m3_eligible"]),
            "historical_contribution": stable_float(historical_values[number]),
            "hypothesis_contribution": stable_float(hypothesis_values[number]),
            "physical_contribution": stable_float(physical_values[number]),
            "uncertainty_rate": stable_float(rates[number]),
            "pre_center_logit": stable_float(raw_values[number] * (1.0 - rates[number])),
            "final_logit": stable_float(final_logits[number]),
            "component_reasons": common_reasons,
        })
    return {"ablation_id": ablation_id, "score_vector": rows, "final_logits": final_logits, "score_vector_hash": sha256_value(rows), "run_abstained": bool(reasons), "run_abstention_reasons": list(dict.fromkeys(reasons)), "support": stable_float(support)}


def build_score_bundle(records: Sequence[DrawRecord], *, target_draw_no: int, data_version: str, user_input_registry: Mapping[str, Any] | None = None, hypothesis_registry: Mapping[str, Any] | None = None, physical_adapter: Mapping[str, Any] | None = None, m3_evidence: Mapping[str, Any] | None = None, ablation_id: str = "ENSEMBLE_FULL", config: ResearchEnsembleConfig = DEFAULT_INTEGRATION_CONFIG) -> dict[str, Any]:
    if ablation_id not in ABLATION_IDS:
        raise ValueError(f"unknown ablation_id: {ablation_id}")
    users, user_hash = validate_user_registry(user_input_registry or empty_user_registry())
    hypothesis_registry_value, hypothesis_hash = validate_hypothesis_registry(hypothesis_registry or empty_hypothesis_registry(), single_cap=config.single_hypothesis_cap, total_cap=config.hypothesis_total_cap)
    adapter, adapter_hash = validate_physical_adapter(physical_adapter or empty_physical_adapter(), field_cap=config.single_physical_field_cap, total_cap=config.physical_total_cap)
    historical = build_historical_component(records, target_draw_no=target_draw_no, data_version=data_version, config=config, m3_evidence=m3_evidence)
    physical = physical_component(users, hypothesis_registry_value, adapter, config)
    hypotheses = hypothesis_component(users, hypothesis_registry_value, set(physical["used_hypothesis_ids"]), config)
    full = {name: assemble_ablation(name, historical, hypotheses, physical, config) for name in ABLATION_IDS}
    summary = {name: {"score_vector_hash": value["score_vector_hash"], "run_abstained": value["run_abstained"], "run_abstention_reasons": value["run_abstention_reasons"]} for name, value in full.items()}
    selected = full[ablation_id]
    return {
        "selected": selected,
        "ablations": summary,
        "ablation_manifest_hash": sha256_value(summary),
        "historical": historical,
        "hypothesis": hypotheses,
        "physical": physical,
        "hashes": {
            "feature_snapshot_hash": historical["feature_snapshot_hash"],
            "historical_loss_sequence_hash": historical["historical_loss_sequence_hash"],
            "historical_weight_hash": historical["historical_weight_hash"],
            "user_input_hash": user_hash,
            "hypothesis_registry_hash": hypothesis_hash,
            "physical_adapter_config_hash": adapter_hash,
            "score_config_hash": config.config_hash,
            "score_vector_hash": selected["score_vector_hash"],
        },
        "component_summary": {
            "historical_support": stable_float(float(historical["support"])),
            "historical_weights": {name: stable_float(float(value)) for name, value in historical["weights"].items()},
            "m3_eligible": historical["m3_eligible"],
            "m3_reasons": historical["m3_reasons"],
            "hypothesis_support": stable_float(float(hypotheses["support"])),
            "hypothesis_reasons": hypotheses["reasons"],
            "physical_support": stable_float(float(physical["support"])),
            "physical_reasons": physical["reasons"],
        },
    }
