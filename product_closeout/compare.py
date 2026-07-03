"""Reproducibility comparison for Product Closeout Gate C2."""

from __future__ import annotations

import argparse
import json
import pathlib
from collections.abc import Sequence
from typing import Any

from engine.hashing import canonical_json, sha256_value

from .constants import QA_CONTRACT_VERSION, SPEC_CONTRACT_VERSION


def _load(path: str | pathlib.Path) -> dict[str, Any]:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def compare_results(paths: Sequence[str | pathlib.Path], *, cross_runtime: bool) -> dict[str, Any]:
    results = [_load(path) for path in paths]
    hashes = [str(result.get("canonical_result_hash", "")) for result in results]
    statuses = [str(result.get("canonical_result", {}).get("status", "")) for result in results]
    runtime_versions = [str(result.get("runtime", {}).get("python_version", "")) for result in results]
    hash_match = len(set(hashes)) == 1 and bool(hashes[0])
    status_match = len(set(statuses)) == 1 and bool(statuses[0])
    required_runtimes = True
    if cross_runtime:
        required_runtimes = {".".join(version.split(".")[:2]) for version in runtime_versions} == {"3.11", "3.12"}
    reproducibility_pass = hash_match and status_match and required_runtimes

    candidate = statuses[0] if status_match else "PRODUCT_CLOSEOUT_QA_FAIL"
    if not reproducibility_pass:
        final_status = "PRODUCT_CLOSEOUT_QA_FAIL"
    elif not cross_runtime:
        final_status = candidate
    elif candidate == "PRODUCT_CLOSEOUT_QA_PASS_CANDIDATE":
        final_status = "PRODUCT_CLOSEOUT_QA_PASS"
    elif candidate in {"PRODUCT_CLOSEOUT_QA_FAIL", "PRODUCT_CLOSEOUT_QA_BLOCKED"}:
        final_status = candidate
    else:
        final_status = "PRODUCT_CLOSEOUT_QA_FAIL"

    reasons: list[str] = []
    if not hash_match:
        reasons.append("canonical_hash_mismatch")
    if not status_match:
        reasons.append("runtime_status_mismatch")
    if not required_runtimes:
        reasons.append("required_runtime_missing")
    if status_match and candidate != "PRODUCT_CLOSEOUT_QA_PASS_CANDIDATE":
        reasons.extend(results[0].get("canonical_result", {}).get("decision_reasons", []))

    output: dict[str, Any] = {
        "status": final_status,
        "contract_version": QA_CONTRACT_VERSION,
        "spec_contract_version": SPEC_CONTRACT_VERSION,
        "cross_runtime": cross_runtime,
        "input_count": len(results),
        "runtime_versions": runtime_versions,
        "canonical_hashes": hashes,
        "candidate_statuses": statuses,
        "reproducibility": {
            "pass": reproducibility_pass,
            "canonical_hash_match": hash_match,
            "status_match": status_match,
            "required_runtime_pass": required_runtimes,
        },
        "decision_reasons": list(dict.fromkeys(reasons)),
        "canonical_result_hash": hashes[0] if hash_match else None,
        "research_only": True,
        "public_release_allowed": False,
        "next_gate_authorized": False,
    }
    output["decision_hash"] = sha256_value(output)
    return output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Product Closeout C2 QA results.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--within-runtime", nargs=2, metavar=("RUN1", "RUN2"))
    group.add_argument("--cross-runtime", nargs=4, metavar=("PY311_RUN1", "PY311_RUN2", "PY312_RUN1", "PY312_RUN2"))
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    paths = args.within_runtime or args.cross_runtime
    result = compare_results(paths, cross_runtime=bool(args.cross_runtime))
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(result) + "\n", encoding="utf-8")
    print(f"PRODUCT_CLOSEOUT_QA_FINAL_STATUS={result['status']}")
    print(f"PRODUCT_CLOSEOUT_QA_DECISION_HASH={result['decision_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
