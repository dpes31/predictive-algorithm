# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-r3m-feasibility-spec`  
기준 브랜치: `feature/gate2p-r3-dev-grid`  
관련 이슈: #26  
현재 Draft PR: #27

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-1 | 승인 완료 | 100% |
| Gate 2-3P-2 | 완료 | 100% |
| Gate 2-3P-3 | NOT PASSED | 100% |
| Gate 2-3P-R1 | 승인 완료 | 100% |
| Gate 2-3P-R2 | 구현 완료·CI 통과 | 100% |
| Gate 2-3P-R3 | **완료·NO_ELIGIBLE_CONFIG** | 100% |
| Gate 2-3P-R4 | **BLOCKED** | 0% |
| Gate 2-3P-R3M-1 | **수학적 분석·교정 명세 완료, 승인 대기** | 100% |
| Gate 2-3P-R3M-2 | 미승인·미구현 | 0% |
| 실제 메타데이터 파일럿 | 차단 | 0% |
| 실제 Walk-forward | 차단 | 0% |
| 모바일 MVP | 차단 | 0% |

## R3 잠금 결과

- model `4.0.0-research`
- feature contract `3.0.0`
- mandatory scenario: P4 regime reversal
- lift: 1.25
- deterministic series: 200
- draw count: 1230
- M3 activation: `0 / 200 = 0%`
- maximum e-value: `1.2128703085422197`
- activation threshold: `1000`
- eligible `k_m3`: 없음
- selected config: `null`
- pruned combined configurations: `81 / 81`
- decision: `NO_ELIGIBLE_CONFIG`
- implementation commit: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run: `28489870505` — success
- unit tests: `87 PASS`
- DEV report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`
- CAL executed: false
- SEALED executed: false

R3 실패 결과와 hash는 영구 보존한다.

## R3M 수학적 분석

P4 lift 1.25 exact 6-of-45 대안에서:

```text
oracle KL = 0.024294585890841103 nats/draw
208 × KL = 5.053273865294949
log(1000) = 6.907755278982137
```

Favored group과 change point를 아는 oracle도 208회 기대 evidence가 threshold 1000에 미달한다.

정규근사 기준 80% power 필요기간:

- single oracle: 약 448회
- 2-way mixture: 약 483회
- 4-way mixture: 약 518회
- 8-way mixture: 약 552회
- 45-way mixture: 약 636회

기존 detector는 최대 약 `45 × 8 × 16 = 5,760` component를 평균해 추가 dilution이 발생했다.

판정:

```text
threshold 1000
+ evidence life 208
+ lift 1.25
+ 80% power
= incompatible
```

## 신규 5.0 제안

제안 모델: `5.0.0-research`

Threshold와 R3 실패결과를 유지하며 시간계약을 분리한다.

```text
pre-activation evidence horizon = 520 draws
post-activation active life = 208 draws
activation / deactivation = 1000 / 100
```

구조:

- exact 6-of-45 group likelihood-ratio
- activation primary hypotheses 최대 4개
- 개별 번호·다중 lambda는 diagnostic-only
- past-only predict-then-bet group construction
- oracle feasibility gate 우선
- oracle 통과 후 predictable-group gate
- 이후에만 full M3 DEV
- M4 구조 변경 없음

## 고정 기준

- M0~M4 역할과 6개 번호 × 5세트 유지
- M3·M4 cap 각각 10%
- activation / deactivation `1000 / 100`
- false activation 0.1%
- one-sided 95% upper 0.2%
- lift 1.25 strict detection 80%
- lift 1.50 strict detection 95%
- 기존 실패 시나리오·seed 유지
- Pair-number interaction 비활성
- RESEARCH 최종분포 M0-only
- 208회 post-activation active life 유지

## 현재 차단

- `5.0.0-research` Python 구현
- 추가 DEV 탐색
- R4 CAL·SEALED
- threshold 완화 또는 실패 seed 제거
- 실제 데이터·모바일 UI·main 병합

## 다음 권고 단계

사용자 승인 후 Gate 2-3P-R3M-2에서 exact fixed-size group LR과 520-draw oracle detector만 구현한다. Oracle DEV PASS 전에는 predictable-group learner, full M3 grid, CAL, SEALED를 실행하지 않는다.
