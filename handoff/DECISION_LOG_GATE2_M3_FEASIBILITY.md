# Gate 2 M3 Feasibility Decision Record

## D-023 — R3 NO_ELIGIBLE_CONFIG 및 R4 차단 승인

- 결정일: 2026-07-01
- 사용자 승인:
  - Gate 2-3P-R3 `NO_ELIGIBLE_CONFIG`
  - Gate 2-3P-R4 차단
  - threshold와 실패결과 보존
  - M3 수학적 양립 가능성 분석 및 신규 교정 명세 작성
- 기준 모델: `4.0.0-research`
- 기준 브랜치: `feature/gate2p-r3-dev-grid`
- 기준 잠금:
  - implementation commit `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
  - workflow `28489870505`
  - report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
  - lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

## D-024 — 수학적 비양립 판정

P4 lift 1.25 exact 6-of-45 대안에서 oracle KL은 회차당 다음이다.

```text
0.024294585890841103 nats
```

208회 기대 log evidence:

```text
208 × KL = 5.053273865294949
```

Activation threshold:

```text
log(1000) = 6.907755278982137
```

따라서 다음 네 조건은 동시에 만족할 수 없다.

```text
threshold 1000
+ evidence life 208
+ lift 1.25
+ strict detection power 80%
```

이는 파라미터 grid 선택 문제가 아니라 정보량 한계와 mixture dilution의 구조적 문제로 판정한다.

## D-025 — 5.0 교정 방향

제안 모델: `5.0.0-research`

유지:

- threshold `1000`
- deactivation `100`
- R3 실패결과와 seed
- post-activation active life `208`
- M3 cap `10%`
- RESEARCH M0-only
- 6개 번호 × 5세트

변경 제안:

```text
pre-activation evidence horizon = 520 draws
post-activation active life = 208 draws
```

구조 변경:

1. 번호별 Bernoulli betting mixture를 exact 6-of-45 group LR로 교체
2. activation primary hypotheses를 최대 4개로 제한
3. 나머지 번호·lambda 탐색은 diagnostic-only
4. past-only predict-then-bet group construction
5. oracle feasibility gate 선행
6. oracle 통과 후 predictable-group gate
7. 이후에만 full M3 DEV 허용

## D-026 — 현재 차단과 승인 상태

완료:

- 수학적 feasibility report
- 신규 M3 correction specification
- AGENTS 및 handoff 동기화
- Issue #26
- Draft PR #27

미승인:

- `5.0.0-research` 모델 채택
- Python 구현
- oracle DEV 실행
- predictable-group 구현
- full M3 DEV
- CAL
- SEALED

현재 판정:

```text
Gate 2-3P-R3M-1 = SPEC COMPLETE / APPROVAL PENDING
Gate 2-3P-R4 = BLOCKED
Final distribution = M0 only
```

## 다음 승인 대상

사용자가 다음을 명시적으로 승인한 뒤에만 Gate 2-3P-R3M-2로 이동한다.

```text
Gate 2-3P-R3M-1 교정 명세와 모델 버전 5.0.0-research 승인
```

승인 후에도 첫 구현 범위는 exact fixed-size group LR과 520-draw oracle feasibility engine으로 제한한다. Oracle PASS 전에는 후속 group learner, full grid, CAL, SEALED를 진행하지 않는다.
