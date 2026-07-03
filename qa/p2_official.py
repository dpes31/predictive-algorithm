"""Authoritative Donghaeng Lottery source access and reconciliation."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from engine.hashing import sha256_value
from product.config import DATASET_VERSION, EXPECTED_DATA_HASH

from .p2_common import (
    CANONICAL_LAST_DRAW,
    CANONICAL_RECORD_COUNT,
    P2_CONTRACT_VERSION,
    sha256_bytes,
)

OFFICIAL_SOURCES = (
    {
        "id": "donghaeng-json-endpoint",
        "operator": "Donghaeng Lottery",
        "authority": "official_operator",
        "domain": "www.dhlottery.co.kr",
        "kind": "structured_json_per_draw",
        "url_template": "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}",
    },
    {
        "id": "donghaeng-result-page",
        "operator": "Donghaeng Lottery",
        "authority": "official_operator",
        "domain": "www.dhlottery.co.kr",
        "kind": "official_html_per_draw",
        "url_template": "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={draw_no}",
    },
)


class OfficialSourceUnavailable(RuntimeError):
    """Raised when the authoritative source cannot be evaluated."""


@dataclass(frozen=True)
class OfficialRecord:
    draw_no: int
    draw_date: str
    numbers: tuple[int, ...]
    bonus_number: int
    raw_sha256: str
    source_url: str

    def comparison_dict(self) -> dict[str, Any]:
        return {
            "draw_no": self.draw_no,
            "draw_date": self.draw_date,
            "numbers": list(self.numbers),
            "bonus_number": self.bonus_number,
        }


def _parse_json_record(raw: bytes, draw_no: int, source_url: str) -> OfficialRecord:
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OfficialSourceUnavailable(f"official JSON response is not valid JSON for draw {draw_no}") from exc
    if not isinstance(payload, dict) or payload.get("returnValue") != "success":
        raise OfficialSourceUnavailable(f"official JSON endpoint did not return success for draw {draw_no}")
    returned_draw = int(payload.get("drwNo", draw_no))
    if returned_draw != draw_no:
        raise OfficialSourceUnavailable(f"official JSON endpoint returned draw {returned_draw} for request {draw_no}")
    numbers = tuple(sorted(int(payload[f"drwtNo{index}"]) for index in range(1, 7)))
    return OfficialRecord(
        draw_no=draw_no,
        draw_date=str(payload["drwNoDate"]),
        numbers=numbers,
        bonus_number=int(payload["bnusNo"]),
        raw_sha256=sha256_bytes(raw),
        source_url=source_url,
    )


def _parse_html_record(raw: bytes, draw_no: int, source_url: str) -> OfficialRecord:
    text = raw.decode("utf-8", errors="replace")
    blocked_markers = ("서비스 접근 대기", "접속이 차단", "ERROR 404", "페이지를 찾을 수 없습니다")
    if any(marker in text for marker in blocked_markers):
        raise OfficialSourceUnavailable(f"official result page unavailable for draw {draw_no}")
    date_match = re.search(r"(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일", text)
    numbers = [int(value) for value in re.findall(r'class=["\'][^"\']*ball_645[^"\']*["\'][^>]*>\s*(\d{1,2})\s*<', text)]
    if date_match is None or len(numbers) < 7:
        raise OfficialSourceUnavailable(f"official result page structure is unsupported for draw {draw_no}")
    draw_date = f"{int(date_match.group(1)):04d}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"
    return OfficialRecord(
        draw_no=draw_no,
        draw_date=draw_date,
        numbers=tuple(sorted(numbers[:6])),
        bonus_number=numbers[6],
        raw_sha256=sha256_bytes(raw),
        source_url=source_url,
    )


def fetch_official_record(
    source: Mapping[str, str],
    draw_no: int,
    *,
    timeout_seconds: float,
    retries: int,
) -> OfficialRecord:
    source_url = source["url_template"].format(draw_no=draw_no)
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            source_url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Product-P2-QA/1.0; +https://github.com/dpes31/predictive-algorithm)",
                "Accept": "application/json,text/html;q=0.9,*/*;q=0.1",
                "Referer": "https://www.dhlottery.co.kr/",
                "Cache-Control": "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read()
            if source["kind"] == "structured_json_per_draw":
                return _parse_json_record(raw, draw_no, source_url)
            return _parse_html_record(raw, draw_no, source_url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OfficialSourceUnavailable) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise OfficialSourceUnavailable(str(last_error) if last_error else f"official source unavailable for {draw_no}")


def reconcile_official(
    canonical_records: Sequence[Any],
    *,
    timeout_seconds: float,
    retries: int,
    delay_seconds: float,
    retrieved_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    selected: Mapping[str, str] | None = None

    for source in OFFICIAL_SOURCES:
        source_attempt = {"source": dict(source), "preflight": [], "selected": False}
        try:
            for draw_no in (1, CANONICAL_LAST_DRAW):
                record = fetch_official_record(
                    source,
                    draw_no,
                    timeout_seconds=timeout_seconds,
                    retries=retries,
                )
                source_attempt["preflight"].append(
                    {"draw_no": draw_no, "status": "PASS", "raw_sha256": record.raw_sha256}
                )
            source_attempt["selected"] = True
            selected = source
            attempts.append(source_attempt)
            break
        except OfficialSourceUnavailable as exc:
            source_attempt["preflight"].append({"status": "BLOCKED", "error": str(exc)})
            attempts.append(source_attempt)

    base_manifest: dict[str, Any] = {
        "contract_version": P2_CONTRACT_VERSION,
        "retrieved_at": retrieved_at,
        "authority_policy": "official_operator_only",
        "source_candidates": [dict(source) for source in OFFICIAL_SOURCES],
        "selection_attempts": attempts,
        "selected_source": None if selected is None else dict(selected),
        "canonical_data_version": DATASET_VERSION,
        "canonical_data_sha256": EXPECTED_DATA_HASH,
        "draw_range": [1, CANONICAL_LAST_DRAW],
    }

    if selected is None:
        reconciliation = {
            "contract_version": P2_CONTRACT_VERSION,
            "status": "OFFICIAL_RECONCILIATION_BLOCKED",
            "canonical_state_before": "AUTO_CHECKED",
            "state_transitions": [
                "AUTO_CHECKED -> RECONCILIATION_PENDING",
                "RECONCILIATION_PENDING -> OFFICIAL_RECONCILIATION_BLOCKED",
            ],
            "canonical_state_after": "OFFICIAL_RECONCILIATION_BLOCKED",
            "expected_draws": CANONICAL_RECORD_COUNT,
            "matched": 0,
            "missing": CANONICAL_RECORD_COUNT,
            "extra": 0,
            "field_mismatches": 0,
            "unresolved": CANONICAL_RECORD_COUNT,
            "mismatches": [],
            "source_inventory": base_manifest,
            "reason": "authoritative official source unavailable or structurally inaccessible",
        }
        base_manifest.update(
            {
                "status": "OFFICIAL_RECONCILIATION_BLOCKED",
                "official_records_sha256": None,
                "response_hashes": [],
            }
        )
        return reconciliation, base_manifest

    official_records: list[OfficialRecord] = []
    unresolved: list[dict[str, Any]] = []
    canonical_by_draw = {record.draw_no: record for record in canonical_records}
    mismatches: list[dict[str, Any]] = []

    for draw_no in range(1, CANONICAL_LAST_DRAW + 1):
        try:
            official = fetch_official_record(
                selected,
                draw_no,
                timeout_seconds=timeout_seconds,
                retries=retries,
            )
            official_records.append(official)
            canonical = canonical_by_draw.get(draw_no)
            if canonical is None:
                mismatches.append({"draw_no": draw_no, "fields": ["canonical_missing"]})
            else:
                fields: list[str] = []
                if canonical.draw_date != official.draw_date:
                    fields.append("draw_date")
                if tuple(canonical.numbers) != official.numbers:
                    fields.append("numbers")
                if canonical.bonus_number != official.bonus_number:
                    fields.append("bonus_number")
                if fields:
                    mismatches.append(
                        {
                            "draw_no": draw_no,
                            "fields": fields,
                            "canonical": {
                                "draw_date": canonical.draw_date,
                                "numbers": list(canonical.numbers),
                                "bonus_number": canonical.bonus_number,
                            },
                            "official": official.comparison_dict(),
                        }
                    )
        except OfficialSourceUnavailable as exc:
            unresolved.append({"draw_no": draw_no, "error": str(exc)})
        if delay_seconds > 0:
            time.sleep(delay_seconds)

    matched = CANONICAL_RECORD_COUNT - len(mismatches) - len(unresolved)
    if mismatches:
        status = "OFFICIAL_RECONCILIATION_FAIL"
        state_after = status
        transitions = [
            "AUTO_CHECKED -> RECONCILIATION_PENDING",
            "RECONCILIATION_PENDING -> OFFICIAL_RECONCILIATION_FAIL",
        ]
    elif unresolved or len(official_records) != CANONICAL_RECORD_COUNT:
        status = "OFFICIAL_RECONCILIATION_BLOCKED"
        state_after = status
        transitions = [
            "AUTO_CHECKED -> RECONCILIATION_PENDING",
            "RECONCILIATION_PENDING -> OFFICIAL_RECONCILIATION_BLOCKED",
        ]
    else:
        status = "OFFICIALLY_VERIFIED"
        state_after = status
        transitions = [
            "AUTO_CHECKED -> RECONCILIATION_PENDING",
            "RECONCILIATION_PENDING -> OFFICIALLY_VERIFIED",
        ]

    normalized_records = [record.comparison_dict() for record in official_records]
    response_hashes = [
        {"draw_no": record.draw_no, "raw_sha256": record.raw_sha256, "source_url": record.source_url}
        for record in official_records
    ]
    official_records_sha256 = sha256_value(normalized_records) if normalized_records else None
    base_manifest.update(
        {
            "status": status,
            "official_records_sha256": official_records_sha256,
            "retrieved_record_count": len(official_records),
            "response_hashes": response_hashes,
        }
    )
    reconciliation = {
        "contract_version": P2_CONTRACT_VERSION,
        "status": status,
        "canonical_state_before": "AUTO_CHECKED",
        "state_transitions": transitions,
        "canonical_state_after": state_after,
        "expected_draws": CANONICAL_RECORD_COUNT,
        "matched": matched,
        "missing": len(unresolved),
        "extra": 0,
        "field_mismatches": len(mismatches),
        "unresolved": len(unresolved),
        "mismatches": mismatches,
        "unresolved_records": unresolved,
        "source_inventory": {
            "selected_source": dict(selected),
            "official_records_sha256": official_records_sha256,
            "response_hash_count": len(response_hashes),
        },
    }
    return reconciliation, base_manifest
