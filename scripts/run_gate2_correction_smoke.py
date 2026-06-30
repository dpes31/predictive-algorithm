#!/usr/bin/env python3
"""Deterministic implementation smoke for Gate 2-3P-R2."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from engine.config import DEFAULT_CONFIG
from engine.experts.change_eprocess import ChangeEProcessDetector
from engine.prediction_run import run_research_prediction
from simulation.physical_scenarios import BALL_SET_LIFT_125, generate_physical_series, holdout_target


def build_report(seed: int = 20260701, draw_count: int = 321) -> dict[str, object]:
    records, metadata = generate_physical_series(BALL_SET_LIFT_125, draw_count=draw_count, seed=seed)
    history, metadata_history, target_result, target_metadata = holdout_target(records, metadata)
    research_history = tuple(replace(record, verification_status="auto_checked") for record in history)
    change_result = ChangeEProcessDetector().replay(research_history)
    prediction = run_research_prediction(
        research_history,
        target_draw_no=target_result.draw_no,
        data_version=f"gate2-correction-smoke-{seed}",
        generated_at="2026-07-01T00:00:00Z",
        physical_metadata_records=metadata_history,
        target_physical_metadata=target_metadata,
        change_eprocess_result=change_result,
    )
    return {
        "gate": "Gate 2-3P-R2",
        "model_version": DEFAULT_CONFIG.model_version,
        "feature_contract_version": DEFAULT_CONFIG.feature_contract_version,
        "physical_data_schema_version": DEFAULT_CONFIG.physical_data_schema_version,
        "target_draw_no": target_result.draw_no,
        "prediction_hash": prediction.prediction_hash,
        "candidate_sets": [list(candidate.numbers) for candidate in prediction.candidate_sets],
        "candidate_count": len(prediction.candidate_sets),
        "pick_count": DEFAULT_CONFIG.pick_count,
        "gate_state": prediction.gate_state,
        "model_weights": dict(prediction.model_weights),
        "physical_status": prediction.metadata["physical_evidence"]["status"],
        "physical_active": prediction.metadata["physical_evidence"]["active"],
        "change_status": change_result.status,
        "research_only": prediction.research_only,
        "public_release_allowed": prediction.public_release_allowed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=20260701)
    parser.add_argument("--draw-count", type=int, default=321)
    args = parser.parse_args()
    report = build_report(seed=args.seed, draw_count=args.draw_count)
    if report["candidate_count"] != 5:
        raise SystemExit("candidate count contract failed")
    if any(len(numbers) != 6 for numbers in report["candidate_sets"]):
        raise SystemExit("pick count contract failed")
    if report["model_weights"]["M0"] != 1.0:
        raise SystemExit("RESEARCH final distribution must remain M0 only")
    if report["public_release_allowed"] is not False:
        raise SystemExit("public release must remain blocked")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
