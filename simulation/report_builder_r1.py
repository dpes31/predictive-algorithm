"""Markdown reporting for Gate 2-3R synthetic validation."""

from __future__ import annotations

from typing import Mapping


def _percent(value: object) -> str:
    if value is None:
        return "측정 불가"
    return f"{100.0 * float(value):.2f}%"


def build_markdown_report(report: Mapping[str, object]) -> str:
    experiment = report["experiment"]
    null_validation = report["null_validation"]
    positives = report["positive_controls"]
    minimum = report["minimum_detectable_effect"]

    proxy = null_validation["proxy_false_activation"]
    m3 = null_validation["m3_diagnostic_false_activation"]
    all_pair = null_validation["exploratory_pair_false_activation"]
    planted_pair = null_validation["target_pair_false_activation"]

    lines = [
        "# Gate 2-3R 합성 검증 결과",
        "",
        "## 1. 목적",
        "",
        "이 보고서는 보정된 2.1.0-research 엔진의 무작위 오탐과 사전지정 합성신호 탐지력을 평가합니다.",
        "실제 로또 데이터는 사용하지 않았습니다.",
        "",
        "## 2. 실험 규모",
        "",
        f"- 모델 버전: {report['model_version']}",
        f"- Temperature grid: {report['temperature_grid']}",
        f"- 균등 null 캘리브레이션: {experiment['null_calibration_series']}개 시계열",
        f"- 독립 null 검증: {experiment['null_validation_series']}개 시계열",
        f"- Positive-control 반복: 시나리오당 {experiment['positive_series_per_scenario']}개",
        f"- 시계열 길이: {experiment['draw_count']}회",
        "",
        "## 3. 균등 무작위 오탐",
        "",
        "| 검사 | 관측 오탐률 | 95% 단측 상한 | 0.1% 점추정 | 0.1% 상한 |",
        "|---|---:|---:|---:|---:|",
        f"| 합성 Gate proxy | {_percent(proxy['rate'])} | {_percent(proxy['one_sided_95_upper'])} | {'통과' if proxy['point_estimate_le_0_001'] else '미통과'} | {'통과' if proxy['upper_bound_le_0_001'] else '미통과'} |",
        f"| M3 raw 진단 | {_percent(m3['rate'])} | {_percent(m3['one_sided_95_upper'])} | {'통과' if m3['point_estimate_le_0_001'] else '미통과'} | {'통과' if m3['upper_bound_le_0_001'] else '미통과'} |",
        f"| 전체 번호쌍 탐색 진단 | {_percent(all_pair['rate'])} | {_percent(all_pair['one_sided_95_upper'])} | {'통과' if all_pair['point_estimate_le_0_001'] else '미통과'} | {'통과' if all_pair['upper_bound_le_0_001'] else '미통과'} |",
        f"| 사전지정 번호쌍 진단 | {_percent(planted_pair['rate'])} | {_percent(planted_pair['one_sided_95_upper'])} | {'통과' if planted_pair['point_estimate_le_0_001'] else '미통과'} | {'통과' if planted_pair['upper_bound_le_0_001'] else '미통과'} |",
        "",
        "## 4. Positive controls",
        "",
        "| 시나리오 | 효과크기 | 기대모형 | 엄격 탐지율 | 기대모형 양의 점수율 | Proxy 탐지율 | M3 활성률 | 사전지정 Pair 탐지율 |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for name, result in positives.items():
        lines.append(
            f"| {name} | {result['effect_size']} | {result['expected_model']} | {_percent(result.get('strict_detection_rate'))} | {_percent(result.get('matched_model_positive_score_rate'))} | {_percent(result.get('proxy_detection_rate'))} | {_percent(result.get('m3_activation_rate'))} | {_percent(result.get('target_pair_activation_rate'))} |"
        )

    lines.extend(
        [
            "",
            "## 5. 최소 탐지 가능 효과",
            "",
            f"- 고정 번호 상대가중치, 엄격 탐지력 80%: {minimum['fixed_number_relative_lift_at_80pct_power']}",
            f"- 사전지정 번호쌍 factor, 탐지력 80%: {minimum['pair_factor_at_80pct_power']}",
            "",
            "`None`은 사전지정 효과크기 범위에서 80% 탐지력을 확보하지 못했다는 뜻입니다.",
            "",
            "## 6. 해석 제한",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["interpretation_limits"])
    lines.extend(
        [
            "",
            "## 7. Gate 판단",
            "",
            "이 보고서의 수치는 자동 생성 결과이며, Gate 2-4 이동 여부는 사전지정 완료기준 검토 후 별도로 결정합니다.",
            "",
            f"Report hash: `{report['report_hash']}`",
            "",
        ]
    )
    return "\n".join(lines)
