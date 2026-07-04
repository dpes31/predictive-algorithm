"""Product Gate P1 M0-only deterministic five-set runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from engine.candidate_optimizer import optimize_candidates
from engine.config import EngineConfig
from engine.data_loader import load_dataset, records_for_target
from engine.distributions import FixedSizeDistribution
from engine.hashing import canonical_json, deterministic_seed, sha256_value

from .config import (
    CANDIDATE_CONTRACT_VERSION,
    DATASET_VERSION,
    DEFAULT_PRODUCT_CONFIG,
    ENGINE_CORE_VERSION,
    EXPECTED_DATA_HASH,
    FEATURE_CONTRACT_VERSION,
    MODEL_VERSION,
    PRODUCT_CONTRACT_VERSION,
    PRODUCT_WEIGHTS,
    SCHEMA_VERSION,
)
from .contracts import ProductCandidate, ProductPrediction


_MODEL_SOURCE_PATHS = (
    "engine/distributions.py",
    "engine/elementary_symmetric.py",
    "engine/candidate_optimizer.py",
    "engine/hashing.py",
    "product/config.py",
    "product/contracts.py",
    "product/run_prediction.py",
)


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_generated_at(value: str) -> str:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("generated_at must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("generated_at must include a timezone")
    return value


def _model_hash(root: pathlib.Path) -> str:
    sources: dict[str, str] = {}
    for relative_path in _MODEL_SOURCE_PATHS:
        path = root / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"model source missing: {relative_path}")
        sources[relative_path] = _sha256_bytes(path.read_bytes())
    return sha256_value(
        {
            "contract_version": PRODUCT_CONTRACT_VERSION,
            "engine_core_version": ENGINE_CORE_VERSION,
            "product_weights": PRODUCT_WEIGHTS,
            "source_hashes": sources,
        }
    )


def run_product_prediction(
    *,
    target_draw_no: int,
    dataset_path: str | pathlib.Path,
    generated_at: str,
    shadow_diagnostics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a deterministic M0-only product prediction payload.

    ``shadow_diagnostics`` is an internal diagnostics input. It is deliberately
    excluded from the seed, candidate selection, and prediction hash.
    """

    generated_at = _validate_generated_at(generated_at)
    path = pathlib.Path(dataset_path)
    raw_data = path.read_bytes()
    data_hash = _sha256_bytes(raw_data)
    if data_hash != EXPECTED_DATA_HASH:
        raise ValueError(f"dataset hash mismatch: expected {EXPECTED_DATA_HASH}, got {data_hash}")

    data_version, records = load_dataset(path)
    if data_version != DATASET_VERSION:
        raise ValueError(f"dataset version mismatch: expected {DATASET_VERSION}, got {data_version}")

    engine_config = EngineConfig(
        model_version=ENGINE_CORE_VERSION,
        feature_contract_version=FEATURE_CONTRACT_VERSION,
        number_count=DEFAULT_PRODUCT_CONFIG.number_count,
        pick_count=DEFAULT_PRODUCT_CONFIG.pick_count,
        candidate_count=DEFAULT_PRODUCT_CONFIG.candidate_count,
        uniform_candidate_pool=DEFAULT_PRODUCT_CONFIG.uniform_candidate_pool,
    )
    usable = records_for_target(
        records,
        target_draw_no=target_draw_no,
        research_only=True,
        minimum_history=engine_config.min_history,
    )

    cutoff_payload = {
        "target_draw_no": target_draw_no,
        "input_first_draw": usable[0].draw_no,
        "input_last_draw": usable[-1].draw_no,
        "input_record_count": len(usable),
        "excluded_draws_at_or_after_target": 0,
    }
    cutoff = {**cutoff_payload, "cutoff_hash": sha256_value(cutoff_payload)}

    root = _repo_root()
    model_hash = _model_hash(root)
    config_hash = DEFAULT_PRODUCT_CONFIG.config_hash
    seed = deterministic_seed(
        PRODUCT_CONTRACT_VERSION,
        data_hash,
        MODEL_VERSION,
        config_hash,
        target_draw_no,
    )

    distribution = FixedSizeDistribution(
        logits=(0.0,) * DEFAULT_PRODUCT_CONFIG.number_count,
        pick_count=DEFAULT_PRODUCT_CONFIG.pick_count,
    )
    uniform_probability = 1.0 / math.comb(
        DEFAULT_PRODUCT_CONFIG.number_count,
        DEFAULT_PRODUCT_CONFIG.pick_count,
    )
    engine_candidates = optimize_candidates(
        distribution,
        seed=seed,
        uniform_probability=uniform_probability,
        config=engine_config,
    )
    candidates = tuple(
        ProductCandidate(
            rank=candidate.rank,
            numbers=tuple(candidate.numbers),
            joint_probability=uniform_probability,
            lift_vs_uniform=1.0,
        )
        for candidate in engine_candidates
    )

    versions = {
        "data_version": data_version,
        "model_version": MODEL_VERSION,
        "engine_core_version": ENGINE_CORE_VERSION,
        "feature_contract_version": FEATURE_CONTRACT_VERSION,
        "candidate_contract_version": CANDIDATE_CONTRACT_VERSION,
    }
    candidate_payload = [candidate.to_dict() for candidate in candidates]
    prediction_hash_payload = {
        "contract_version": PRODUCT_CONTRACT_VERSION,
        "target_draw_no": target_draw_no,
        "input_last_draw": usable[-1].draw_no,
        "data_version": data_version,
        "data_hash": data_hash,
        "model_version": MODEL_VERSION,
        "model_hash": model_hash,
        "config_hash": config_hash,
        "seed": seed,
        "product_weights": PRODUCT_WEIGHTS,
        "candidate_sets": candidate_payload,
        "statistical_edge": False,
        "reason": "no_validated_nonuniform_signal",
    }
    prediction_hash = sha256_value(prediction_hash_payload)

    shadow = None if shadow_diagnostics is None else dict(shadow_diagnostics)
    result = ProductPrediction(
        schema_version=SCHEMA_VERSION,
        contract_version=PRODUCT_CONTRACT_VERSION,
        target_draw_no=target_draw_no,
        input_last_draw=usable[-1].draw_no,
        generated_at=generated_at,
        research_only=True,
        public_release_allowed=False,
        statistical_edge=False,
        reason="no_validated_nonuniform_signal",
        advantage_status="통계적 우위 없음",
        final_distribution="M0_ONLY",
        product_weights=PRODUCT_WEIGHTS,
        candidate_sets=candidates,
        versions=versions,
        hashes={
            "data_hash": data_hash,
            "model_hash": model_hash,
            "config_hash": config_hash,
            "prediction_hash": prediction_hash,
        },
        seed=seed,
        diagnostics={
            "shadow_enabled": shadow is not None,
            "shadow": shadow,
            "cutoff": cutoff,
        },
        limitations=(
            "canonical_data_auto_checked_not_officially_locked",
            "no_validated_nonuniform_signal",
            "not_a_claim_of_improved_lottery_odds",
        ),
    )
    return result.to_dict()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate five deterministic M0-only Lotto 6/45 research sets.")
    parser.add_argument("--target-draw-no", required=True, type=int)
    parser.add_argument("--dataset", default="data/draws.json")
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    result = run_product_prediction(
        target_draw_no=args.target_draw_no,
        dataset_path=args.dataset,
        generated_at=args.generated_at,
    )
    serialized = canonical_json(result)
    if args.output:
        pathlib.Path(args.output).write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
