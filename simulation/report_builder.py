"""Markdown reporting for Gate 2-3 synthetic validation."""

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
    pair = null_validation["pair_diagnostic_false_activation"]

    lines = [
        "# Gate 2-3 합성 검증 결과",
        "",
        "## 1. 결론",
        "",
        "이 보고서는 알고리즘이 **무작위 데이터에서 허위 신호를 얼마나 만드는지**, 그리고 **의도적으로 심은 편향을 탐지할 수 있는지** 평가합니다.",
        "실제 로또 데이터의 예측력은 아직 평가하지 않았습니다.",
        "",
        "## 2. 실험 규모",
        "",
        f"- 균등 null 캘리브레이션: {experiment['null_calibration_series']}개 시계열",
        f"- 독립 null 검증: {experiment['null_validation_series']}개 시계열",
        f"- positive-control 반복: 시나리오당 {experiment['positive_series_per_scenario']}개",
        f"- 시계열 길이: {experiment['draw_count']}회",
        "",
        "## 3. 균등 무작위 오탐",
        "",
        "| 검사 | 관측 오탐률 | 95% 단측 상한 | 0.1% 기준 점추정 통과 | 0.1% 상한 통과 |",
        "|---|---:|---:|---:|---:|",
        f"| 합성 Gate proxy | {_percent(proxy['rate'])} | {_percent(proxy['one_sided_95_upper'])} | {'예' if proxy['point_estimate_le_0_001'] else '아니오'} | {'예' if proxy['upper_bound_le_0_001'] else '아니오'} |",
        f"| M3 변화진단 | {_percent(m3['rate'])} | {_percent(m3['one_sided_95_upper'])} | {'예' if m3['point_estimate_le_0_001'] else '아니오'} | {'예' if m3['upper_bound_le_0_001'] else '아니오'} |",
        f"| 번호쌍 진단 | {_percent(pair['rate'])} | {_percent(pair['one_sided_95_upper'])} | {'예' if pair['point_estimate_le_0_001'] else '아니오'} | {'예' if pair['upper_bound_le_0_001'] else '아니오'} |",
        "",
        "관측 오탐이 0건이어도 1,000개 시계열만으로 95% 상한이 0.1% 이하라고 확정할 수 없습니다.",
        "",
        "## 4. Positive controls",
        "",
        "| 시나리오 | 효과크기 | 기대모형 | 방향 일치율 | Proxy 탐지율 | M3 탐지율 | Pair 탐지율 |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for name, result in positives.items():
        win_rate = result.get("matched_model_win_rate")
        lines.append(
            f"| {name} | {result['effect_size']} | {result['expected_model']} | {_percent(win_rate)} | {_percent(result.get('proxy_detection_rate'))} | {_percent(result.get('m3_activation_rate'))} | {_percent(result.get('pair_activation_rate'))} |"
        )

    lines.extend(
        [
            "",
            "## 5. 최소 탐지 가능 효과",
            "",
            f"- 고정 번호 상대가중치(80% power): {minimum['fixed_number_relative_lift_at_80pct_power']}",
            f"- 번호쌍 factor(80% power): {minimum['pair_factor_at_80pct_power']}",
            "",
            "`None`은 사전지정한 효과크기 범위에서 80% 탐지력을 확보하지 못했다는 뜻입니다.",
            "",
            "## 6. 해석 제한",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["interpretation_limits"])
    lines.extend(
        [
            "",
            "## 7. 다음 단계",
            "",
            "Gate 2-3을 승인한 뒤에만 1~1230회 실제 데이터의 300~1230회 Walk-forward를 Gate 2-4에서 실행합니다.",
            "",
            f"Report hash: `{report['report_hash']}`",
            "",
        ]
    )
    return "\n".join(lines)
