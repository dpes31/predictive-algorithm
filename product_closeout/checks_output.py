"""Product output checks for Closeout C2."""

from __future__ import annotations

import math
import pathlib
from typing import Any

from engine.hashing import canonical_json, deterministic_seed, sha256_value
from product.config import DEFAULT_PRODUCT_CONFIG, EXPECTED_DATA_HASH, MODEL_VERSION, PRODUCT_CONTRACT_VERSION
from product.run_prediction import run_product_prediction

from .constants import EXPECTED_WEIGHTS, FIXED_GENERATED_AT, FIXED_TARGET


def verify_prediction(root: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    dataset = root / "data/draws.json"
    first = run_product_prediction(
        target_draw_no=FIXED_TARGET, dataset_path=dataset, generated_at=FIXED_GENERATED_AT
    )
    second = run_product_prediction(
        target_draw_no=FIXED_TARGET, dataset_path=dataset, generated_at=FIXED_GENERATED_AT
    )
    shadow = run_product_prediction(
        target_draw_no=FIXED_TARGET,
        dataset_path=dataset,
        generated_at=FIXED_GENERATED_AT,
        shadow_diagnostics={
            "source": "C2_SYNTHETIC_SHADOW_FIXTURE",
            "research_ensemble_score": [0.1, -0.1],
        },
    )
    candidates = first["candidate_sets"]
    combinations = [tuple(item["numbers"]) for item in candidates]
    uniform_probability = 1.0 / math.comb(45, 6)
    expected_seed = deterministic_seed(
        PRODUCT_CONTRACT_VERSION,
        EXPECTED_DATA_HASH,
        MODEL_VERSION,
        DEFAULT_PRODUCT_CONFIG.config_hash,
        FIXED_TARGET,
    )
    conditions = {
        "two_repeats_identical": canonical_json(first) == canonical_json(second),
        "target_minus_one": first["input_last_draw"] == FIXED_TARGET - 1,
        "candidate_count": len(candidates) == 5,
        "candidate_size": all(len(item["numbers"]) == 6 for item in candidates),
        "number_range": all(all(1 <= number <= 45 for number in item["numbers"]) for item in candidates),
        "numbers_sorted": all(item["numbers"] == sorted(item["numbers"]) for item in candidates),
        "within_set_unique": all(len(set(item["numbers"])) == 6 for item in candidates),
        "between_set_unique": len(set(combinations)) == 5,
        "ranks": sorted(item["rank"] for item in candidates) == [1, 2, 3, 4, 5],
        "uniform_probability": all(
            abs(float(item["joint_probability"]) - uniform_probability) <= 1e-18
            for item in candidates
        ),
        "uniform_lift": all(item["lift_vs_uniform"] == 1.0 for item in candidates),
        "weights": first["product_weights"] == EXPECTED_WEIGHTS,
        "distribution": first["final_distribution"] == "M0_ONLY",
        "statistical_edge": first["statistical_edge"] is False,
        "reason": first["reason"] == "no_validated_nonuniform_signal",
        "research_only": first["research_only"] is True,
        "public_release_allowed": first["public_release_allowed"] is False,
        "advantage_status": first["advantage_status"] == "통계적 우위 없음",
        "seed": first["seed"] == expected_seed,
        "shadow_candidates_isolated": shadow["candidate_sets"] == first["candidate_sets"],
        "shadow_seed_isolated": shadow["seed"] == first["seed"],
        "shadow_prediction_hash_isolated": (
            shadow["hashes"]["prediction_hash"] == first["hashes"]["prediction_hash"]
        ),
        "shadow_weights_isolated": shadow["product_weights"] == first["product_weights"],
        "shadow_enabled_only_diagnostic": (
            shadow["diagnostics"]["shadow_enabled"] is True
            and first["diagnostics"]["shadow_enabled"] is False
        ),
    }
    return (
        {
            "pass": all(conditions.values()),
            "conditions": conditions,
            "canonical_prediction_hash": sha256_value(first),
            "prediction_hash": first["hashes"]["prediction_hash"],
            "candidate_sets_hash": sha256_value(candidates),
            "seed": first["seed"],
        },
        first,
    )
