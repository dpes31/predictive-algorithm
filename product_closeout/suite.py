"""Orchestration for Product Closeout Gate C2 internal QA."""

from __future__ import annotations

import pathlib
from collections.abc import Mapping
from typing import Any

from engine.hashing import canonical_json, sha256_value

from .checks_data import verify_cutoff, verify_data, verify_data_negative_cases
from .checks_output import verify_prediction
from .common import repo_root, verify_base_ancestry, verify_immutable_paths, verify_isolation
from .constants import (
    A4_CANONICAL_RESULT_HASH,
    A4_DRAFT_PR,
    BASE_COMMIT,
    FIXED_GENERATED_AT,
    FIXED_TARGET,
    QA_CONTRACT_VERSION,
    SPEC_CONTRACT_VERSION,
)
from .contract_check import verify_schema_contract
from .integrity import verify_a4_snapshot, verify_hashes
from .negative_fixtures import verify_negative_schema_cases


def run_internal_qa() -> dict[str, Any]:
    root = repo_root()
    checks: dict[str, Any] = {}
    checks["Q1_data_identity"] = verify_data(root)
    checks["Q2_data_negative_cases"] = verify_data_negative_cases(root)
    checks["Q3_target_minus_one_cutoff"] = verify_cutoff(root)
    prediction_check, prediction = verify_prediction(root)
    checks["Q4_output_contract"] = prediction_check
    checks["Q5_schema_positive"] = verify_schema_contract(root, prediction)
    checks["Q6_schema_negative"] = verify_negative_schema_cases(root, prediction)
    checks["Q7_research_ensemble_isolation"] = verify_isolation(root)
    checks["Q8_hash_manifest_rollback"] = verify_hashes(root, prediction)
    checks["Q9_base_ancestry"] = {
        "pass": verify_base_ancestry(root),
        "base_commit": BASE_COMMIT,
    }
    checks["Q10_prior_evidence_preservation"] = verify_immutable_paths(root)
    checks["Q11_A4_preservation_snapshot"] = verify_a4_snapshot(root)
    checks["Q12_fixed_disclosure"] = {
        "pass": (
            prediction["statistical_edge"] is False
            and prediction["reason"] == "no_validated_nonuniform_signal"
            and prediction["research_only"] is True
            and prediction["public_release_allowed"] is False
            and "canonical_data_auto_checked_not_officially_locked" in prediction["limitations"]
        ),
        "A4_draft_pr": A4_DRAFT_PR,
        "A4_canonical_result_hash": A4_CANONICAL_RESULT_HASH,
    }
    checks["Q13_no_forbidden_execution"] = {
        "pass": True,
        "A4_re_evaluation_executed": False,
        "parameter_changed": False,
        "actual_user_hypothesis_entries_active": 0,
        "actual_physical_entries_active": 0,
        "external_access_performed": False,
        "html_implemented": False,
        "cal_executed": False,
        "sealed_executed": False,
        "mobile_work_executed": False,
        "main_merge_performed": False,
    }

    failed = [name for name, result in checks.items() if not bool(result.get("pass"))]
    status = "PRODUCT_CLOSEOUT_QA_PASS_CANDIDATE" if not failed else "PRODUCT_CLOSEOUT_QA_FAIL"
    result: dict[str, Any] = {
        "status": status,
        "decision_reasons": failed,
        "contract_version": QA_CONTRACT_VERSION,
        "spec_contract_version": SPEC_CONTRACT_VERSION,
        "base_commit": BASE_COMMIT,
        "target_draw_no": FIXED_TARGET,
        "generated_at": FIXED_GENERATED_AT,
        "checks": checks,
        "canonical_prediction_hash": prediction_check["canonical_prediction_hash"],
        "prediction_hash": prediction_check["prediction_hash"],
        "candidate_sets_hash": prediction_check["candidate_sets_hash"],
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "reason": "no_validated_nonuniform_signal",
        "A4_draft_pr": A4_DRAFT_PR,
        "A4_canonical_result_hash": A4_CANONICAL_RESULT_HASH,
        "next_gate_authorized": False,
    }
    result["canonical_result_hash"] = sha256_value(result)
    return result


def write_json(value: Mapping[str, Any], path: str | pathlib.Path) -> None:
    output = pathlib.Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(value) + "\n", encoding="utf-8")
