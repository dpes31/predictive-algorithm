# Project Handoff

최종 갱신일: 2026-07-03  
현재 작업: **Algorithm Integration Gate A4 평가 실패 evidence 고정**  
현재 브랜치: `feature/algorithm-integration-a4-evaluation`  
기준 브랜치: `feature/product-p1-release-candidate`  
기준 커밋: `09e6b19f0e351e59982e6167335cbe23fada83b0`  
계약: `research-ensemble-evaluation-implementation-1.0.0`  
Draft PR: `#51`

## 현재 상태

```text
P1 = P1_ASSEMBLED
A1 = A1_SPEC_COMPLETE / MERGED
A2 = A2_IMPLEMENTATION_PASS / MERGED
A3 = A3_SPEC_COMPLETE / MERGED
A4 = A4_EVALUATION_FAIL / DRAFT PR #51

CONTROL_M0 = default and rollback
RESEARCH_ENSEMBLE = implemented / evaluated / failed vs M0
actual user hypothesis entries = 0
actual physical entries = 0
next Gate = NOT AUTHORIZED
main merge = NOT PERFORMED
```

## A4 검증 기준점

- evaluated commit: `ee10a16b8c6259948bc8b2ed77d555452b9ff3a9`
- workflow: `28653030201` / run #37
- Python 3.11 two repeats: PASS
- Python 3.12 two repeats: PASS
- cross-runtime canonical hash: PASS
- E1~E16 integrity: PASS
- canonical result hash: `c886f07c2fa7fd01cfa49d2d0e4174d6c9802ac0856aff2fd13d54da44fde3b7`

## A4 판정

```text
mean joint log-score delta = -0.0541462386
one-sided 95% lower bound = -0.0739087181
p-value = 1.0
mean marginal Brier gain = -0.000294872446
positive quarters = 0 / 4
cumulative delta = -47.5945437
result = A4_EVALUATION_FAIL
```

구조·누출·재현성 검증은 통과했지만 M0 대비 세 필수 성능기준을 모두 통과하지 못했다.

## 필수 읽기

1. `AGENTS.md`
2. `handoff/ALGORITHM_INTEGRATION_A4_HANDOFF.md`
3. `docs/ALGORITHM_INTEGRATION_A3_EVALUATION_SPEC.md`
4. `docs/ALGORITHM_INTEGRATION_A3_METRICS.md`
5. `docs/ALGORITHM_INTEGRATION_A3_ACCEPTANCE.md`
6. `reports/ALGORITHM_INTEGRATION_A4_STATUS.md`
7. `reports/algorithm_integration_a4_evaluation.json`
8. `reports/algorithm_integration_a4_evaluation_lock.json`
9. `release/algorithm_integration_a4_rollback_manifest.json`
10. Product P1·A1·A2·A3 report, lock, rollback
11. 기존 failure evidence와 workflow history

## 금지 범위

- 결과를 보고 parameter·window·threshold·weight·target subset 변경
- A4 재평가 또는 후속 알고리즘 Gate 시작
- 실제 hypothesis·physical entry 활성화
- hyperparameter 탐색
- 외부접속·새 데이터 수집
- HTML·CAL·SEALED·모바일
- `main` 병합
- 사용자 승인 없는 PR #51 병합

실패 run과 모든 evidence를 보존하고 `CONTROL_M0`를 기본·rollback으로 유지한다.
