#!/usr/bin/env python3
"""Build the Gate 1 canonical Lotto 6/45 archive.

The script fetches a complete public mirror, validates every record, and then
attempts an independent comparison with the official Donghaeng Lottery JSON
endpoint. Records are marked ``verified`` and ``locked`` only when the official
response is available and matches exactly. A mirror-only record remains
``auto_checked`` and is never silently presented as officially verified.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.request
from collections import Counter
from typing import Any

PRIMARY_URL = "https://smok95.github.io/lotto/results/all.json"
OFFICIAL_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
USER_AGENT = "predictive-algorithm-gate1/1.0 (+https://github.com/dpes31/predictive-algorithm)"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def request_json(url: str, timeout: int = 20, retries: int = 3) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return json.loads(response.read().decode(charset))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch JSON from {url}: {last_error}")


def official_payload(draw_no: int) -> dict[str, Any] | None:
    try:
        payload = request_json(OFFICIAL_URL.format(draw_no=draw_no), timeout=12, retries=2)
    except RuntimeError:
        return None
    if not isinstance(payload, dict) or payload.get("returnValue") != "success":
        return None
    try:
        return {
            "draw_no": int(payload["drwNo"]),
            "draw_date": str(payload["drwNoDate"]),
            "numbers": sorted(int(payload[f"drwtNo{i}"]) for i in range(1, 7)),
            "bonus_number": int(payload["bnusNo"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def normalize_primary(raw: dict[str, Any]) -> dict[str, Any]:
    date_value = str(raw["date"]).split("T", 1)[0]
    return {
        "draw_no": int(raw["draw_no"]),
        "draw_date": date_value,
        "numbers": sorted(int(number) for number in raw["numbers"]),
        "bonus_number": int(raw["bonus_no"]),
    }


def record_checksum(core: dict[str, Any]) -> str:
    return sha256_text(canonical_json(core))


def structural_validation(records: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    draw_numbers = [record["draw_no"] for record in records]
    duplicate_draws = sorted(number for number, count in Counter(draw_numbers).items() if count > 1)
    if duplicate_draws:
        errors.append(f"Duplicate draw numbers: {duplicate_draws}")

    expected = list(range(1, max(draw_numbers, default=0) + 1))
    missing = sorted(set(expected) - set(draw_numbers))
    if missing:
        errors.append(f"Missing draw numbers: {missing}")

    date_gaps: list[dict[str, Any]] = []
    previous_date: dt.date | None = None
    previous_draw: int | None = None

    for record in records:
        draw_no = record["draw_no"]
        numbers = record["numbers"]
        bonus = record["bonus_number"]
        if len(numbers) != 6:
            errors.append(f"Draw {draw_no}: expected six numbers")
        if len(set(numbers)) != 6:
            errors.append(f"Draw {draw_no}: duplicate winning number")
        if numbers != sorted(numbers):
            errors.append(f"Draw {draw_no}: winning numbers are not sorted")
        if not all(1 <= number <= 45 for number in numbers):
            errors.append(f"Draw {draw_no}: winning number outside 1..45")
        if not 1 <= bonus <= 45:
            errors.append(f"Draw {draw_no}: bonus outside 1..45")
        if bonus in numbers:
            errors.append(f"Draw {draw_no}: bonus duplicates a winning number")
        try:
            draw_date = dt.date.fromisoformat(record["draw_date"])
        except ValueError:
            errors.append(f"Draw {draw_no}: invalid ISO date")
            continue
        if draw_date.weekday() != 5:
            warnings.append(f"Draw {draw_no}: date is not Saturday ({draw_date.isoformat()})")
        if previous_date is not None and previous_draw is not None:
            delta = (draw_date - previous_date).days
            if delta != 7:
                date_gaps.append({"from_draw": previous_draw, "to_draw": draw_no, "days": delta})
        previous_date = draw_date
        previous_draw = draw_no

    if date_gaps:
        warnings.append(f"Non-seven-day intervals: {date_gaps}")

    return {
        "errors": errors,
        "warnings": warnings,
        "duplicate_draws": duplicate_draws,
        "missing_draws": missing,
        "date_gaps": date_gaps,
    }


def verify_official(records: list[dict[str, Any]], mode: str) -> tuple[dict[int, dict[str, Any]], list[str]]:
    warnings: list[str] = []
    if mode == "none" or not records:
        return {}, ["Official verification disabled by configuration."]

    latest_draw = records[-1]["draw_no"]
    probe = official_payload(latest_draw)
    if probe is None:
        return {}, ["Official JSON endpoint unavailable; records remain auto_checked."]

    if mode == "latest":
        return {latest_draw: probe}, warnings

    verified: dict[int, dict[str, Any]] = {latest_draw: probe}
    remaining = [record["draw_no"] for record in records[:-1]]
    max_workers = max(1, min(int(os.getenv("OFFICIAL_VERIFY_WORKERS", "6")), 12))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(official_payload, draw_no): draw_no for draw_no in remaining}
        for future in concurrent.futures.as_completed(future_map):
            draw_no = future_map[future]
            try:
                payload = future.result()
            except Exception as exc:  # defensive: a single request must not hide other results
                warnings.append(f"Draw {draw_no}: official request error: {exc}")
                continue
            if payload is not None:
                verified[draw_no] = payload

    if len(verified) != len(records):
        warnings.append(
            f"Official endpoint returned {len(verified)} of {len(records)} records; "
            "unavailable records remain auto_checked."
        )
    return verified, warnings


def build(args: argparse.Namespace) -> int:
    generated_at = utc_now()
    raw_payload = request_json(args.primary_url, timeout=30, retries=4)
    if not isinstance(raw_payload, list):
        raise RuntimeError("Primary source must return a JSON array.")

    primary_records = [normalize_primary(item) for item in raw_payload]
    primary_records.sort(key=lambda item: item["draw_no"])
    if args.max_draw:
        primary_records = [item for item in primary_records if item["draw_no"] <= args.max_draw]
    if not primary_records:
        raise RuntimeError("No records were returned by the primary source.")

    validation = structural_validation(primary_records)
    if validation["errors"]:
        raise RuntimeError("Primary data failed structural validation: " + "; ".join(validation["errors"]))

    official_records, official_warnings = verify_official(primary_records, args.official_verify)
    mismatches: list[dict[str, Any]] = []
    official_matches = 0
    output_records: list[dict[str, Any]] = []

    for core in primary_records:
        draw_no = core["draw_no"]
        official = official_records.get(draw_no)
        status = "auto_checked"
        source = "smok95_lotto_mirror"
        source_reference = f"https://smok95.github.io/lotto/results/{draw_no}.json"
        verified_at: str | None = None
        locked = False

        if official is not None:
            comparable = {key: official[key] for key in ("draw_no", "draw_date", "numbers", "bonus_number")}
            if comparable == core:
                status = "verified"
                source = "dhlottery_official_json"
                source_reference = OFFICIAL_URL.format(draw_no=draw_no)
                verified_at = generated_at
                locked = True
                official_matches += 1
            else:
                mismatches.append({"draw_no": draw_no, "primary": core, "official": comparable})

        output_records.append(
            {
                **core,
                "source": source,
                "source_reference": source_reference,
                "verification_status": status,
                "verified_at": verified_at,
                "checksum": record_checksum(core),
                "created_at": generated_at,
                "updated_at": generated_at,
                "locked": locked,
            }
        )

    if mismatches:
        pathlib.Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.report).write_text(
            json.dumps({"status": "failed", "official_mismatches": mismatches}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        raise RuntimeError(f"Official comparison found {len(mismatches)} mismatched draws.")

    last = output_records[-1]
    data_version = f"draws-{last['draw_date'].replace('-', '.')}-r1"
    source_manifest = [
        {
            "name": "smok95/lotto public mirror",
            "url": args.primary_url,
            "role": "complete bootstrap source",
            "retrieved_at": generated_at,
            "notes": "The mirror itself warns that the official Donghaeng Lottery result is authoritative.",
        },
        {
            "name": "Donghaeng Lottery JSON endpoint",
            "url": OFFICIAL_URL,
            "role": "independent official comparison when available",
            "retrieved_at": generated_at if official_records else None,
            "notes": "Only exact matches are marked verified and locked.",
        },
    ]
    dataset = {
        "data_version": data_version,
        "generated_at": generated_at,
        "source_manifest": source_manifest,
        "records": output_records,
    }

    output_path = pathlib.Path(args.output)
    report_path = pathlib.Path(args.report)
    manifest_path = pathlib.Path(args.manifest)
    checksum_path = pathlib.Path(args.checksums)
    for path in (output_path, report_path, manifest_path, checksum_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    output_text = json.dumps(dataset, ensure_ascii=False, indent=2) + "\n"
    output_path.write_text(output_text, encoding="utf-8")
    manifest_path.write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status_counts = Counter(record["verification_status"] for record in output_records)
    report = {
        "status": "passed",
        "data_version": data_version,
        "generated_at": generated_at,
        "record_count": len(output_records),
        "first_draw": output_records[0]["draw_no"],
        "last_draw": last["draw_no"],
        "last_draw_date": last["draw_date"],
        "verification_counts": dict(status_counts),
        "official_matches": official_matches,
        "structural_validation": validation,
        "official_warnings": official_warnings,
        "official_mismatches": mismatches,
        "dataset_sha256": sha256_text(output_text),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checksum_lines = []
    for path in (output_path, report_path, manifest_path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {path.as_posix()}")
    checksum_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-url", default=PRIMARY_URL)
    parser.add_argument("--max-draw", type=int, default=1230)
    parser.add_argument("--official-verify", choices=("none", "latest", "all"), default="all")
    parser.add_argument("--output", default="data/draws.json")
    parser.add_argument("--report", default="reports/data_integrity.json")
    parser.add_argument("--manifest", default="data/source_manifest.json")
    parser.add_argument("--checksums", default="data/checksums.sha256")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(build(parse_args()))
