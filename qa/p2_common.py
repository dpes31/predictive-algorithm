"""Shared Product Gate P2 constants, serialization, and deterministic checks."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import pathlib
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from engine.hashing import deterministic_seed, sha256_value
from product.config import (
    DEFAULT_PRODUCT_CONFIG,
    EXPECTED_DATA_HASH,
    MODEL_VERSION,
    PRODUCT_CONTRACT_VERSION,
)
from product.run_prediction import run_product_prediction

P2_CONTRACT_VERSION = "product-qa-1.0.0"
P1_IMPLEMENTATION_LOCK = "099d917abd1b635c830fee343a47d3bd23e0c052"
P1_ACCEPTANCE_SHA256 = "a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139"
P1_WORKFLOW_RUN_ID = 28525611462
CANONICAL_TARGET_DRAW = 1231
CANONICAL_LAST_DRAW = 1230
CANONICAL_RECORD_COUNT = 1230
CANONICAL_GENERATED_AT = "2026-07-03T00:00:00Z"
UNIFORM_PROBABILITY = 1.0 / math.comb(45, 6)


@dataclass(frozen=True)
class CheckResult:
    status: str
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "details": dict(self.details)}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(root: pathlib.Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()}")
    return completed.stdout.strip()


def commit_exists(root: pathlib.Path, commit: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def blob_at(root: pathlib.Path, commit: str, path: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"{commit}:{path}"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def is_ancestor(root: pathlib.Path, ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", ancestor, descendant],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def canonical_core(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return product-effective fields, excluding wall-clock and shadow diagnostics."""

    cutoff = dict(payload["diagnostics"]["cutoff"])
    return {
        "schema_version": payload["schema_version"],
        "contract_version": payload["contract_version"],
        "target_draw_no": payload["target_draw_no"],
        "input_last_draw": payload["input_last_draw"],
        "research_only": payload["research_only"],
        "public_release_allowed": payload["public_release_allowed"],
        "statistical_edge": payload["statistical_edge"],
        "reason": payload["reason"],
        "advantage_status": payload["advantage_status"],
        "final_distribution": payload["final_distribution"],
        "product_weights": payload["product_weights"],
        "candidate_sets": payload["candidate_sets"],
        "versions": payload["versions"],
        "hashes": payload["hashes"],
        "seed": payload["seed"],
        "cutoff": cutoff,
        "limitations": payload["limitations"],
    }


def semantic_contract_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    candidates = payload.get("candidate_sets")
    if isinstance(candidates, list):
        ranks = [candidate.get("rank") for candidate in candidates if isinstance(candidate, dict)]
        if ranks != [1, 2, 3, 4, 5]:
            errors.append("candidate ranks must be ordered exactly 1..5")
        number_sets: list[tuple[int, ...]] = []
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                continue
            numbers = candidate.get("numbers")
            if isinstance(numbers, list):
                if numbers != sorted(numbers):
                    errors.append(f"candidate {index}: numbers must be ascending")
                number_sets.append(tuple(numbers))
            if candidate.get("joint_probability") != UNIFORM_PROBABILITY:
                errors.append(f"candidate {index}: joint_probability must equal exact uniform probability")
        if len(number_sets) != len(set(number_sets)):
            errors.append("candidate number sets must be distinct regardless of rank")

    target = payload.get("target_draw_no")
    input_last = payload.get("input_last_draw")
    if isinstance(target, int) and isinstance(input_last, int) and input_last != target - 1:
        errors.append("input_last_draw must equal target_draw_no - 1")

    diagnostics = payload.get("diagnostics")
    if isinstance(diagnostics, dict) and isinstance(diagnostics.get("cutoff"), dict):
        cutoff = diagnostics["cutoff"]
        if cutoff.get("target_draw_no") != target:
            errors.append("cutoff target_draw_no must match top-level target_draw_no")
        if cutoff.get("input_last_draw") != input_last:
            errors.append("cutoff input_last_draw must match top-level input_last_draw")
        cutoff_payload = {key: value for key, value in cutoff.items() if key != "cutoff_hash"}
        if cutoff.get("cutoff_hash") != sha256_value(cutoff_payload):
            errors.append("cutoff_hash does not match cutoff payload")
        first = cutoff.get("input_first_draw")
        count = cutoff.get("input_record_count")
        if all(isinstance(value, int) for value in (first, input_last, count)):
            if count != input_last - first + 1:
                errors.append("cutoff input_record_count is inconsistent with contiguous range")
    return errors


