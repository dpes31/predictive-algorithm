"""Product Gate P2 official reconciliation and integration QA CLI."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any, Mapping, Sequence

from engine.data_loader import load_dataset
from product.config import DATASET_VERSION, EXPECTED_DATA_HASH
from product.run_prediction import _repo_root, run_product_prediction

from .p2_contract_checks import (
    cutoff_checks,
    disclosure_check,
    hash_checks,
    schema_checks,
    shadow_and_repeatability_checks,
)
from .p2_repository_checks import (
    assembly_manifest_check,
    frozen_research_check,
    p1_preflight,
    rollback_manifest_check,
)
from .p2_common import (
    CANONICAL_GENERATED_AT,
    CANONICAL_RECORD_COUNT,
    CANONICAL_TARGET_DRAW,
    P1_IMPLEMENTATION_LOCK,
    P2_CONTRACT_VERSION,
    CheckResult,
    generate_core_snapshot,
    read_json,
    sha256_file,
    utc_now,
    write_json,
)
from .p2_official import reconcile_official


def run_full_qa(
    *,
    root: pathlib.Path,
    dataset: pathlib.Path,
    core_snapshots: Sequence[Mapping[str, Any]],
    output_dir: pathlib.Path,
    qa_commit: str,
    workflow_run_id: str,
    workflow_run_number: str,
    actor: str,
    timeout_seconds: float,
    retries: int,
    delay_seconds: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    executed_at = utc_now()
    canonical = run_product_prediction(
        target_draw_no=CANONICAL_TARGET_DRAW,
        dataset_path=dataset,
        generated_at=CANONICAL_GENERATED_AT,
    )

    preflight = p1_preflight(root)
    reconciliation, source_manifest = reconcile_official(
        load_dataset(dataset)[1],
        timeout_seconds=timeout_seconds,
        retries=retries,
        delay_seconds=delay_seconds,
        retrieved_at=executed_at,
    )
    reconciliation_path = output_dir / "product_p2_official_reconciliation.json"
    source_manifest_path = output_dir / "product_p2_source_manifest.json"
    write_json(reconciliation_path, reconciliation)
    write_json(source_manifest_path, source_manifest)
    reconciliation_hash = sha256_file(reconciliation_path)
    source_manifest_hash = sha256_file(source_manifest_path)

    schema_positive, schema_negative = schema_checks(root, canonical)
    cutoff_positive, cutoff_negative = cutoff_checks(root, canonical)
    shadow, repeatability, cross_runtime = shadow_and_repeatability_checks(core_snapshots)
    hashes = hash_checks(root, canonical)
    assembly = assembly_manifest_check(root)
    rollback = rollback_manifest_check(root)
    distribution, disclosure = disclosure_check(canonical)
    frozen = frozen_research_check(root)

    official_status = reconciliation["status"]
    if official_status == "OFFICIALLY_VERIFIED":
        b2 = CheckResult(
            "PASS",
            {
                "selected_source": source_manifest["selected_source"],
                "source_manifest_sha256": source_manifest_hash,
                "official_records_sha256": source_manifest["official_records_sha256"],
            },
        )
        b3 = CheckResult(
            "PASS" if all(reconciliation[key] == expected for key, expected in {
                "matched": CANONICAL_RECORD_COUNT,
                "missing": 0,
                "extra": 0,
                "field_mismatches": 0,
                "unresolved": 0,
            }.items()) else "FAIL",
            {key: reconciliation[key] for key in ("matched", "missing", "extra", "field_mismatches", "unresolved")},
        )
        b4 = CheckResult("PASS", {"state": "OFFICIALLY_VERIFIED", "transitions": reconciliation["state_transitions"]})
        lock_package = {
            "canonical_data_version": DATASET_VERSION,
            "canonical_data_sha256": EXPECTED_DATA_HASH,
            "official_records_sha256": source_manifest["official_records_sha256"],
            "source_manifest_sha256": source_manifest_hash,
            "reconciliation_report_sha256": reconciliation_hash,
            "approval_identity": f"github-actions:{actor}",
            "approval_timestamp": executed_at,
            "immutable_qa_commit": qa_commit,
        }
        lock_complete = all(lock_package.values()) and re.fullmatch(r"[a-f0-9]{40}", qa_commit) is not None
        b5 = CheckResult("PASS" if lock_complete else "FAIL", {"canonical_state": "LOCKED" if lock_complete else "OFFICIALLY_VERIFIED", "lock_package": lock_package})
        canonical_final_state = "LOCKED" if lock_complete else "OFFICIALLY_VERIFIED"
    elif official_status == "OFFICIAL_RECONCILIATION_BLOCKED":
        reason = reconciliation.get("reason", "official source unavailable")
        b2 = CheckResult("BLOCKED", {"reason": reason, "source_attempts": source_manifest["selection_attempts"]})
        b3 = CheckResult("BLOCKED", {"reason": "full zero-mismatch reconciliation unavailable"})
        b4 = CheckResult("BLOCKED", {"state": "OFFICIAL_RECONCILIATION_BLOCKED", "transitions": reconciliation["state_transitions"]})
        b5 = CheckResult("BLOCKED", {"reason": "OFFICIALLY_VERIFIED prerequisite not reached"})
        canonical_final_state = "OFFICIAL_RECONCILIATION_BLOCKED"
    else:
        b2 = CheckResult("PASS", {"selected_source": source_manifest["selected_source"], "source_manifest_sha256": source_manifest_hash})
        b3 = CheckResult("FAIL", {key: reconciliation[key] for key in ("matched", "missing", "extra", "field_mismatches", "unresolved")})
        b4 = CheckResult("FAIL", {"state": "OFFICIAL_RECONCILIATION_FAIL", "transitions": reconciliation["state_transitions"]})
        b5 = CheckResult("FAIL", {"reason": "official reconciliation mismatch"})
        canonical_final_state = "OFFICIAL_RECONCILIATION_FAIL"

    criteria: dict[str, CheckResult] = {
        "B1": preflight,
        "B2": b2,
        "B3": b3,
        "B4": b4,
        "B5": b5,
        "B6": schema_positive,
        "B7": schema_negative,
        "B8": cutoff_positive,
        "B9": cutoff_negative,
        "B10": shadow,
        "B11": repeatability,
        "B12": cross_runtime,
        "B13": hashes,
        "B14": assembly,
        "B15": rollback,
        "B16": distribution,
        "B17": disclosure,
        "B18": frozen,
    }
    statuses = [result.status for result in criteria.values()]
    if "FAIL" in statuses:
        final_status = "P2_QA_FAIL"
    elif "BLOCKED" in statuses:
        final_status = "P2_QA_BLOCKED"
    else:
        final_status = "P2_QA_PASS"

    qa_report = {
        "contract_version": P2_CONTRACT_VERSION,
        "status": final_status,
        "phase_status": "P2_PREFLIGHT_FAIL" if preflight.status == "FAIL" else "P2_EXECUTED",
        "p1_lock_commit": P1_IMPLEMENTATION_LOCK,
        "qa_commit": qa_commit,
        "workflow": {
            "run_id": workflow_run_id,
            "run_number": workflow_run_number,
            "python_versions": sorted(snapshot["python_version"] for snapshot in core_snapshots),
        },
        "executed_at": executed_at,
        "official_source_inventory": source_manifest,
        "reconciliation": {
            "status": reconciliation["status"],
            "counts": {key: reconciliation[key] for key in ("expected_draws", "matched", "missing", "extra", "field_mismatches", "unresolved")},
            "mismatch_count": len(reconciliation.get("mismatches", [])),
            "reconciliation_report_sha256": reconciliation_hash,
        },
        "canonical_state": {
            "initial": "AUTO_CHECKED",
            "transitions": reconciliation["state_transitions"],
            "final": canonical_final_state,
        },
        "schema": {"positive": schema_positive.to_dict(), "negative": schema_negative.to_dict()},
        "cutoff": {"positive": cutoff_positive.to_dict(), "negative": cutoff_negative.to_dict()},
        "shadow_isolation": shadow.to_dict(),
        "reproducibility": {"repeatability": repeatability.to_dict(), "cross_runtime": cross_runtime.to_dict()},
        "hash_recomputation": hashes.to_dict(),
        "manifests": {"assembly": assembly.to_dict(), "rollback": rollback.to_dict(), "source_manifest_sha256": source_manifest_hash},
        "acceptance": {key: value.to_dict() for key, value in criteria.items()},
        "excluded_work": [
            "p3_html_mvp",
            "historical_or_prospective_walk_forward",
            "m1_m4_activation_or_tuning",
            "cal",
            "sealed",
            "mobile_ui",
            "supabase",
            "main_merge",
        ],
        "p3_authorized": False,
    }
    qa_report_path = output_dir / "product_p2_qa.json"
    write_json(qa_report_path, qa_report)
    qa_report_hash = sha256_file(qa_report_path)

    qa_lock = {
        "contract_version": P2_CONTRACT_VERSION,
        "status": final_status,
        "report_path": "reports/product_p2_qa.json",
        "report_sha256": qa_report_hash,
        "reconciliation_report_path": "reports/product_p2_official_reconciliation.json",
        "reconciliation_report_sha256": reconciliation_hash,
        "source_manifest_path": "release/product_p2_source_manifest.json",
        "source_manifest_sha256": source_manifest_hash,
        "qa_commit": qa_commit,
        "workflow_run_id": workflow_run_id,
        "workflow_run_number": workflow_run_number,
        "canonical_data_version": DATASET_VERSION,
        "canonical_data_sha256": EXPECTED_DATA_HASH,
        "canonical_data_state": canonical_final_state,
        "final_distribution": "M0_ONLY",
        "p3_authorized": False,
        "walk_forward_run": False,
        "html_modified": False,
        "cal": False,
        "sealed": False,
        "mobile_modified": False,
        "main_merged": False,
    }
    write_json(output_dir / "product_p2_qa_lock.json", qa_lock)
    return qa_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Product Gate P2 data and integration QA")
    subparsers = parser.add_subparsers(dest="command", required=True)

    core = subparsers.add_parser("core", help="Generate deterministic product-core snapshot")
    core.add_argument("--dataset", default="data/draws.json")
    core.add_argument("--output", required=True)

    full = subparsers.add_parser("full", help="Execute official reconciliation and B1-B18 QA")
    full.add_argument("--dataset", default="data/draws.json")
    full.add_argument("--core-snapshot", action="append", required=True)
    full.add_argument("--output-dir", required=True)
    full.add_argument("--qa-commit", required=True)
    full.add_argument("--workflow-run-id", required=True)
    full.add_argument("--workflow-run-number", required=True)
    full.add_argument("--actor", required=True)
    full.add_argument("--timeout-seconds", type=float, default=15.0)
    full.add_argument("--retries", type=int, default=2)
    full.add_argument("--delay-seconds", type=float, default=0.02)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _repo_root()
    if args.command == "core":
        snapshot = generate_core_snapshot(root, root / args.dataset)
        write_json(pathlib.Path(args.output), snapshot)
        return 0

    snapshots = [read_json(pathlib.Path(path)) for path in args.core_snapshot]
    report = run_full_qa(
        root=root,
        dataset=root / args.dataset,
        core_snapshots=snapshots,
        output_dir=pathlib.Path(args.output_dir),
        qa_commit=args.qa_commit,
        workflow_run_id=args.workflow_run_id,
        workflow_run_number=args.workflow_run_number,
        actor=args.actor,
        timeout_seconds=args.timeout_seconds,
        retries=args.retries,
        delay_seconds=args.delay_seconds,
    )
    print(json.dumps({"status": report["status"], "acceptance": {key: value["status"] for key, value in report["acceptance"].items()}}, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "P2_QA_FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
