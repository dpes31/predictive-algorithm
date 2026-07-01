# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/r3m3-predictable-group-engine`  
기준 브랜치: `feature/r3m3-predictable-group-spec`  
현재 Draft PR: #32

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-R3 | NO_ELIGIBLE_CONFIG | 100% |
| Gate 2-3P-R3M-2 | ORACLE_PASS | 100% |
| Gate 2-3P-R3M-3-1 | 승인 완료 | 100% |
| Gate 2-3P-R3M-3-2 | **PREDICTABLE_GROUP_FAIL** | 100% |
| full M3 DEV | BLOCKED | 0% |
| Gate 2-3P-R4 | BLOCKED | 0% |
| CAL·SEALED | BLOCKED | 0% |
| 실제 데이터·모바일 | BLOCKED | 0% |

## DEV-PG 결과

- availability `33.66%` — FAIL
- activation `1.35%` — FAIL
- median delay `421` — PASS
- direction `78.6839%` — FAIL
- direction trials `6,732` — FAIL
- mean delta Log Loss `-0.0029845604` — FAIL
- lower delta Log Loss `-0.0031943119` — FAIL
- mean delta Brier `-0.00001694195` — FAIL
- lower delta Brier `-0.00001808760` — FAIL
- null false activation `0.01%` — PASS
- null one-sided upper `0.04743%` — PASS

## 선택 분포

- size 6: `3,304`
- size 10: `1,969`
- size 15: `1,459`
- abstain: `13,268`

## 잠금

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests `105 PASS`
- artifact `8002526507`
- artifact digest `sha256:8ba3958b1dcd45dac6ee436b9911f39281138287cd212fc1591283f985d1c6b1`
- seed hash `5fa4ab0038468a38f7a06a41928752c1a444ba9a17eef64e10a2d3d64cc69038`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

## 판정

```text
R3M-3-2 = PREDICTABLE_GROUP_FAIL
Full M3 DEV = BLOCKED
R4 = BLOCKED
Final distribution = M0 only
```

Null 안전성은 통과했지만 과거 번호 이력 learner의 가용성, 검출력, 방향성과 예측효용이 실패했다. 결과를 본 뒤 고정 기준을 변경하지 않는다.

## 다음 단계

추가 Python 튜닝이 아니라 실패 원인 분석과 M3 중단 또는 M4 중심 전환을 위한 별도 명세가 필요하다.
