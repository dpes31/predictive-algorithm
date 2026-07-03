"""Frozen retrospective evaluator for research-ensemble-evaluation-implementation-1.0.0."""

from __future__ import annotations

import ast
import hashlib
import math
import pathlib
import platform
import subprocess
from collections.abc import Mapping, Sequence
from typing import Any

from engine.data_loader import load_dataset
from engine.distributions import FixedSizeDistribution
from engine.feature_engineering import build_feature_snapshot
from engine.hashing import canonical_json, sha256_value
from engine.weights import uniform_weights, update_weights
from product.run_prediction import run_product_prediction

from .components import hypothesis_component, physical_component
from .config import ABLATION_IDS, DEFAULT_INTEGRATION_CONFIG, ResearchEnsembleConfig
from .historical import family_raw_vectors
from .registry import empty_hypothesis_registry, empty_physical_adapter, empty_user_registry
from .scoring import assemble_ablation
from .vector import normalize_vector, stable_float

EVALUATION_CONTRACT_VERSION = "research-ensemble-evaluation-implementation-1.0.0"
SPEC_CONTRACT_VERSION = "research-ensemble-evaluation-spec-1.0.0"
BASE_COMMIT = "09e6b19f0e351e59982e6167335cbe23fada83b0"
EXPECTED_DATA_VERSION = "draws-2026.06.27-r1"
EXPECTED_DATA_HASH = "57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1"
MINIMUM_HISTORY = 299
WARMUP_START = 300
WARMUP_END = 351
TARGET_START = 352
TARGET_END = 1230
TARGET_COUNT = 879
BOOTSTRAP_BLOCK_LENGTH = 52
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_ALPHA = 0.05
PROFILE_ID = "A3-EMPTY-REGISTRY-HISTORICAL-V1"
PRIMARY_LANE = "ENSEMBLE_FULL"
CONTROL_LANE = "CONTROL_M0"

EQUIVALENCE_PAIRS = (
    ("ENSEMBLE_FULL", "HISTORICAL_ONLY"),
    ("ENSEMBLE_FULL", "ENSEMBLE_MINUS_M3"),
    ("ENSEMBLE_FULL", "ENSEMBLE_MINUS_HYPOTHESES"),
    ("ENSEMBLE_FULL", "ENSEMBLE_MINUS_PHYSICAL"),
    ("HYPOTHESIS_ONLY", "CONTROL_M0"),
    ("PHYSICAL_ONLY", "CONTROL_M0"),
)

FROZEN_PATHS = (
    "engine/candidate_optimizer.py",
    "engine/config.py",
    "engine/data_loader.py",
    "engine/distributions.py",
    "engine/elementary_symmetric.py",
    "engine/feature_engineering.py",
    "engine/hashing.py",
    "engine/weights.py",
    "product/config.py",
    "product/contracts.py",
    "product/run_prediction.py",
    "research_ensemble/components.py",
    "research_ensemble/config.py",
    "research_ensemble/historical.py",
    "research_ensemble/registry.py",
    "research_ensemble/runner_core.py",
    "research_ensemble/scoring.py",
    "research_ensemble/vector.py",
    "reports/product_p1_acceptance.json",
    "reports/product_p1_acceptance_lock.json",
    "reports/algorithm_integration_a1_spec_report.json",
    "reports/algorithm_integration_a1_spec_lock.json",
    "reports/ALGORITHM_INTEGRATION_A2_STATUS.md",
    "reports/algorithm_integration_a2_implementation.json",
    "reports/algorithm_integration_a2_implementation_lock.json",
    "release/algorithm_integration_a2_rollback_manifest.json",
    "reports/gate2_3p3_full_summary.md",
    "reports/gate2_3p_r3_dev_lock.json",
    "reports/gate2_3p_r3m2_oracle_dev_lock.json",
    "reports/gate2_3p_r3m3_predictable_group_dev_lock.json",
    "docs/ALGORITHM_INTEGRATION_A3_EVALUATION_SPEC.md",
    "docs/ALGORITHM_INTEGRATION_A3_METRICS.md",
    "docs/ALGORITHM_INTEGRATION_A3_ACCEPTANCE.md",
    "reports/algorithm_integration_a3_spec_report.json",
    "reports/algorithm_integration_a3_spec_lock.json",
)

