#!/usr/bin/env python3
"""Validate the canonical draw archive without network access."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
from collections import Counter
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def checksum_core(record: dict[str, Any]) -> str:
    core = {
        "draw_no": record["draw_no"],
        "draw_date": record["draw_date"],
        "numbers": record["numbers"],
        "bonus_number": record["bonus_number"],
    }
    return hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()


def validate(path: pathlib.Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(records, list) or not records:
        return {"status": "failed", "errors": ["records must be a non-empty array"], "warnings": []}

    draw_numbers = [record.get("draw_no") for record in records]
    duplicates = sorted(number for number, count in Counter(draw_numbers).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate draw numbers: {duplicates}")

    expected = list(range(1, max(draw_numbers) + 1))
    missing = sorted(set(expected) - set(draw_numbers))
    if missing:
        errors.append(f"missing draw numbers: {missing}")

    previous_date: dt.date | None = None
    previous_draw: int | None = None
    date_gaps: list[dict[str, int]] = []

    for record in records:
        draw_no = record.get("draw_no")
        numbers = record.get("numbers")
        bonus = record.get("bonus_number")
        status = record.get("verification_status")
        locked = record.get("locked")

        if not isinstance(draw_no, int) or draw_no < 1:
            errors.append(f"invalid draw number: {draw_no!r}")
            continue
        if not isinstance(numbers, list) or len(numbers) != 6:
            errors.append(f"draw {draw_no}: numbers must contain six values")
            continue
        if len(set(numbers)) != 6:
            errors.append(f"draw {draw_no}: duplicate winning number")
        if numbers != sorted(numbers):
            errors.append(f"draw {draw_no}: numbers are not sorted")
        if not all(isinstance(number, int) and 1 <= number <= 45 for number in numbers):
            errors.append(f"draw {draw_no}: number outside 1..45")
        if not isinstance(bonus, int) or not 1 <= bonus <= 45:
            errors.append(f"draw {draw_no}: invalid bonus")
        elif bonus in numbers:
            errors.append(f"draw {draw_no}: bonus duplicates main number")

        try:
            draw_date = dt.date.fromisoformat(record["draw_date"])
        except (KeyError, ValueError, TypeError):
            errors.append(f"draw {draw_no}: invalid draw_date")
            continue
        if draw_date.weekday() != 5:
            warnings.append(f"draw {draw_no}: draw date is not Saturday")
        if previous_date is not None and previous_draw is not None:
            gap = (draw_date - previous_date).days
            if gap != 7:
                date_gaps.append({"from_draw": previous_draw, "to_draw": draw_no, "days": gap})
        previous_date = draw_date
        previous_draw = draw_no

        expected_checksum = checksum_core(record)
        if record.get("checksum") != expected_checksum:
            errors.append(f"draw {draw_no}: checksum mismatch")

        if status in {"verified", "locked"} and not record.get("verified_at"):
            errors.append(f"draw {draw_no}: verified record missing verified_at")
        if locked and status not in {"verified", "locked"}:
            errors.append(f"draw {draw_no}: unlocked verification status marked locked")
        if status == "auto_checked" and locked:
            errors.append(f"draw {draw_no}: mirror-only record must not be locked")

    if date_gaps:
        warnings.append(f"non-seven-day intervals: {date_gaps}")

    return {
        "status": "passed" if not errors else "failed",
        "record_count": len(records),
        "first_draw": records[0]["draw_no"],
        "last_draw": records[-1]["draw_no"],
        "verification_counts": dict(Counter(record.get("verification_status") for record in records)),
        "locked_count": sum(bool(record.get("locked")) for record in records),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/draws.json")
    args = parser.parse_args()
    result = validate(pathlib.Path(args.path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
