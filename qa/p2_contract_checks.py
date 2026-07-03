"""Product Gate P2 schema, cutoff, reproducibility, hash, and disclosure checks."""

from __future__ import annotations

import copy
import json
import pathlib
import tempfile
from typing import Any, Mapping, Sequence
from unittest.mock import patch

from jsonschema import Draft202012Validator

from engine.hashing import sha256_value
from product.config import DEFAULT_PRODUCT_CONFIG, EXPECTED_DATA_HASH, PRODUCT_WEIGHTS
from product.run_prediction import _model_hash, run_product_prediction

from .p2_common import (
    CANONICAL_GENERATED_AT,
    CANONICAL_LAST_DRAW,
    CANONICAL_RECORD_COUNT,
    CANONICAL_TARGET_DRAW,
    UNIFORM_PROBABILITY,
    CheckResult,
    negative_payload_mutations,
    read_json,
    sha256_file,
    validate_payload,
)


def schema_checks(root: pathlib.Path, canonical: Mapping[str, Any]) -> tuple[CheckResult, CheckResult]:
    schema = read_json(root / "schemas" / "product_prediction.schema.json")
    Draft202012Validator.check_schema(schema)
    positive_errors = validate_payload(canonical, schema)
    negative_results: dict[str, Any] = {}
    for name, mutation in negative_payload_mutations(canonical).items():
        errors = validate_payload(mutation, schema)
        negative_results[name] = {"rejected": bool(errors), "errors": errors[:5]}
    positive = CheckResult("PASS" if not positive_errors else "FAIL", {"errors": positive_errors})
    negative = CheckResult(
        "PASS" if all(result["rejected"] for result in negative_results.values()) else "FAIL",
        {"mutations": negative_results},
    )
    return positive, negative


def cutoff_checks(root: pathlib.Path, canonical: Mapping[str, Any]) -> tuple[CheckResult, CheckResult]:
    cutoff = canonical["diagnostics"]["cutoff"]
    positive_checks = {
        "target": cutoff["target_draw_no"] == CANONICAL_TARGET_DRAW,
        "first": cutoff["input_first_draw"] == 1,
        "last": cutoff["input_last_draw"] == CANONICAL_LAST_DRAW,
        "count": cutoff["input_record_count"] == CANONICAL_RECORD_COUNT,
        "no_silent_exclusion": cutoff["excluded_draws_at_or_after_target"] == 0,
        "hash": cutoff["cutoff_hash"] == sha256_value({key: value for key, value in cutoff.items() if key != "cutoff_hash"}),
    }

    dataset_payload = read_json(root / "data" / "draws.json")
    cases: dict[str, dict[str, Any]] = {}

    def runner_rejects(name: str, payload: dict[str, Any], target: int) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "draws.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            expected_hash = sha256_file(path)
            error: str | None = None
            optimizer_called = False
            with patch("product.run_prediction.EXPECTED_DATA_HASH", expected_hash), patch(
                "product.run_prediction.optimize_candidates"
            ) as optimizer:
                try:
                    run_product_prediction(
                        target_draw_no=target,
                        dataset_path=path,
                        generated_at=CANONICAL_GENERATED_AT,
                    )
                except Exception as exc:  # noqa: BLE001 - the contract is rejection, not exception class.
                    error = f"{type(exc).__name__}: {exc}"
                optimizer_called = optimizer.called
            cases[name] = {"rejected": error is not None, "before_candidate_generation": not optimizer_called, "error": error}

    future = copy.deepcopy(dataset_payload)
    next_record = copy.deepcopy(future["records"][-1])
    next_record["draw_no"] = CANONICAL_TARGET_DRAW
    next_record["draw_date"] = "2026-07-04"
    future["records"].append(next_record)
    runner_rejects("target_or_later_record", future, CANONICAL_TARGET_DRAW)
    runner_rejects("silent_future_truncation_forbidden", copy.deepcopy(future), CANONICAL_TARGET_DRAW)

    missing_last = copy.deepcopy(dataset_payload)
    missing_last["records"] = missing_last["records"][:-1]
    runner_rejects("missing_target_minus_one", missing_last, CANONICAL_TARGET_DRAW)

    duplicate = copy.deepcopy(dataset_payload)
    duplicate["records"].append(copy.deepcopy(duplicate["records"][-1]))
    runner_rejects("duplicate_draw", duplicate, CANONICAL_TARGET_DRAW)

    runner_rejects("invalid_target", copy.deepcopy(dataset_payload), 1)

    false_metadata = copy.deepcopy(canonical)
    false_metadata["diagnostics"]["cutoff"]["input_record_count"] -= 1
    schema = read_json(root / "schemas" / "product_prediction.schema.json")
    false_errors = validate_payload(false_metadata, schema)
    cases["false_cutoff_metadata"] = {
        "rejected": bool(false_errors),
        "before_candidate_generation": True,
        "error": false_errors[:5],
    }

    positive = CheckResult("PASS" if all(positive_checks.values()) else "FAIL", {"checks": positive_checks})
    negative = CheckResult(
        "PASS" if all(item["rejected"] and item["before_candidate_generation"] for item in cases.values()) else "FAIL",
        {"cases": cases},
    )
    return positive, negative


