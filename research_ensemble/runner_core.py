"""Core dual-mode A2 prediction execution."""
from __future__ import annotations
import hashlib
import math
import pathlib
from collections.abc import Mapping
from typing import Any
from engine.candidate_optimizer import optimize_candidates
from engine.data_loader import load_dataset
from engine.distributions import FixedSizeDistribution
from engine.hashing import deterministic_seed, sha256_value
from product.run_prediction import run_product_prediction
from .config import DEFAULT_INTEGRATION_CONFIG, ResearchEnsembleConfig
from .registry import empty_hypothesis_registry, empty_physical_adapter, empty_user_registry
from .runtime import validate_generated_at
from .scoring import build_score_bundle


def run_integrated_prediction(*, target_draw_no: int, dataset_path: str | pathlib.Path, generated_at: str, mode: str = "CONTROL_M0", user_input_registry: Mapping[str, Any] | None = None, hypothesis_registry: Mapping[str, Any] | None = None, physical_adapter: Mapping[str, Any] | None = None, m3_evidence: Mapping[str, Any] | None = None, ablation_id: str = "ENSEMBLE_FULL", config: ResearchEnsembleConfig = DEFAULT_INTEGRATION_CONFIG) -> dict[str, Any]:
    if mode == "CONTROL_M0":
        return run_product_prediction(target_draw_no=target_draw_no, dataset_path=dataset_path, generated_at=generated_at)
    if mode != "RESEARCH_ENSEMBLE":
        raise ValueError("invalid execution mode")
    generated_at = validate_generated_at(generated_at)
    path = pathlib.Path(dataset_path)
    data_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    data_version, records = load_dataset(path)
    bundle = build_score_bundle(records, target_draw_no=target_draw_no, data_version=data_version, user_input_registry=user_input_registry or empty_user_registry(), hypothesis_registry=hypothesis_registry or empty_hypothesis_registry(), physical_adapter=physical_adapter or empty_physical_adapter(), m3_evidence=m3_evidence, ablation_id=ablation_id, config=config)
    selected = bundle["selected"]
    seed = deterministic_seed(config.integration_contract_version, data_hash, bundle["hashes"]["feature_snapshot_hash"], bundle["hashes"]["user_input_hash"], bundle["hashes"]["hypothesis_registry_hash"], config.config_hash, target_draw_no, mode, ablation_id)
    fallback = bool(selected["run_abstained"])
    if fallback:
        control = run_product_prediction(target_draw_no=target_draw_no, dataset_path=dataset_path, generated_at=generated_at)
        candidates = control["candidate_sets"]
        effective_mode = "CONTROL_M0"
    else:
        distribution = FixedSizeDistribution(tuple(selected["final_logits"][number] for number in range(1, config.number_count + 1)), config.pick_count)
        uniform_probability = 1.0 / math.comb(config.number_count, config.pick_count)
        candidates = []
        for candidate in optimize_candidates(distribution, seed=seed, uniform_probability=uniform_probability, config=config.engine_config):
            item = candidate.to_dict()
            item["diversity_selection_effect"] = "near_tie_diversification"
            candidates.append(item)
        effective_mode = "RESEARCH_ENSEMBLE"
    model_source_hash = sha256_value({"implementation_contract_version": config.implementation_contract_version, "score_config_hash": config.config_hash})
    hashes = {"data_hash": data_hash, **bundle["hashes"], "ablation_manifest_hash": bundle["ablation_manifest_hash"], "model_source_hash": model_source_hash}
    identity = {"target_draw_no": target_draw_no, "input_last_draw": target_draw_no - 1, "data_version": data_version, "mode_requested": mode, "mode_effective": effective_mode, "ablation_id": ablation_id, "fallback_applied": fallback, "fallback_reasons": selected["run_abstention_reasons"], "candidate_sets": candidates, "score_vector_hash": selected["score_vector_hash"], "hashes": hashes, "seed": seed, "research_only": True, "public_release_allowed": False, "statistical_edge": False}
    hashes["prediction_hash"] = sha256_value(identity)
    return {
        "schema_version": config.output_schema_version,
        "integration_contract_version": config.integration_contract_version,
        "implementation_contract_version": config.implementation_contract_version,
        "mode_requested": mode,
        "mode_effective": effective_mode,
        "ablation_id": ablation_id,
        "fallback_applied": fallback,
        "fallback_reasons": selected["run_abstention_reasons"],
        "target_draw_no": target_draw_no,
        "input_last_draw": target_draw_no - 1,
        "generated_at": generated_at,
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "advantage_status": "미검증 연구 점수",
        "candidate_sets": candidates,
        "score_vector": selected["score_vector"],
        "component_summary": bundle["component_summary"],
        "component_details": {"hypotheses": bundle["hypothesis"]["by_hypothesis"], "physical_fields": bundle["physical"]["by_field"]},
        "ablation_summary": bundle["ablations"],
        "versions": {"model_version": config.model_version, "score_contract_version": config.score_contract_version, "hypothesis_registry_contract": config.hypothesis_registry_contract, "user_input_registry_contract": config.user_input_registry_contract, "physical_adapter_contract": config.physical_adapter_contract},
        "hashes": hashes,
        "seed": seed,
        "limitations": ["canonical_data_auto_checked_not_officially_locked", "research_ensemble_not_walk_forward_validated", "empty_registries_used_unless_user_approved_payloads_are_supplied", "not_a_claim_of_improved_lottery_odds"],
    }
