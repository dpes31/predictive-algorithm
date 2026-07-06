"""Tests for the shared Supabase-backed draw overlay store and its wiring
into /api/predict and /api/overlay.

These tests must pass both with and without SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY
set, and must never perform real network I/O: urllib.request.urlopen is
monkeypatched wherever Supabase would otherwise be contacted.
"""

from __future__ import annotations

import io
import json
import pathlib
import unittest
import urllib.error
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]

import api.overlay as overlay_api
import api.predict as predict_api
from server_store import overlay_store

GOLDEN_OVERLAY_RECORD = {
    "draw_no": 1231,
    "draw_date": "2026-07-04",
    "numbers": [4, 13, 14, 18, 31, 38],
    "bonus_number": 15,
}
GOLDEN_TARGET_DRAW_NO = 1232
GOLDEN_SEED = "9b12ba1c500af1eef6f1413ef75637fa5d6d227fdc28ae3ed1fa4ed2677c3499"
GOLDEN_PREDICTION_HASH = "a096870b0bc59da044b024b66144509ee40e30fa13909cefcc29cb95fec02d1b"


class _FakeHttpResponse:
    def __init__(self, status: int, body: bytes) -> None:
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeHttpResponse":
        return self

    def __exit__(self, *exc_info) -> None:
        return None


def _make_handler(cls, *, headers: dict, body: bytes):
    """Build a bare handler instance without touching real sockets.

    BaseHTTPRequestHandler normally requires a live socket in __init__; for
    unit testing we bypass __init__, stub out the request-body/response
    plumbing, and capture whatever handler._write_json(status, payload) is
    called with.
    """
    instance = cls.__new__(cls)
    instance.headers = headers
    instance.rfile = io.BytesIO(body)
    instance.wfile = io.BytesIO()
    captured: dict = {}

    def _write_json(status, payload):
        captured["status"] = status
        captured["payload"] = payload

    instance._write_json = _write_json  # type: ignore[attr-defined]
    return instance, captured


class OverlayStoreConfigurationTests(unittest.TestCase):
    def test_not_configured_without_env_vars(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            for key in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
                import os

                os.environ.pop(key, None)
            self.assertFalse(overlay_store.is_configured())

    def test_configured_with_both_env_vars(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "dummy-service-key"},
        ):
            self.assertTrue(overlay_store.is_configured())


class OverlayStoreUrllibTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patch = mock.patch.dict(
            "os.environ",
            {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_SERVICE_ROLE_KEY": "dummy-service-key"},
        )
        self._env_patch.start()
        self.addCleanup(self._env_patch.stop)

    def test_fetch_overlay_shapes_records_and_sends_auth_header(self) -> None:
        rows = [
            {"draw_no": 1231, "draw_date": "2026-07-04", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7},
        ]
        body = json.dumps(rows).encode("utf-8")

        captured_request = {}

        def fake_urlopen(req, timeout=None):
            captured_request["url"] = req.full_url
            captured_request["method"] = req.get_method()
            captured_request["headers"] = {k.lower(): v for k, v in req.header_items()}
            return _FakeHttpResponse(200, body)

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            records = overlay_store.fetch_overlay()

        self.assertEqual(
            records,
            [{"draw_no": 1231, "draw_date": "2026-07-04", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7}],
        )
        self.assertEqual(captured_request["method"], "GET")
        self.assertIn("draw_overlay", captured_request["url"])
        self.assertIn("order=draw_no.asc", captured_request["url"])
        self.assertEqual(captured_request["headers"]["authorization"], "Bearer dummy-service-key")
        self.assertEqual(captured_request["headers"]["apikey"], "dummy-service-key")

    def test_base_url_variants_build_single_rest_v1_path(self) -> None:
        # The Supabase dashboard shows both the project URL and the REST URL
        # (with /rest/v1); either must produce exactly one /rest/v1 segment.
        variants = [
            "https://example.supabase.co",
            "https://example.supabase.co/",
            "https://example.supabase.co/rest/v1",
            "https://example.supabase.co/rest/v1/",
        ]
        for variant in variants:
            with self.subTest(url=variant):
                captured_request = {}

                def fake_urlopen(req, timeout=None):
                    captured_request["url"] = req.full_url
                    return _FakeHttpResponse(200, b"[]")

                with mock.patch.dict("os.environ", {"SUPABASE_URL": variant}):
                    with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
                        overlay_store.fetch_overlay()

                self.assertTrue(
                    captured_request["url"].startswith("https://example.supabase.co/rest/v1/draw_overlay"),
                    captured_request["url"],
                )
                self.assertEqual(captured_request["url"].count("/rest/v1"), 1, captured_request["url"])

    def test_insert_record_sends_expected_payload_and_prefer_header(self) -> None:
        insert_seen = {}

        def fake_urlopen(req, timeout=None):
            if req.get_method() == "POST":
                insert_seen["body"] = json.loads(req.data.decode("utf-8"))
                insert_seen["prefer"] = dict(req.header_items()).get("Prefer") or dict(req.header_items()).get(
                    "prefer"
                )
                return _FakeHttpResponse(201, b"[]")
            # subsequent fetch_overlay() call after insert
            rows = [{"draw_no": 1231, "draw_date": "2026-07-04", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7}]
            return _FakeHttpResponse(200, json.dumps(rows).encode("utf-8"))

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = overlay_store.insert_record(
                {"draw_no": 1231, "draw_date": "2026-07-04", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7}
            )

        self.assertEqual(
            insert_seen["body"],
            {"draw_no": 1231, "draw_date": "2026-07-04", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7},
        )
        self.assertEqual(insert_seen["prefer"], "return=representation")
        self.assertEqual(result[0]["draw_no"], 1231)

    def test_delete_record_targets_draw_no_filter(self) -> None:
        delete_seen = {}

        def fake_urlopen(req, timeout=None):
            if req.get_method() == "DELETE":
                delete_seen["url"] = req.full_url
                return _FakeHttpResponse(200, b"[]")
            return _FakeHttpResponse(200, b"[]")

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            result = overlay_store.delete_record(1231)

        self.assertIn("draw_no=eq.1231", delete_seen["url"])
        self.assertEqual(result, [])

    def test_fetch_overlay_raises_on_http_error(self) -> None:
        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(b'{"message":"relation missing"}'))

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(overlay_store.OverlayStoreError):
                overlay_store.fetch_overlay()

    def test_fetch_overlay_raises_on_network_error(self) -> None:
        def fake_urlopen(req, timeout=None):
            raise urllib.error.URLError("connection refused")

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(overlay_store.OverlayStoreError):
                overlay_store.fetch_overlay()

    def test_fetch_overlay_raises_on_bad_json(self) -> None:
        def fake_urlopen(req, timeout=None):
            return _FakeHttpResponse(200, b"not json")

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(overlay_store.OverlayStoreError):
                overlay_store.fetch_overlay()

    def test_insert_conflict_raises_conflict_error(self) -> None:
        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(
                req.full_url, 409, "Conflict", {}, io.BytesIO(b'{"message":"duplicate key value violates unique constraint"}')
            )

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(overlay_store.OverlayStoreConflictError):
                overlay_store.insert_record(
                    {"draw_no": 1231, "draw_date": "2026-07-04", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7}
                )

    def test_fetch_without_configuration_raises_not_configured(self) -> None:
        self._env_patch.stop()
        try:
            import os

            os.environ.pop("SUPABASE_URL", None)
            os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)
            with self.assertRaises(overlay_store.OverlayStoreNotConfigured):
                overlay_store.fetch_overlay()
        finally:
            self._env_patch.start()