def shadow_and_repeatability_checks(core_snapshots: Sequence[Mapping[str, Any]]) -> tuple[CheckResult, CheckResult, CheckResult]:
    per_runtime = {
        snapshot["python_version"]: {
            "repeats_equal": snapshot.get("repeats_equal"),
            "generated_at_invariant": snapshot.get("generated_at_invariant"),
            "shadow_isolation": snapshot.get("shadow_isolation"),
            "target_change_invalidates_seed": snapshot.get("target_change_invalidates_seed"),
        }
        for snapshot in core_snapshots
    }
    shadow_pass = all(value["shadow_isolation"] for value in per_runtime.values())
    repeat_pass = all(
        value["repeats_equal"] and value["generated_at_invariant"] and value["target_change_invalidates_seed"]
        for value in per_runtime.values()
    )
    versions = {".".join(snapshot["python_version"].split(".")[:2]) for snapshot in core_snapshots}
    cross_pass = versions == {"3.11", "3.12"} and len(core_snapshots) == 2 and core_snapshots[0]["core"] == core_snapshots[1]["core"]
    return (
        CheckResult("PASS" if shadow_pass else "FAIL", {"per_runtime": per_runtime}),
        CheckResult("PASS" if repeat_pass else "FAIL", {"per_runtime": per_runtime}),
        CheckResult(
            "PASS" if cross_pass else "FAIL",
            {"python_versions": sorted(versions), "product_core_equal": len(core_snapshots) == 2 and core_snapshots[0]["core"] == core_snapshots[1]["core"]},
        ),
    )


def hash_checks(root: pathlib.Path, canonical: Mapping[str, Any]) -> CheckResult:
    data_hash = sha256_file(root / "data" / "draws.json")
    assembly = read_json(root / "release" / "assembly_manifest.json")
    rollback = read_json(root / "release" / "rollback_manifest.json")
    p1_report = read_json(root / "reports" / "product_p1_acceptance.json")
    assembly_data = next(asset for asset in assembly["source_assets"] if asset["destination_path"] == "data/draws.json")

    config_hash = sha256_value(DEFAULT_PRODUCT_CONFIG.effective_payload)
    model_hash = _model_hash(root)
    cutoff = canonical["diagnostics"]["cutoff"]
    cutoff_hash = sha256_value({key: value for key, value in cutoff.items() if key != "cutoff_hash"})
    prediction_payload = {
        "contract_version": canonical["contract_version"],
        "target_draw_no": canonical["target_draw_no"],
        "input_last_draw": canonical["input_last_draw"],
        "data_version": canonical["versions"]["data_version"],
        "data_hash": canonical["hashes"]["data_hash"],
        "model_version": canonical["versions"]["model_version"],
        "model_hash": canonical["hashes"]["model_hash"],
        "config_hash": canonical["hashes"]["config_hash"],
        "seed": canonical["seed"],
        "product_weights": canonical["product_weights"],
        "candidate_sets": canonical["candidate_sets"],
        "statistical_edge": canonical["statistical_edge"],
        "reason": canonical["reason"],
    }
    prediction_hash = sha256_value(prediction_payload)
    checks = {
        "data_vs_config": data_hash == EXPECTED_DATA_HASH,
        "data_vs_assembly": data_hash == assembly_data.get("content_sha256"),
        "data_vs_rollback": data_hash == rollback["source_asset_hashes"]["data/draws.json"],
        "data_vs_p1_report": data_hash == p1_report["dataset"]["sha256"],
        "config_hash": config_hash == canonical["hashes"]["config_hash"],
        "model_hash": model_hash == canonical["hashes"]["model_hash"],
        "prediction_hash": prediction_hash == canonical["hashes"]["prediction_hash"],
        "cutoff_hash": cutoff_hash == cutoff["cutoff_hash"],
    }
    return CheckResult(
        "PASS" if all(checks.values()) else "FAIL",
        {
            "checks": checks,
            "recomputed": {
                "data_hash": data_hash,
                "config_hash": config_hash,
                "model_hash": model_hash,
                "prediction_hash": prediction_hash,
                "cutoff_hash": cutoff_hash,
            },
        },
    )


def disclosure_check(canonical: Mapping[str, Any]) -> tuple[CheckResult, CheckResult]:
    distribution_checks = {
        "final_distribution": canonical["final_distribution"] == "M0_ONLY",
        "weights": canonical["product_weights"] == PRODUCT_WEIGHTS,
        "uniform_probability": all(candidate["joint_probability"] == UNIFORM_PROBABILITY for candidate in canonical["candidate_sets"]),
        "uniform_lift": all(candidate["lift_vs_uniform"] == 1.0 for candidate in canonical["candidate_sets"]),
    }
    disclosure_checks = {
        "statistical_edge": canonical["statistical_edge"] is False,
        "reason": canonical["reason"] == "no_validated_nonuniform_signal",
        "research_only": canonical["research_only"] is True,
        "public_release_allowed": canonical["public_release_allowed"] is False,
        "advantage_status": canonical["advantage_status"] == "통계적 우위 없음",
    }
    return (
        CheckResult("PASS" if all(distribution_checks.values()) else "FAIL", {"checks": distribution_checks}),
        CheckResult("PASS" if all(disclosure_checks.values()) else "FAIL", {"checks": disclosure_checks}),
    )
