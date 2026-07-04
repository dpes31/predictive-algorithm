"""Leakage-safe physical and operational metadata contracts for M4."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

from .config import DEFAULT_CONFIG, EngineConfig

_ALLOWED_STATUSES = {"unknown", "reported", "observed", "verified", "inferred"}
_ALLOWED_SOURCE_TYPES = {
    "official_document",
    "official_broadcast",
    "official_webpage",
    "press_report",
    "observer_report",
    "manual_video_review",
    "machine_extracted_video",
    "none",
}
_ELIGIBLE_STATUSES = {"reported", "observed", "verified"}
_EVIDENCE_KEYS = {
    "value",
    "status",
    "source_type",
    "source_url",
    "observed_at",
    "available_before_draw",
    "confidence",
    "notes",
}
_FORBIDDEN_RESULT_FIELDS = {
    "ordered_numbers",
    "winning_numbers",
    "bonus_number",
    "draw_results",
    "current_draw_result",
    "current_ordered_numbers",
}


def _parse_datetime(value: str, *, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO-8601: {value}") from exc


def _flatten_evidence(
    value: Mapping[str, Any],
    *,
    prefix: str = "",
) -> dict[str, "EvidenceValue"]:
    output: dict[str, EvidenceValue] = {}
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if key in {"draw_no", "draw_datetime", "metadata_version"} and not prefix:
            continue
        if key in _FORBIDDEN_RESULT_FIELDS or path.split(".")[-1] in _FORBIDDEN_RESULT_FIELDS:
            raise ValueError(f"result field is forbidden in physical metadata: {path}")
        if isinstance(item, Mapping) and set(item).intersection(_EVIDENCE_KEYS):
            output[path] = EvidenceValue.from_mapping(item)
        elif isinstance(item, Mapping):
            output.update(_flatten_evidence(item, prefix=path))
        else:
            raise ValueError(f"physical metadata leaf must be an evidence object: {path}")
    return output


@dataclass(frozen=True)
class EvidenceValue:
    value: Any = None
    status: str = "unknown"
    source_type: str = "none"
    source_url: str | None = None
    observed_at: str | None = None
    available_before_draw: bool = False
    confidence: float = 0.0
    notes: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "EvidenceValue":
        evidence = cls(
            value=value.get("value"),
            status=str(value.get("status", "unknown")),
            source_type=str(value.get("source_type", "none")),
            source_url=(None if value.get("source_url") is None else str(value["source_url"])),
            observed_at=(None if value.get("observed_at") is None else str(value["observed_at"])),
            available_before_draw=bool(value.get("available_before_draw", False)),
            confidence=float(value.get("confidence", 0.0)),
            notes=(None if value.get("notes") is None else str(value["notes"])),
        )
        evidence.validate()
        return evidence

    def validate(self) -> None:
        if self.status not in _ALLOWED_STATUSES:
            raise ValueError(f"invalid evidence status: {self.status}")
        if self.source_type not in _ALLOWED_SOURCE_TYPES:
            raise ValueError(f"invalid source_type: {self.source_type}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        if self.observed_at is not None:
            _parse_datetime(self.observed_at, field_name="observed_at")
        if self.status == "verified" and not self.source_url:
            raise ValueError("verified evidence requires source_url")
        if self.status in {"unknown", "inferred"} and self.available_before_draw:
            raise ValueError(f"{self.status} evidence cannot be prediction-eligible")

    def is_present(self) -> bool:
        return self.value is not None and self.status != "unknown"

    def is_traceable(self) -> bool:
        return bool(self.source_url) and self.source_type != "none"

    def is_prediction_eligible(self, draw_datetime: str) -> bool:
        if (
            self.value is None
            or self.status not in _ELIGIBLE_STATUSES
            or not self.available_before_draw
            or self.confidence <= 0.0
            or self.observed_at is None
        ):
            return False
        draw_time = _parse_datetime(draw_datetime, field_name="draw_datetime")
        observed_time = _parse_datetime(self.observed_at, field_name="observed_at")
        if draw_time.tzinfo is None or observed_time.tzinfo is None:
            raise ValueError("draw_datetime and observed_at must include timezone offsets")
        return observed_time <= draw_time


@dataclass(frozen=True)
class MetadataQuality:
    required_field_completeness: float
    weighted_reliability: float
    pre_draw_availability_rate: float
    source_traceability_rate: float
    active: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "required_field_completeness": self.required_field_completeness,
            "weighted_reliability": self.weighted_reliability,
            "pre_draw_availability_rate": self.pre_draw_availability_rate,
            "source_traceability_rate": self.source_traceability_rate,
            "active": self.active,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class PhysicalDrawMetadata:
    draw_no: int
    draw_datetime: str
    metadata_version: str
    fields: Mapping[str, EvidenceValue]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PhysicalDrawMetadata":
        record = cls(
            draw_no=int(value["draw_no"]),
            draw_datetime=str(value["draw_datetime"]),
            metadata_version=str(value.get("metadata_version", "unknown")),
            fields=_flatten_evidence(value),
        )
        record.validate()
        return record

    def validate(self) -> None:
        if self.draw_no < 1:
            raise ValueError("draw_no must be positive")
        draw_time = _parse_datetime(self.draw_datetime, field_name="draw_datetime")
        if draw_time.tzinfo is None:
            raise ValueError("draw_datetime must include a timezone offset")
        if not self.fields:
            raise ValueError("physical metadata must contain at least one evidence field")
        for path, evidence in self.fields.items():
            if path.split(".")[-1] in _FORBIDDEN_RESULT_FIELDS:
                raise ValueError(f"result field is forbidden in physical metadata: {path}")
            evidence.validate()
            if evidence.available_before_draw and evidence.observed_at is not None:
                observed_time = _parse_datetime(evidence.observed_at, field_name=f"{path}.observed_at")
                if observed_time.tzinfo is None:
                    raise ValueError(f"{path}.observed_at must include timezone offset")
                if observed_time > draw_time:
                    raise ValueError(f"{path} was observed after the draw but marked pre-draw")

    def eligible_fields(self) -> dict[str, EvidenceValue]:
        return {
            path: evidence
            for path, evidence in self.fields.items()
            if evidence.is_prediction_eligible(self.draw_datetime)
        }

    def context_values(self, config: EngineConfig = DEFAULT_CONFIG) -> dict[str, EvidenceValue]:
        eligible = self.eligible_fields()
        return {
            path: eligible[path]
            for path in config.physical_context_fields
            if path in eligible
        }

    def quality(self, config: EngineConfig = DEFAULT_CONFIG) -> MetadataQuality:
        required = tuple(config.physical_required_fields)
        present = [self.fields.get(path) for path in required]
        present_values = [evidence for evidence in present if evidence is not None and evidence.is_present()]
        completeness = len(present_values) / len(required) if required else 1.0
        weighted_reliability = (
            sum(evidence.confidence for evidence in present_values) / len(required)
            if required
            else 1.0
        )
        pre_draw_count = sum(
            evidence.is_prediction_eligible(self.draw_datetime) for evidence in present_values
        )
        pre_draw_rate = pre_draw_count / len(present_values) if present_values else 0.0
        traceable_count = sum(evidence.is_traceable() for evidence in present_values)
        traceability = traceable_count / len(present_values) if present_values else 0.0

        reasons: list[str] = []
        if completeness < config.physical_min_completeness:
            reasons.append("required_field_completeness_below_threshold")
        if weighted_reliability < config.physical_min_weighted_reliability:
            reasons.append("weighted_reliability_below_threshold")
        if pre_draw_rate < config.physical_required_pre_draw_rate:
            reasons.append("pre_draw_availability_below_threshold")
        if traceability < config.physical_min_source_traceability:
            reasons.append("source_traceability_below_threshold")
        return MetadataQuality(
            required_field_completeness=completeness,
            weighted_reliability=weighted_reliability,
            pre_draw_availability_rate=pre_draw_rate,
            source_traceability_rate=traceability,
            active=not reasons,
            reasons=tuple(reasons),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "draw_no": self.draw_no,
            "draw_datetime": self.draw_datetime,
            "metadata_version": self.metadata_version,
            "fields": {
                path: {
                    "value": evidence.value,
                    "status": evidence.status,
                    "source_type": evidence.source_type,
                    "source_url": evidence.source_url,
                    "observed_at": evidence.observed_at,
                    "available_before_draw": evidence.available_before_draw,
                    "confidence": evidence.confidence,
                    "notes": evidence.notes,
                }
                for path, evidence in sorted(self.fields.items())
            },
        }


def validate_metadata_sequence(
    metadata: Sequence[PhysicalDrawMetadata],
    *,
    target_draw_no: int | None = None,
) -> tuple[PhysicalDrawMetadata, ...]:
    ordered = tuple(sorted(metadata, key=lambda item: item.draw_no))
    if len({item.draw_no for item in ordered}) != len(ordered):
        raise ValueError("physical metadata contains duplicate draw_no values")
    if target_draw_no is not None and any(item.draw_no > target_draw_no for item in ordered):
        raise ValueError("physical metadata contains a future draw")
    for item in ordered:
        item.validate()
    return ordered
