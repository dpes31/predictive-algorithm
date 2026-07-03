"""Within-runtime and cross-runtime reproducibility comparison for A4."""

from __future__ import annotations

import argparse
import json
import pathlib
from collections.abc import Sequence
from typing import Any

from engine.hashing import canonical_json, sha256_value

from .evaluation import EVALUATION_CONTRACT_VERSION, SPEC_CONTRACT_VERSION


def _load(path: str | pathlib.Path) -> dict[str, Any]:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def _write(value: dict[str, Any], path: str | pathlib.Path) -> None:
    output = pathlib.Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(value) + "\n", encoding="utf-8")


def compare_results(paths: Sequence[str | pathlib.Path], *, cross_runtime: bool) -> dict[str, Any]:
    results = [_load(path) for path in paths]
    hashes = [str(result.get("canonical_result_hash", "")) for result in results]
    canonical_hash_match = len(set(hashes)) == 1 and bool(hashes[0])
    statuses = [str(result.get("canonical_result", {}).get("status", "")) for result in results]
    status_match = len(set(statuses)) == 1 and bool(statuses[0])
    runtime_versions = [result.get("runtime", {}).get("python_version") for result in results]
    required_runtime_pass = True
    if cross_runtime:
        major_minor = {".".join(str(version).split(".")[:2]) for version in runtime_versions if version}
        required_runtime_pass = major_minor == {"3.11", "3.12"}
    reproducibility_pass = canonical_hash_match and status_match and required_runtime_pass

    candidate = statuses[0] if status_match else "A4_EVALUATION_FAIL"
    if not reproducibility_pass:
        final_status = "A4_EVALUATION_FAIL"
    elif not cross_runtime:
        final_status = candidate
    elif candidate == "A4_EVALUATION_PASS_CANDIDATE":
        final_status = "A4_EVALUATION_PASS"
    elif candidate in {"A4_EVALUATION_FAIL", "A4_EVALUATION_BLOCKED"}:
        final_status = candidate
    else:
        final_status = "A4_EVALUATION_FAIL"

    reasons: list[str] = []
    if not canonical_hash_match:
        reasons.append("E11_canonical_hash_mismatch")
    if not status_match:
        reasons.append("E11_status_mismatch")
    if not required_runtime_pass:
        reasons.append("E11_required_runtime_missing")
    if status_match and candidate != "A4_EVALUATION_PASS_CANDIDATE":
        reasons.extend(results[0].get("canonical_result", {}).get("decision_reasons", []))

    output = {
        "status": final_status,
        "contract_version": EVALUATION_CONTRACT_VERSION,
        "spec_contract_version": SPEC_CONTRACT_VERSION,
        "cross_runtime": cross_runtime,
        "input_count": len(results),
        "runtime_versions": runtime_versions,
        "canonical_hashes": hashes,
        "candidate_statuses": statuses,
        "E11_reproducibility": {
            "pass": reproducibility_pass,
            "canonical_hash_match": canonical_hash_match,
            "status_match": status_match,
            "required_runtime_pass": required_runtime_pass,
        },
        "decision_reasons": list(dict.fromkeys(reasons)),
        "canonical_result_hash": hashes[0] if canonical_hash_match else None,
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "next_gate_authorized": False,
    }
    output["decision_hash"] = sha256_value(output)
    return output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare A4 evaluation outputs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--within-runtime", nargs=2, metavar=("RUN1", "RUN2"))
    group.add_argument("--cross-runtime", nargs=4, metavar=("PY311_RUN1", "PY311_RUN2", "PY312_RUN1", "PY312_RUN2"))
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    paths = args.within_runtime or args.cross_runtime
    result = compare_results(paths, cross_runtime=bool(args.cross_runtime))
    _write(result, args.output)
    print(f"A4_FINAL_STATUS={result['status']}")
    print(f"A4_FINAL_DECISION_HASH={result['decision_hash']}")
    print("A4_FINAL_RESULT_JSON=" + canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
