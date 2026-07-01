"""Hard metadata veto for post-draw leakage and invalid evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from .config import DEFAULT_CONFIG, EngineConfig
from .physical_metadata import EvidenceValue, PhysicalDrawMetadata

_RESULT_KEYS = {
    "ordered_numbers", "winning_numbers", "bonus_number", "draw_results",
    "current_draw_result", "current_ordered_numbers",
}
_EVIDENCE_KEYS = {
    "value", "status", "source_type", "source_url", "observed_at",
    "available_before_draw", "confidence", "notes",
}


def _time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed


@dataclass(frozen=True)
class MetadataVetoResult:
    vetoed: bool
    status: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"vetoed": self.vetoed, "status": self.status, "reasons": list(self.reasons)}


def _check(path: str, item: EvidenceValue | Mapping[str, Any], draw_time: datetime, reasons: list[str]) -> None:
    if isinstance(item, EvidenceValue):
        status, source_type, source_url = item.status, item.source_type, item.source_url
        observed_at, available, value = item.observed_at, item.available_before_draw, item.value
    else:
        status = str(item.get("status", "unknown"))
        source_type = str(item.get("source_type", "none"))
        source_url = item.get("source_url")
        observed_at = item.get("observed_at")
        available = bool(item.get("available_before_draw", False))
        value = item.get("value")
    if path.split(".")[-1] in _RESULT_KEYS:
        reasons.append(f"result_field:{path}")
    if isinstance(value, Mapping) and any(str(key) in _RESULT_KEYS for key in value):
        reasons.append(f"result_payload:{path}")
    if available and not observed_at:
        reasons.append(f"missing_timestamp:{path}")
    if observed_at:
        try:
            if _time(str(observed_at)) > draw_time:
                reasons.append(f"post_draw_timestamp:{path}")
        except ValueError:
            reasons.append(f"invalid_timestamp:{path}")
    if status == "verified" and (not source_url or source_type == "none"):
        reasons.append(f"untraceable_verified:{path}")


def _walk(payload: Mapping[str, Any], prefix: str, draw_time: datetime, reasons: list[str]) -> None:
    for key, value in payload.items():
        name = str(key)
        path = f"{prefix}.{name}" if prefix else name
        if not prefix and name in {"draw_no", "draw_datetime", "metadata_version"}:
            continue
        if name in _RESULT_KEYS:
            reasons.append(f"result_field:{path}")
        elif isinstance(value, Mapping) and set(value).intersection(_EVIDENCE_KEYS):
            _check(path, value, draw_time, reasons)
        elif isinstance(value, Mapping):
            _walk(value, path, draw_time, reasons)


def evaluate_metadata_global_veto(
    metadata: PhysicalDrawMetadata | Mapping[str, Any],
    *,
    target_draw_no: int | None = None,
    config: EngineConfig = DEFAULT_CONFIG,
) -> MetadataVetoResult:
    reasons: list[str] = []
    if isinstance(metadata, PhysicalDrawMetadata):
        draw_no, version = metadata.draw_no, metadata.metadata_version
        try:
            draw_time = _time(metadata.draw_datetime)
        except ValueError:
            return MetadataVetoResult(True, "INVALID_METADATA", ("invalid_draw_datetime",))
        for path, item in metadata.fields.items():
            _check(path, item, draw_time, reasons)
    else:
        try:
            draw_no = int(metadata["draw_no"])
            version = str(metadata.get("metadata_version", "unknown"))
            draw_time = _time(str(metadata["draw_datetime"]))
        except (KeyError, TypeError, ValueError):
            return MetadataVetoResult(True, "INVALID_METADATA", ("invalid_draw_identity",))
        _walk(metadata, "", draw_time, reasons)
    if version != config.physical_data_schema_version:
        reasons.append("schema_version_mismatch")
    if target_draw_no is not None and draw_no != target_draw_no:
        reasons.append("target_draw_mismatch")
    unique = tuple(sorted(set(reasons)))
    return MetadataVetoResult(bool(unique), "INVALID_METADATA" if unique else "VALID_METADATA", unique)
