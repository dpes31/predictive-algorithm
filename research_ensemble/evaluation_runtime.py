"""Canonical runtime adapter for cross-Python A4 evaluation evidence."""

from __future__ import annotations

import copy
import math
from typing import Any

from engine.hashing import sha256_value

CANONICAL_SIGNIFICANT_DIGITS = 12
CANONICAL_ZERO_TOLERANCE = 5e-13
RUNTIME_ADAPTER_PATH = "research_ensemble/evaluation_runtime.py"


def canonical_float(value: float) -> float:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError("non-finite evaluation value")
    if abs(numeric) < CANONICAL_ZERO_TOLERANCE:
        return 0.0
    return float(format(numeric, f".{CANONICAL_SIGNIFICANT_DIGITS}g"))


def install_canonical_serialization() -> None:
    from . import evaluation, scoring

    evaluation.stable_float = canonical_float
    scoring.stable_float = canonical_float
    if RUNTIME_ADAPTER_PATH not in evaluation.EVALUATION_SOURCE_PATHS:
        evaluation.EVALUATION_SOURCE_PATHS = (*evaluation.EVALUATION_SOURCE_PATHS, RUNTIME_ADAPTER_PATH)


def normalize_evaluation_result(result: dict[str, Any]) -> dict[str, Any]:
    output = copy.deepcopy(result)
    canonical = output["canonical_result"]
    canonical.get("integrity", {}).get("E13_hash_recomputation", {}).pop("rows_file_sha256", None)
    canonical.pop("canonical_result_hash", None)
    canonical_hash = sha256_value(canonical)
    canonical["canonical_result_hash"] = canonical_hash
    output["canonical_result_hash"] = canonical_hash
    return output
