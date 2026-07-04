"""Same-origin dynamic CONTROL_M0 prediction endpoint for Vercel."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from product.dynamic_prediction import run_dynamic_prediction

MAX_BODY_BYTES = 1_000_000


class handler(BaseHTTPRequestHandler):
    def _write_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValueError("request body is missing or too large")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request body must be an object")
            result = run_dynamic_prediction(overlay=payload.get("overlay", []))
            self._write_json(200, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self._write_json(400, {"error": "invalid_request", "detail": str(exc)})
        except Exception as exc:  # pragma: no cover - Vercel boundary
            self._write_json(500, {"error": "prediction_unavailable", "detail": str(exc)})

    def do_GET(self) -> None:
        self._write_json(405, {"error": "method_not_allowed", "allowed": ["POST"]})