def validate_payload(payload: Mapping[str, Any], schema: Mapping[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = [
        f"schema:{'/'.join(str(part) for part in error.absolute_path)}:{error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
    ]
    errors.extend(f"semantic:{message}" for message in semantic_contract_errors(payload))
    return errors


def negative_payload_mutations(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    mutations: dict[str, dict[str, Any]] = {}

    def mutated(name: str) -> dict[str, Any]:
        value = copy.deepcopy(payload)
        mutations[name] = value
        return value

    mutated("missing_required").pop("reason")
    mutated("unknown_top_level")["unexpected"] = True
    mutated("candidate_five_numbers")["candidate_sets"][0]["numbers"] = [1, 2, 3, 4, 5]
    mutated("candidate_seven_numbers")["candidate_sets"][0]["numbers"] = [1, 2, 3, 4, 5, 6, 7]
    duplicate = mutated("duplicate_number")
    duplicate["candidate_sets"][0]["numbers"][1] = duplicate["candidate_sets"][0]["numbers"][0]
    mutated("number_outside_range")["candidate_sets"][0]["numbers"][0] = 0
    duplicate_set = mutated("duplicate_candidate_set")
    duplicate_set["candidate_sets"][1]["numbers"] = list(duplicate_set["candidate_sets"][0]["numbers"])
    mutated("invalid_rank_sequence")["candidate_sets"][1]["rank"] = 1
    mutated("nonuniform_probability")["candidate_sets"][0]["joint_probability"] = UNIFORM_PROBABILITY * 2
    mutated("invalid_lift")["candidate_sets"][0]["lift_vs_uniform"] = 1.01
    mutated("statistical_edge_true")["statistical_edge"] = True
    mutated("nonzero_shadow_weight")["product_weights"]["M1"] = 0.01
    mutated("malformed_hash")["hashes"]["prediction_hash"] = "not-a-sha256"
    mutated("missing_hash")["hashes"].pop("model_hash")
    invalid_target = mutated("invalid_target_relation")
    invalid_target["target_draw_no"] += 1
    false_cutoff = mutated("false_cutoff_metadata")
    false_cutoff["diagnostics"]["cutoff"]["input_record_count"] -= 1
    return mutations


def generate_core_snapshot(root: pathlib.Path, dataset: pathlib.Path) -> dict[str, Any]:
    repeats = [
        run_product_prediction(
            target_draw_no=CANONICAL_TARGET_DRAW,
            dataset_path=dataset,
            generated_at=CANONICAL_GENERATED_AT,
        )
        for _ in range(3)
    ]
    cores = [canonical_core(value) for value in repeats]
    generated_at_variant = canonical_core(
        run_product_prediction(
            target_draw_no=CANONICAL_TARGET_DRAW,
            dataset_path=dataset,
            generated_at="2026-07-03T01:02:03Z",
        )
    )
    shadows = [
        None,
        {},
        {"M1": {"score": 0.1}, "M4": {"state": "shadow"}},
        {"M4": {"state": "different"}, "M2": [3, 2, 1]},
        {"M2": [3, 2, 1], "M4": {"state": "different"}},
    ]
    shadow_cores = [
        canonical_core(
            run_product_prediction(
                target_draw_no=CANONICAL_TARGET_DRAW,
                dataset_path=dataset,
                generated_at=CANONICAL_GENERATED_AT,
                shadow_diagnostics=shadow,
            )
        )
        for shadow in shadows
    ]
    seed_other_target = deterministic_seed(
        PRODUCT_CONTRACT_VERSION,
        EXPECTED_DATA_HASH,
        MODEL_VERSION,
        DEFAULT_PRODUCT_CONFIG.config_hash,
        CANONICAL_TARGET_DRAW + 1,
    )
    return {
        "contract_version": P2_CONTRACT_VERSION,
        "python_version": platform.python_version(),
        "repeat_count": len(repeats),
        "repeats_equal": all(core == cores[0] for core in cores[1:]),
        "generated_at_invariant": generated_at_variant == cores[0],
        "shadow_isolation": all(core == shadow_cores[0] for core in shadow_cores[1:]),
        "target_change_invalidates_seed": seed_other_target != cores[0]["seed"],
        "core": cores[0],
    }