class PredictFallbackTests(unittest.TestCase):
    """Without Supabase env vars, /api/predict must behave exactly as before."""

    def test_predict_uses_client_overlay_when_not_configured(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("SUPABASE_URL", None)
            os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)

            body = json.dumps({"overlay": [GOLDEN_OVERLAY_RECORD]}).encode("utf-8")
            instance, captured = _make_handler(
                predict_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        self.assertEqual(captured["status"], 200)
        payload = captured["payload"]
        self.assertEqual(payload["target_draw_no"], GOLDEN_TARGET_DRAW_NO)
        self.assertEqual(payload["seed"], GOLDEN_SEED)
        self.assertEqual(payload["hashes"]["prediction_hash"], GOLDEN_PREDICTION_HASH)
        self.assertEqual(payload["data"]["overlay_source"], "client")
        self.assertNotIn("overlay_warning", payload["data"])

    def test_predict_no_overlay_matches_baseline(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("SUPABASE_URL", None)
            os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)

            body = json.dumps({"overlay": []}).encode("utf-8")
            instance, captured = _make_handler(
                predict_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        self.assertEqual(captured["status"], 200)
        self.assertEqual(captured["payload"]["target_draw_no"], 1231)
        self.assertEqual(captured["payload"]["data"]["overlay_source"], "client")


class PredictServerOverlayTests(unittest.TestCase):
    """With a configured (mocked) store, /api/predict must use server records
    and produce bit-identical golden hashes to the client-overlay path.
    """

    def test_predict_uses_server_overlay_and_matches_golden_vector(self) -> None:
        with mock.patch("api.predict.is_configured", return_value=True), mock.patch(
            "api.predict.fetch_overlay", return_value=[GOLDEN_OVERLAY_RECORD]
        ):
            # request body overlay is intentionally different/invalid to prove
            # it is ignored whenever the server overlay is active.
            body = json.dumps({"overlay": [{"draw_no": 9999}]}).encode("utf-8")
            instance, captured = _make_handler(
                predict_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        self.assertEqual(captured["status"], 200)
        payload = captured["payload"]
        self.assertEqual(payload["target_draw_no"], GOLDEN_TARGET_DRAW_NO)
        self.assertEqual(payload["seed"], GOLDEN_SEED)
        self.assertEqual(payload["hashes"]["prediction_hash"], GOLDEN_PREDICTION_HASH)
        self.assertEqual(payload["data"]["overlay_source"], "server")

    def test_predict_falls_back_to_client_overlay_when_fetch_fails(self) -> None:
        with mock.patch("api.predict.is_configured", return_value=True), mock.patch(
            "api.predict.fetch_overlay", side_effect=overlay_store.OverlayStoreRequestError("boom")
        ):
            body = json.dumps({"overlay": [GOLDEN_OVERLAY_RECORD]}).encode("utf-8")
            instance, captured = _make_handler(
                predict_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        self.assertEqual(captured["status"], 200)
        payload = captured["payload"]
        self.assertEqual(payload["target_draw_no"], GOLDEN_TARGET_DRAW_NO)
        self.assertEqual(payload["seed"], GOLDEN_SEED)
        self.assertEqual(payload["hashes"]["prediction_hash"], GOLDEN_PREDICTION_HASH)
        self.assertEqual(payload["data"]["overlay_source"], "client")
        self.assertIn("overlay_warning", payload["data"])


class OverlayEndpointTests(unittest.TestCase):
    def test_get_returns_not_configured_when_env_missing(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("SUPABASE_URL", None)
            os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)

            instance, captured = _make_handler(overlay_api.handler, headers={}, body=b"")
            instance.do_GET()

        self.assertEqual(captured["status"], 200)
        self.assertEqual(captured["payload"], {"configured": False, "records": []})

    def test_get_returns_validated_server_records_when_configured(self) -> None:
        with mock.patch("api.overlay.is_configured", return_value=True), mock.patch(
            "api.overlay.fetch_overlay", return_value=[GOLDEN_OVERLAY_RECORD]
        ):
            instance, captured = _make_handler(overlay_api.handler, headers={}, body=b"")
            instance.do_GET()

        self.assertEqual(captured["status"], 200)
        payload = captured["payload"]
        self.assertTrue(payload["configured"])
        self.assertEqual(len(payload["records"]), 1)
        self.assertEqual(payload["records"][0]["draw_no"], 1231)
        self.assertEqual(payload["records"][0]["source"], "user_overlay")

    def test_get_returns_warning_when_store_errors(self) -> None:
        with mock.patch("api.overlay.is_configured", return_value=True), mock.patch(
            "api.overlay.fetch_overlay", side_effect=overlay_store.OverlayStoreRequestError("relation missing")
        ):
            instance, captured = _make_handler(overlay_api.handler, headers={}, body=b"")
            instance.do_GET()

        self.assertEqual(captured["status"], 200)
        payload = captured["payload"]
        self.assertTrue(payload["configured"])
        self.assertEqual(payload["records"], [])
        self.assertIn("warning", payload)

    def test_post_returns_503_when_not_configured(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("SUPABASE_URL", None)
            os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)

            body = json.dumps({"record": GOLDEN_OVERLAY_RECORD}).encode("utf-8")
            instance, captured = _make_handler(
                overlay_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        self.assertEqual(captured["status"], 503)

    def test_post_inserts_validated_record_and_returns_updated_overlay(self) -> None:
        with mock.patch("api.overlay.is_configured", return_value=True), mock.patch(
            "api.overlay.fetch_overlay", return_value=[]
        ), mock.patch(
            "api.overlay.insert_record", return_value=[GOLDEN_OVERLAY_RECORD]
        ) as mock_insert:
            body = json.dumps({"record": GOLDEN_OVERLAY_RECORD}).encode("utf-8")
            instance, captured = _make_handler(
                overlay_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        mock_insert.assert_called_once()
        self.assertEqual(captured["status"], 200)
        self.assertEqual(captured["payload"]["records"][0]["draw_no"], 1231)

    def test_post_rejects_non_consecutive_record(self) -> None:
        bad_record = {**GOLDEN_OVERLAY_RECORD, "draw_no": 1240}
        with mock.patch("api.overlay.is_configured", return_value=True), mock.patch(
            "api.overlay.fetch_overlay", return_value=[]
        ):
            body = json.dumps({"record": bad_record}).encode("utf-8")
            instance, captured = _make_handler(
                overlay_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_POST()

        self.assertEqual(captured["status"], 400)
        self.assertEqual(captured["payload"]["error"], "invalid_overlay")

    def test_delete_only_allows_highest_draw_no(self) -> None:
        overlay_records = [
            GOLDEN_OVERLAY_RECORD,
            {"draw_no": 1232, "draw_date": "2026-07-11", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7},
        ]
        with mock.patch("api.overlay.is_configured", return_value=True), mock.patch(
            "api.overlay.fetch_overlay", return_value=overlay_records
        ):
            body = json.dumps({"draw_no": 1231}).encode("utf-8")
            instance, captured = _make_handler(
                overlay_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_DELETE()

        self.assertEqual(captured["status"], 400)

    def test_delete_removes_highest_draw_no(self) -> None:
        overlay_records = [
            GOLDEN_OVERLAY_RECORD,
            {"draw_no": 1232, "draw_date": "2026-07-11", "numbers": [1, 2, 3, 4, 5, 6], "bonus_number": 7},
        ]
        with mock.patch("api.overlay.is_configured", return_value=True), mock.patch(
            "api.overlay.fetch_overlay", return_value=overlay_records
        ), mock.patch(
            "api.overlay.delete_record", return_value=[GOLDEN_OVERLAY_RECORD]
        ) as mock_delete:
            body = json.dumps({"draw_no": 1232}).encode("utf-8")
            instance, captured = _make_handler(
                overlay_api.handler, headers={"Content-Length": str(len(body))}, body=body
            )
            instance.do_DELETE()

        mock_delete.assert_called_once_with(1232)
        self.assertEqual(captured["status"], 200)
        self.assertEqual(len(captured["payload"]["records"]), 1)


if __name__ == "__main__":
    unittest.main()
