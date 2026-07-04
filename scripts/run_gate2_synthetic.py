#!/usr/bin/env python3
"""Run Gate 2-3 synthetic null and positive-control experiments."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from simulation.experiment_config import ExperimentConfig
from simulation.experiment_runner import run_gate2_3_experiment
from simulation.report_builder import build_markdown_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draw-count", type=int, default=1230)
    parser.add_argument("--null-calibration", type=int, default=1000)
    parser.add_argument("--null-validation", type=int, default=1000)
    parser.add_argument("--positive", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260630)
    parser.add_argument("--alpha", type=float, default=0.001)
    parser.add_argument("--json-output", default="reports/gate2_3_synthetic_summary.json")
    parser.add_argument("--markdown-output", default="reports/gate2_3_synthetic_summary.md")
    args = parser.parse_args()

    experiment = ExperimentConfig(
        draw_count=args.draw_count,
        null_calibration_series=args.null_calibration,
        null_validation_series=args.null_validation,
        positive_series_per_scenario=args.positive,
        seed_base=args.seed,
        alpha=args.alpha,
    )

    def progress(message: str) -> None:
        print(f"[gate2-3] {message}", file=sys.stderr, flush=True)

    report = run_gate2_3_experiment(experiment, progress=progress)
    json_path = pathlib.Path(args.json_output)
    markdown_path = pathlib.Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown_report(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
