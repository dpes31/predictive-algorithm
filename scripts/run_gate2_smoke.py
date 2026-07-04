#!/usr/bin/env python3
"""Run a deterministic Gate 2-2 research smoke prediction on synthetic data."""

from __future__ import annotations

import argparse
import json
import pathlib

from engine.prediction_run import run_research_prediction
from simulation.uniform_lottery import generate_uniform_draws


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draw-count", type=int, default=320)
    parser.add_argument("--seed", type=int, default=20260630)
    parser.add_argument("--output", default="reports/gate2_engine_smoke.json")
    args = parser.parse_args()

    records = generate_uniform_draws(args.draw_count, seed=args.seed)
    result = run_research_prediction(
        records,
        target_draw_no=args.draw_count + 1,
        data_version=f"synthetic-uniform-{args.seed}-{args.draw_count}",
        generated_at="2026-06-30T00:00:00Z",
    )
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
