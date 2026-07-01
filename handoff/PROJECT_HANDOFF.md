# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R3M-3-2 PREDICTABLE_GROUP_FAIL**  
현재 브랜치: `feature/r3m3-predictable-group-engine`  
기준 브랜치: `feature/r3m3-predictable-group-spec`  
현재 Draft PR: #32

## 목적

로또 6/45의 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## Gate 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R3M-2: `ORACLE_PASS`
- Gate 2-3P-R3M-3-1: 승인 완료
- Gate 2-3P-R3M-3-2: **구현 완료·PREDICTABLE_GROUP_FAIL**
- full M3 DEV: `BLOCKED`
- Gate 2-3P-R4: `BLOCKED`
- CAL·SEALED·실제 데이터·모바일 MVP: `BLOCKED`

현재 모델은 `5.0.0-research`, contract는 `predictable-group-1.0.0`, Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`다.

## 이전 잠금 보존

R3 실패:

- implementation `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow `28489870505`
- report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

Oracle PASS:

- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

## R3M-3-2 구현

- fixed 520-draw past-only learner
- half-life 104 and prior strength 52
- 260 warmup plus five 52-draw folds
- deterministic group size 6, 10, 15 selection
- 52-draw group freeze
- exact group LR with lift 1.25
- DEV-PG and DEV-PG-CI namespace separation
- positive 2,000 and null 10,000 series
- 10,000 deterministic bootstrap resamples
- full unit tests and scope locks

## DEV-PG 결과

Positive:

- availability `33.66%` / 80% — FAIL
- activation `27/2000 = 1.35%` / 80% — FAIL
- median delay `421` / 520 — PASS
- direction `5297/6732 = 78.6839%` / 80% — FAIL
- direction trials `6732` / 16000 — FAIL
- mean delta Log Loss `-0.0029845604` — FAIL
- lower delta Log Loss `-0.0031943119` — FAIL
- mean delta Brier `-0.00001694195` — FAIL
- lower delta Brier `-0.00001808760` — FAIL

Selected blocks:

- size 6: 3,304
- size 10: 1,969
- size 15: 1,459
- abstain: 13,268

Null:

- false activation `1/10000 = 0.01%` — PASS
- one-sided 95% upper `0.04743%` — PASS

## 실행 잠금

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746` — success
- tests `105 PASS`
- artifact `8002526507`
- artifact digest `sha256:8ba3958b1dcd45dac6ee436b9911f39281138287cd212fc1591283f985d1c6b1`
- seed hash `5fa4ab0038468a38f7a06a41928752c1a444ba9a17eef64e10a2d3d64cc69038`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

## 판정

```text
Gate 2-3P-R3M-3-2 = PREDICTABLE_GROUP_FAIL
Full M3 DEV = BLOCKED
Gate 2-3P-R4 = BLOCKED
Final distribution = M0 only
```

Null 안전성은 유지됐지만 과거 번호 이력만으로 favored group을 충분히 예측하지 못했다. 사전 계약대로 기준이나 하이퍼파라미터를 변경하지 않는다.

## 현재 금지

- 추가 DEV 탐색 또는 튜닝
- full M3 detector 또는 grid
- R4 CAL·SEALED
- 실제 Walk-forward
- 사용자용 번호 생성
- 모바일 UI
- main 병합

## 다음 단계

다음 단계는 실패 원인 분석과 연구방향 결정 명세다. 과거 번호만 사용하는 M3 경로를 중단할지, 선행 물리·운영변수 M4를 중심으로 별도 Gate를 설계할지 사용자 승인이 필요하다.

## 링크

- Draft PR #32: `https://github.com/dpes31/predictive-algorithm/pull/32`
