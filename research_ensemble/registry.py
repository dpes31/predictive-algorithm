"""Versioned user-input, hypothesis, and adapter registries."""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from typing import Any

from engine.hashing import sha256_value

USER_CLASSIFICATIONS = {
    "NUMBER_LEVEL",
    "BALL_SET_LEVEL",
    "DRAW_LEVEL",
    "STATIC_ASSUMPTION",
    "NON_DISCRIMINATIVE_REFERENCE",
}
MISSING_POLICIES = {"ZERO_AND_FLAG", "ABSTAIN_COMPONENT", "ABSTAIN_RUN"}
HYPOTHESIS_STATUSES = {"DRAFT", "ACTIVE", "DIAGNOSTIC", "RETIRED"}
TRANSFORMS = {
    "LINEAR_NUMBER_SCORE",
    "SIGNED_NUMBER_SCORE",
    "RANK_BUCKET",
    "DRAW_STRENGTH_MODIFIER",
    "BALL_SET_NUMBER_MAP",
    "ADDITIVE_PROJECTION",
}


class RegistryValidationError(ValueError):
    """Raised when a registry violates the approved A1 contract."""


def _strip_hash(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: copy.deepcopy(item) for name, item in value.items() if name != key}


def seal_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    output = copy.deepcopy(dict(registry))
    registry_type = str(output.get("registry_type", ""))
    id_key = "hypothesis_id" if registry_type == "hypothesis" else "entry_id"
    entries = []
    for raw in output.get("entries", []):
        entry = _strip_hash(dict(raw), "hypothesis_hash" if registry_type == "hypothesis" else "entry_hash")
        hash_key = "hypothesis_hash" if registry_type == "hypothesis" else "entry_hash"
        entry[hash_key] = sha256_value(entry)
        entries.append(entry)
    output["entries"] = sorted(entries, key=lambda item: str(item.get(id_key, "")))
    output = _strip_hash(output, "registry_hash")
    output["registry_hash"] = sha256_value(output)
    return output


def seal_physical_adapter(value: Mapping[str, Any]) -> dict[str, Any]:
    output = _strip_hash(dict(value), "adapter_hash")
    output["fields"] = sorted(
        [copy.deepcopy(dict(item)) for item in output.get("fields", [])],
        key=lambda item: str(item.get("field_id", "")),
    )
    output["adapter_hash"] = sha256_value(output)
    return output


def empty_user_registry() -> dict[str, Any]:
    return seal_registry(
        {
            "registry_type": "user_input",
            "contract_version": "user-input-registry-1.0.0",
            "registry_version": "empty-1.0.0",
            "status": "APPROVED",
            "approved_by": "user",
            "approved_at": "2026-07-03T00:00:00+09:00",
            "entries": [],
        }
    )


def empty_hypothesis_registry() -> dict[str, Any]:
    return seal_registry(
        {
            "registry_type": "hypothesis",
            "contract_version": "hypothesis-registry-1.0.0",
            "registry_version": "empty-1.0.0",
            "status": "APPROVED",
            "approved_by": "user",
            "approved_at": "2026-07-03T00:00:00+09:00",
            "entries": [],
        }
    )


def empty_physical_adapter() -> dict[str, Any]:
    return seal_physical_adapter(
        {
            "registry_type": "physical_adapter",
            "contract_version": "user-physical-adapter-1.0.0",
            "adapter_version": "empty-1.0.0",
            "status": "APPROVED",
            "approved_by": "user",
            "approved_at": "2026-07-03T00:00:00+09:00",
            "fields": [],
        }
    )


def _validate_number_mapping(value: Any) -> dict[int, float]:
    if not isinstance(value, Mapping):
        raise RegistryValidationError("number_mapping must be an object")
    output: dict[int, float] = {}
    for raw_number, raw_value in value.items():
        number = int(raw_number)
        number_value = float(raw_value)
        if not 1 <= number <= 45:
            raise RegistryValidationError("number_mapping key outside 1..45")
        if not math.isfinite(number_value):
            raise RegistryValidationError("number_mapping values must be finite")
        if number in output:
            raise RegistryValidationError("duplicate number_mapping key")
        output[number] = number_value
    return output


