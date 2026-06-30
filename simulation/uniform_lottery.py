"""Deterministic uniform 6/45 synthetic draw generator."""

from __future__ import annotations

import datetime as dt
import random

from engine.contracts import DrawRecord


def generate_uniform_draws(draw_count: int, *, seed: int = 0) -> list[DrawRecord]:
    if draw_count < 1:
        raise ValueError("draw_count must be positive")
    rng = random.Random(seed)
    start = dt.date(2002, 12, 7)
    records: list[DrawRecord] = []
    for index in range(draw_count):
        main = tuple(sorted(rng.sample(range(1, 46), 6)))
        remaining = [number for number in range(1, 46) if number not in main]
        bonus = rng.choice(remaining)
        records.append(
            DrawRecord(
                draw_no=index + 1,
                draw_date=(start + dt.timedelta(days=7 * index)).isoformat(),
                numbers=main,
                bonus_number=bonus,
                verification_status="auto_checked",
                locked=False,
                source="synthetic_uniform",
            )
        )
    return records
