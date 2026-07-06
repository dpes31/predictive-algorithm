"""Same-origin shared draw-overlay endpoint backed by Supabase, with a
transparent "not configured" fallback so the client can fall back to its
local-only overlay when no shared store is available.

GET    -> {"configured": bool, "records": [...], "warning"?: str}
POST   -> body {"record": {...}} inserts one new consecutive overlay record
DELETE -> body {"draw_no": n} removes the highest (most recent) overlay record
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from product.dynamic_prediction import _canonical_dataset, _root, validate_overlay
from server_store.overlay_store import (
    OverlayStoreError,
    delete_record,
    fetch_overlay,
    insert_record,
    is_configured,
)

MAX_BODY_BYTES = 1_000_000


def _canonical_records():
    canonical, _ = _canonical_dataset(_root())
    return canonical["records"]


class handler(BaseHTTPRequestHandler):
    def _write_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body is missing or too large")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request body must be an object")
        return payload

    def do_GET(self) -> None:
        if not is_configured():
            self._write_json(200, {"configured": False, "records": []})
            return
        try:
            canonical_records = _canonical_records()
            raw_records = fetch_overlay()
            validated = validate_overlay(raw_records, canonical_records)
            self._write_json(200, {"configured": True, "records": validated})
        except OverlayStoreError as exc:
            self._write_json(
                200,
                {"configured": True, "records": [], "warning": f"서버 overlay를 불러오지 못했습니다: {exc}"},
            )
        except ValueError as exc:
            self._write_json(
                200,
                {"configured": True, "records": [], "warning": f"서버 overlay 데이터가 올바르지 않습니다: {exc}"},
            )
        except Exception as exc:  # pragma: no cover - Vercel boundary
            self._write_json(
                200,
                {"configured": True, "records": [], "warning": f"서버 overlay 조회 중 오류가 발생했습니다: {exc}"},
            )

    def do_POST(self) -> None:
        try:
            payload = self._read_body()
        except (ValueError, json.JSONDecodeError) as exc:
            self._write_json(400, {"error": "invalid_request", "detail": str(exc)})
            return

        if not is_configured():
            self._write_json(
                503,
                {
                    "error": "overlay_store_not_configured",
                    "detail": "서버 공유 저장소(Supabase)가 설정되지 않았습니다. 이 브라우저에만 저장됩니다.",
                },
            )
            return

        new_record = payload.get("record")
        if not isinstance(new_record, dict):
            self._write_json(400, {"error": "invalid_request", "detail": "record 필드가 필요합니다."})
            return

        try:
            canonical_records = _canonical_records()
            current_overlay = fetch_overlay()
            candidate_overlay = [*current_overlay, new_record]
            validated = validate_overlay(candidate_overlay, canonical_records)
        except ValueError as exc:
            self._write_json(400, {"error": "invalid_overlay", "detail": str(exc)})
            return
        except OverlayStoreError as exc:
            self._write_json(502, {"error": "overlay_store_unavailable", "detail": str(exc)})
            return

        try:
            updated_records = insert_record(validated[-1])
            validated_updated = validate_overlay(updated_records, canonical_records)
            self._write_json(200, {"configured": True, "records": validated_updated})
        except OverlayStoreError as exc:
            self._write_json(502, {"error": "overlay_store_unavailable", "detail": str(exc)})
        except ValueError as exc:  # pragma: no cover - defensive
            self._write_json(500, {"error": "overlay_store_inconsistent", "detail": str(exc)})

    def do_DELETE(self) -> None:
        try:
            payload = self._read_body()
        except (ValueError, json.JSONDecodeError) as exc:
            self._write_json(400, {"error": "invalid_request", "detail": str(exc)})
            return

        if not is_configured():
            self._write_json(
                503,
                {
                    "error": "overlay_store_not_configured",
                    "detail": "서버 공유 저장소(Supabase)가 설정되지 않았습니다.",
                },
            )
            return

        draw_no = payload.get("draw_no")
        if not isinstance(draw_no, int) or isinstance(draw_no, bool):
            self._write_json(400, {"error": "invalid_request", "detail": "draw_no는 정수여야 합니다."})
            return

        try:
            current_overlay = fetch_overlay()
        except OverlayStoreError as exc:
            self._write_json(502, {"error": "overlay_store_unavailable", "detail": str(exc)})
            return

        if not current_overlay:
            self._write_json(400, {"error": "invalid_request", "detail": "삭제할 사용자 입력 회차가 없습니다."})
            return

        highest = max(int(r["draw_no"]) for r in current_overlay)
        if draw_no != highest:
            self._write_json(
                400,
                {
                    "error": "invalid_request",
                    "detail": f"가장 최근 회차({highest}회)만 삭제할 수 있습니다.",
                },
            )
            return

        try:
            updated_records = delete_record(draw_no)
            canonical_records = _canonical_records()
            validated_updated = validate_overlay(updated_records, canonical_records)
            self._write_json(200, {"configured": True, "records": validated_updated})
        except OverlayStoreError as exc:
            self._write_json(502, {"error": "overlay_store_unavailable", "detail": str(exc)})
        except ValueError as exc:  # pragma: no cover - defensive
            self._write_json(500, {"error": "overlay_store_inconsistent", "detail": str(exc)})