def validate_user_registry(registry: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    value = copy.deepcopy(dict(registry))
    if value.get("registry_type") != "user_input":
        raise RegistryValidationError("invalid user registry type")
    if value.get("contract_version") != "user-input-registry-1.0.0":
        raise RegistryValidationError("invalid user registry contract")
    if value.get("status") != "APPROVED" or value.get("approved_by") != "user":
        raise RegistryValidationError("user registry must be user-approved")
    if value.get("registry_hash") != sha256_value(_strip_hash(value, "registry_hash")):
        raise RegistryValidationError("user registry hash mismatch")
    seen: set[str] = set()
    for entry in value.get("entries", []):
        entry_id = str(entry.get("entry_id", ""))
        if not entry_id or entry_id in seen:
            raise RegistryValidationError("invalid or duplicate user entry_id")
        seen.add(entry_id)
        if entry.get("source_type") != "USER_SUPPLIED":
            raise RegistryValidationError("user input source must be USER_SUPPLIED")
        if entry.get("classification") not in USER_CLASSIFICATIONS:
            raise RegistryValidationError("invalid user input classification")
        if entry.get("missing_policy") not in MISSING_POLICIES:
            raise RegistryValidationError("invalid user input missing policy")
        if entry.get("number_mapping") is not None:
            _validate_number_mapping(entry["number_mapping"])
        expected = sha256_value(_strip_hash(dict(entry), "entry_hash"))
        if entry.get("entry_hash") != expected:
            raise RegistryValidationError("user entry hash mismatch")
    return value, str(value["registry_hash"])


def validate_hypothesis_registry(registry: Mapping[str, Any], *, single_cap: float, total_cap: float) -> tuple[dict[str, Any], str]:
    value = copy.deepcopy(dict(registry))
    if value.get("registry_type") != "hypothesis":
        raise RegistryValidationError("invalid hypothesis registry type")
    if value.get("contract_version") != "hypothesis-registry-1.0.0":
        raise RegistryValidationError("invalid hypothesis registry contract")
    if value.get("status") != "APPROVED" or value.get("approved_by") != "user":
        raise RegistryValidationError("hypothesis registry must be user-approved")
    if value.get("registry_hash") != sha256_value(_strip_hash(value, "registry_hash")):
        raise RegistryValidationError("hypothesis registry hash mismatch")
    active_cap = 0.0
    seen: set[str] = set()
    for entry in value.get("entries", []):
        hypothesis_id = str(entry.get("hypothesis_id", ""))
        if not hypothesis_id or hypothesis_id in seen:
            raise RegistryValidationError("invalid or duplicate hypothesis_id")
        seen.add(hypothesis_id)
        if entry.get("status") not in HYPOTHESIS_STATUSES:
            raise RegistryValidationError("invalid hypothesis status")
        if entry.get("source_type") != "USER_APPROVED":
            raise RegistryValidationError("hypothesis source must be USER_APPROVED")
        if entry.get("transform_type") not in TRANSFORMS:
            raise RegistryValidationError("invalid hypothesis transform")
        if entry.get("missing_policy") not in MISSING_POLICIES:
            raise RegistryValidationError("invalid hypothesis missing policy")
        cap = float(entry.get("single_hypothesis_cap", 0.0))
        if cap < 0.0 or cap > single_cap + 1e-15:
            raise RegistryValidationError("single hypothesis cap exceeded")
        if entry.get("status") == "ACTIVE":
            if entry.get("approved_by") != "user" or not entry.get("approved_at"):
                raise RegistryValidationError("ACTIVE hypothesis requires user approval")
            active_cap += cap
        expected = sha256_value(_strip_hash(dict(entry), "hypothesis_hash"))
        if entry.get("hypothesis_hash") != expected:
            raise RegistryValidationError("hypothesis entry hash mismatch")
    if active_cap > total_cap + 1e-15:
        raise RegistryValidationError("hypothesis aggregate cap exceeded")
    return value, str(value["registry_hash"])


def validate_physical_adapter(value: Mapping[str, Any], *, field_cap: float, total_cap: float) -> tuple[dict[str, Any], str]:
    adapter = copy.deepcopy(dict(value))
    if adapter.get("registry_type") != "physical_adapter":
        raise RegistryValidationError("invalid physical adapter type")
    if adapter.get("contract_version") != "user-physical-adapter-1.0.0":
        raise RegistryValidationError("invalid physical adapter contract")
    if adapter.get("status") != "APPROVED" or adapter.get("approved_by") != "user":
        raise RegistryValidationError("physical adapter must be user-approved")
    if adapter.get("adapter_hash") != sha256_value(_strip_hash(adapter, "adapter_hash")):
        raise RegistryValidationError("physical adapter hash mismatch")
    total = 0.0
    seen: set[str] = set()
    for field in adapter.get("fields", []):
        field_id = str(field.get("field_id", ""))
        if not field_id or field_id in seen:
            raise RegistryValidationError("invalid or duplicate physical field_id")
        seen.add(field_id)
        if field.get("direction_source") != "HYPOTHESIS_ONLY":
            raise RegistryValidationError("physical direction must come from hypothesis")
        cap = float(field.get("field_cap", 0.0))
        if cap < 0.0 or cap > field_cap + 1e-15:
            raise RegistryValidationError("single physical field cap exceeded")
        total += cap
    if total > total_cap + 1e-15:
        raise RegistryValidationError("physical aggregate cap exceeded")
    return adapter, str(adapter["adapter_hash"])


def number_mapping(entry: Mapping[str, Any]) -> dict[int, float]:
    return _validate_number_mapping(entry.get("number_mapping"))
