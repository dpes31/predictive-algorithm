"""Negative JSON contract fixtures for Product Closeout Gate C2."""

from __future__ import annotations

import copy
import pathlib
from collections.abc import Mapping
from typing import Any

from .common import load_json
from .schema_validator import SchemaValidationError, validate_json_schema


def verify_negative_schema_cases(root: pathlib.Path, prediction: Mapping[str, Any]) -> dict[str, Any]:
    schema = load_json(root / "schemas/product_prediction.schema.json")
    cases: dict[str, bool] = {}

    def rejected(name: str, mutator: Any) -> None:
        value = copy.deepcopy(prediction)
        mutator(value)
        try:
            validate_json_schema(value, schema)
        except SchemaValidationError:
            cases[name] = True
        else:
            cases[name] = False

    rejected("missing_required", lambda value: value.pop("reason"))
    rejected("additional_property", lambda value: value.__setitem__("unexpected", True))
    rejected("invalid_target_type", lambda value: value.__setitem__("target_draw_no", "1231"))
    rejected("candidate_count", lambda value: value["candidate_sets"].pop())
    rejected("number_range", lambda value: value["candidate_sets"][0]["numbers"].__setitem__(0, 0))
    rejected(
        "duplicate_number",
        lambda value: value["candidate_sets"][0]["numbers"].__setitem__(
            1, value["candidate_sets"][0]["numbers"][0]
        ),
    )
    rejected("non_m0_weight", lambda value: value["product_weights"].__setitem__("M1", 0.1))
    rejected("reason_change", lambda value: value.__setitem__("reason", "other"))
    rejected("lift_change", lambda value: value["candidate_sets"][0].__setitem__("lift_vs_uniform", 1.1))
    rejected("candidate_extra_property", lambda value: value["candidate_sets"][0].__setitem__("extra", 1))
    rejected("datetime_without_timezone", lambda value: value.__setitem__("generated_at", "2026-07-03"))
    return {
        "pass": all(cases.values()),
        "negative_case_count": len(cases),
        "negative_cases": cases,
    }
