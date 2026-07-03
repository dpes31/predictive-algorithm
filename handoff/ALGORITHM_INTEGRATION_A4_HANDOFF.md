# Algorithm Integration Gate A4 Handoff

## 상태

- Branch: `feature/algorithm-integration-a4-evaluation`
- Base commit: `09e6b19f0e351e59982e6167335cbe23fada83b0`
- Contract: `research-ensemble-evaluation-implementation-1.0.0`
- Draft PR: `#51`
- Evaluated commit: `ee10a16b8c6259948bc8b2ed77d555452b9ff3a9`
- Workflow: `28653030201` (#37)
- Result: `A4_EVALUATION_FAIL`

## 검증 결과

```text
confirmatory targets 352..1230 = 879
10 lanes / 8790 metric rows = PASS
future-data cutoff = PASS
CONTROL_M0 regression = PASS
empty-registry equivalence = PASS
Python 3.11 two repeats = PASS
Python 3.12 two repeats = PASS
cross-runtime canonical hash = PASS
E1..E16 integrity = PASS
```

## 성능 결과

```text
mean joint log-score delta = -0.0541462386
one-sided 95% lower bound = -0.0739087181
p-value = 1.0
mean marginal Brier gain = -0.000294872446
positive quarters = 0 / 4
cumulative delta = -47.5945437
```

실패 사유:

- `primary_joint_log_score_criterion`
- `marginal_brier_guardrail`
- `temporal_stability_guardrail`

## Evidence

- `reports/ALGORITHM_INTEGRATION_A4_STATUS.md`
- `reports/algorithm_integration_a4_evaluation.json`
- `reports/algorithm_integration_a4_evaluation_lock.json`
- `release/algorithm_integration_a4_rollback_manifest.json`
- canonical result hash: `c886f07c2fa7fd01cfa49d2d0e4174d6c9802ac0856aff2fd13d54da44fde3b7`
- final decision hash: `fdccc0fa50e8d81a76cd827c20a0702362f61468e9a2ed665288fd144b8e40d3`

실패 run과 모든 hash를 보존한다. 결과를 보고 parameter, window, threshold, weight 또는 target subset을 변경하지 않는다. `CONTROL_M0`를 기본·rollback 경로로 유지한다.

실제 hypothesis·physical entry 활성화, 외부접속, HTML, CAL, SEALED, 모바일 및 `main` 병합은 수행하지 않았다.

A4 이후의 추가 Gate는 승인되지 않았다. Draft PR #51은 사용자 별도 승인 전 병합하지 않는다.
