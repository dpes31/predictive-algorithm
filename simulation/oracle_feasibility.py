"""Gate 2-3P-R3M-2 DEV-only oracle feasibility evaluation.

The module evaluates the approved 5.0 oracle contract only. It does not learn
favored groups, search the full M3 space, or touch CAL/SEALED namespaces.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from statistics import median
from typing import Any, Sequence

from engine.experts.oracle_group_eprocess import (
    ExactGroupAlternative,
    OracleGroupEProcess,
)

DEV_NAMESPACE = "DEV"
MODEL_VERSION = "5.0.0-research"
GATE_NAME = "Gate 2-3P-R3M-2"
SCENARIO_NAME = "p4_regime_reversal_oracle"
FAVORED_NUMBERS = tuple(range(36, 46))
LIFT = 1.25
DETECTION_HORIZON = 520
ACTIVE_LIFE = 208
ACTIVATION_THRESHOLD = 1000.0
POSITIVE_ACTIVATION_TARGET = 0.80
NULL_FALSE_ACTIVATION_TARGET = 0.001
NULL_UPPER_TARGET = 0.002


@dataclass(frozen=True)
class OracleSeriesResult:
    seed: int
    alternative: bool
    activated: bool
    trigger_delay: int | None
    max_e_value: float
    terminal_e_value: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def oracle_seed(kind: str, replicate: int, *, namespace: str = DEV_NAMESPACE) -> int:
    if namespace != DEV_NAMESPACE:
        raise ValueError("Gate 2-3P-R3M-2 accepts DEV namespace only")
    if kind not in {"positive", "null"}:
        raise ValueError("kind must be positive or null")
    if replicate < 0:
        raise ValueError("replicate must be non-negative")
    material = (
        f"{GATE_NAME}|{MODEL_VERSION}|{namespace}|{kind}|"
        f"{SCENARIO_NAME}|{LIFT:.8f}|{replicate}"
    )
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _cdf(probabilities: Sequence[float]) -> tuple[float, ...]:
    cumulative = 0.0
    output = []
    for probability in probabilities:
        cumulative += probability
        output.append(cumulative)
    output[-1] = 1.0
    return tuple(output)


def _sample_count(rng: random.Random, support: Sequence[int], cdf: Sequence[float]) -> int:
    index = bisect.bisect_left(cdf, rng.random())
    return support[index]


def run_oracle_series(*, kind: str, replicate: int) -> OracleSeriesResult:
    alternative = ExactGroupAlternative(FAVORED_NUMBERS, LIFT)
    probabilities = alternative.count_probabilities(alternative=kind == "positive")
    count_cdf = _cdf(probabilities)
    rng_seed = oracle_seed(kind, replicate)
    rng = random.Random(rng_seed)
    process = OracleGroupEProcess(
        alternative,
        activation_threshold=ACTIVATION_THRESHOLD,
        detection_horizon=DETECTION_HORIZON,
        active_life=ACTIVE_LIFE,
    )

    final = None
    for _ in range(DETECTION_HORIZON):
        selected_favored = _sample_count(rng, alternative.support, count_cdf)
        final = process.update_count(selected_favored)

    if final is None:
        raise RuntimeError("oracle series produced no draws")
    return OracleSeriesResult(
        seed=rng_seed,
        alternative=kind == "positive",
        activated=final.ever_activated,
        trigger_delay=final.trigger_draw_index,
        max_e_value=process.max_e_value,
        terminal_e_value=final.e_value,
    )


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(probability * len(ordered)) - 1))
    return ordered[index]


def one_sided_binomial_upper(
    successes: int,
    trials: int,
    *,
    alpha: float = 0.05,
) -> float:
    """Exact Clopper-Pearson one-sided upper confidence limit."""

    if trials < 1:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be between zero and trials")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between zero and one")
    if successes == trials:
        return 1.0

    def binomial_cdf(probability: float) -> float:
        if probability <= 0.0:
            return 1.0
        if probability >= 1.0:
            return 0.0
        log_terms = [
            math.lgamma(trials + 1)
            - math.lgamma(index + 1)
            - math.lgamma(trials - index + 1)
            + index * math.log(probability)
            + (trials - index) * math.log1p(-probability)
            for index in range(successes + 1)
        ]
        maximum = max(log_terms)
        return math.exp(maximum) * sum(math.exp(value - maximum) for value in log_terms)

    lower = 0.0
    upper = 1.0
    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        if binomial_cdf(midpoint) > alpha:
            lower = midpoint
        else:
            upper = midpoint
    return upper


def _report_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_oracle_gate(
    *,
    positive_replicates: int = 2000,
    null_replicates: int = 10000,
    implementation_commit: str | None = None,
) -> dict[str, Any]:
    if positive_replicates < 1 or null_replicates < 1:
        raise ValueError("replicate counts must be positive")

    positive_rows = [
        run_oracle_series(kind="positive", replicate=index)
        for index in range(positive_replicates)
    ]
    null_rows = [
        run_oracle_series(kind="null", replicate=index)
        for index in range(null_replicates)
    ]

    activated_positive = [row for row in positive_rows if row.activated]
    activated_null = [row for row in null_rows if row.activated]
    positive_rate = len(activated_positive) / positive_replicates
    false_rate = len(activated_null) / null_replicates
    upper_95 = one_sided_binomial_upper(len(activated_null), null_replicates)
    trigger_delays = [row.trigger_delay for row in activated_positive if row.trigger_delay is not None]
    median_delay = float(median(trigger_delays)) if trigger_delays else None

    positive_pass = (
        positive_rate >= POSITIVE_ACTIVATION_TARGET
        and median_delay is not None
        and median_delay <= DETECTION_HORIZON
    )
    null_pass = (
        false_rate <= NULL_FALSE_ACTIVATION_TARGET
        and upper_95 <= NULL_UPPER_TARGET
    )
    status = "ORACLE_PASS" if positive_pass and null_pass else "ORACLE_FAIL"

    alternative = ExactGroupAlternative(FAVORED_NUMBERS, LIFT)
    payload: dict[str, Any] = {
        "gate": GATE_NAME,
        "namespace": DEV_NAMESPACE,
        "model_version": MODEL_VERSION,
        "scenario": SCENARIO_NAME,
        "alternative": alternative.to_dict(),
        "detection_horizon": DETECTION_HORIZON,
        "post_activation_active_life": ACTIVE_LIFE,
        "activation_threshold": ACTIVATION_THRESHOLD,
        "positive_replicates": positive_replicates,
        "positive_activated": len(activated_positive),
        "positive_activation_rate": positive_rate,
        "positive_target": POSITIVE_ACTIVATION_TARGET,
        "median_activation_delay": median_delay,
        "positive_max_e_q50": _quantile(
            [row.max_e_value for row in positive_rows], 0.50
        ),
        "positive_max_e_q95": _quantile(
            [row.max_e_value for row in positive_rows], 0.95
        ),
        "null_replicates": null_replicates,
        "null_activated": len(activated_null),
        "null_false_activation_rate": false_rate,
        "null_false_activation_target": NULL_FALSE_ACTIVATION_TARGET,
        "null_false_activation_upper_95": upper_95,
        "null_upper_target": NULL_UPPER_TARGET,
        "null_max_e_value": max(row.max_e_value for row in null_rows),
        "positive_pass": positive_pass,
        "null_pass": null_pass,
        "status": status,
        "implementation_commit": implementation_commit,
        "predictable_group_executed": False,
        "full_m3_dev_executed": False,
        "calibration_executed": False,
        "sealed_validation_executed": False,
        "real_data_executed": False,
        "mobile_work_executed": False,
        "research_only": True,
        "public_release_allowed": False,
    }
    payload["report_hash"] = _report_hash(payload)
    return payload
