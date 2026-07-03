"""Canonical runtime adapter for cross-Python A4 evaluation evidence."""

from __future__ import annotations

import copy
import math
from typing import Any, Callable

from engine.hashing import sha256_value

CANONICAL_SIGNIFICANT_DIGITS = 10
CANONICAL_ZERO_TOLERANCE = 5e-13
RUNTIME_ADAPTER_PATH = "research_ensemble/evaluation_runtime.py"
_ORIGINAL_ASSEMBLE: Callable[..., dict[str, Any]] | None = None


def canonical_float(value: float) -> float:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError("non-finite evaluation value")
    if abs(numeric) < CANONICAL_ZERO_TOLERANCE:
        return 0.0
    return float(format(numeric, f".{CANONICAL_SIGNIFICANT_DIGITS}g"))


def _canonical_assemble(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if _ORIGINAL_ASSEMBLE is None:
        raise RuntimeError("canonical serializer not installed")
    result = _ORIGINAL_ASSEMBLE(*args, **kwargs)
    logits = result["final_logits"]
    payload = [
        {"number": number, "final_logit": canonical_float(logits[number])}
        for number in range(1, 46)
    ]
    result["score_vector_hash"] = sha256_value(payload)
    return result


def install_canonical_serialization() -> None:
    global _ORIGINAL_ASSEMBLE
    from . import evaluation, scoring

    evaluation.stable_float = canonical_float
    scoring.stable_float = canonical_float
    if RUNTIME_ADAPTER_PATH not in evaluation.EVALUATION_SOURCE_PATHS:
        evaluation.EVALUATION_SOURCE_PATHS = (*evaluation.EVALUATION_SOURCE_PATHS, RUNTIME_ADAPTER_PATH)
    if _ORIGINAL_ASSEMBLE is None:
        _ORIGINAL_ASSEMBLE = evaluation.assemble_ablation
        evaluation.assemble_ablation = _canonical_assemble


def normalize_evaluation_result(result: dict[str, Any]) -> dict[str, Any]:
    output = copy.deepcopy(result)
    canonical = output["canonical_result"]
    canonical.get("integrity", {}).get("E13_hash_recomputation", {}).pop("rows_file_sha256", None)
    canonical.pop("canonical_result_hash", None)
    canonical_hash = sha256_value(canonical)
    canonical["canonical_result_hash"] = canonical_hash
    output["canonical_result_hash"] = canonical_hash
    return output
