"""Shared helpers for Product Closeout Gate C2."""

from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import subprocess
from typing import Any

from engine.hashing import sha256_value

from .constants import BASE_COMMIT, IMMUTABLE_BASE_PATHS, PROHIBITED_NETWORK_IMPORTS


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("utf-8")
    return hashlib.sha1(header + value, usedforsecurity=False).hexdigest()


def file_sha256(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())


def file_git_blob(path: pathlib.Path) -> str:
    return git_blob_sha(path.read_bytes())


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_output(root: pathlib.Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def verify_base_ancestry(root: pathlib.Path) -> bool:
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE_COMMIT, "HEAD"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def verify_immutable_paths(root: pathlib.Path) -> dict[str, Any]:
    details: dict[str, Any] = {}
    all_match = True
    for relative in IMMUTABLE_BASE_PATHS:
        current = root / relative
        try:
            expected = git_output(root, "show", f"{BASE_COMMIT}:{relative}")
            actual = current.read_bytes()
            match = expected == actual
            details[relative] = {
                "match": match,
                "base_blob_sha": git_blob_sha(expected),
                "current_blob_sha": git_blob_sha(actual),
            }
            all_match = all_match and match
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            details[relative] = {"match": False, "error": type(exc).__name__}
            all_match = False
    return {
        "pass": all_match,
        "base_commit": BASE_COMMIT,
        "path_count": len(IMMUTABLE_BASE_PATHS),
        "details": details,
        "manifest_hash": sha256_value(details),
    }


def raises_value_error(callback: Any) -> bool:
    try:
        callback()
    except ValueError:
        return True
    return False


def raises_file_not_found(callback: Any) -> bool:
    try:
        callback()
    except FileNotFoundError:
        return True
    return False


def module_names(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module:
        return [node.module]
    return []


def verify_isolation(root: pathlib.Path) -> dict[str, Any]:
    runtime_files = sorted((root / "product").glob("*.py")) + sorted((root / "engine").glob("*.py"))
    research_findings: list[dict[str, str]] = []
    local_imports: list[str] = []
    for path in runtime_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for module in module_names(node):
                root_name = module.split(".", 1)[0]
                if root_name == "research_ensemble":
                    research_findings.append({"path": str(path.relative_to(root)), "module": module})
                if root_name in {"product", "engine", "research_ensemble"}:
                    local_imports.append(module)
    network_findings: list[dict[str, str]] = []
    for path in sorted((root / "product_closeout").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for module in module_names(node):
                if module.split(".", 1)[0] in PROHIBITED_NETWORK_IMPORTS:
                    network_findings.append({"path": str(path.relative_to(root)), "module": module})
    return {
        "pass": not research_findings and not network_findings,
        "runtime_file_count": len(runtime_files),
        "product_local_imports": sorted(set(local_imports)),
        "research_import_findings": research_findings,
        "QA_network_import_findings": network_findings,
    }
