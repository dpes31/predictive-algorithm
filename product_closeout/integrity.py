"""Hash and manifest checks for Product Closeout Gate C2."""

from __future__ import annotations

import pathlib
from typing import Any

from engine.hashing import sha256_value
from product.config import (
    DEFAULT_PRODUCT_CONFIG,
    ENGINE_CORE_VERSION,
    EXPECTED_DATA_HASH,
    PRODUCT_CONTRACT_VERSION,
    PRODUCT_WEIGHTS,
)

from .common import file_git_blob, file_sha256, load_json
from .constants import A4_CANONICAL_RESULT_HASH, EXPECTED_WEIGHTS, MODEL_SOURCE_PATHS


def independent_model_hash(root: pathlib.Path) -> str:
    sources = {relative: file_sha256(root / relative) for relative in MODEL_SOURCE_PATHS}
    return sha256_value(
        {
            "contract_version": PRODUCT_CONTRACT_VERSION,
            "engine_core_version": ENGINE_CORE_VERSION,
            "product_weights": PRODUCT_WEIGHTS,
            "source_hashes": sources,
        }
    )


def independent_prediction_hash(result: dict[str, Any]) -> str:
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


def verify_hashes(root: pathlib.Path, prediction: dict[str, Any]) -> dict[str, Any]:
    assembly = load_json(root / "release/assembly_manifest.json")
    rollback = load_json(root / "release/rollback_manifest.json")
    c1_report = load_json(root / "reports/product_closeout_spec_report.json")
    c1_lock = load_json(root / "reports/product_closeout_spec_lock.json")
    c1_spec_path = root / "docs/PRODUCT_CLOSEOUT_M0_SPEC.md"
    c1_report_path = root / "reports/product_closeout_spec_report.json"
    c1_lock_path = root / "reports/product_closeout_spec_lock.json"
    model_hash = independent_model_hash(root)
    prediction_hash = independent_prediction_hash(prediction)
    config_hash = sha256_value(DEFAULT_PRODUCT_CONFIG.effective_payload)
    source_asset = next(item for item in assembly["source_assets"] if item["destination_path"] == "data/draws.json")
    conditions = {
        "data_hash": prediction["hashes"]["data_hash"] == EXPECTED_DATA_HASH,
        "model_hash": prediction["hashes"]["model_hash"] == model_hash,
        "config_hash": prediction["hashes"]["config_hash"] == config_hash,
        "prediction_hash": prediction["hashes"]["prediction_hash"] == prediction_hash,
        "assembly_contract": assembly["contract_version"] == PRODUCT_CONTRACT_VERSION,
        "assembly_distribution": assembly["final_distribution"] == "M0_ONLY",
        "assembly_weights": assembly["product_weights"] == EXPECTED_WEIGHTS,
        "assembly_data_sha256": source_asset["content_sha256"] == EXPECTED_DATA_HASH,
        "assembly_data_blob": source_asset["source_blob_sha"] == file_git_blob(root / "data/draws.json"),
        "rollback_contract": rollback["contract_version"] == PRODUCT_CONTRACT_VERSION,
        "rollback_main_unaffected": rollback["main_affected"] is False,
        "rollback_force_rewrite_false": rollback["force_history_rewrite_after_artifact"] is False,
        "c1_spec_blob": c1_report["spec_blob_sha"] == file_git_blob(c1_spec_path),
        "c1_lock_spec_blob": c1_lock["spec_blob_sha"] == file_git_blob(c1_spec_path),
        "c1_lock_report_blob": c1_lock["report_blob_sha"] == file_git_blob(c1_report_path),
        "c1_status": c1_report["status"] == "PRODUCT_CLOSEOUT_SPEC_COMPLETE",
        "c1_locked": c1_lock["status"] == "LOCKED",
        "c1_A4_hash": c1_lock["A4_canonical_result_hash"] == A4_CANONICAL_RESULT_HASH,
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
        "c1_spec_blob_sha": file_git_blob(c1_spec_path),
        "c1_report_blob_sha": file_git_blob(c1_report_path),
        "c1_lock_blob_sha": file_git_blob(c1_lock_path),
    }
