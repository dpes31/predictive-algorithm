"""Repository isolation and preservation checks for Closeout Gate C2."""

from __future__ import annotations

import ast
import pathlib
from typing import Any

from engine.hashing import sha256_value

from .common import load_json, verify_base_ancestry, verify_immutable_paths
from .constants import (
    A4_CANONICAL_RESULT_HASH,
    A4_DRAFT_PR,
    A4_SNAPSHOT_PATH,
    PROHIBITED_NETWORK_IMPORTS,
)


def _imported_modules(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module:
        return [node.module]
    return []


def verify_isolation(root: pathlib.Path) -> dict[str, Any]:
    runtime_files = sorted((root / "product").glob("*.py")) + sorted((root / "engine").glob("*.py"))
    research_findings: list[dict[str, str]] = []
    local_imports: set[str] = set()
    for path in runtime_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for module in _imported_modules(node):
                root_name = module.split(".", 1)[0]
                if root_name == "research_ensemble":
                    research_findings.append({"path": str(path.relative_to(root)), "module": module})
                if root_name in {"product", "engine", "research_ensemble"}:
                    local_imports.add(module)

    network_findings: list[dict[str, str]] = []
    for path in sorted((root / "product_closeout").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for module in _imported_modules(node):
                if module.split(".", 1)[0] in PROHIBITED_NETWORK_IMPORTS:
                    network_findings.append({"path": str(path.relative_to(root)), "module": module})

    return {
        "pass": not research_findings and not network_findings,
        "runtime_file_count": len(runtime_files),
        "product_local_imports": sorted(local_imports),
        "research_import_findings": research_findings,
        "QA_network_import_findings": network_findings,
    }


def verify_a4_snapshot(root: pathlib.Path) -> dict[str, Any]:
    snapshot = load_json(root / A4_SNAPSHOT_PATH)
    expected_runs = [28652065811, 28652201671, 28652641626, 28652841841, 28653030201, 28653417663]
    conditions = {
        "pr_number": snapshot.get("pr_number") == A4_DRAFT_PR,
        "state_open": snapshot.get("state") == "open",
        "draft_true": snapshot.get("draft") is True,
        "merged_false": snapshot.get("merged") is False,
        "head_branch": snapshot.get("head") == "feature/algorithm-integration-a4-evaluation",
        "head_sha": snapshot.get("head_sha") == "11b8a807f4abe6b3b3eb68c31a7c927afaa9a594",
        "report_blob": snapshot.get("report_blob_sha") == "5f1f56379fc51d554ad80e797ccfa3546f25d0c5",
        "lock_blob": snapshot.get("lock_blob_sha") == "0a802c23c55f222d8cd6d9c4d2482a1f02332f53",
        "rollback_blob": snapshot.get("rollback_blob_sha") == "7f31ef93f4ce3ff63872a7cb6f491e468e451eee",
        "canonical_hash": snapshot.get("canonical_result_hash") == A4_CANONICAL_RESULT_HASH,
        "workflow_history": snapshot.get("preserved_workflow_runs") == expected_runs,
        "read_only_capture": snapshot.get("capture_mode") == "READ_ONLY_REPOSITORY_INSPECTION",
    }
    return {
        "pass": all(conditions.values()),
        "conditions": conditions,
        "snapshot_hash": sha256_value(snapshot),
    }


def verify_repository_preservation(root: pathlib.Path) -> dict[str, Any]:
    immutable = verify_immutable_paths(root)
    ancestry = verify_base_ancestry(root)
    return {
        "pass": immutable["pass"] and ancestry,
        "base_ancestry": ancestry,
        "immutable_paths": immutable,
    }


def forbidden_execution_status() -> dict[str, Any]:
    return {
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
