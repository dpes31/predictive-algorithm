"""Local HTTP server for browser-level full-product UI verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from product.config import EXPECTED_DATA_HASH
from product.dynamic_prediction import run_dynamic_prediction

PUBLIC = ROOT / "public"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC), **kwargs)

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] != "/api/archive":
            return super().do_GET()
        raw = (ROOT / "data/draws.json").read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != EXPECTED_DATA_HASH:
            self._json(500, {"error": "canonical_hash_mismatch"})
            return
        source = json.loads(raw.decode("utf-8"))
        records = source["records"]
        self._json(
            200,
            {
                "data_version": source["data_version"],
                "canonical_data_hash": digest,
                "record_count": len(records),
                "first_draw": records[0]["draw_no"],
                "last_draw": records[-1]["draw_no"],
                "verification_status": "auto_checked",
                "officially_locked": False,
                "records": records,
            },
        )

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/api/predict":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = run_dynamic_prediction(overlay=payload.get("overlay", []))
            self._json(200, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": "invalid_request", "detail": str(exc)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving full UI on http://127.0.0.1:{args.port}", flush=True)
    server.serve_forever()
