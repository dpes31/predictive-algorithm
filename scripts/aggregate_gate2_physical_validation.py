#!/usr/bin/env python3
"""Aggregate Gate 2-3P-3 shard artifacts and issue the frozen decision."""

from __future__ import annotations

import argparse
import bisect
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, median
from typing import Any, Iterable, Mapping, Sequence

from engine.config import DEFAULT_CONFIG
from engine.hashing import sha256_value
from simulation.physical_validation import EFFECT_SIZES, positive_scenarios, robustness_scenarios

ALPHA = 0.001
MAXT_SCALE_SERIES = 2_000
MAXT_TOTAL = 10_000
MODEL_NULL_TOTAL = 4_000
NULL_VALIDATION_TOTAL = 5_000
POSITIVE_PER_CELL = 500
ROBUSTNESS_PER_SCENARIO = 500


def _load_shards(input_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payloads: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    paths = sorted(input_dir.rglob("*.json"))
    if not paths:
        raise ValueError(f"no shard JSON files found under {input_dir}")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("gate") != "2-3P-3" or "rows" not in payload:
            continue
        if payload.get("model_version") != DEFAULT_CONFIG.model_version:
            raise ValueError(f"model version mismatch in {path}")
        if payload.get("research_only") is not True or payload.get("public_release_allowed") is not False:
            raise ValueError(f"research safety contract failed in {path}")
        payloads.append(payload)
        rows.extend(payload["rows"])
    if not payloads:
        raise ValueError("no valid shard payloads found")
    shard_indexes = [int(payload["shard_index"]) for payload in payloads]
    if len(shard_indexes) != len(set(shard_indexes)):
        raise ValueError("duplicate shard indexes")
    expected_shards = int(payloads[0]["shard_count"])
    if set(shard_indexes) != set(range(expected_shards)):
        raise ValueError(f"incomplete shards: got {sorted(shard_indexes)}, expected 0..{expected_shards - 1}")
    identities = [(row["category"], row["scenario"], int(row["seed"])) for row in rows]
    if len(identities) != len(set(identities)):
        raise ValueError("duplicate validation rows")
    return payloads, rows


def _mean_sd(vectors: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    width = len(vectors[0])
    means = tuple(fmean(float(row[index]) for row in vectors) for index in range(width))
    variances = tuple(
        fmean((float(row[index]) - means[index]) ** 2 for row in vectors)
        for index in range(width)
    )
    sds = tuple(max(math.sqrt(value), 1e-12) for value in variances)
    return means, sds


def _maxt_score(values: Sequence[float], means: Sequence[float], sds: Sequence[float]) -> float:
    return max((float(value) - means[index]) / sds[index] for index, value in enumerate(values))


def _empirical_upper_p(sorted_calibration: Sequence[float], observed: float) -> float:
    first_ge = bisect.bisect_left(sorted_calibration, observed)
    exceedances = len(sorted_calibration) - first_ge
    return (1.0 + exceedances) / (len(sorted_calibration) + 1.0)


def _wilson_upper(successes: int, trials: int, z: float = 1.6448536269514722) -> float:
    if trials <= 0:
        return 1.0
    p = successes / trials
    denominator = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denominator
    radius = z * math.sqrt(p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) / denominator
    return min(1.0, center + radius)


def _mean(rows: Sequence[Mapping[str, Any]], getter) -> float:
    return fmean(float(getter(row)) for row in rows) if rows else 0.0


def _strict_proxy(row: Mapping[str, Any], score_calibration: Sequence[float]) -> tuple[bool, float]:
    score = float(row["mean_delta_log_loss"]["M4"])
    p_value = _empirical_upper_p(score_calibration, score)
    decision = (
        p_value <= ALPHA
        and score > 0.0
        and float(row["mean_delta_brier"]["M4"]) >= 0.0
        and int(row["positive_macro_blocks"]["M4"]) >= 2
        and row.get("strict_winner") == "M4"
    )
    return decision, p_value


def _m3_active(
    row: Mapping[str, Any],
    means: Sequence[float],
    sds: Sequence[float],
    calibration_scores: Sequence[float],
) -> tuple[bool, float | None]:
    values = row.get("m3_diagnostic_maxima")
    if values is None:
        return False, None
    score = _maxt_score(values, means, sds)
    p_value = _empirical_upper_p(calibration_scores, score)
    return p_value <= ALPHA, p_value


def _group_summary(
    rows: Sequence[dict[str, Any]],
    score_calibration: Sequence[float],
    maxt_means: Sequence[float],
    maxt_sds: Sequence[float],
    maxt_calibration: Sequence[float],
    *,
    require_direction: bool,
    require_m3: bool,
) -> dict[str, Any]:
    strict_count = 0
    proxy_count = 0
    direction_values: list[float] = []
    m3_count = 0
    p_values: list[float] = []
    for row in rows:
        proxy, p_value = _strict_proxy(row, score_calibration)
        proxy_count += int(proxy)
        p_values.append(p_value)
        direction = row.get("direction_accuracy")
        direction_ok = direction is not None and float(direction) >= 0.80
        if direction is not None:
            direction_values.append(float(direction))
        m3, _ = _m3_active(row, maxt_means, maxt_sds, maxt_calibration)
        m3_count += int(m3)
        strict_count += int(proxy and (direction_ok if require_direction else True) and (m3 if require_m3 else True))

    strength_values = [
        fmean(float(value) for _, value in row.get("m4_strength_by_origin", []))
        for row in rows
        if row.get("m4_strength_by_origin")
    ]
    return_delays = [int(row["return_delay"]) for row in rows if row.get("return_delay") is not None]
    adaptation_delays = [int(row["adaptation_delay"]) for row in rows if row.get("adaptation_delay") is not None]
    return {
        "trials": len(rows),
        "strict_detection_count": strict_count,
        "strict_detection_rate": strict_count / len(rows) if rows else 0.0,
        "proxy_detection_rate": proxy_count / len(rows) if rows else 0.0,
        "m3_activation_rate": m3_count / len(rows) if rows else 0.0,
        "mean_delta_log_loss_m4": _mean(rows, lambda row: row["mean_delta_log_loss"]["M4"]),
        "mean_delta_brier_m4": _mean(rows, lambda row: row["mean_delta_brier"]["M4"]),
        "m4_strict_winner_rate": (
            sum(row.get("strict_winner") == "M4" for row in rows) / len(rows) if rows else 0.0
        ),
        "mean_positive_macro_blocks_m4": _mean(rows, lambda row: row["positive_macro_blocks"]["M4"]),
        "mean_direction_accuracy": fmean(direction_values) if direction_values else None,
        "mean_calibration_error_m4": _mean(rows, lambda row: row["calibration_error_m4"]),
        "median_empirical_p": median(p_values) if p_values else None,
        "mean_m4_strength": fmean(strength_values) if strength_values else 0.0,
        "return_within_208_rate": (
            sum(value <= 208 for value in return_delays) / len(rows) if rows else None
        ),
        "mean_return_delay": fmean(return_delays) if return_delays else None,
        "adapt_within_208_rate": (
            sum(value <= 208 for value in adaptation_delays) / len(rows) if rows else None
        ),
        "mean_adaptation_delay": fmean(adaptation_delays) if adaptation_delays else None,
    }


def _critical_value(sorted_values: Sequence[float], alpha: float) -> float:
    allowed_exceedances = max(0, math.floor(alpha * (len(sorted_values) + 1) - 1.0))
    index = max(0, len(sorted_values) - allowed_exceedances - 1)
    return float(sorted_values[index])


def aggregate(input_dir: Path) -> dict[str, Any]:
    payloads, rows = _load_shards(input_dir)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_category[str(row["category"])].append(row)

    expected_counts = {
        "maxt_calibration": MAXT_TOTAL,
        "model_null_calibration": MODEL_NULL_TOTAL,
        "independent_null_validation": NULL_VALIDATION_TOTAL,
        "positive_control": len(EFFECT_SIZES) * 6 * POSITIVE_PER_CELL,
        "robustness": len(robustness_scenarios()) * ROBUSTNESS_PER_SCENARIO,
    }
    actual_counts = {name: len(by_category.get(name, [])) for name in expected_counts}
    if actual_counts != expected_counts:
        raise ValueError(f"row count mismatch: actual={actual_counts}, expected={expected_counts}")

    maxt_rows = sorted(by_category["maxt_calibration"], key=lambda row: int(row["seed"]))
    scale_vectors = [row["m3_diagnostic_maxima"] for row in maxt_rows[:MAXT_SCALE_SERIES]]
    threshold_vectors = [row["m3_diagnostic_maxima"] for row in maxt_rows[MAXT_SCALE_SERIES:]]
    maxt_means, maxt_sds = _mean_sd(scale_vectors)
    maxt_calibration_scores = sorted(
        _maxt_score(values, maxt_means, maxt_sds) for values in threshold_vectors
    )

    model_null_rows = sorted(by_category["model_null_calibration"], key=lambda row: int(row["seed"]))
    score_calibration = sorted(float(row["mean_delta_log_loss"]["M4"]) for row in model_null_rows)

    null_rows = by_category["independent_null_validation"]
    proxy_count = 0
    m3_count = 0
    null_by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in null_rows:
        proxy, _ = _strict_proxy(row, score_calibration)
        m3, _ = _m3_active(row, maxt_means, maxt_sds, maxt_calibration_scores)
        proxy_count += int(proxy)
        m3_count += int(m3)
        null_by_scenario[str(row["scenario"])].append(row)

    null_report = {
        "trials": len(null_rows),
        "proxy_false_activation_count": proxy_count,
        "proxy_false_activation_rate": proxy_count / len(null_rows),
        "proxy_one_sided_95_upper": _wilson_upper(proxy_count, len(null_rows)),
        "m3_false_activation_count": m3_count,
        "m3_false_activation_rate": m3_count / len(null_rows),
        "m3_one_sided_95_upper": _wilson_upper(m3_count, len(null_rows)),
        "by_scenario": {},
    }
    for scenario, scenario_rows in sorted(null_by_scenario.items()):
        scenario_proxy = sum(_strict_proxy(row, score_calibration)[0] for row in scenario_rows)
        scenario_m3 = sum(
            _m3_active(row, maxt_means, maxt_sds, maxt_calibration_scores)[0]
            for row in scenario_rows
        )
        null_report["by_scenario"][scenario] = {
            "trials": len(scenario_rows),
            "proxy_false_activation_rate": scenario_proxy / len(scenario_rows),
            "m3_false_activation_rate": scenario_m3 / len(scenario_rows),
            "mean_delta_log_loss_m4": _mean(
                scenario_rows, lambda row: row["mean_delta_log_loss"]["M4"]
            ),
            "mean_m4_strength": _mean(
                scenario_rows,
                lambda row: fmean(value for _, value in row["m4_strength_by_origin"]),
            ),
        }

    positive_rows: dict[tuple[str, float], list[dict[str, Any]]] = defaultdict(list)
    for row in by_category["positive_control"]:
        positive_rows[(str(row["scenario"]), float(row["effect_size"]))].append(row)
    positive_report: dict[str, dict[str, Any]] = defaultdict(dict)
    for (scenario, effect), scenario_rows in sorted(positive_rows.items()):
        positive_report[scenario][f"{effect:.2f}"] = _group_summary(
            scenario_rows,
            score_calibration,
            maxt_means,
            maxt_sds,
            maxt_calibration_scores,
            require_direction=True,
            require_m3=scenario == "p4_regime_reversal",
        )

    robustness_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in by_category["robustness"]:
        robustness_rows[str(row["scenario"])].append(row)
    robustness_report = {
        scenario: _group_summary(
            scenario_rows,
            score_calibration,
            maxt_means,
            maxt_sds,
            maxt_calibration_scores,
            require_direction=scenario != "r_pretest_independent",
            require_m3=scenario == "r_direction_reversal",
        )
        for scenario, scenario_rows in sorted(robustness_rows.items())
    }

    missing_rates = [
        robustness_report["r_missing_10"]["strict_detection_rate"],
        robustness_report["r_missing_30"]["strict_detection_rate"],
        robustness_report["r_missing_50"]["strict_detection_rate"],
    ]
    missing_strengths = [
        robustness_report["r_missing_10"]["mean_m4_strength"],
        robustness_report["r_missing_30"]["mean_m4_strength"],
        robustness_report["r_missing_50"]["mean_m4_strength"],
    ]
    missingness_monotone = all(
        missing_rates[index] + 1e-12 >= missing_rates[index + 1]
        and missing_strengths[index] + 1e-12 >= missing_strengths[index + 1]
        for index in range(2)
    )

    preregistered_checks: dict[str, bool] = {
        "null_proxy_rate_le_0_001": null_report["proxy_false_activation_rate"] <= 0.001,
        "null_proxy_upper_le_0_002": null_report["proxy_one_sided_95_upper"] <= 0.002,
        "null_m3_rate_le_0_001": null_report["m3_false_activation_rate"] <= 0.001,
        "irrelevant_metadata_not_activated": (
            null_report["by_scenario"]["n1_irrelevant_metadata"]["proxy_false_activation_rate"] <= 0.001
            and null_report["by_scenario"]["n1_irrelevant_metadata"]["mean_delta_log_loss_m4"] <= 0.0
        ),
        "missingness_does_not_increase_confidence": missingness_monotone,
        "independent_pretest_not_activated": (
            robustness_report["r_pretest_independent"]["proxy_detection_rate"] <= 0.001
        ),
        "post_draw_error_not_activated": (
            robustness_report["r_observed_after_draw"]["proxy_detection_rate"] <= 0.001
        ),
        "temporary_signal_returns_within_208": (
            positive_report["p5_temporary_environment"]["1.25"]["return_within_208_rate"] is not None
            and positive_report["p5_temporary_environment"]["1.25"]["return_within_208_rate"] >= 0.80
        ),
        "direction_reversal_adapts_within_208": (
            robustness_report["r_direction_reversal"]["adapt_within_208_rate"] is not None
            and robustness_report["r_direction_reversal"]["adapt_within_208_rate"] >= 0.80
        ),
    }

    for spec in positive_scenarios(1.25):
        summary = positive_report[spec.name]["1.25"]
        preregistered_checks[f"{spec.name}_lift_1_25_strict_detection_ge_0_80"] = (
            summary["strict_detection_rate"] >= 0.80
        )
        preregistered_checks[f"{spec.name}_lift_1_25_log_loss_positive"] = (
            summary["mean_delta_log_loss_m4"] > 0.0
        )
        preregistered_checks[f"{spec.name}_lift_1_25_brier_nonnegative"] = (
            summary["mean_delta_brier_m4"] >= 0.0
        )
        preregistered_checks[f"{spec.name}_lift_1_25_direction_ge_0_80"] = (
            summary["mean_direction_accuracy"] is not None
            and summary["mean_direction_accuracy"] >= 0.80
        )
    preregistered_checks["p4_regime_reversal_m3_activation_ge_0_80"] = (
        positive_report["p4_regime_reversal"]["1.25"]["m3_activation_rate"] >= 0.80
    )

    passed = all(preregistered_checks.values())
    shard_hashes = sorted(str(payload["shard_hash"]) for payload in payloads)
    report: dict[str, Any] = {
        "gate": "2-3P-3",
        "decision": "PASS" if passed else "NOT PASSED",
        "model_version": DEFAULT_CONFIG.model_version,
        "feature_contract_version": DEFAULT_CONFIG.feature_contract_version,
        "physical_data_schema_version": DEFAULT_CONFIG.physical_data_schema_version,
        "research_only": True,
        "public_release_allowed": False,
        "actual_counts": actual_counts,
        "calibration": {
            "alpha": ALPHA,
            "maxt_total_series": MAXT_TOTAL,
            "maxt_scale_series": MAXT_SCALE_SERIES,
            "maxt_threshold_series": MAXT_TOTAL - MAXT_SCALE_SERIES,
            "maxt_means": list(maxt_means),
            "maxt_sds": list(maxt_sds),
            "maxt_critical_score": _critical_value(maxt_calibration_scores, ALPHA),
            "maxt_minimum_empirical_p": 1.0 / (len(maxt_calibration_scores) + 1.0),
            "model_null_series": MODEL_NULL_TOTAL,
            "m4_score_critical_value": _critical_value(score_calibration, ALPHA),
            "m4_minimum_empirical_p": 1.0 / (len(score_calibration) + 1.0),
        },
        "null_validation": null_report,
        "positive_controls": positive_report,
        "robustness": robustness_report,
        "preregistered_checks": preregistered_checks,
        "failed_checks": sorted(name for name, value in preregistered_checks.items() if not value),
        "shard_hashes": shard_hashes,
        "interpretation_limits": [
            "Synthetic validation does not establish predictability in official lottery draws.",
            "The blockwise baselines are frozen validation comparators, not replacements for the production M1-M3 ensemble.",
            "Real metadata collection and historical walk-forward remain blocked unless this gate passes.",
            "Public future-number release remains prohibited regardless of this synthetic result.",
        ],
    }
    report["report_hash"] = sha256_value(report)
    return report


def markdown_report(report: Mapping[str, Any]) -> str:
    null = report["null_validation"]
    lines = [
        "# Gate 2-3P-3 Full Synthetic Validation",
        "",
        f"- Decision: **{report['decision']}**",
        f"- Model: `{report['model_version']}`",
        f"- Report hash: `{report['report_hash']}`",
        "- Research only: `true`",
        "- Public release allowed: `false`",
        "",
        "## Experiment size",
        "",
    ]
    for name, count in report["actual_counts"].items():
        lines.append(f"- {name}: {count:,}")
    lines.extend(
        [
            "",
            "## Independent null validation",
            "",
            f"- Proxy false activation: {null['proxy_false_activation_count']}/{null['trials']} ({null['proxy_false_activation_rate']:.6%})",
            f"- Proxy one-sided 95% upper: {null['proxy_one_sided_95_upper']:.6%}",
            f"- M3 false activation: {null['m3_false_activation_count']}/{null['trials']} ({null['m3_false_activation_rate']:.6%})",
            "",
            "## Positive controls at lift 1.25",
            "",
            "| Scenario | Strict detection | Mean Δ Log Loss | Mean Δ Brier | Direction | M3 activation |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for scenario, values in report["positive_controls"].items():
        summary = values["1.25"]
        direction = summary["mean_direction_accuracy"]
        lines.append(
            f"| {scenario} | {summary['strict_detection_rate']:.1%} | "
            f"{summary['mean_delta_log_loss_m4']:.6f} | {summary['mean_delta_brier_m4']:.8f} | "
            f"{('n/a' if direction is None else f'{direction:.1%}')} | {summary['m3_activation_rate']:.1%} |"
        )
    lines.extend(["", "## Preregistered checks", ""])
    for name, value in report["preregistered_checks"].items():
        lines.append(f"- {'PASS' if value else 'FAIL'} — `{name}`")
    lines.extend(["", "## Interpretation", ""])
    if report["decision"] == "PASS":
        lines.append("The synthetic gate passed. This permits only the real-metadata feasibility pilot; it does not establish real lottery predictability.")
    else:
        lines.append("The synthetic gate did not pass. Real-data walk-forward, public predictions, and mobile product activation remain blocked.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    report = aggregate(Path(args.input_dir))
    json_path = Path(args.json_output)
    markdown_path = Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({"decision": report["decision"], "report_hash": report["report_hash"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
