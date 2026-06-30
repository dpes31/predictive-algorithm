#!/usr/bin/env python3
"""Run one deterministic shard of the Gate 2-3P-3 validation."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from engine.config import DEFAULT_CONFIG
from engine.hashing import sha256_value
from simulation.physical_validation import (
    EFFECT_SIZES,
    ScenarioSpec,
    _m3_diagnostic_maxima,
    assigned_null_scenario,
    evaluate_series,
    generate_fast_series,
    null_scenarios,
    positive_scenarios,
    robustness_scenarios,
)


def _assigned(index: int, shard_index: int, shard_count: int) -> bool:
    return index % shard_count == shard_index


def run_shard(
    *,
    shard_index: int,
    shard_count: int,
    draw_count: int,
    maxt_total: int,
    model_null_total: int,
    null_validation_total: int,
    positive_per_cell: int,
    robustness_per_scenario: int,
) -> dict[str, object]:
    if not 0 <= shard_index < shard_count:
        raise ValueError("invalid shard index")
    started = time.time()
    rows: list[dict[str, object]] = []

    # M3 maxT calibration uses pure uniform results. Metadata is irrelevant.
    uniform_spec = ScenarioSpec("maxt_uniform", "null_no_metadata")
    for global_index in range(maxt_total):
        if not _assigned(global_index, shard_index, shard_count):
            continue
        seed = 10_000_000 + global_index
        series = generate_fast_series(uniform_spec, draw_count=draw_count, seed=seed)
        rows.append(
            {
                "category": "maxt_calibration",
                "scenario": uniform_spec.name,
                "effect_size": 1.0,
                "seed": seed,
                "m3_diagnostic_maxima": list(_m3_diagnostic_maxima(series, DEFAULT_CONFIG)),
            }
        )

    for global_index in range(model_null_total):
        if not _assigned(global_index, shard_index, shard_count):
            continue
        spec = assigned_null_scenario(global_index, model_null_total)
        seed = 20_000_000 + global_index
        rows.append(
            evaluate_series(
                spec,
                category="model_null_calibration",
                draw_count=draw_count,
                seed=seed,
                include_m3_diagnostics=False,
            ).to_dict()
        )

    for global_index in range(null_validation_total):
        if not _assigned(global_index, shard_index, shard_count):
            continue
        spec = assigned_null_scenario(global_index, null_validation_total)
        seed = 30_000_000 + global_index
        rows.append(
            evaluate_series(
                spec,
                category="independent_null_validation",
                draw_count=draw_count,
                seed=seed,
                include_m3_diagnostics=True,
            ).to_dict()
        )

    positive_cells = [
        (effect_index, scenario_index, spec)
        for effect_index, effect in enumerate(EFFECT_SIZES)
        for scenario_index, spec in enumerate(positive_scenarios(effect))
    ]
    for effect_index, scenario_index, spec in positive_cells:
        for replicate in range(positive_per_cell):
            global_index = (
                effect_index * len(positive_scenarios(spec.lift)) * positive_per_cell
                + scenario_index * positive_per_cell
                + replicate
            )
            if not _assigned(global_index, shard_index, shard_count):
                continue
            seed = 40_000_000 + global_index
            rows.append(
                evaluate_series(
                    spec,
                    category="positive_control",
                    draw_count=draw_count,
                    seed=seed,
                    include_m3_diagnostics=spec.family == "regime_reversal",
                ).to_dict()
            )

    robustness = robustness_scenarios()
    for scenario_index, spec in enumerate(robustness):
        for replicate in range(robustness_per_scenario):
            global_index = scenario_index * robustness_per_scenario + replicate
            if not _assigned(global_index, shard_index, shard_count):
                continue
            seed = 60_000_000 + global_index
            rows.append(
                evaluate_series(
                    spec,
                    category="robustness",
                    draw_count=draw_count,
                    seed=seed,
                    include_m3_diagnostics=spec.family in {"regime_reversal", "late_regime"},
                ).to_dict()
            )

    payload: dict[str, object] = {
        "gate": "2-3P-3",
        "model_version": DEFAULT_CONFIG.model_version,
        "feature_contract_version": DEFAULT_CONFIG.feature_contract_version,
        "physical_data_schema_version": DEFAULT_CONFIG.physical_data_schema_version,
        "shard_index": shard_index,
        "shard_count": shard_count,
        "draw_count": draw_count,
        "requested": {
            "maxt_total": maxt_total,
            "model_null_total": model_null_total,
            "null_validation_total": null_validation_total,
            "positive_per_cell": positive_per_cell,
            "robustness_per_scenario": robustness_per_scenario,
        },
        "row_count": len(rows),
        "elapsed_seconds": time.time() - started,
        "research_only": True,
        "public_release_allowed": False,
        "rows": rows,
    }
    payload["shard_hash"] = sha256_value(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, default=20)
    parser.add_argument("--draw-count", type=int, default=1230)
    parser.add_argument("--maxt-total", type=int, default=10_000)
    parser.add_argument("--model-null-total", type=int, default=4_000)
    parser.add_argument("--null-validation-total", type=int, default=5_000)
    parser.add_argument("--positive-per-cell", type=int, default=500)
    parser.add_argument("--robustness-per-scenario", type=int, default=500)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = run_shard(
        shard_index=args.shard_index,
        shard_count=args.shard_count,
        draw_count=args.draw_count,
        maxt_total=args.maxt_total,
        model_null_total=args.model_null_total,
        null_validation_total=args.null_validation_total,
        positive_per_cell=args.positive_per_cell,
        robustness_per_scenario=args.robustness_per_scenario,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "shard_index": payload["shard_index"],
                "row_count": payload["row_count"],
                "elapsed_seconds": payload["elapsed_seconds"],
                "shard_hash": payload["shard_hash"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
