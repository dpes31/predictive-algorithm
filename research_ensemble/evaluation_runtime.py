"""Canonical runtime adapter for cross-Python A4 evaluation evidence."""

from __future__ import annotations

import copy
import math
from typing import Any

from engine.hashing import sha256_value


CANONICAL_SIGNIFICANT_DIGITS = 12
CANONICAL_ZERO_TOLERANCE = 5e-13


def canonical_float(value: float) -> float:
    """Return a runtime-stable report value without changing model calculations."""
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError("non-finite evaluation value")
    if abs(numeric) < CANONICAL_ZERO_TOLERANCE:
        return 0.0
    return float(format(numeric, f".{CANONICAL_SIGNIFICANT_DIGITS}g"))


def install_canonical_serialization() -> None:
    """Patch only report serializers used by A4; model formulas stay frozen."""
    from . import evaluation, scoring

    evaluation.stable_float = canonical_float
    scoring.stable_float = canonical_float


def normalize_evaluation_result(result: dict[str, Any]) -> dict[str, Any]:
    """Remove file-presence metadata from the canonical decision identity."""
    output = copy.deepcopy(result)
    canonical = output["canonical_result"]
    e13 = canonical.get("integrity", {}).get("E13_hash_recomputation", {})
    e13.pop("rows_file_sha256", None)
    canonical.pop("canonical_result_hash", None)
    canonical_hash = sha256_value(canonical)
    canonical["canonical_result_hash"] = canonical_hash
    output["canonical_result_hash"] = canonical_hash
    return output
