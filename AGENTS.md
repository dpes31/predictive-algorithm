# AGENTS.md

모든 작업 전 이 문서와 실제 branch·commit·report·lock 상태를 대조한다.

## 공통 원칙

- 미래 데이터 누출 금지
- 동일 data/version/config/registry에서 재현 가능한 결과
- 실패 결과, hash, report, lock, rollback, workflow history 보존
- 사용자 승인 전 다음 Gate 진행 금지
- `main` 직접 작업·병합 금지
- 외부 결과 사이트 접속, 외부기관 문의, 새 출처 탐색 금지
- 사용자가 제공하지 않은 물리변수 수집·추정 금지

## 현재 기준점

```text
current branch = feature/algorithm-integration-a4-evaluation
base branch = feature/product-p1-release-candidate
base commit = 09e6b19f0e351e59982e6167335cbe23fada83b0
Draft PR = #51

P1 = P1_ASSEMBLED
A1 = A1_SPEC_COMPLETE / MERGED
A2 = A2_IMPLEMENTATION_PASS / MERGED
A3 = A3_SPEC_COMPLETE / MERGED
A4 = A4_EVALUATION_FAIL / DRAFT PR

A4 implementation contract = research-ensemble-evaluation-implementation-1.0.0
A4 evaluated commit = ee10a16b8c6259948bc8b2ed77d555452b9ff3a9
A4 workflow = 28653030201 / run #37
A4 canonical result hash = c886f07c2fa7fd01cfa49d2d0e4174d6c9802ac0856aff2fd13d54da44fde3b7
rollback mode = CONTROL_M0
next Gate authorized = false
```

## 필수 읽기

1. `AGENTS.md`
2. `handoff/PROJECT_HANDOFF.md`
3. `handoff/ALGORITHM_INTEGRATION_A4_HANDOFF.md`
4. `docs/ALGORITHM_INTEGRATION_A3_EVALUATION_SPEC.md`
5. `docs/ALGORITHM_INTEGRATION_A3_METRICS.md`
6. `docs/ALGORITHM_INTEGRATION_A3_ACCEPTANCE.md`
7. `reports/algorithm_integration_a3_spec_report.json`
8. `reports/algorithm_integration_a3_spec_lock.json`
9. `reports/ALGORITHM_INTEGRATION_A4_STATUS.md`
10. `reports/algorithm_integration_a4_evaluation.json`
11. `reports/algorithm_integration_a4_evaluation_lock.json`
12. `release/algorithm_integration_a4_rollback_manifest.json`
13. Product P1·A1·A2 report, lock, rollback
14. 기존 실패 report·lock과 workflow history

## 잠긴 제품 기준

```text
data range = 1..1230
data version = draws-2026.06.27-r1
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
officially locked = false

default runner = python -m product.run_prediction
final distribution = M0_ONLY
M0=1.0, M1=M2=M3=M4=0.0
statistical_edge=false
research_only=true
public_release_allowed=false
```

`CONTROL_M0`는 계속 기본·rollback 경로다. `RESEARCH_ENSEMBLE`은 연구 전용이며 A4에서 M0 대비 성능 기준을 통과하지 못했다.

## A4 고정 평가 결과

```text
confirmatory targets = 352..1230
confirmatory target count = 879
lane count = 10
metric rows = 8790
Python 3.11 two repeats = PASS
Python 3.12 two repeats = PASS
cross-runtime reproducibility = PASS
E1..E16 integrity = PASS

mean joint log-score delta = -0.0541462386
one-sided 95% lower bound = -0.0739087181
p-value = 1.0
mean marginal Brier gain = -0.000294872446
positive quarters = 0 / 4
cumulative delta = -47.5945437
```

판정:

```text
A4_EVALUATION_FAIL
```

실패 사유:

- `primary_joint_log_score_criterion`
- `marginal_brier_guardrail`
- `temporal_stability_guardrail`

결과를 보고 parameter, window, threshold, weight, target subset을 변경하지 않는다.

## 보존 대상

- workflow runs `28652065811`, `28652201671`, `28652641626`, `28652841841`, `28653030201`
- Product P1, A1, A2, A3 report·lock·hash·rollback
- 기존 M3/M4 및 predictable-group 실패 evidence
- A4 실패 report·lock·rollback

삭제, 재분류, force push, history rewrite를 금지한다.

## 현재 금지사항

사용자 별도 승인 전 다음을 수행하지 않는다.

- A4 parameter 수정 또는 재평가
- 새로운 알고리즘 Gate 시작
- 실제 hypothesis·physical entry 활성화
- hyperparameter 탐색
- 외부접속 또는 신규 데이터 수집
- canonical data 수정
- HTML·CAL·SEALED·모바일
- `main` 병합
- Draft PR #51 병합

## 현재 승인 경계

A4 실패 판정 이후 다음 단계는 승인되지 않았다. 현재 작업은 Draft PR #51과 실패 evidence를 보존하고 결과만 보고하는 것이다.
