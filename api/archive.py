"""Same-origin canonical draw archive endpoint for Vercel."""

from __future__ import annotations

import hashlib
import json
import pathlib
from http.server import BaseHTTPRequestHandler

from product.config import EXPECTED_DATA_HASH


class handler(BaseHTTPRequestHandler):
    def _write_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=300, stale-while-revalidate=3600")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        try:
            root = pathlib.Path.cwd()
            raw = (root / "data/draws.json").read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != EXPECTED_DATA_HASH:
                raise ValueError("canonical dataset hash mismatch")
            source = json.loads(raw.decode("utf-8"))
            records = source["records"]
            payload = {
                "data_version": source["data_version"],
                "canonical_data_hash": digest,
                "record_count": len(records),
                "first_draw": records[0]["draw_no"],
                "last_draw": records[-1]["draw_no"],
                "verification_status": "auto_checked",
                "officially_locked": False,
                "records": [
                    {
                        "draw_no": item["draw_no"],
                        "draw_date": item["draw_date"],
                        "numbers": item["numbers"],
                        "bonus_number": item["bonus_number"],
                        "verification_status": item["verification_status"],
                        "locked": item["locked"],
                        "checksum": item["checksum"],
                        "source": item["source"],
                    }
                    for item in records
                ],
            }
            self._write_json(200, payload)
        except Exception as exc:  # pragma: no cover - Vercel boundary
            self._write_json(500, {"error": "archive_unavailable", "detail": str(exc)})
