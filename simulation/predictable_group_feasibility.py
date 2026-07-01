"""DEV-PG validation for predictable-group contract 1.0.0.

This module executes only Gate 2-3P-R3M-3-2. It does not implement the full M3
mixture, CAL/SEALED validation, real-data evaluation, or product predictions.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from functools import lru_cache
from statistics import fmean, median
from typing import Any, Sequence

from engine.experts.oracle_group_eprocess import ExactGroupAlternative
from engine.experts.predictable_group import (
    GROUP_SIZES,
    LIFT,
    NUMBER_COUNT,
    OUTER_WINDOW,
    PICK_COUNT,
    OccurrenceIndex,
    group_to_mask,
    numbers_to_mask,
    select_predictable_group,
)
from simulation.oracle_feasibility import one_sided_binomial_upper

MODEL_VERSION = "5.0.0-research"
CONTRACT_VERSION = "predictable-group-1.0.0"
GATE_NAME = "Gate 2-3P-R3M-3-2"
MAIN_NAMESPACE = "DEV-PG"
BOOTSTRAP_NAMESPACE = "DEV-PG-CI"
SERIES_LENGTH = 1230
CHANGE_POINT = 615
EVALUATION_ORIGIN = 625
BLOCK_LENGTH = 52
BLOCK_COUNT = 10
EVALUATION_HORIZON = BLOCK_LENGTH * BLOCK_COUNT
ACTIVATION_THRESHOLD = 1000.0
POST_ACTIVATION_ACTIVE_LIFE = 208
POSITIVE_REPLICATES = 2000
NULL_REPLICATES = 10000
BOOTSTRAP_RESAMPLES = 10000
TRUE_POST_GROUP = tuple(range(36, 46))
TRUE_PRE_GROUP = tuple(range(1, 11))
UNIFORM_MARGINAL = PICK_COUNT / NUMBER_COUNT
UNIFORM_BRIER = (
    PICK_COUNT * (1.0 - UNIFORM_MARGINAL) ** 2
    + (NUMBER_COUNT - PICK_COUNT) * UNIFORM_MARGINAL**2
) / NUMBER_COUNT


@dataclass(frozen=True)
class SeriesResult:
    kind: str
    seed: int
    activated: bool
    activation_delay: int | None
    non_abstain_blocks: int
    size_counts: dict[int, int]
    abstain_blocks: int
    eligible_counts: dict[int, int]
    positive_fold_histogram: dict[int, dict[int, int]]
    cv_scores: dict[int, tuple[float, ...]]
    direction_hits: int
    direction_trials: int
    mean_delta_log_loss: float
    mean_delta_brier: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def seed_for(kind: str, replicate: int, *, namespace: str = MAIN_NAMESPACE) -> int:
    if namespace != MAIN_NAMESPACE:
        raise ValueError("predictable-group execution accepts DEV-PG only")
    if kind not in {"positive", "null"}:
        raise ValueError("kind must be positive or null")
    if replicate < 0:
        raise ValueError("replicate must be non-negative")
    material = (
        f"Gate2-3P-R3M-3|{MODEL_VERSION}|{namespace}|main|"
        f"{kind}|p4_regime_reversal|{LIFT:.8f}|{replicate}"
    )
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def bootstrap_seed(metric: str, replicate_set_hash: str) -> int:
    if metric not in {"delta_log_loss", "delta_brier"}:
        raise ValueError("unsupported bootstrap metric")
    material = (
        f"Gate2-3P-R3M-3|{MODEL_VERSION}|{BOOTSTRAP_NAMESPACE}|"
        f"{metric}|{replicate_set_hash}"
    )
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


@lru_cache(maxsize=None)
def _count_cdf(group_size: int, lift: float) -> tuple[float, ...]:
    alternative = ExactGroupAlternative(tuple(range(1, group_size + 1)), lift)
    probabilities = alternative.count_probabilities(alternative=True)
    cumulative = 0.0
    output = []
    for probability in probabilities:
        cumulative += probability
        output.append(cumulative)
    output[-1] = 1.0
    return tuple(output)


def _sample_weighted_mask(
    rng: random.Random,
    favored: Sequence[int],
    lift: float,
) -> int:
    favored_values = tuple(favored)
    favored_set = set(favored_values)
    other = tuple(number for number in range(1, NUMBER_COUNT + 1) if number not in favored_set)
    alternative = ExactGroupAlternative(tuple(sorted(favored_values)), lift)
    draw = rng.random()
    cdf = _count_cdf(len(favored_values), lift)
    offset = next(index for index, value in enumerate(cdf) if draw <= value)
    selected_favored = alternative.support[offset]
    numbers = rng.sample(favored_values, selected_favored)
    numbers.extend(rng.sample(other, PICK_COUNT - selected_favored))
    return numbers_to_mask(numbers)


def generate_series(kind: str, seed: int) -> tuple[int, ...]:
    rng = random.Random(seed)
    output: list[int] = []
    universe = tuple(range(1, NUMBER_COUNT + 1))
    for draw_no in range(1, SERIES_LENGTH + 1):
        if kind == "null":
            output.append(numbers_to_mask(rng.sample(universe, PICK_COUNT)))
        elif kind == "positive":
            favored = TRUE_PRE_GROUP if draw_no < CHANGE_POINT else TRUE_POST_GROUP
            output.append(_sample_weighted_mask(rng, favored, LIFT))
        else:
            raise ValueError("kind must be positive or null")
    return tuple(output)


@lru_cache(maxsize=None)
def group_marginals(group_size: int) -> tuple[float, float]:
    alternative = ExactGroupAlternative(tuple(range(1, group_size + 1)), LIFT)
    probabilities = alternative.count_probabilities(alternative=True)
    expected_group_count = sum(
        count * probability
        for count, probability in zip(alternative.support, probabilities, strict=True)
    )
    inside = expected_group_count / group_size
    outside = (PICK_COUNT - expected_group_count) / (NUMBER_COUNT - group_size)
    return inside, outside


def brier_delta(draw_mask: int, group_mask: int, group_size: int) -> float:
    selected_inside = (draw_mask & group_mask).bit_count()
    inside, outside = group_marginals(group_size)
    selected_outside = PICK_COUNT - selected_inside
    predicted = (
        selected_inside * (1.0 - inside) ** 2
        + (group_size - selected_inside) * inside**2
        + selected_outside * (1.0 - outside) ** 2
        + (NUMBER_COUNT - group_size - selected_outside) * outside**2
    ) / NUMBER_COUNT
    return UNIFORM_BRIER - predicted


def direction_hit(group_mask: int, group_size: int) -> bool:
    true_mask = group_to_mask(TRUE_POST_GROUP)
    overlap = (group_mask & true_mask).bit_count()
    inside, outside = group_marginals(group_size)
    true_mean = (overlap * inside + (len(TRUE_POST_GROUP) - overlap) * outside) / len(
        TRUE_POST_GROUP
    )
    complement_inside = group_size - overlap
    complement_mean = (
        complement_inside * inside
        + (NUMBER_COUNT - len(TRUE_POST_GROUP) - complement_inside) * outside
    ) / (NUMBER_COUNT - len(TRUE_POST_GROUP))
    return true_mean > complement_mean


def evaluate_series(kind: str, replicate: int) -> SeriesResult:
    seed = seed_for(kind, replicate)
    masks = generate_series(kind, seed)
    index = OccurrenceIndex.build(masks)
    cumulative_log_e = 0.0
    activation_delay: int | None = None
    non_abstain = 0
    size_counts = {size: 0 for size in GROUP_SIZES}
    eligible_counts = {size: 0 for size in GROUP_SIZES}
    fold_histogram = {
        size: {folds: 0 for folds in range(6)} for size in GROUP_SIZES
    }
    cv_values = {size: [] for size in GROUP_SIZES}
    direction_hits = 0
    direction_trials = 0
    delta_log_total = 0.0
    delta_brier_total = 0.0

    for block in range(BLOCK_COUNT):
        block_start = EVALUATION_ORIGIN + block * BLOCK_LENGTH
        decision = select_predictable_group(index, block_start=block_start)
        for size in GROUP_SIZES:
            cv_values[size].append(float(decision.cv_scores[size]))
            fold_histogram[size][decision.positive_folds[size]] += 1
            if size in decision.eligible_sizes:
                eligible_counts[size] += 1

        if decision.abstain:
            continue

        non_abstain += 1
        selected_size = int(decision.selected_size or 0)
        size_counts[selected_size] += 1
        group_mask = decision.group_mask
        alternative = ExactGroupAlternative(decision.group, LIFT)
        if kind == "positive":
            direction_trials += 1
            if direction_hit(group_mask, selected_size):
                direction_hits += 1

        for offset in range(BLOCK_LENGTH):
            draw_no = block_start + offset
            draw_mask = masks[draw_no - 1]
            selected = (draw_mask & group_mask).bit_count()
            log_lr = alternative.log_likelihood_ratio_from_count(selected)
            cumulative_log_e += log_lr
            delta_log_total += log_lr
            delta_brier_total += brier_delta(draw_mask, group_mask, selected_size)
            delay = draw_no - EVALUATION_ORIGIN + 1
            if (
                activation_delay is None
                and cumulative_log_e >= math.log(ACTIVATION_THRESHOLD)
            ):
                activation_delay = delay

    return SeriesResult(
        kind=kind,
        seed=seed,
        activated=activation_delay is not None,
        activation_delay=activation_delay,
        non_abstain_blocks=non_abstain,
        size_counts=size_counts,
        abstain_blocks=BLOCK_COUNT - non_abstain,
        eligible_counts=eligible_counts,
        positive_fold_histogram=fold_histogram,
        cv_scores={size: tuple(values) for size, values in cv_values.items()},
        direction_hits=direction_hits,
        direction_trials=direction_trials,
        mean_delta_log_loss=delta_log_total / EVALUATION_HORIZON,
        mean_delta_brier=delta_brier_total / EVALUATION_HORIZON,
    )


def _seed_manifest_hash(rows: Sequence[SeriesResult]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(f"{row.kind}:{row.seed}\n".encode())
    return digest.hexdigest()


def _nearest_rank(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    rank = max(1, math.ceil(probability * len(ordered)))
    return ordered[rank - 1]


def bootstrap_lower(
    values: Sequence[float],
    *,
    metric: str,
    seed_manifest_hash: str,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> float:
    if not values:
        raise ValueError("bootstrap values must not be empty")
    rng = random.Random(bootstrap_seed(metric, seed_manifest_hash))
    count = len(values)
    means = []
    for _ in range(resamples):
        means.append(sum(values[rng.randrange(count)] for _ in range(count)) / count)
    return _nearest_rank(means, 0.05)


def _quantile(values: Sequence[float], probability: float) -> float:
    return _nearest_rank(values, probability)


def _hash_payload(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def run_predictable_group_gate(
    *,
    positive_replicates: int = POSITIVE_REPLICATES,
    null_replicates: int = NULL_REPLICATES,
    bootstrap_resamples: int = BOOTSTRAP_RESAMPLES,
    implementation_commit: str | None = None,
) -> dict[str, Any]:
    positive = [evaluate_series("positive", index) for index in range(positive_replicates)]
    null = [evaluate_series("null", index) for index in range(null_replicates)]
    manifest_hash = _seed_manifest_hash((*positive, *null))

    positive_blocks = positive_replicates * BLOCK_COUNT
    non_abstain_blocks = sum(row.non_abstain_blocks for row in positive)
    availability = non_abstain_blocks / positive_blocks
    activated_positive = [row for row in positive if row.activated]
    positive_activation_rate = len(activated_positive) / positive_replicates
    delays = [int(row.activation_delay) for row in activated_positive if row.activation_delay is not None]
    median_delay = float(median(delays)) if delays else None
    direction_hits_total = sum(row.direction_hits for row in positive)
    direction_trials_total = sum(row.direction_trials for row in positive)
    direction_accuracy = (
        direction_hits_total / direction_trials_total if direction_trials_total else None
    )

    log_values = [row.mean_delta_log_loss for row in positive]
    brier_values = [row.mean_delta_brier for row in positive]
    mean_log = fmean(log_values)
    mean_brier = fmean(brier_values)
    log_lower = bootstrap_lower(
        log_values,
        metric="delta_log_loss",
        seed_manifest_hash=manifest_hash,
        resamples=bootstrap_resamples,
    )
    brier_lower = bootstrap_lower(
        brier_values,
        metric="delta_brier",
        seed_manifest_hash=manifest_hash,
        resamples=bootstrap_resamples,
    )

    activated_null = sum(row.activated for row in null)
    null_rate = activated_null / null_replicates
    null_upper = one_sided_binomial_upper(activated_null, null_replicates)

    size_counts = {size: sum(row.size_counts[size] for row in positive) for size in GROUP_SIZES}
    eligible_counts = {
        size: sum(row.eligible_counts[size] for row in positive) for size in GROUP_SIZES
    }
    fold_histogram = {
        size: {
            folds: sum(row.positive_fold_histogram[size][folds] for row in positive)
            for folds in range(6)
        }
        for size in GROUP_SIZES
    }
    cv_diagnostics = {}
    for size in GROUP_SIZES:
        values = [value for row in positive for value in row.cv_scores[size]]
        cv_diagnostics[str(size)] = {
            "mean": fmean(values),
            "q05": _quantile(values, 0.05),
            "q50": _quantile(values, 0.50),
            "q95": _quantile(values, 0.95),
        }

    criteria = {
        "availability": availability >= 0.80,
        "activation": positive_activation_rate >= 0.80,
        "median_delay": median_delay is not None and median_delay <= OUTER_WINDOW,
        "direction_accuracy": direction_accuracy is not None and direction_accuracy >= 0.80,
        "direction_trials": direction_trials_total >= 16000,
        "mean_delta_log_loss": mean_log > 0.0,
        "lower_delta_log_loss": log_lower > 0.0,
        "mean_delta_brier": mean_brier >= 0.0,
        "lower_delta_brier": brier_lower >= 0.0,
        "null_rate": null_rate <= 0.001,
        "null_upper": null_upper <= 0.002,
    }
    status = "PREDICTABLE_GROUP_PASS" if all(criteria.values()) else "PREDICTABLE_GROUP_FAIL"

    payload: dict[str, Any] = {
        "gate": GATE_NAME,
        "model_version": MODEL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "namespace": MAIN_NAMESPACE,
        "bootstrap_namespace": BOOTSTRAP_NAMESPACE,
        "implementation_commit": implementation_commit,
        "status": status,
        "criteria": criteria,
        "positive_replicates": positive_replicates,
        "null_replicates": null_replicates,
        "bootstrap_resamples": bootstrap_resamples,
        "evaluation_origin": EVALUATION_ORIGIN,
        "evaluation_horizon": EVALUATION_HORIZON,
        "activation_threshold": ACTIVATION_THRESHOLD,
        "post_activation_active_life": POST_ACTIVATION_ACTIVE_LIFE,
        "group_availability": availability,
        "positive_activated": len(activated_positive),
        "positive_activation_rate": positive_activation_rate,
        "median_activation_delay": median_delay,
        "direction_hits": direction_hits_total,
        "direction_trials": direction_trials_total,
        "direction_accuracy": direction_accuracy,
        "mean_delta_log_loss": mean_log,
        "lower_95_delta_log_loss": log_lower,
        "mean_delta_brier": mean_brier,
        "lower_95_delta_brier": brier_lower,
        "null_activated": activated_null,
        "null_false_activation_rate": null_rate,
        "null_false_activation_upper_95": null_upper,
        "positive_size_counts": {str(size): size_counts[size] for size in GROUP_SIZES},
        "positive_abstain_blocks": positive_blocks - non_abstain_blocks,
        "positive_eligible_counts": {str(size): eligible_counts[size] for size in GROUP_SIZES},
        "positive_fold_histogram": {
            str(size): {str(folds): count for folds, count in fold_histogram[size].items()}
            for size in GROUP_SIZES
        },
        "positive_cv_diagnostics": cv_diagnostics,
        "seed_manifest_hash": manifest_hash,
        "full_m3_dev_executed": False,
        "calibration_executed": False,
        "sealed_validation_executed": False,
        "real_data_executed": False,
        "mobile_work_executed": False,
        "main_merge_performed": False,
        "public_release_allowed": False,
        "final_distribution": "M0_ONLY",
    }
    payload["report_hash"] = _hash_payload(payload)
    return payload
