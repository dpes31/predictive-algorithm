"""Small standard-library JSON Schema validator for the frozen Product P1 schema."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any


class SchemaValidationError(ValueError):
    """Raised when an instance violates the supported schema contract."""


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, Mapping)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise SchemaValidationError(f"unsupported schema type: {expected}")


def _validate_datetime(value: str, path: str) -> None:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SchemaValidationError(f"{path}: invalid date-time") from exc
    if parsed.tzinfo is None:
        raise SchemaValidationError(f"{path}: date-time must include timezone")


def validate_json_schema(instance: Any, schema: Mapping[str, Any], path: str = "$") -> None:
    if "const" in schema and instance != schema["const"]:
        raise SchemaValidationError(f"{path}: expected const {schema['const']!r}")

    if "type" in schema:
        expected_types = schema["type"]
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(_type_matches(instance, expected) for expected in expected_types):
            raise SchemaValidationError(f"{path}: type mismatch")

    if isinstance(instance, Mapping):
        required = schema.get("required", [])
        missing = [name for name in required if name not in instance]
        if missing:
            raise SchemaValidationError(f"{path}: missing required properties {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unexpected = sorted(set(instance) - set(properties))
            if unexpected:
                raise SchemaValidationError(f"{path}: unexpected properties {unexpected}")
        for name, child_schema in properties.items():
            if name in instance:
                validate_json_schema(instance[name], child_schema, f"{path}.{name}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < int(schema["minItems"]):
            raise SchemaValidationError(f"{path}: too few items")
        if "maxItems" in schema and len(instance) > int(schema["maxItems"]):
            raise SchemaValidationError(f"{path}: too many items")
        if schema.get("uniqueItems") is True:
            serialized = [
                json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                for value in instance
            ]
            if len(serialized) != len(set(serialized)):
                raise SchemaValidationError(f"{path}: duplicate items")
        if "items" in schema:
            for index, value in enumerate(instance):
                validate_json_schema(value, schema["items"], f"{path}[{index}]")
        if "contains" in schema:
            found = False
            for index, value in enumerate(instance):
                try:
                    validate_json_schema(value, schema["contains"], f"{path}[{index}]")
                except SchemaValidationError:
                    continue
                found = True
                break
            if not found:
                raise SchemaValidationError(f"{path}: contains constraint not satisfied")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaValidationError(f"{path}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaValidationError(f"{path}: above maximum")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            raise SchemaValidationError(f"{path}: below exclusive minimum")

    if isinstance(instance, str):
        if "pattern" in schema and re.fullmatch(str(schema["pattern"]), instance) is None:
            raise SchemaValidationError(f"{path}: pattern mismatch")
        if schema.get("format") == "date-time":
            _validate_datetime(instance, path)