MODEL_SOURCE_PATHS = (
    "engine/distributions.py",
    "engine/elementary_symmetric.py",
    "engine/feature_engineering.py",
    "engine/weights.py",
    "research_ensemble/components.py",
    "research_ensemble/config.py",
    "research_ensemble/historical.py",
    "research_ensemble/registry.py",
    "research_ensemble/scoring.py",
    "research_ensemble/vector.py",
)

METRIC_CONTRACT_PATHS = (
    "docs/ALGORITHM_INTEGRATION_A3_EVALUATION_SPEC.md",
    "docs/ALGORITHM_INTEGRATION_A3_METRICS.md",
    "docs/ALGORITHM_INTEGRATION_A3_ACCEPTANCE.md",
    "reports/algorithm_integration_a3_spec_lock.json",
)

EVALUATION_SOURCE_PATHS = (
    "research_ensemble/evaluation.py",
    "research_ensemble/run_evaluation.py",
    "research_ensemble/compare_evaluation.py",
)

DISALLOWED_NETWORK_IMPORTS = {
    "aiohttp",
    "ftplib",
    "http",
    "httpx",
    "requests",
    "socket",
    "urllib",
    "urllib3",
}


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _source_manifest(root: pathlib.Path, paths: Sequence[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for relative in paths:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"required source missing: {relative}")
        output[relative] = _sha256_bytes(path.read_bytes())
    return output


def _git_output(root: pathlib.Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def verify_frozen_paths(root: pathlib.Path) -> dict[str, Any]:
    results: dict[str, dict[str, Any]] = {}
    all_match = True
    for relative in FROZEN_PATHS:
        current_path = root / relative
        try:
            expected_blob = _git_output(root, "rev-parse", f"{BASE_COMMIT}:{relative}")
            current_blob = _git_output(root, "hash-object", str(current_path))
            match = expected_blob == current_blob
            results[relative] = {
                "expected_blob": expected_blob,
                "current_blob": current_blob,
                "match": match,
            }
            all_match = all_match and match
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            results[relative] = {"match": False, "error": type(exc).__name__}
            all_match = False
    return {"all_match": all_match, "paths": results, "manifest_hash": sha256_value(results)}


def verify_base_ancestry(root: pathlib.Path) -> bool:
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE_COMMIT, "HEAD"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def scan_network_imports(root: pathlib.Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for relative in EVALUATION_SOURCE_PATHS:
        path = root / relative
        if not path.is_file():
            findings.append({"path": relative, "module": "MISSING"})
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                root_name = name.split(".", 1)[0]
                if name in DISALLOWED_NETWORK_IMPORTS or root_name in DISALLOWED_NETWORK_IMPORTS:
                    findings.append({"path": relative, "module": name})
    return {"pass": not findings, "findings": findings}


def fixed_config_check(config: ResearchEnsembleConfig) -> dict[str, Any]:
    actual = {
        "min_history": config.min_history,
        "prior_concentration": config.prior_concentration,
        "recent_windows": list(config.recent_windows),
        "ewma_half_life": config.ewma_half_life,
        "winsor_limit": config.winsor_limit,
        "weight_decay": config.weight_decay,
        "learning_rate": config.learning_rate,
        "loss_difference_clip": config.loss_difference_clip,
        "minimum_weight": config.minimum_weight,
        "historical_budget": config.historical_budget,
        "single_hypothesis_cap": config.single_hypothesis_cap,
        "hypothesis_total_cap": config.hypothesis_total_cap,
        "single_physical_field_cap": config.single_physical_field_cap,
        "physical_total_cap": config.physical_total_cap,
        "final_logit_abs_cap": config.final_logit_abs_cap,
        "historical_weight_support_draws": config.historical_weight_support_draws,
    }
    expected = {
        "min_history": 299,
        "prior_concentration": 90.0,
        "recent_windows": [10, 30, 52, 104],
        "ewma_half_life": 26.0,
        "winsor_limit": 3.0,
        "weight_decay": 0.995,
        "learning_rate": 0.10,
        "loss_difference_clip": 5.0,
        "minimum_weight": 0.01,
        "historical_budget": 0.60,
        "single_hypothesis_cap": 0.10,
        "hypothesis_total_cap": 0.25,
        "single_physical_field_cap": 0.05,
        "physical_total_cap": 0.15,
        "final_logit_abs_cap": 0.35,
        "historical_weight_support_draws": 52,
    }
    return {"pass": actual == expected, "actual": actual, "expected": expected, "config_hash": config.config_hash}


def control_m0_regression(dataset_path: pathlib.Path) -> dict[str, Any]:
    first = run_product_prediction(
        target_draw_no=1231,
        dataset_path=dataset_path,
        generated_at="2026-07-03T00:00:00Z",
    )
    second = run_product_prediction(
        target_draw_no=1231,
        dataset_path=dataset_path,
        generated_at="2026-07-03T00:00:00Z",
    )
    candidates = first.get("candidate_sets", [])
    pass_value = (
        first == second
        and first.get("input_last_draw") == 1230
        and first.get("final_distribution") == "M0_ONLY"
        and first.get("product_weights") == {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0}
        and first.get("statistical_edge") is False
        and first.get("reason") == "no_validated_nonuniform_signal"
        and len(candidates) == 5
        and len({tuple(item["numbers"]) for item in candidates}) == 5
        and all(len(item["numbers"]) == 6 for item in candidates)
        and all(abs(float(item["lift_vs_uniform"]) - 1.0) <= 1e-15 for item in candidates)
    )
    return {
        "pass": pass_value,
        "prediction_hash": first.get("hashes", {}).get("prediction_hash"),
        "candidate_sets_hash": sha256_value(candidates),
    }


def _distribution_identity(distribution: FixedSizeDistribution) -> dict[str, Any]:
    logits = [stable_float(value) for value in distribution.logits]
    payload = {
        "labels": list(distribution.labels or ()),
        "pick_count": distribution.pick_count,
        "logits": logits,
        "log_normalizer": stable_float(distribution.log_normalizer),
    }
    return {"hash": sha256_value(payload), "payload": payload}


def _brier(marginals: Mapping[int, float], outcome: set[int], number_count: int) -> float:
    return sum((float(marginals[number]) - (1.0 if number in outcome else 0.0)) ** 2 for number in range(1, number_count + 1)) / number_count


def _cutoff_hash(target: int, data_hash: str) -> str:
    return sha256_value(
        {
            "target_draw_no": target,
            "input_first_draw": 1,
            "input_last_draw": target - 1,
            "input_record_count": target - 1,
            "excluded_draws_at_or_after_target": TARGET_END - target + 1,
            "data_hash": data_hash,
        }
    )


def _block_starts(seed: str, n: int, block_length: int, replicates: int) -> list[tuple[int, ...]]:
    blocks = math.ceil(n / block_length)
    output: list[tuple[int, ...]] = []
    for replicate in range(replicates):
        starts = []
        for block in range(blocks):
            digest = hashlib.sha256(f"{seed}:{replicate}:{block}".encode("utf-8")).digest()
            starts.append(int.from_bytes(digest[:8], "big") % n)
        output.append(tuple(starts))
    return output


def _prefix(values: Sequence[float]) -> list[float]:
    output = [0.0]
    for value in values:
        output.append(output[-1] + float(value))
    return output


def moving_block_bootstrap_means(
    values: Sequence[float],
    *,
    starts: Sequence[Sequence[int]],
    block_length: int,
) -> list[float]:
    n = len(values)
    if n <= 0:
        raise ValueError("bootstrap values must not be empty")
    extended = list(values) + list(values)
    prefix = _prefix(extended)
    full_blocks, remainder = divmod(n, block_length)
    output: list[float] = []
    for replicate_starts in starts:
        if len(replicate_starts) != full_blocks + (1 if remainder else 0):
            raise ValueError("bootstrap start count mismatch")
        total = 0.0
        for index in range(full_blocks):
            start = replicate_starts[index]
            total += prefix[start + block_length] - prefix[start]
        if remainder:
            start = replicate_starts[-1]
            total += prefix[start + remainder] - prefix[start]
        output.append(total / n)
    return output


def _nearest_rank(values: Sequence[float], quantile: float) -> float:
    if not values:
        raise ValueError("quantile values must not be empty")
    ordered = sorted(float(value) for value in values)
    index = max(0, min(len(ordered) - 1, math.ceil(quantile * len(ordered)) - 1))
    return ordered[index]


def bootstrap_summary(values: Sequence[float], *, starts: Sequence[Sequence[int]], block_length: int) -> dict[str, float]:
    observed = sum(values) / len(values)
    raw_means = moving_block_bootstrap_means(values, starts=starts, block_length=block_length)
    centered = [value - observed for value in values]
    centered_means = moving_block_bootstrap_means(centered, starts=starts, block_length=block_length)
    p_value = (1.0 + sum(value >= observed for value in centered_means)) / (len(centered_means) + 1.0)
    return {
        "mean": stable_float(observed),
        "lower_95_one_sided": stable_float(_nearest_rank(raw_means, BOOTSTRAP_ALPHA)),
        "p_value_one_sided": stable_float(p_value),
    }


def holm_adjust(p_values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(((name, float(value)) for name, value in p_values.items()), key=lambda item: (item[1], item[0]))
    total = len(ordered)
    running = 0.0
    adjusted: dict[str, float] = {}
    for index, (name, value) in enumerate(ordered):
        candidate = min(1.0, (total - index) * value)
        running = max(running, candidate)
        adjusted[name] = stable_float(running)
    return adjusted


def calibration_summary(values: Sequence[tuple[float, int, int, int]]) -> dict[str, Any]:
    ordered = sorted(values, key=lambda item: (item[0], item[1], item[2]))
    count = len(ordered)
    bins: list[dict[str, Any]] = []
    weighted_ece = 0.0
    for index in range(10):
        start = index * count // 10
        end = (index + 1) * count // 10
        chunk = ordered[start:end]
        mean_prediction = sum(item[0] for item in chunk) / len(chunk)
        empirical = sum(item[3] for item in chunk) / len(chunk)
        gap = abs(mean_prediction - empirical)
        weighted_ece += len(chunk) / count * gap
        bins.append(
            {
                "bin": index + 1,
                "count": len(chunk),
                "mean_prediction": stable_float(mean_prediction),
                "empirical_frequency": stable_float(empirical),
                "absolute_gap": stable_float(gap),
            }
        )
    return {"bin_count": 10, "weighted_ece": stable_float(weighted_ece), "bins": bins}


def _quarter_ranges() -> tuple[tuple[int, int], ...]:
    return ((352, 571), (572, 791), (792, 1011), (1012, 1230))


def _quarter_means(targets: Sequence[int], values: Sequence[float]) -> list[dict[str, Any]]:
    by_target = dict(zip(targets, values, strict=True))
    output: list[dict[str, Any]] = []
    for start, end in _quarter_ranges():
        chunk = [by_target[target] for target in range(start, end + 1)]
        output.append({"start": start, "end": end, "count": len(chunk), "mean": stable_float(sum(chunk) / len(chunk))})
    return output


def _empty_components(config: ResearchEnsembleConfig) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    users = empty_user_registry()
    hypotheses_registry = empty_hypothesis_registry()
    adapter = empty_physical_adapter()
    physical = physical_component(users, hypotheses_registry, adapter, config)
    hypotheses = hypothesis_component(users, hypotheses_registry, set(physical["used_hypothesis_ids"]), config)
    return hypotheses, physical, {
        "user_input_hash": users["registry_hash"],
        "hypothesis_registry_hash": hypotheses_registry["registry_hash"],
        "physical_adapter_hash": adapter["adapter_hash"],
    }


def evaluate_dataset(
    *,
    dataset_path: str | pathlib.Path,
    rows_output: str | pathlib.Path | None = None,
    config: ResearchEnsembleConfig = DEFAULT_INTEGRATION_CONFIG,
) -> dict[str, Any]:
    root = _repo_root()
    path = pathlib.Path(dataset_path)
    raw_data = path.read_bytes()
    data_hash = _sha256_bytes(raw_data)
    data_version, records = load_dataset(path)
    target_sequence = list(range(TARGET_START, TARGET_END + 1))
    integrity: dict[str, Any] = {}

    integrity["E1_contract_and_base"] = {
        "pass": EVALUATION_CONTRACT_VERSION == "research-ensemble-evaluation-implementation-1.0.0" and verify_base_ancestry(root),
        "contract": EVALUATION_CONTRACT_VERSION,
        "base_commit": BASE_COMMIT,
    }
    integrity["E2_dataset"] = {
        "pass": data_hash == EXPECTED_DATA_HASH and data_version == EXPECTED_DATA_VERSION and len(records) == 1230 and records[0].draw_no == 1 and records[-1].draw_no == 1230,
        "data_hash": data_hash,
        "data_version": data_version,
        "record_count": len(records),
        "draw_range": [records[0].draw_no, records[-1].draw_no],
    }
    integrity["E3_target_sequence"] = {
        "pass": len(target_sequence) == TARGET_COUNT and target_sequence[0] == TARGET_START and target_sequence[-1] == TARGET_END,
        "target_count": len(target_sequence),
        "target_sequence_hash": sha256_value(target_sequence),
    }
    integrity["E6_control_m0_regression"] = control_m0_regression(path)
    integrity["E9_unapproved_entries"] = {"pass": True, "active_user_entries": 0, "active_physical_entries": 0}
    integrity["E14_network_dependency"] = scan_network_imports(root)
    frozen = verify_frozen_paths(root)
    integrity["E15_prior_evidence_unchanged"] = {"pass": bool(frozen["all_match"]), "manifest_hash": frozen["manifest_hash"], "details": frozen["paths"]}
    integrity["E16_fixed_configuration"] = fixed_config_check(config)

    if not integrity["E2_dataset"]["pass"]:
        return _terminal_result(
            integrity=integrity,
            status="A4_EVALUATION_FAIL",
            reasons=["E2_dataset"],
            data_hash=data_hash,
            data_version=data_version,
        )

    hypotheses, physical, registry_hashes = _empty_components(config)
    weights = uniform_weights(("M1", "M2"))
    loss_count = 0
    uniform = FixedSizeDistribution((0.0,) * config.number_count, config.pick_count)

    rows: list[dict[str, Any]] = []
    lane_jls: dict[str, list[float]] = {lane: [] for lane in ABLATION_IDS}
    lane_brier: dict[str, list[float]] = {lane: [] for lane in ABLATION_IDS}
    primary_calibration: list[tuple[float, int, int, int]] = []
    equivalence = {f"{left}=={right}": True for left, right in EQUIVALENCE_PAIRS}
    equivalence_failures: list[dict[str, Any]] = []
    cutoff_pass = True
    probability_pass = True
    row_hash_pass = True
    lane_count_pass = True

    for target in range(WARMUP_START, TARGET_END + 1):
        history = records[: target - 1]
        outcome_record = records[target - 1]
        if history[-1].draw_no != target - 1 or outcome_record.draw_no != target:
            cutoff_pass = False
            break
        snapshot = build_feature_snapshot(
            history,
            target_draw_no=target,
            data_version=data_version,
            config=config.engine_config,
        )
        raw = family_raw_vectors(snapshot, m3_eligible=False, number_count=config.number_count)
        normalized = {
            family: normalize_vector(raw[family], number_count=config.number_count)
            for family in ("M1", "M2", "M3")
        }
        historical = {
            "raw": raw,
            "normalized": normalized,
            "weights": {"M1": weights["M1"], "M2": weights["M2"], "M3": 0.0},
            "support": min(1.0, 0.5 + 0.5 * loss_count / config.historical_weight_support_draws),
            "m3_eligible": False,
            "m3_reasons": ["m3_evidence_not_provided"],
        }

        if target >= TARGET_START:
            target_rows: dict[str, dict[str, Any]] = {}
            target_distribution_hashes: dict[str, str] = {}
            target_score_hashes: dict[str, str] = {}
            outcome = set(outcome_record.numbers)
            cutoff_hash = _cutoff_hash(target, data_hash)
            baseline_jls: float | None = None
            baseline_brier: float | None = None

            for lane in ABLATION_IDS:
                assembled = assemble_ablation(lane, historical, hypotheses, physical, config)
                distribution = FixedSizeDistribution(
                    tuple(assembled["final_logits"][number] for number in range(1, config.number_count + 1)),
                    config.pick_count,
                )
                identity = _distribution_identity(distribution)
                marginals = distribution.marginal_probabilities()
                marginal_sum = sum(marginals.values())
                jls = distribution.joint_log_probability(outcome_record.numbers)
                brier = _brier(marginals, outcome, config.number_count)
                if not math.isfinite(jls) or not math.isfinite(brier) or abs(marginal_sum - config.pick_count) > 1e-10:
                    probability_pass = False
                if lane == CONTROL_LANE:
                    baseline_jls = jls
                    baseline_brier = brier
                target_distribution_hashes[lane] = identity["hash"]
                target_score_hashes[lane] = assembled["score_vector_hash"]
                target_rows[lane] = {
                    "target_draw_no": target,
                    "input_last_draw": target - 1,
                    "lane_id": lane,
                    "joint_log_score": stable_float(jls),
                    "marginal_brier": stable_float(brier),
                    "score_vector_hash": assembled["score_vector_hash"],
                    "distribution_hash": identity["hash"],
                    "cutoff_hash": cutoff_hash,
                }
                if lane == PRIMARY_LANE:
                    for number in range(1, config.number_count + 1):
                        primary_calibration.append((float(marginals[number]), target, number, 1 if number in outcome else 0))

            if baseline_jls is None or baseline_brier is None:
                lane_count_pass = False
                break

            for lane in ABLATION_IDS:
                row = target_rows[lane]
                delta = float(row["joint_log_score"]) - baseline_jls
                brier_gain = baseline_brier - float(row["marginal_brier"])
                row["joint_log_score_delta_vs_m0"] = stable_float(delta)
                row["marginal_brier_gain_vs_m0"] = stable_float(brier_gain)
                row["metric_row_hash"] = sha256_value(row)
                if row["metric_row_hash"] != sha256_value({key: value for key, value in row.items() if key != "metric_row_hash"}):
                    row_hash_pass = False
                rows.append(row)
                lane_jls[lane].append(float(row["joint_log_score"]))
                lane_brier[lane].append(float(row["marginal_brier"]))

            for left, right in EQUIVALENCE_PAIRS:
                key = f"{left}=={right}"
                match = target_distribution_hashes[left] == target_distribution_hashes[right] and target_score_hashes[left] == target_score_hashes[right]
                if not match:
                    equivalence[key] = False
                    if len(equivalence_failures) < 20:
                        equivalence_failures.append(
                            {
                                "target": target,
                                "left": left,
                                "right": right,
                                "left_distribution_hash": target_distribution_hashes[left],
                                "right_distribution_hash": target_distribution_hashes[right],
                                "left_score_hash": target_score_hashes[left],
                                "right_score_hash": target_score_hashes[right],
                            }
                        )

        if target < TARGET_END:
            family_distributions = {
                family: FixedSizeDistribution(
                    tuple(normalized[family][number] for number in range(1, config.number_count + 1)),
                    config.pick_count,
                )
                for family in ("M1", "M2")
            }
            losses = {
                family: -family_distributions[family].joint_log_probability(outcome_record.numbers)
                for family in ("M1", "M2")
            }
            baseline_loss = -uniform.joint_log_probability(outcome_record.numbers)
            weights = update_weights(weights, losses, baseline_loss=baseline_loss, config=config.engine_config)
            loss_count += 1

    expected_rows = TARGET_COUNT * len(ABLATION_IDS)
    lane_count_pass = lane_count_pass and len(rows) == expected_rows and all(len(lane_jls[lane]) == TARGET_COUNT for lane in ABLATION_IDS)
    integrity["E4_target_minus_one"] = {"pass": cutoff_pass, "last_evaluated_target": rows[-1]["target_draw_no"] if rows else None}
    integrity["E5_future_data_access"] = {"pass": cutoff_pass, "policy": "history_slice_1_to_target_minus_1"}
    integrity["E7_ten_lanes"] = {"pass": lane_count_pass, "lane_count": len(ABLATION_IDS), "row_count": len(rows)}
    integrity["E8_equivalence"] = {"pass": all(equivalence.values()), "checks": equivalence, "failures": equivalence_failures}
    integrity["E10_probability_validity"] = {"pass": probability_pass, "marginal_sum_tolerance": 1e-10}
    integrity["E12_complete_rows"] = {"pass": lane_count_pass, "expected": expected_rows, "actual": len(rows)}
    integrity["E13_hash_recomputation"] = {"pass": row_hash_pass, "metric_rows_hash": sha256_value(rows)}

    if rows_output is not None:
        rows_path = pathlib.Path(rows_output)
        rows_path.parent.mkdir(parents=True, exist_ok=True)
        rows_path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")
        integrity["E13_hash_recomputation"]["rows_file_sha256"] = _sha256_bytes(rows_path.read_bytes())

    targets = target_sequence
    lane_delta: dict[str, list[float]] = {}
    lane_brier_gain: dict[str, list[float]] = {}
    for lane in ABLATION_IDS:
        lane_delta[lane] = [value - baseline for value, baseline in zip(lane_jls[lane], lane_jls[CONTROL_LANE], strict=True)]
        lane_brier_gain[lane] = [baseline - value for value, baseline in zip(lane_brier[lane], lane_brier[CONTROL_LANE], strict=True)]

    bootstrap_seed = sha256_value([SPEC_CONTRACT_VERSION, data_hash, sha256_value(targets), "PRIMARY_MBB"])
    starts = _block_starts(bootstrap_seed, TARGET_COUNT, BOOTSTRAP_BLOCK_LENGTH, BOOTSTRAP_REPLICATES)
    lane_metrics: dict[str, Any] = {}
    lane_p_values: dict[str, float] = {}
    for lane in ABLATION_IDS:
        summary = bootstrap_summary(lane_delta[lane], starts=starts, block_length=BOOTSTRAP_BLOCK_LENGTH)
        quarters = _quarter_means(targets, lane_delta[lane])
        lane_metrics[lane] = {
            "joint_log_score": summary,
            "mean_brier_gain": stable_float(sum(lane_brier_gain[lane]) / TARGET_COUNT),
            "quarter_means": quarters,
            "positive_quarter_count": sum(item["mean"] > 0.0 for item in quarters),
            "final_cumulative_delta": stable_float(sum(lane_delta[lane])),
        }
        if lane != CONTROL_LANE:
            lane_p_values[lane] = summary["p_value_one_sided"]

    component_series = {
        "C1_FULL_MINUS_MINUS_M1": [
            left - right for left, right in zip(lane_jls[PRIMARY_LANE], lane_jls["ENSEMBLE_MINUS_M1"], strict=True)
        ],
        "C2_FULL_MINUS_MINUS_M2": [
            left - right for left, right in zip(lane_jls[PRIMARY_LANE], lane_jls["ENSEMBLE_MINUS_M2"], strict=True)
        ],
    }
    component_metrics: dict[str, Any] = {}
    component_p_values: dict[str, float] = {}
    for name, values in component_series.items():
        summary = bootstrap_summary(values, starts=starts, block_length=BOOTSTRAP_BLOCK_LENGTH)
        component_metrics[name] = summary
        component_p_values[name] = summary["p_value_one_sided"]

    calibration = calibration_summary(primary_calibration)
    primary = lane_metrics[PRIMARY_LANE]
    primary_pass = primary["joint_log_score"]["mean"] > 0.0 and primary["joint_log_score"]["lower_95_one_sided"] > 0.0
    brier_pass = primary["mean_brier_gain"] >= 0.0
    stability_pass = primary["positive_quarter_count"] >= 3 and primary["final_cumulative_delta"] > 0.0

    mandatory_keys = (
        "E1_contract_and_base",
        "E2_dataset",
        "E3_target_sequence",
        "E4_target_minus_one",
        "E5_future_data_access",
        "E6_control_m0_regression",
        "E7_ten_lanes",
        "E8_equivalence",
        "E9_unapproved_entries",
        "E10_probability_validity",
        "E12_complete_rows",
        "E13_hash_recomputation",
        "E14_network_dependency",
        "E15_prior_evidence_unchanged",
        "E16_fixed_configuration",
    )
    integrity_pass = all(bool(integrity[key]["pass"]) for key in mandatory_keys)
    reasons: list[str] = []
    if not integrity_pass:
        reasons.extend(key for key in mandatory_keys if not bool(integrity[key]["pass"]))
    if not primary_pass:
        reasons.append("primary_joint_log_score_criterion")
    if not brier_pass:
        reasons.append("marginal_brier_guardrail")
    if not stability_pass:
        reasons.append("temporal_stability_guardrail")

    preliminary_status = "A4_EVALUATION_PASS_CANDIDATE" if not reasons else "A4_EVALUATION_FAIL"
    source_manifest = _source_manifest(root, MODEL_SOURCE_PATHS)
    metric_contract_manifest = _source_manifest(root, METRIC_CONTRACT_PATHS)
    evaluation_source_manifest = _source_manifest(root, EVALUATION_SOURCE_PATHS)
    lane_holm = holm_adjust(lane_p_values)
    component_holm = holm_adjust(component_p_values)
    hashes = {
        "data_hash": data_hash,
        "target_sequence_hash": sha256_value(targets),
        "lane_manifest_hash": sha256_value(list(ABLATION_IDS)),
        "A2_model_source_hash": sha256_value(source_manifest),
        "score_config_hash": config.config_hash,
        "metric_contract_hash": sha256_value(metric_contract_manifest),
        "evaluation_source_hash": sha256_value(evaluation_source_manifest),
        "metric_rows_hash": sha256_value(rows),
        "aggregate_metrics_hash": sha256_value({"lanes": lane_metrics, "components": component_metrics, "calibration": calibration}),
        "multiple_comparison_report_hash": sha256_value({"lane_holm": lane_holm, "component_holm": component_holm}),
    }
    manifest = {
        "evaluation_contract_version": EVALUATION_CONTRACT_VERSION,
        "spec_contract_version": SPEC_CONTRACT_VERSION,
        "profile_id": PROFILE_ID,
        "base_commit": BASE_COMMIT,
        "data_version": data_version,
        "data_hash": data_hash,
        "minimum_history": MINIMUM_HISTORY,
        "warmup_targets": [WARMUP_START, WARMUP_END],
        "confirmatory_targets": [TARGET_START, TARGET_END],
        "confirmatory_count": TARGET_COUNT,
        "lanes": list(ABLATION_IDS),
        "bootstrap": {
            "type": "CIRCULAR_MOVING_BLOCK",
            "block_length": BOOTSTRAP_BLOCK_LENGTH,
            "replicates": BOOTSTRAP_REPLICATES,
            "alpha": BOOTSTRAP_ALPHA,
            "seed": bootstrap_seed,
        },
        "registry_hashes": registry_hashes,
        "source_hashes": hashes,
    }
    hashes["evaluation_manifest_hash"] = sha256_value(manifest)
    decision_payload = {
        "preliminary_status": preliminary_status,
        "reasons": reasons,
        "integrity_pass": integrity_pass,
        "primary_pass": primary_pass,
        "brier_pass": brier_pass,
        "stability_pass": stability_pass,
        "evaluation_manifest_hash": hashes["evaluation_manifest_hash"],
        "aggregate_metrics_hash": hashes["aggregate_metrics_hash"],
    }
    hashes["decision_hash"] = sha256_value(decision_payload)

    canonical_result = {
        "status": preliminary_status,
        "decision_reasons": reasons,
        "contract_version": EVALUATION_CONTRACT_VERSION,
        "spec_contract_version": SPEC_CONTRACT_VERSION,
        "profile_id": PROFILE_ID,
        "base_commit": BASE_COMMIT,
        "data": integrity["E2_dataset"],
        "target_sequence": integrity["E3_target_sequence"],
        "integrity": integrity,
        "primary": primary,
        "secondary": {
            "mean_brier_gain": primary["mean_brier_gain"],
            "quarter_means": primary["quarter_means"],
            "positive_quarter_count": primary["positive_quarter_count"],
            "final_cumulative_delta": primary["final_cumulative_delta"],
            "calibration": calibration,
        },
        "lanes": lane_metrics,
        "component_contrasts": component_metrics,
        "multiple_comparison": {"lane_holm": lane_holm, "component_holm": component_holm},
        "equivalence": integrity["E8_equivalence"],
        "hashes": hashes,
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "advantage_status": "retrospective research evaluation only",
        "actual_user_entries_active": 0,
        "actual_physical_entries_active": 0,
        "hyperparameter_exploration_executed": False,
        "external_access_performed": False,
    }
    canonical_result["canonical_result_hash"] = sha256_value(canonical_result)
    return {
        "runtime": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        },
        "canonical_result": canonical_result,
        "canonical_result_hash": canonical_result["canonical_result_hash"],
    }


def _terminal_result(
    *,
    integrity: Mapping[str, Any],
    status: str,
    reasons: Sequence[str],
    data_hash: str | None,
    data_version: str | None,
) -> dict[str, Any]:
    canonical_result = {
        "status": status,
        "decision_reasons": list(reasons),
        "contract_version": EVALUATION_CONTRACT_VERSION,
        "spec_contract_version": SPEC_CONTRACT_VERSION,
        "profile_id": PROFILE_ID,
        "base_commit": BASE_COMMIT,
        "data": {"data_hash": data_hash, "data_version": data_version},
        "integrity": dict(integrity),
        "research_only": True,
        "public_release_allowed": False,
        "statistical_edge": False,
        "advantage_status": "retrospective research evaluation only",
        "actual_user_entries_active": 0,
        "actual_physical_entries_active": 0,
        "hyperparameter_exploration_executed": False,
        "external_access_performed": False,
    }
    canonical_result["canonical_result_hash"] = sha256_value(canonical_result)
    return {
        "runtime": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        },
        "canonical_result": canonical_result,
        "canonical_result_hash": canonical_result["canonical_result_hash"],
    }


def write_result(result: Mapping[str, Any], path: str | pathlib.Path) -> None:
    output = pathlib.Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(result) + "\n", encoding="utf-8")
