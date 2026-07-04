"""Dataset and future-cutoff checks for Product Closeout Gate C2."""

from __future__ import annotations

import copy
import pathlib
import tempfile
from typing import Any

from engine.data_loader import load_dataset, parse_records, records_for_target
from engine.hashing import canonical_json
from product.config import DATASET_VERSION, EXPECTED_DATA_HASH
from product.run_prediction import run_product_prediction

from .common import file_sha256, load_json, raises_file_not_found, raises_value_error, sha256_bytes
from .constants import (
    EXPECTED_FIRST_DRAW,
    EXPECTED_LAST_DRAW,
    EXPECTED_RECORD_COUNT,
    EXPECTED_VERIFICATION_STATUS,
    FIXED_GENERATED_AT,
    FIXED_TARGET,
)


def parse_checksum_file(path: pathlib.Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        digest, relative = line.split(maxsplit=1)
        result[relative.strip()] = digest
    return result


def verify_data(root: pathlib.Path) -> dict[str, Any]:
    dataset_path = root / "data/draws.json"
    data_hash = sha256_bytes(dataset_path.read_bytes())
    data_version, records = load_dataset(dataset_path)
    draw_numbers = [record.draw_no for record in records]
    statuses: dict[str, int] = {}
    for record in records:
        statuses[record.verification_status] = statuses.get(record.verification_status, 0) + 1

    integrity = load_json(root / "reports/data_integrity.json")
    checksums = parse_checksum_file(root / "data/checksums.sha256")
    actual = {relative: file_sha256(root / relative) for relative in checksums}
    conditions = {
        "hash": data_hash == EXPECTED_DATA_HASH,
        "version": data_version == DATASET_VERSION,
        "record_count": len(records) == EXPECTED_RECORD_COUNT,
        "draw_range": draw_numbers == list(range(EXPECTED_FIRST_DRAW, EXPECTED_LAST_DRAW + 1)),
        "verification_status": statuses == {EXPECTED_VERIFICATION_STATUS: EXPECTED_RECORD_COUNT},
        "officially_locked_false": all(record.locked is False for record in records),
        "integrity_report": (
            integrity.get("status") == "passed"
            and integrity.get("record_count") == EXPECTED_RECORD_COUNT
            and integrity.get("first_draw") == EXPECTED_FIRST_DRAW
            and integrity.get("last_draw") == EXPECTED_LAST_DRAW
            and integrity.get("verification_counts") == {EXPECTED_VERIFICATION_STATUS: EXPECTED_RECORD_COUNT}
            and integrity.get("official_matches") == 0
            and integrity.get("dataset_sha256") == EXPECTED_DATA_HASH
        ),
        "checksums": all(checksums[key] == actual[key] for key in checksums),
    }
    return {
        "pass": all(conditions.values()),
        "conditions": conditions,
        "data_hash": data_hash,
        "data_version": data_version,
        "record_count": len(records),
        "first_draw": records[0].draw_no,
        "last_draw": records[-1].draw_no,
        "verification_counts": statuses,
        "officially_locked": all(record.locked for record in records),
        "checksums": {"expected": checksums, "actual": actual},
    }


def verify_data_negative_cases(root: pathlib.Path) -> dict[str, Any]:
    payload = load_json(root / "data/draws.json")
    records = payload["records"]
    cases: dict[str, bool] = {}

    duplicate = copy.deepcopy(records)
    duplicate[1]["draw_no"] = duplicate[0]["draw_no"]
    cases["duplicate_draw"] = raises_value_error(lambda: parse_records(duplicate))

    missing = copy.deepcopy(records)
    missing.pop(1)
    cases["missing_draw"] = raises_value_error(lambda: parse_records(missing))

    invalid_number = copy.deepcopy(records)
    invalid_number[0]["numbers"][0] = 0
    cases["invalid_number"] = raises_value_error(lambda: parse_records(invalid_number))

    duplicate_number = copy.deepcopy(records)
    duplicate_number[0]["numbers"][1] = duplicate_number[0]["numbers"][0]
    cases["duplicate_number"] = raises_value_error(lambda: parse_records(duplicate_number))

    with tempfile.TemporaryDirectory() as temporary:
        bad_path = pathlib.Path(temporary) / "draws.json"
        bad_payload = copy.deepcopy(payload)
        bad_payload["data_version"] = "tampered"
        bad_path.write_text(canonical_json(bad_payload), encoding="utf-8")
        cases["product_hash_mismatch"] = raises_value_error(
            lambda: run_product_prediction(
                target_draw_no=FIXED_TARGET,
                dataset_path=bad_path,
                generated_at=FIXED_GENERATED_AT,
            )
        )
        missing_path = pathlib.Path(temporary) / "missing.json"
        cases["missing_dataset"] = raises_file_not_found(
            lambda: run_product_prediction(
                target_draw_no=FIXED_TARGET,
                dataset_path=missing_path,
                generated_at=FIXED_GENERATED_AT,
            )
        )
    return {"pass": all(cases.values()), "cases": cases}


def verify_cutoff(root: pathlib.Path) -> dict[str, Any]:
    _, records = load_dataset(root / "data/draws.json")
    positive = records_for_target(records, target_draw_no=FIXED_TARGET, research_only=True, minimum_history=299)
    truncated = records_for_target(
        records[:-1],
        target_draw_no=EXPECTED_LAST_DRAW,
        research_only=True,
        minimum_history=299,
    )
    full_rejected = raises_value_error(
        lambda: records_for_target(
            records,
            target_draw_no=EXPECTED_LAST_DRAW,
            research_only=True,
            minimum_history=299,
        )
    )
    conditions = {
        "positive_target_minus_one": positive[-1].draw_no == FIXED_TARGET - 1,
        "positive_count": len(positive) == EXPECTED_RECORD_COUNT,
        "truncated_target_minus_one": truncated[-1].draw_no == EXPECTED_LAST_DRAW - 1,
        "full_future_rejected": full_rejected,
    }
    return {
        "pass": all(conditions.values()),
        "conditions": conditions,
        "positive_last_draw": positive[-1].draw_no,
        "truncated_last_draw": truncated[-1].draw_no,
    }
