"""Product output, schema, and hash checks for Closeout Gate C2."""

from __future__ import annotations

import copy
import math
import pathlib
from collections.abc import Mapping
from typing import Any

from engine.hashing import deterministic_seed, sha256_value
from product.config import (
    DEFAULT_PRODUCT_CONFIG,
    ENGINE_CORE_VERSION,
    EXPECTED_DATA_HASH,
    MODEL_VERSION,
    PRODUCT_CONTRACT_VERSION,
    PRODUCT_WEIGHTS,
)
from product.run_prediction import run_product_prediction

from .common import file_git_blob, file_sha256, load_json
from .constants import FIXED_GENERATED_AT, FIXED_TARGET, MODEL_SOURCE_PATHS
from .schema_validator import SchemaValidationError, validate_json_schema


def independent_model_hash(root: pathlib.Path) -> str:
    source_hashes = {relative: file_sha256(root / relative) for relative in MODEL_SOURCE_PATHS}
    return sha256_value(
        {
            "contract_version": PRODUCT_CONTRACT_VERSION,
            "engine_core_version": ENGINE_CORE_VERSION,
            "product_weights": PRODUCT_WEIGHTS,
            "source_hashes": source_hashes,
        }
    )


def independent_prediction_hash(result: Mapping[str, Any]) -> str:
    return sha256_value(
        {
            "contract_version": result["contract_version"],
            "target_draw_no": result["target_draw_no"],
            "input_last_draw": result["input_last_draw"],
            "data_version": result["versions"]["data_version"],
            "data_hash": result["hashes"]["data_hash"],
            "model_version": result["versions"]["model_version"],
            "model_hash": result["hashes"]["model_hash"],
            "config_hash": result["hashes"]["config_hash"],
            "seed": result["seed"],
            "product_weights": result["product_weights"],
            "candidate_sets": result["candidate_sets"],
            "statistical_edge": result["statistical_edge"],
            "reason": result["reason"],
        }
    )


