"""Schema contract checks for Product Closeout Gate C2."""

from __future__ import annotations

import pathlib
from collections.abc import Mapping
from typing import Any

from product.config import PRODUCT_CONTRACT_VERSION

from .common import load_json
from .schema_validator import validate_json_schema


def verify_schema_contract(root: pathlib.Path, prediction: Mapping[str, Any]) -> dict[str, Any]:
    schema = load_json(root / "schemas/product_prediction.schema.json")
    validate_json_schema(prediction, schema)
    properties = schema["properties"]
    conditions = {
        "positive_validation": True,
        "schema_version": properties["schema_version"]["const"] == prediction["schema_version"],
        "contract_version": properties["contract_version"]["const"] == PRODUCT_CONTRACT_VERSION,
        "research_only": properties["research_only"]["const"] is True,
        "public_release_allowed": properties["public_release_allowed"]["const"] is False,
        "statistical_edge": properties["statistical_edge"]["const"] is False,
        "reason": properties["reason"]["const"] == "no_validated_nonuniform_signal",
        "distribution": properties["final_distribution"]["const"] == "M0_ONLY",
        "candidate_count": properties["candidate_sets"]["minItems"] == 5 == properties["candidate_sets"]["maxItems"],
        "candidate_size": (
            properties["candidate_sets"]["items"]["properties"]["numbers"]["minItems"] == 6
            == properties["candidate_sets"]["items"]["properties"]["numbers"]["maxItems"]
        ),
    }
    return {"pass": all(conditions.values()), "conditions": conditions}
