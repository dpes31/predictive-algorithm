"""Single research-only Gate 2 prediction run."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from .candidate_optimizer import optimize_candidates
from .config import DEFAULT_CONFIG, EngineConfig
from .contracts import DrawRecord, PredictionResult
from .data_loader import records_for_target
from .distributions import MixtureDistribution
from .experts import (
    build_persistence_model,
    build_regime_change_model,
    build_reversal_model,
    build_uniform_model,
)
from .feature_engineering import build_feature_snapshot
from .hashing import deterministic_seed, sha256_value
from .randomness_gate import GateEvidence, effective_weights, evaluate_gate


def run_research_prediction(
    records: Sequence[DrawRecord],
    *,
    target_draw_no: int,
    data_version: str,
    generated_at: str,
    shadow_weights: Mapping[str, float] | None = None,
    gate_evidence: GateEvidence | None = None,
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

    models = {
        "M0": build_uniform_model(config),
        "M1": build_persistence_model(snapshot, config),
        "M2": build_reversal_model(snapshot, config),
        "M3": build_regime_change_model(snapshot, config),
    }
    shadow = dict(shadow_weights or {name: 0.25 for name in models})
    state = evaluate_gate(gate_evidence or GateEvidence())
    final_weights = effective_weights(state, shadow)
    final_distribution = MixtureDistribution(
        tuple(models[name] for name in ("M0", "M1", "M2", "M3")),
        tuple(final_weights[name] for name in ("M0", "M1", "M2", "M3")),
    )

    seed = deterministic_seed(
        data_version,
        config.model_version,
        target_draw_no,
        config.config_hash,
    )
    uniform_probability = 1.0 / math.comb(config.number_count, config.pick_count)
    candidates = optimize_candidates(
        final_distribution,
        seed=seed,
        uniform_probability=uniform_probability,
        config=config,
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
        "research_only": True,
        "public_release_allowed": False,
    }
    return PredictionResult(
        target_draw_no=target_draw_no,
        model_version=config.model_version,
        data_version=data_version,
        gate_state=state.value,
        advantage_status=("통계적 우위 없음" if final_weights["M0"] == 1.0 else "연구 후보 신호"),
        model_weights=final_weights,
        shadow_weights=shadow,
        candidate_sets=candidates,
        generated_at=generated_at,
        input_last_draw=usable[-1].draw_no,
        seed=seed,
        prediction_hash=sha256_value(hash_payload),
        research_only=True,
        public_release_allowed=False,
        uncertainty_status="pending_gate2_3",
        metadata={
            "feature_snapshot_hash": snapshot.snapshot_hash,
            "change_gate_status": snapshot.global_features["change_gate_status"],
            "engine_config_hash": config.config_hash,
        },
    )
