"""Orchestrator for Product Closeout Gate C2 offline QA."""

from __future__ import annotations

import platform
from typing import Any

from engine.hashing import sha256_value

from .checks_data import verify_cutoff, verify_data, verify_data_negative_cases
from .checks_product import verify_hashes, verify_prediction, verify_schema
from .checks_repo import (
    forbidden_execution_status,
    verify_a4_snapshot,
    verify_isolation,
    verify_repository_preservation,
)
from .common import repo_root
from .constants import (
    A4_CANONICAL_RESULT_HASH,
    A4_DRAFT_PR,
    BASE_COMMIT,
    FIXED_GENERATED_AT,
    FIXED_TARGET,
    QA_CONTRACT_VERSION,
    SPEC_CONTRACT_VERSION,
)


def run_internal_qa() -> dict[str, Any]:
    root = repo_root()
    checks: dict[str, Any] = {}
    checks["Q1_data_identity"] = verify_data(root)
    checks["Q2_data_negative_cases"] = verify_data_negative_cases(root)
    checks["Q3_target_minus_one_cutoff"] = verify_cutoff(root)
    prediction_check, prediction = verify_prediction(root)
    checks["Q4_output_contract"] = prediction_check
    checks["Q5_schema_positive_negative"] = verify_schema(root, prediction)
    checks["Q6_research_ensemble_isolation"] = verify_isolation(root)
    checks["Q7_hash_manifest_rollback"] = verify_hashes(root, prediction)
    checks["Q8_repository_preservation"] = verify_repository_preservation(root)
    checks["Q9_A4_preservation_snapshot"] = verify_a4_snapshot(root)
    checks["Q10_fixed_disclosure"] = {
        "pass": (
            prediction["statistical_edge"] is False
            and prediction["reason"] == "no_validated_nonuniform_signal"
            and prediction["research_only"] is True
            and prediction["public_release_allowed"] is False
            and "canonical_data_auto_checked_not_officially_locked" in prediction["limitations"]
        ),
        "statistical_edge": prediction["statistical_edge"],
        "reason": prediction["reason"],
        "limitations": prediction["limitations"],
    }
    checks["Q11_forbidden_execution"] = forbidden_execution_status()

    failed = [name for name, value in checks.items() if not bool(value.get("pass"))]
    status = "PRODUCT_CLOSEOUT_QA_PASS_CANDIDATE" if not failed else "PRODUCT_CLOSEOUT_QA_FAIL"
    canonical_result: dict[str, Any] = {
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
        "A4_draft_pr": A4_DRAFT_PR,
        "A4_canonical_result_hash": A4_CANONICAL_RESULT_HASH,
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "reason": "no_validated_nonuniform_signal",
        "next_gate_authorized": False,
    }
    canonical_result_hash = sha256_value(canonical_result)
    canonical_result["canonical_result_hash"] = canonical_result_hash
    return {
        "runtime": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "canonical_result": canonical_result,
        "canonical_result_hash": canonical_result_hash,
    }
