"""Canonical draw loading with hard future-data cutoffs."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Iterable, Mapping

from .contracts import DrawRecord


RESEARCH_ALLOWED_STATUSES = {"auto_checked", "verified", "locked"}
PUBLIC_ALLOWED_STATUSES = {"verified", "locked"}


def parse_records(values: Iterable[Mapping[str, Any]]) -> list[DrawRecord]:
    records = [DrawRecord.from_mapping(value) for value in values]
    records.sort(key=lambda record: record.draw_no)
    draw_numbers = [record.draw_no for record in records]
    if len(draw_numbers) != len(set(draw_numbers)):
        raise ValueError("duplicate draw numbers")
    if draw_numbers and draw_numbers != list(range(draw_numbers[0], draw_numbers[-1] + 1)):
        raise ValueError("draw numbers must be contiguous")
    return records


def load_dataset(path: str | pathlib.Path) -> tuple[str, list[DrawRecord]]:
    payload = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise ValueError("dataset must contain a records array")
    return str(payload.get("data_version", "unknown")), parse_records(payload["records"])


def records_for_target(
    records: Iterable[DrawRecord],
    *,
    target_draw_no: int,
    research_only: bool,
    minimum_history: int,
) -> list[DrawRecord]:
    ordered = sorted(records, key=lambda record: record.draw_no)
    if not ordered:
        raise ValueError("records must not be empty")
    if any(record.draw_no >= target_draw_no for record in ordered):
        raise ValueError("future-data cutoff violation: target or later draw is present")
    if ordered[-1].draw_no != target_draw_no - 1:
        raise ValueError("input_last_draw must equal target_draw_no - 1")
    if len(ordered) < minimum_history:
        raise ValueError(f"at least {minimum_history} historical draws are required")
    allowed = RESEARCH_ALLOWED_STATUSES if research_only else PUBLIC_ALLOWED_STATUSES
    invalid = sorted({record.verification_status for record in ordered if record.verification_status not in allowed})
    if invalid:
        raise ValueError(f"data status not allowed for this run: {invalid}")
    if not research_only and not all(record.locked for record in ordered):
        raise ValueError("public prediction requires locked records")
    return ordered
