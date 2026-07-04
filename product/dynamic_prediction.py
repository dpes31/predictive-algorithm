"""Dynamic CONTROL_M0 prediction wrapper for user-supplied draw overlays.

The canonical 1..1230 dataset remains immutable. User-entered draws are validated
as a consecutive overlay and only affect the effective input hash, target draw,
seed, candidate sets, and prediction hash for that request.
"""

from __future__ import annotations

import json
import math
import pathlib
from datetime import date, datetime, timezone
from typing import Any, Mapping, Sequence

from engine.candidate_optimizer import optimize_candidates
from engine.config import EngineConfig
from engine.distributions import FixedSizeDistribution
from engine.hashing import deterministic_seed, sha256_value
from product.config import (
    DEFAULT_PRODUCT_CONFIG,
    ENGINE_CORE_VERSION,
    EXPECTED_DATA_HASH,
    FEATURE_CONTRACT_VERSION,
    MODEL_VERSION,
    PRODUCT_CONTRACT_VERSION,
    PRODUCT_WEIGHTS,
)
from product.run_prediction import _model_hash

DYNAMIC_CONTRACT_VERSION = "product-dynamic-ui-1.0.0"
OVERLAY_SCHEMA_VERSION = "1.0.0"
MAX_OVERLAY_RECORDS = 500


def _root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical_dataset(root: pathlib.Path) -> tuple[dict[str, Any], bytes]:
    path = root / "data/draws.json"
    raw = path.read_bytes()
    import hashlib

    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_DATA_HASH:
        raise ValueError(f"canonical dataset hash mismatch: expected {EXPECTED_DATA_HASH}, got {digest}")
    payload = json.loads(raw.decode("utf-8"))
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("canonical dataset records are missing")
    return payload, raw


def _normalized_overlay_record(value: Mapping[str, Any], expected_draw_no: int, previous_date: date) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("overlay record must be an object")

    draw_no = value.get("draw_no")
    if not isinstance(draw_no, int) or isinstance(draw_no, bool):
        raise ValueError("draw_no must be an integer")
    if draw_no != expected_draw_no:
        raise ValueError(f"overlay draw_no must be consecutive: expected {expected_draw_no}")

    draw_date = value.get("draw_date")
    if not isinstance(draw_date, str):
        raise ValueError("draw_date must be YYYY-MM-DD")
    try:
        parsed_date = date.fromisoformat(draw_date)
    except ValueError as exc:
        raise ValueError("draw_date must be YYYY-MM-DD") from exc
    if parsed_date <= previous_date:
        raise ValueError("draw_date must be later than the previous draw date")

    numbers = value.get("numbers")
    if not isinstance(numbers, Sequence) or isinstance(numbers, (str, bytes)):
        raise ValueError("numbers must contain exactly six integers")
    if len(numbers) != 6:
        raise ValueError("numbers must contain exactly six integers")
    normalized_numbers: list[int] = []
    for number in numbers:
        if not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= 45:
            raise ValueError("numbers must be integers from 1 to 45")
        normalized_numbers.append(number)
    if len(set(normalized_numbers)) != 6:
        raise ValueError("numbers must not contain duplicates")
    normalized_numbers.sort()

    bonus = value.get("bonus_number")
    if not isinstance(bonus, int) or isinstance(bonus, bool) or not 1 <= bonus <= 45:
        raise ValueError("bonus_number must be an integer from 1 to 45")
    if bonus in normalized_numbers:
        raise ValueError("bonus_number must not duplicate a winning number")

    return {
        "draw_no": draw_no,
        "draw_date": draw_date,
        "numbers": normalized_numbers,
        "bonus_number": bonus,
        "source": "user_overlay",
        "verification_status": "user_entered",
        "locked": False,
    }