def generate_prediction(root: pathlib.Path, *, shadow: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return run_product_prediction(
        target_draw_no=FIXED_TARGET,
        dataset_path=root / "data/draws.json",
        generated_at=FIXED_GENERATED_AT,
        shadow_diagnostics=shadow,
    )


def verify_prediction(root: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    first = generate_prediction(root)
    second = generate_prediction(root)
    shadow = generate_prediction(
        root,
        shadow={"source": "C2_SYNTHETIC_SHADOW_FIXTURE", "research_ensemble_score": [0.1, -0.1]},
    )
    candidates = first["candidate_sets"]
    number_sets = [tuple(candidate["numbers"]) for candidate in candidates]
    uniform_probability = 1.0 / math.comb(45, 6)
    expected_seed = deterministic_seed(
        PRODUCT_CONTRACT_VERSION,
        EXPECTED_DATA_HASH,
        MODEL_VERSION,
        DEFAULT_PRODUCT_CONFIG.config_hash,
        FIXED_TARGET,
    )
    conditions = {
        "two_repeats_identical": first == second,
        "target_minus_one": first["input_last_draw"] == FIXED_TARGET - 1,
        "candidate_count": len(candidates) == 5,
        "candidate_size": all(len(candidate["numbers"]) == 6 for candidate in candidates),
        "number_range": all(all(1 <= number <= 45 for number in c["numbers"]) for c in candidates),
        "numbers_sorted": all(c["numbers"] == sorted(c["numbers"]) for c in candidates),
        "within_set_unique": all(len(set(c["numbers"])) == 6 for c in candidates),
        "between_set_unique": len(set(number_sets)) == 5,
        "ranks": sorted(c["rank"] for c in candidates) == [1, 2, 3, 4, 5],
        "uniform_probability": all(
            abs(float(c["joint_probability"]) - uniform_probability) <= 1e-18 for c in candidates
        ),
        "uniform_lift": all(c["lift_vs_uniform"] == 1.0 for c in candidates),
        "weights": first["product_weights"] == PRODUCT_WEIGHTS,
        "distribution": first["final_distribution"] == "M0_ONLY",
        "statistical_edge": first["statistical_edge"] is False,
        "reason": first["reason"] == "no_validated_nonuniform_signal",
        "research_only": first["research_only"] is True,
        "public_release_allowed": first["public_release_allowed"] is False,
        "advantage_status": first["advantage_status"] == "통계적 우위 없음",
        "seed": first["seed"] == expected_seed,
        "shadow_candidates_isolated": shadow["candidate_sets"] == first["candidate_sets"],
        "shadow_seed_isolated": shadow["seed"] == first["seed"],
        "shadow_prediction_hash_isolated": shadow["hashes"]["prediction_hash"] == first["hashes"]["prediction_hash"],
        "shadow_weights_isolated": shadow["product_weights"] == first["product_weights"],
    }
    result = {
        "pass": all(conditions.values()),
        "conditions": conditions,
        "canonical_prediction_hash": sha256_value(first),
        "prediction_hash": first["hashes"]["prediction_hash"],
        "candidate_sets_hash": sha256_value(candidates),
        "seed": first["seed"],
    }
    return result, first


def verify_schema(root: pathlib.Path, prediction: Mapping[str, Any]) -> dict[str, Any]:
    schema = load_json(root / "schemas/product_prediction.schema.json")
    validate_json_schema(prediction, schema)
    cases: dict[str, bool] = {}

    def rejected(name: str, mutator: Any) -> None:
        candidate = copy.deepcopy(prediction)
        mutator(candidate)
        try:
            validate_json_schema(candidate, schema)
        except SchemaValidationError:
            cases[name] = True
        else:
            cases[name] = False

    rejected("missing_required", lambda value: value.pop("reason"))
    rejected("additional_property", lambda value: value.__setitem__("unexpected", True))
    rejected("invalid_target_type", lambda value: value.__setitem__("target_draw_no", "1231"))
    rejected("candidate_count", lambda value: value["candidate_sets"].pop())
    rejected("number_range", lambda value: value["candidate_sets"][0]["numbers"].__setitem__(0, 0))
    rejected("duplicate_number", lambda value: value["candidate_sets"][0]["numbers"].__setitem__(1, value["candidate_sets"][0]["numbers"][0]))
    rejected("wrong_weights", lambda value: value["product_weights"].__setitem__("M1", 0.1))
    rejected("wrong_reason", lambda value: value.__setitem__("reason", "other"))
    rejected("wrong_lift", lambda value: value["candidate_sets"][0].__setitem__("lift_vs_uniform", 1.1))
    rejected("candidate_extra_property", lambda value: value["candidate_sets"][0].__setitem__("extra", 1))
    rejected("bad_datetime", lambda value: value.__setitem__("generated_at", "2026-07-03"))
    return {"pass": all(cases.values()), "positive": "PASS", "negative_cases": cases}


def verify_hashes(root: pathlib.Path, prediction: Mapping[str, Any]) -> dict[str, Any]:
    assembly = load_json(root / "release/assembly_manifest.json")
    rollback = load_json(root / "release/rollback_manifest.json")
    c1_report = load_json(root / "reports/product_closeout_spec_report.json")
    c1_lock = load_json(root / "reports/product_closeout_spec_lock.json")
    c1_spec = root / "docs/PRODUCT_CLOSEOUT_M0_SPEC.md"
    c1_report_path = root / "reports/product_closeout_spec_report.json"
    model_hash = independent_model_hash(root)
    prediction_hash = independent_prediction_hash(prediction)
    config_hash = sha256_value(DEFAULT_PRODUCT_CONFIG.effective_payload)
    data_asset = next(a for a in assembly["source_assets"] if a["destination_path"] == "data/draws.json")
    conditions = {
        "data_hash": prediction["hashes"]["data_hash"] == EXPECTED_DATA_HASH,
        "model_hash": prediction["hashes"]["model_hash"] == model_hash,
        "config_hash": prediction["hashes"]["config_hash"] == config_hash,
        "prediction_hash": prediction["hashes"]["prediction_hash"] == prediction_hash,
        "assembly_distribution": assembly["final_distribution"] == "M0_ONLY",
        "assembly_weights": assembly["product_weights"] == PRODUCT_WEIGHTS,
        "assembly_data_sha256": data_asset["content_sha256"] == EXPECTED_DATA_HASH,
        "rollback_main_unaffected": rollback["main_affected"] is False,
        "rollback_force_rewrite_false": rollback["force_history_rewrite_after_artifact"] is False,
        "c1_spec_blob": c1_report["spec_blob_sha"] == file_git_blob(c1_spec),
        "c1_lock_spec_blob": c1_lock["spec_blob_sha"] == file_git_blob(c1_spec),
        "c1_lock_report_blob": c1_lock["report_blob_sha"] == file_git_blob(c1_report_path),
    }
    return {
        "pass": all(conditions.values()),
        "conditions": conditions,
        "data_hash": EXPECTED_DATA_HASH,
        "model_hash": model_hash,
        "config_hash": config_hash,
        "prediction_hash": prediction_hash,
        "schema_hash": file_sha256(root / "schemas/product_prediction.schema.json"),
        "assembly_manifest_hash": file_sha256(root / "release/assembly_manifest.json"),
        "rollback_manifest_hash": file_sha256(root / "release/rollback_manifest.json"),
    }
