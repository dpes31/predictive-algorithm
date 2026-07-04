"""Single research-only Gate 2 prediction run."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from .abstention import MacroPerformance
from .candidate_optimizer import optimize_candidates
from .config import DEFAULT_CONFIG, EngineConfig
from .contracts import DrawRecord, FeatureSnapshot, PredictionResult
from .data_loader import records_for_target
from .distributions import MixtureDistribution
from .experts import (
    ChangeEProcessResult,
    build_persistence_model,
    build_physical_evidence_model,
    build_post_change_model,
    build_regime_change_model,
    build_reversal_model,
    build_uniform_model,
)
from .feature_engineering import build_feature_snapshot
from .hashing import deterministic_seed, sha256_value
from .maxt_gate import MaxTResult
from .physical_metadata import PhysicalDrawMetadata
from .randomness_gate import GateEvidence, effective_weights, evaluate_gate


def _snapshot_with_change_gate(
    snapshot: FeatureSnapshot,
    *,
    maxt_result: MaxTResult | None,
    change_eprocess_result: ChangeEProcessResult | None,
) -> FeatureSnapshot:
    if maxt_result is None and change_eprocess_result is None:
        return snapshot
    global_features = dict(snapshot.global_features)
    if change_eprocess_result is not None:
        global_features.update(
            {
                "change_gate": 1.0 if change_eprocess_result.active else 0.0,
                "change_gate_calibrated": True,
                "change_gate_status": (
                    "active_eprocess"
                    if change_eprocess_result.active
                    else change_eprocess_result.status.lower()
                ),
                "change_e_value": change_eprocess_result.e_value,
                "change_log_e_value": change_eprocess_result.log_e_value,
                "change_restart_count": change_eprocess_result.restart_count,
                "change_trigger_draw_no": change_eprocess_result.trigger_draw_no,
                "change_active_age": change_eprocess_result.active_age,
            }
        )
    elif maxt_result is not None:
        global_features.update(
            {
                "change_gate": 1.0 if maxt_result.active else 0.0,
                "change_gate_calibrated": maxt_result.full_contract_ready,
                "change_gate_status": (
                    "active_legacy_maxT"
                    if maxt_result.active
                    else (
                        "legacy_maxT_no_signal"
                        if maxt_result.full_contract_ready
                        else "insufficient_legacy_maxT_calibration"
                    )
                ),
                "maxT_observed": maxt_result.observed_max_t,
                "maxT_empirical_p": maxt_result.empirical_p_value,
                "maxT_calibration_series": maxt_result.calibrated_series,
            }
        )
    payload = {
        "target_draw_no": snapshot.target_draw_no,
        "input_last_draw": snapshot.input_last_draw,
        "data_version": snapshot.data_version,
        "feature_contract_version": snapshot.feature_contract_version,
        "number_features": {
            str(number): dict(features)
            for number, features in sorted(snapshot.number_features.items())
        },
        "global_features": global_features,
    }
    return FeatureSnapshot(
        target_draw_no=snapshot.target_draw_no,
        input_last_draw=snapshot.input_last_draw,
        data_version=snapshot.data_version,
        feature_contract_version=snapshot.feature_contract_version,
        number_features=snapshot.number_features,
        global_features=global_features,
        snapshot_hash=sha256_value(payload),
    )


def run_research_prediction(
    records: Sequence[DrawRecord],
    *,
    target_draw_no: int,
    data_version: str,
    generated_at: str,
    shadow_weights: Mapping[str, float] | None = None,
    gate_evidence: GateEvidence | None = None,
    physical_metadata_records: Sequence[PhysicalDrawMetadata] | None = None,
    target_physical_metadata: PhysicalDrawMetadata | None = None,
    physical_macro_performance: Sequence[MacroPerformance] = (),
    maxt_result: MaxTResult | None = None,
    change_eprocess_result: ChangeEProcessResult | None = None,
    config: EngineConfig = DEFAULT_CONFIG,
) -> PredictionResult:
    usable = records_for_target(
        records,
        target_draw_no=target_draw_no,
        research_only=True,
        minimum_history=config.min_history,
    )
    snapshot = build_feature_snapshot(
        usable,
        target_draw_no=target_draw_no,
        data_version=data_version,
        config=config,
    )
    snapshot = _snapshot_with_change_gate(
        snapshot,
        maxt_result=maxt_result,
        change_eprocess_result=change_eprocess_result,
    )

    if target_physical_metadata is not None:
        if target_physical_metadata.draw_no != target_draw_no:
            raise ValueError("target physical metadata draw_no does not match prediction target")
        physical_model = build_physical_evidence_model(
            usable,
            tuple(physical_metadata_records or ()),
            target_physical_metadata,
            config,
            recent_macro_performance=physical_macro_performance,
            research_only=True,
        )
        m4_distribution = physical_model.distribution
        physical_diagnostics = physical_model.diagnostics.to_dict()
        physical_metadata_hash = sha256_value(target_physical_metadata.to_dict())
    else:
        m4_distribution = build_uniform_model(config)
        physical_diagnostics = {
            "active": False,
            "status": "ABSTAIN",
            "reasons": ["target_physical_metadata_not_provided"],
            "quality": None,
            "matched_contexts": 0,
            "weighted_context_support": 0.0,
            "context_support": {},
        }
        physical_metadata_hash = None

    if change_eprocess_result is not None:
        post_change_model = build_post_change_model(usable, change_eprocess_result, config)
        m3_distribution = post_change_model.distribution
        m3_diagnostics = post_change_model.diagnostics.to_dict()
    else:
        m3_distribution = build_regime_change_model(snapshot, config)
        m3_diagnostics = {
            "active": bool(snapshot.global_features.get("change_gate", 0.0)),
            "legacy_feature_model": True,
            "reasons": ["change_eprocess_result_not_provided"],
        }

    models = {
        "M0": build_uniform_model(config),
        "M1": build_persistence_model(snapshot, config),
        "M2": build_reversal_model(snapshot, config),
        "M3": m3_distribution,
        "M4": m4_distribution,
    }
    if shadow_weights is None:
        shadow = {name: 1.0 / len(models) for name in models}
    else:
        shadow = {name: float(shadow_weights.get(name, 0.0)) for name in models}
        if sum(shadow.values()) <= 0:
            raise ValueError("shadow weights must contain positive mass")

    state = evaluate_gate(gate_evidence or GateEvidence())
    final_weights = effective_weights(
        state,
        shadow,
        physical_weight_cap=config.physical_candidate_weight_cap,
    )
    model_order = tuple(models)
    final_distribution = MixtureDistribution(
        tuple(models[name] for name in model_order),
        tuple(final_weights[name] for name in model_order),
    )
    seed = deterministic_seed(
        data_version,
        config.model_version,
        target_draw_no,
        config.config_hash,
        physical_metadata_hash or "no-physical-metadata",
    )
    uniform_probability = 1.0 / math.comb(config.number_count, config.pick_count)
    candidates = optimize_candidates(
        final_distribution,
        seed=seed,
        uniform_probability=uniform_probability,
        config=config,
    )
    change_payload = (
        change_eprocess_result.to_dict() if change_eprocess_result is not None else None
    )
    hash_payload = {
        "target_draw_no": target_draw_no,
        "model_version": config.model_version,
        "data_version": data_version,
        "gate_state": state.value,
        "model_weights": final_weights,
        "shadow_weights": shadow,
        "candidate_sets": [candidate.to_dict() for candidate in candidates],
        "input_last_draw": usable[-1].draw_no,
        "seed": seed,
        "feature_snapshot_hash": snapshot.snapshot_hash,
        "physical_metadata_hash": physical_metadata_hash,
        "physical_diagnostics": physical_diagnostics,
        "m3_diagnostics": m3_diagnostics,
        "change_eprocess_result": change_payload,
        "legacy_maxt_result": None if maxt_result is None else maxt_result.to_dict(),
        "research_only": True,
        "public_release_allowed": False,
    }
    return PredictionResult(
        target_draw_no=target_draw_no,
        model_version=config.model_version,
        data_version=data_version,
        gate_state=state.value,
        advantage_status=(
            "통계적 우위 없음" if final_weights["M0"] == 1.0 else "연구 후보 신호"
        ),
        model_weights=final_weights,
        shadow_weights=shadow,
        candidate_sets=candidates,
        generated_at=generated_at,
        input_last_draw=usable[-1].draw_no,
        seed=seed,
        prediction_hash=sha256_value(hash_payload),
        research_only=True,
        public_release_allowed=False,
        uncertainty_status="pending_gate2_3p_r",
        metadata={
            "feature_snapshot_hash": snapshot.snapshot_hash,
            "change_gate_status": snapshot.global_features["change_gate_status"],
            "change_eprocess": change_payload,
            "m3_post_change": m3_diagnostics,
            "legacy_maxT": None if maxt_result is None else maxt_result.to_dict(),
            "physical_metadata_hash": physical_metadata_hash,
            "physical_evidence": physical_diagnostics,
            "physical_data_schema_version": config.physical_data_schema_version,
            "engine_config_hash": config.config_hash,
        },
    )
