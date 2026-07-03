"""Past-only M1/M2/conditional-M3 historical scoring."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from engine.contracts import DrawRecord, FeatureSnapshot
from engine.data_loader import records_for_target
from engine.distributions import FixedSizeDistribution
from engine.feature_engineering import build_feature_snapshot
from engine.hashing import sha256_value
from engine.weights import uniform_weights, update_weights

from .config import ResearchEnsembleConfig
from .vector import normalize_vector, stable_float, zero_vector

M1_FEATURES = (
    "z_recent_10",
    "z_recent_30",
    "z_recent_52",
    "z_recent_104",
    "z_long",
    "z_trend_10_52",
    "z_trend_30_104",
)
M2_FEATURES = (
    ("z_recent_10", -1.0),
    ("z_recent_30", -1.0),
    ("z_recent_52", -1.0),
    ("z_recent_104", -1.0),
    ("z_trend_10_52", -1.0),
    ("z_trend_30_104", -1.0),
    ("z_gap", 1.0),
)
M3_FEATURES = (
    "z_shift_52",
    "z_shift_104",
    "z_ewma_minus_long",
    "signed_cusum_score",
)


def validate_m3_evidence(value: Mapping[str, Any] | None) -> tuple[bool, tuple[str, ...]]:
    if value is None:
        return False, ("m3_evidence_not_provided",)
    reasons: list[str] = []
    if not bool(value.get("pre_target_only", False)):
        reasons.append("m3_evidence_not_pre_target")
    if not bool(value.get("calibrated", False)):
        reasons.append("m3_gate_not_calibrated")
    if not bool(value.get("active", False)):
        reasons.append("m3_gate_inactive")
    if bool(value.get("post_draw_fields_present", False)):
        reasons.append("m3_post_draw_field_present")
    return not reasons, tuple(reasons)


def _validate_history(records: Sequence[DrawRecord]) -> tuple[DrawRecord, ...]:
    ordered = tuple(sorted(records, key=lambda record: record.draw_no))
    draw_numbers = [record.draw_no for record in ordered]
    if len(draw_numbers) != len(set(draw_numbers)):
        raise ValueError("duplicate historical draw")
    if draw_numbers and draw_numbers != list(range(draw_numbers[0], draw_numbers[-1] + 1)):
        raise ValueError("historical draws must be contiguous")
    return ordered


def family_raw_vectors(snapshot: FeatureSnapshot, *, m3_eligible: bool, number_count: int = 45) -> dict[str, dict[int, float]]:
    m1 = {
        number: sum(float(snapshot.number_features[number][name]) for name in M1_FEATURES) / len(M1_FEATURES)
        for number in range(1, number_count + 1)
    }
    m2 = {
        number: sum(sign * float(snapshot.number_features[number][name]) for name, sign in M2_FEATURES) / len(M2_FEATURES)
        for number in range(1, number_count + 1)
    }
    if m3_eligible:
        m3 = {
            number: sum(float(snapshot.number_features[number][name]) for name in M3_FEATURES) / len(M3_FEATURES)
            for number in range(1, number_count + 1)
        }
    else:
        m3 = zero_vector(number_count)
    return {"M1": m1, "M2": m2, "M3": m3}


def _family_distributions(snapshot: FeatureSnapshot, *, families: Sequence[str], m3_eligible: bool, config: ResearchEnsembleConfig) -> dict[str, FixedSizeDistribution]:
    raw = family_raw_vectors(snapshot, m3_eligible=m3_eligible, number_count=config.number_count)
    normalized = {
        family: normalize_vector(raw[family], number_count=config.number_count)
        for family in families
    }
    return {
        family: FixedSizeDistribution(
            tuple(normalized[family][number] for number in range(1, config.number_count + 1)),
            config.pick_count,
        )
        for family in families
    }


def build_historical_component(
    records: Sequence[DrawRecord],
    *,
    target_draw_no: int,
    data_version: str,
    config: ResearchEnsembleConfig,
    m3_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    ordered = _validate_history(records)
    usable = tuple(
        records_for_target(
            ordered,
            target_draw_no=target_draw_no,
            research_only=True,
            minimum_history=config.min_history,
        )
    )
    m3_eligible, m3_reasons = validate_m3_evidence(m3_evidence)
    families = ("M1", "M2", "M3") if m3_eligible else ("M1", "M2")
    weights = uniform_weights(families)
    loss_sequence: list[dict[str, Any]] = []
    engine_config = config.engine_config
    uniform = FixedSizeDistribution((0.0,) * config.number_count, config.pick_count)

    for next_index in range(config.min_history, len(usable)):
        history = usable[:next_index]
        next_record = usable[next_index]
        snapshot = build_feature_snapshot(
            history,
            target_draw_no=next_record.draw_no,
            data_version=data_version,
            config=engine_config,
        )
        distributions = _family_distributions(
            snapshot,
            families=families,
            m3_eligible=m3_eligible,
            config=config,
        )
        losses = {
            family: -distributions[family].joint_log_probability(next_record.numbers)
            for family in families
        }
        baseline_loss = -uniform.joint_log_probability(next_record.numbers)
        weights = update_weights(
            weights,
            losses,
            baseline_loss=baseline_loss,
            config=engine_config,
        )
        loss_sequence.append(
            {
                "draw_no": next_record.draw_no,
                "baseline_loss": stable_float(baseline_loss),
                "losses": {name: stable_float(losses[name]) for name in sorted(losses)},
                "weights_after": {name: stable_float(weights[name]) for name in sorted(weights)},
            }
        )

    target_snapshot = build_feature_snapshot(
        usable,
        target_draw_no=target_draw_no,
        data_version=data_version,
        config=engine_config,
    )
    raw = family_raw_vectors(target_snapshot, m3_eligible=m3_eligible, number_count=config.number_count)
    normalized = {
        family: normalize_vector(raw[family], number_count=config.number_count)
        for family in ("M1", "M2", "M3")
    }
    complete_weights = {"M1": 0.0, "M2": 0.0, "M3": 0.0}
    complete_weights.update(weights)
    combined = {
        number: sum(complete_weights[family] * normalized[family][number] for family in ("M1", "M2", "M3"))
        for number in range(1, config.number_count + 1)
    }
    historical_normalized = normalize_vector(combined, number_count=config.number_count)
    contribution = {
        number: config.historical_budget * historical_normalized[number]
        for number in range(1, config.number_count + 1)
    }
    support = min(
        1.0,
        0.5 + 0.5 * len(loss_sequence) / max(1, config.historical_weight_support_draws),
    )
    return {
        "raw": raw,
        "normalized": normalized,
        "weights": complete_weights,
        "historical_normalized": historical_normalized,
        "contribution": contribution,
        "support": support,
        "m3_eligible": m3_eligible,
        "m3_reasons": list(m3_reasons),
        "feature_snapshot_hash": target_snapshot.snapshot_hash,
        "loss_sequence": loss_sequence,
        "historical_loss_sequence_hash": sha256_value(loss_sequence),
        "historical_weight_hash": sha256_value(
            {name: stable_float(complete_weights[name]) for name in sorted(complete_weights)}
        ),
    }


def historical_contribution_for_ablation(
    historical: Mapping[str, Any],
    *,
    ablation_id: str,
    config: ResearchEnsembleConfig,
) -> dict[int, float]:
    if ablation_id in {"CONTROL_M0", "HYPOTHESIS_ONLY", "PHYSICAL_ONLY"}:
        return zero_vector(config.number_count)
    removed = {
        "ENSEMBLE_MINUS_M1": "M1",
        "ENSEMBLE_MINUS_M2": "M2",
        "ENSEMBLE_MINUS_M3": "M3",
    }.get(ablation_id)
    weights = dict(historical["weights"])
    if removed is not None:
        weights[removed] = 0.0
    active_total = sum(weights.values())
    if active_total <= 0.0:
        return zero_vector(config.number_count)
    weights = {name: value / active_total for name, value in weights.items()}
    combined = {
        number: sum(weights[family] * historical["normalized"][family][number] for family in ("M1", "M2", "M3"))
        for number in range(1, config.number_count + 1)
    }
    normalized = normalize_vector(combined, number_count=config.number_count)
    return {number: config.historical_budget * normalized[number] for number in normalized}
