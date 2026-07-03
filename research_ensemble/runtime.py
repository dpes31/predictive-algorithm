"""A2 runtime support."""

from __future__ import annotations

from datetime import datetime


def validate_generated_at(value: str) -> str:
    parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    if parsed.tzinfo is None:
        raise ValueError("generated_at must include a timezone")
    return value
