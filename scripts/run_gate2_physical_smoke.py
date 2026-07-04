#!/usr/bin/env python3
"""Run deterministic Gate 2-3P-2 M4 smoke scenarios.

This is an implementation smoke test, not the Gate 2-3P-3 statistical
validation. It checks contracts, determinism, leakage barriers and executable
M4 distributions before the full null/positive experiment is authorized.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from engine.config import DEFAULT_CONFIG
from engine.experts.physical_evidence import build_physical_evidence_model
from engine.hashing import sha256_value
from simulation.physical_scenarios import PHYSICAL_SMOKE_SCENARIOS, generate_physical_series


def run_smoke(*, draw_count: int, seed: int) -> dict[str, object]:
    if draw_count <= DEFAULT_CONFIG.min_history:
        raise ValueError(f"draw_count must exceed {DEFAULT_CONFIG.min_history}")
    uniform_joint = 1.0 / math.comb(DEFAULT_CONFIG.number_count, DEFAULT_CONFIG.pick_count)
    scenarios: dict[str, object] = {}

    for scenario_index, spec in enumerate(PHYSICAL_SMOKE_SCENARIOS):
        records, metadata = generate_physical_series(
            spec,
            draw_count=draw_count,
            seed=seed + scenario_index * 10_000,
        )
        history = records[:-1]
        metadata_history = metadata[:-1]
        target_result = records[-1]
        target_metadata = metadata[-1]
        model = build_physical_evidence_model(
            history,
            metadata_history,
            target_metadata,
        )
        probability = model.distribution.joint_probability(target_result.numbers)
        scenarios[spec.name] = {
            "family": spec.family,
            "lift": spec.lift,
            "active": model.diagnostics.active,
            "matched_contexts": model.diagnostics.matched_contexts,
            "weighted_context_support": model.diagnostics.weighted_context_support,
            "quality": model.diagnostics.quality.to_dict(),
            "reasons": list(model.diagnostics.reasons),
            "joint_probability": probability,
            "delta_log_loss_vs_uniform": math.log(probability / uniform_joint),
        }

    payload: dict[str, object] = {
        "gate": "2-3P-2",
        "model_version": DEFAULT_CONFIG.model_version,
        "feature_contract_version": DEFAULT_CONFIG.feature_contract_version,
        "physical_data_schema_version": DEFAULT_CONFIG.physical_data_schema_version,
        "draw_count": draw_count,
        "seed": seed,
        "research_only": True,
        "public_release_allowed": False,
        "statistical_validation_complete": False,
        "scenarios": scenarios,
    }
    payload["report_hash"] = sha256_value(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draw-count", type=int, default=360)
    parser.add_argument("--seed", type=int, default=20260630)
    parser.add_argument("--output", default="reports/gate2_3p2_smoke.json")
    args = parser.parse_args()

    report = run_smoke(draw_count=args.draw_count, seed=args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
