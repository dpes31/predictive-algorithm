"""Global metadata veto for physical evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .config import DEFAULT_CONFIG, EngineConfig
from .physical_metadata import PhysicalDrawMetadata


@dataclass(frozen=True)
class MetadataVetoResult:
    invalid: bool
    reasons: tuple[str, ...]


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate_metadata_veto(
    metadata: PhysicalDrawMetadata,
    *,
    target_draw_no: int,
    config: EngineConfig = DEFAULT_CONFIG,
) -> MetadataVetoResult:
    reasons: list[str] = []
    if metadata.draw_no != target_draw_no:
        reasons.append("target_draw_mismatch")
    if metadata.metadata_version != config.physical_data_schema_version:
        reasons.append("schema_version_mismatch")
    draw_time = _parse(metadata.draw_datetime)
    for path, evidence in metadata.fields.items():
        leaf = path.split(".")[-1]
        if leaf in {
            "ordered_numbers",
            "winning_numbers",
            "bonus_number",
            "draw_results",
            "current_draw_result",
            "current_ordered_numbers",
        }:
            reasons.append(f"result_leakage:{path}")
        if evidence.available_before_draw and evidence.observed_at is None:
            reasons.append(f"missing_predraw_timestamp:{path}")
        if evidence.observed_at is not None and _parse(evidence.observed_at) > draw_time:
            reasons.append(f"post_draw_timestamp:{path}")
        if evidence.status == "verified" and not evidence.is_traceable():
            reasons.append(f"untraceable_verified_field:{path}")
    return MetadataVetoResult(bool(reasons), tuple(sorted(set(reasons))))


def validate_metadata_batch(
    records: Iterable[PhysicalDrawMetadata],
    *,
    target_draw_no: int,
    config: EngineConfig = DEFAULT_CONFIG,
) -> MetadataVetoResult:
    reasons: list[str] = []
    seen: set[int] = set()
    for record in records:
        if record.draw_no in seen:
            reasons.append(f"duplicate_draw:{record.draw_no}")
        seen.add(record.draw_no)
        if record.draw_no > target_draw_no:
            reasons.append(f"future_metadata:{record.draw_no}")
        result = evaluate_metadata_veto(record, target_draw_no=record.draw_no, config=config)
        reasons.extend(result.reasons)
    return MetadataVetoResult(bool(reasons), tuple(sorted(set(reasons))))