def validate_overlay(overlay: Any, canonical_records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if overlay is None:
        overlay = []
    if not isinstance(overlay, list):
        raise ValueError("overlay must be an array")
    if len(overlay) > MAX_OVERLAY_RECORDS:
        raise ValueError(f"overlay exceeds the maximum of {MAX_OVERLAY_RECORDS} records")

    last = canonical_records[-1]
    expected_draw_no = int(last["draw_no"]) + 1
    previous_date = date.fromisoformat(str(last["draw_date"]))
    normalized: list[dict[str, Any]] = []
    for raw_record in overlay:
        record = _normalized_overlay_record(raw_record, expected_draw_no, previous_date)
        normalized.append(record)
        expected_draw_no += 1
        previous_date = date.fromisoformat(record["draw_date"])
    return normalized


def run_dynamic_prediction(
    *,
    overlay: Any,
    generated_at: str | None = None,
    root: pathlib.Path | None = None,
) -> dict[str, Any]:
    root = _root() if root is None else root
    canonical, _ = _canonical_dataset(root)
    canonical_records = canonical["records"]
    normalized_overlay = validate_overlay(overlay, canonical_records)

    canonical_last = canonical_records[-1]
    latest = normalized_overlay[-1] if normalized_overlay else canonical_last
    input_last_draw = int(latest["draw_no"])
    target_draw_no = input_last_draw + 1

    overlay_payload = {
        "schema_version": OVERLAY_SCHEMA_VERSION,
        "records": normalized_overlay,
    }
    overlay_hash = sha256_value(overlay_payload)
    effective_data_hash = sha256_value(
        {
            "canonical_data_hash": EXPECTED_DATA_HASH,
            "overlay_hash": overlay_hash,
            "input_last_draw": input_last_draw,
        }
    )

    engine_config = EngineConfig(
        model_version=ENGINE_CORE_VERSION,
        feature_contract_version=FEATURE_CONTRACT_VERSION,
        number_count=DEFAULT_PRODUCT_CONFIG.number_count,
        pick_count=DEFAULT_PRODUCT_CONFIG.pick_count,
        candidate_count=DEFAULT_PRODUCT_CONFIG.candidate_count,
        uniform_candidate_pool=DEFAULT_PRODUCT_CONFIG.uniform_candidate_pool,
    )
    config_hash = DEFAULT_PRODUCT_CONFIG.config_hash
    seed = deterministic_seed(
        DYNAMIC_CONTRACT_VERSION,
        effective_data_hash,
        MODEL_VERSION,
        config_hash,
        target_draw_no,
    )
    distribution = FixedSizeDistribution(
        logits=(0.0,) * DEFAULT_PRODUCT_CONFIG.number_count,
        pick_count=DEFAULT_PRODUCT_CONFIG.pick_count,
    )
    uniform_probability = 1.0 / math.comb(
        DEFAULT_PRODUCT_CONFIG.number_count,
        DEFAULT_PRODUCT_CONFIG.pick_count,
    )
    engine_candidates = optimize_candidates(
        distribution,
        seed=seed,
        uniform_probability=uniform_probability,
        config=engine_config,
    )
    candidate_sets = [
        {
            "rank": candidate.rank,
            "numbers": list(candidate.numbers),
            "joint_probability": uniform_probability,
            "lift_vs_uniform": 1.0,
        }
        for candidate in engine_candidates
    ]

    model_hash = _model_hash(root)
    prediction_hash_payload = {
        "contract_version": DYNAMIC_CONTRACT_VERSION,
        "underlying_product_contract_version": PRODUCT_CONTRACT_VERSION,
        "target_draw_no": target_draw_no,
        "input_last_draw": input_last_draw,
        "canonical_data_hash": EXPECTED_DATA_HASH,
        "overlay_hash": overlay_hash,
        "effective_data_hash": effective_data_hash,
        "model_version": MODEL_VERSION,
        "model_hash": model_hash,
        "config_hash": config_hash,
        "seed": seed,
        "product_weights": PRODUCT_WEIGHTS,
        "candidate_sets": candidate_sets,
        "statistical_edge": False,
        "reason": "no_validated_nonuniform_signal",
    }
    prediction_hash = sha256_value(prediction_hash_payload)

    return {
        "schema_version": "1.0.0",
        "contract_version": DYNAMIC_CONTRACT_VERSION,
        "underlying_product_contract_version": PRODUCT_CONTRACT_VERSION,
        "target_draw_no": target_draw_no,
        "input_last_draw": input_last_draw,
        "generated_at": generated_at or _utc_now(),
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "reason": "no_validated_nonuniform_signal",
        "advantage_status": "통계적 우위 없음",
        "final_distribution": "M0_ONLY",
        "product_weights": dict(PRODUCT_WEIGHTS),
        "candidate_sets": candidate_sets,
        "versions": {
            "canonical_data_version": canonical["data_version"],
            "overlay_schema_version": OVERLAY_SCHEMA_VERSION,
            "model_version": MODEL_VERSION,
            "engine_core_version": ENGINE_CORE_VERSION,
        },
        "hashes": {
            "canonical_data_hash": EXPECTED_DATA_HASH,
            "overlay_hash": overlay_hash,
            "effective_data_hash": effective_data_hash,
            "model_hash": model_hash,
            "config_hash": config_hash,
            "prediction_hash": prediction_hash,
        },
        "seed": seed,
        "data": {
            "canonical_first_draw": int(canonical_records[0]["draw_no"]),
            "canonical_last_draw": int(canonical_last["draw_no"]),
            "overlay_record_count": len(normalized_overlay),
            "input_last_draw": input_last_draw,
            "verification_status": "auto_checked_plus_user_overlay" if normalized_overlay else "auto_checked",
            "officially_locked": False,
        },
        "limitations": [
            "canonical_data_auto_checked_not_officially_locked",
            "user_overlay_is_local_and_not_officially_verified",
            "no_validated_nonuniform_signal",
            "not_a_claim_of_improved_lottery_odds",
        ],
    }
