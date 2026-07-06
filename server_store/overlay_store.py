"""Supabase (PostgREST) backed shared draw overlay store.

Uses only the Python standard library (urllib) so no new pip dependency is
introduced. The service-role key is read from the environment on every call
and is never logged or echoed back to a client.

The table is expected to be:

    create table public.draw_overlay (
      draw_no integer primary key,
      draw_date date not null,
      numbers integer[] not null,
      bonus_number integer not null,
      created_at timestamptz not null default now()
    );

Row Level Security is enabled with no policies, so only requests carrying the
service_role key (server-side only) can read/write.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

TABLE = "draw_overlay"
TIMEOUT_SECONDS = 5
SELECT_COLUMNS = "draw_no,draw_date,numbers,bonus_number"


class OverlayStoreError(Exception):
    """Base error for any Supabase overlay store failure."""


class OverlayStoreNotConfigured(OverlayStoreError):
    """Raised when SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are missing."""


class OverlayStoreRequestError(OverlayStoreError):
    """Raised for network failures, non-2xx responses, or bad JSON bodies."""


class OverlayStoreConflictError(OverlayStoreError):
    """Raised when an insert violates the draw_no primary key uniqueness."""


def _env() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    return url, key


def is_configured() -> bool:
    url, key = _env()
    return bool(url) and bool(key)


def _base_headers(key: str) -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _request(method: str, path_and_query: str, *, body: bytes | None = None, extra_headers: dict[str, str] | None = None) -> tuple[int, bytes]:
    url, key = _env()
    if not url or not key:
        raise OverlayStoreNotConfigured("Supabase is not configured (missing SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY)")

    endpoint = f"{url.rstrip('/')}/rest/v1/{path_and_query}"
    headers = _base_headers(key)
    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(endpoint, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed https host
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        payload = exc.read()
        detail = payload.decode("utf-8", errors="replace")
        if exc.code == 409 or "duplicate key value" in detail.lower() or "already exists" in detail.lower():
            raise OverlayStoreConflictError("draw_overlay record already exists for this draw_no") from exc
        raise OverlayStoreRequestError(f"Supabase request failed (HTTP {exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise OverlayStoreRequestError(f"Supabase request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise OverlayStoreRequestError("Supabase request timed out") from exc


def _record_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "draw_no": int(row["draw_no"]),
        "draw_date": str(row["draw_date"]),
        "numbers": [int(n) for n in row["numbers"]],
        "bonus_number": int(row["bonus_number"]),
    }


def fetch_overlay() -> list[dict[str, Any]]:
    """Return all overlay records ordered by draw_no ascending.

    Raises OverlayStoreError (or a subclass) on any failure, including a
    missing table, network errors, or malformed JSON.
    """
    status, body = _request(
        "GET",
        f"{TABLE}?select={SELECT_COLUMNS}&order=draw_no.asc",
    )
    try:
        rows = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise OverlayStoreRequestError("Supabase returned an invalid response body") from exc
    if not isinstance(rows, list):
        raise OverlayStoreRequestError("Supabase returned an unexpected response shape")
    try:
        return [_record_from_row(row) for row in rows]
    except (KeyError, TypeError, ValueError) as exc:
        raise OverlayStoreRequestError("Supabase returned malformed draw_overlay rows") from exc


def insert_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Insert a single normalized overlay record and return the full overlay."""
    payload = {
        "draw_no": int(record["draw_no"]),
        "draw_date": str(record["draw_date"]),
        "numbers": [int(n) for n in record["numbers"]],
        "bonus_number": int(record["bonus_number"]),
    }
    body = json.dumps(payload).encode("utf-8")
    _request(
        "POST",
        TABLE,
        body=body,
        extra_headers={"Prefer": "return=representation"},
    )
    return fetch_overlay()


def delete_record(draw_no: int) -> list[dict[str, Any]]:
    """Delete a single overlay record by draw_no and return the remaining overlay."""
    _request("DELETE", f"{TABLE}?draw_no=eq.{int(draw_no)}")
    return fetch_overlay()
