"""Product Gate P2 repository, manifest, rollback, and frozen-history checks."""

from __future__ import annotations

import pathlib
from typing import Any

from product.config import EXPECTED_DATA_HASH
from product.run_prediction import _MODEL_SOURCE_PATHS

from .p2_common import (
    P1_ACCEPTANCE_SHA256,
    P1_IMPLEMENTATION_LOCK,
    P1_WORKFLOW_RUN_ID,
    CheckResult,
    blob_at,
    commit_exists,
    git,
    is_ancestor,
    read_json,
    sha256_file,
)

FROZEN_RESEARCH_PATHS = (
    "reports/data_integrity.json",
    "reports/gate2_3p3_full_summary.md",
    "reports/gate2_3p_r3_dev_lock.json",
    "reports/gate2_3p_r3m2_oracle_dev_lock.json",
    "reports/gate2_3p_r3m3_predictable_group_dev_lock.json",
)


def p1_preflight(root: pathlib.Path) -> CheckResult:
    report_path = root / "reports" / "product_p1_acceptance.json"
    lock_path = root / "reports" / "product_p1_acceptance_lock.json"
    report = read_json(report_path)
    lock = read_json(lock_path)
    actual_report_hash = sha256_file(report_path)
    checks = {
        "p1_report_sha_matches_constant": actual_report_hash == P1_ACCEPTANCE_SHA256,
        "p1_report_sha_matches_lock": actual_report_hash == lock.get("report_sha256"),
        "implementation_lock_matches_report": report.get("implementation_lock_commit") == P1_IMPLEMENTATION_LOCK,
        "implementation_lock_matches_lock": lock.get("implementation_lock_commit") == P1_IMPLEMENTATION_LOCK,
        "workflow_matches": report.get("workflow", {}).get("run_id") == P1_WORKFLOW_RUN_ID,
        "workflow_success": report.get("workflow", {}).get("conclusion") == "success",
        "dataset_hash_matches": report.get("dataset", {}).get("sha256") == EXPECTED_DATA_HASH,
        "distribution_m0_only": report.get("product_lock", {}).get("final_distribution") == "M0_ONLY",
        "lock_commit_exists": commit_exists(root, P1_IMPLEMENTATION_LOCK),
    }
    return CheckResult("PASS" if all(checks.values()) else "FAIL", {"checks": checks, "actual_report_sha256": actual_report_hash})


def assembly_manifest_check(root: pathlib.Path) -> CheckResult:
    manifest = read_json(root / "release" / "assembly_manifest.json")
    source_commits = {
        manifest["gate1_source"]["ref"]: manifest["gate1_source"]["commit"],
        manifest["engine_source"]["ref"]: manifest["engine_source"]["commit"],
    }
    results: list[dict[str, Any]] = []
    all_pass = True
    declared_destinations = {asset["destination_path"] for asset in manifest["source_assets"]}

    for asset in manifest["source_assets"]:
        source_ref = asset["source_ref"]
        source_commit = source_commits.get(source_ref)
        remote_ref = f"refs/remotes/origin/{source_ref}"
        source_blob = None if source_commit is None else blob_at(root, source_commit, asset["source_path"])
        destination = root / asset["destination_path"]
        destination_blob = git(root, "hash-object", asset["destination_path"], check=False) if destination.exists() else None
        checks = {
            "source_ref_exists": bool(git(root, "rev-parse", "--verify", remote_ref, check=False)),
            "source_commit_exists": bool(source_commit and commit_exists(root, source_commit)),
            "source_commit_on_ref": bool(source_commit and git(root, "rev-parse", "--verify", remote_ref, check=False) and is_ancestor(root, source_commit, remote_ref)),
            "source_path_exists": source_blob is not None,
            "source_blob_matches": source_blob == asset["source_blob_sha"],
            "destination_exists": destination.exists(),
            "destination_blob_matches": destination_blob == asset["source_blob_sha"],
        }
        if "content_sha256" in asset:
            checks["content_sha256_matches"] = destination.exists() and sha256_file(destination) == asset["content_sha256"]
        passed = all(checks.values())
        all_pass = all_pass and passed
        results.append({"path": asset["destination_path"], "status": "PASS" if passed else "FAIL", "checks": checks})

    undeclared_engine_sources = [
        path for path in _MODEL_SOURCE_PATHS if path.startswith("engine/") and path not in declared_destinations
    ]
    if undeclared_engine_sources:
        all_pass = False
    return CheckResult(
        "PASS" if all_pass else "FAIL",
        {"assets": results, "undeclared_product_critical_engine_sources": undeclared_engine_sources},
    )


def rollback_manifest_check(root: pathlib.Path) -> CheckResult:
    rollback = read_json(root / "release" / "rollback_manifest.json")
    p1_report = read_json(root / "reports" / "product_p1_acceptance.json")
    implementation_lock = p1_report["implementation_lock_commit"]
    checks = {
        "base_commit_exists": commit_exists(root, rollback["base_commit"]),
        "pre_assembly_commit_exists": commit_exists(root, rollback["pre_assembly_commit"]),
        "assembled_commit_exists": commit_exists(root, rollback["assembled_commit"]),
        "implementation_lock_exists": commit_exists(root, implementation_lock),
        "base_equals_pre_assembly": rollback["base_commit"] == rollback["pre_assembly_commit"],
        "pre_assembly_ancestor_of_assembled": is_ancestor(root, rollback["pre_assembly_commit"], rollback["assembled_commit"]),
        "assembled_ancestor_of_lock": is_ancestor(root, rollback["assembled_commit"], implementation_lock),
        "before_artifact_policy": rollback["rollback_action_before_artifact"] == "reset implementation branch to pre_assembly_commit",
        "after_artifact_policy": rollback["rollback_action_after_artifact"] == "create revert commit",
        "force_rewrite_false": rollback["force_history_rewrite_after_artifact"] is False,
        "main_affected_false": rollback["main_affected"] is False,
    }
    hash_checks = {
        path: (root / path).exists() and sha256_file(root / path) == expected
        for path, expected in rollback["source_asset_hashes"].items()
    }
    checks["source_asset_hashes"] = all(hash_checks.values())
    return CheckResult(
        "PASS" if all(checks.values()) else "FAIL",
        {
            "checks": checks,
            "source_asset_hashes": hash_checks,
            "implementation_lock_source": "reports/product_p1_acceptance.json",
            "implementation_lock_commit": implementation_lock,
        },
    )


def frozen_research_check(root: pathlib.Path) -> CheckResult:
    path_results: dict[str, Any] = {}
    all_pass = True
    for path in FROZEN_RESEARCH_PATHS:
        locked_blob = blob_at(root, P1_IMPLEMENTATION_LOCK, path)
        current = root / path
        current_blob = git(root, "hash-object", path, check=False) if current.exists() else None
        passed = locked_blob is not None and current_blob == locked_blob
        path_results[path] = {"locked_blob": locked_blob, "current_blob": current_blob, "unchanged": passed}
        all_pass = all_pass and passed
    return CheckResult("PASS" if all_pass else "FAIL", {"paths": path_results})
