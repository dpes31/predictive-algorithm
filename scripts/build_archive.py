#!/usr/bin/env python3
"""Generate the read-only archive index consumed by the Gate 1 HTML UI."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
from typing import Any

ARCHIVE_SCHEMA_VERSION = "1.0.0"


def frequency(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = collections.Counter(number for record in records for number in record["numbers"])
    return {str(number): counts.get(number, 0) for number in range(1, 46)}


def gap_since_seen(records: list[dict[str, Any]]) -> dict[str, int | None]:
    latest_draw = records[-1]["draw_no"] if records else 0
    last_seen: dict[int, int] = {}
    for record in records:
        for number in record["numbers"]:
            last_seen[number] = record["draw_no"]
    return {
        str(number): (latest_draw - last_seen[number] if number in last_seen else None)
        for number in range(1, 46)
    }


def read_existing(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/draws.json")
    parser.add_argument("--output", default="app/data/archive_index.json")
    args = parser.parse_args()

    source_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    records = payload["records"]
    if not records:
        raise RuntimeError("Archive source contains no records.")

    source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    existing = read_existing(output_path)
    if (
        existing
        and existing.get("archive_schema_version") == ARCHIVE_SCHEMA_VERSION
        and existing.get("source_sha256") == source_sha256
    ):
        print(f"Archive index already matches source SHA-256: {output_path}")
        return 0

    years: dict[str, int] = collections.Counter(record["draw_date"][:4] for record in records)
    windows = {
        "all": frequency(records),
        "last_10": frequency(records[-10:]),
        "last_30": frequency(records[-30:]),
        "last_52": frequency(records[-52:]),
    }

    archive = {
        "archive_schema_version": ARCHIVE_SCHEMA_VERSION,
        "data_version": payload["data_version"],
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_sha256": source_sha256,
        "record_count": len(records),
        "first_draw": records[0]["draw_no"],
        "last_draw": records[-1]["draw_no"],
        "years": dict(sorted(years.items(), reverse=True)),
        "statistics": {
            "frequencies": windows,
            "gap_since_seen": gap_since_seen(records),
        },
        "draws": [
            {
                "draw_no": record["draw_no"],
                "draw_date": record["draw_date"],
                "numbers": record["numbers"],
                "bonus_number": record["bonus_number"],
                "verification_status": record["verification_status"],
                "locked": record["locked"],
                "source": record["source"],
                "source_reference": record["source_reference"],
                "checksum": record["checksum"],
            }
            for record in reversed(records)
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(archive, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built archive index with {len(records)} draws: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
