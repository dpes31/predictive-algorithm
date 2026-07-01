# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R3M-1 수학적 적합성 분석·교정 명세 완료, 사용자 승인 대기**  
현재 브랜치: `feature/gate2p-r3m-feasibility-spec`  
기준 브랜치: `feature/gate2p-r3-dev-grid`  
관련 Issue: #26  
현재 Draft PR: #27

## 1. 목적

로또 6/45 다음 회차에 대해 정확히 6개 번호 조합 5세트를 출력하는 연구형 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## 2. Gate 상태

- Gate 2-3 / 2-3R: NOT PASSED
- Gate 2-3P-1: 승인 완료
- Gate 2-3P-2: 완료
- Gate 2-3P-3: NOT PASSED
- Gate 2-3P-R1: 승인 완료
- Gate 2-3P-R2: 구현 완료·CI 통과
- Gate 2-3P-R3: **완료·NO_ELIGIBLE_CONFIG**
- Gate 2-3P-R4: **BLOCKED**
- Gate 2-3P-R3M-1: **수학적 분석·신규 교정 명세 완료, 사용자 승인 대기**
- Gate 2-3P-R3M-2: 미승인·미구현
- 실제 메타데이터 파일럿: 차단
- 실제 Walk-forward: 차단
- 모바일 MVP: 차단

현재 Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`, deployable M3·M4 weight는 0이다.

## 3. 버전 상태

동결 모델:

```text
model_version = 4.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

제안 모델:

```text
model_version = 5.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

`5.0.0-research`는 사용자 승인 전이며 Python 구현되지 않았다. 실패한 `3.0.0-research`, `4.0.0-research` 결과와 보고서는 변경하지 않는다.

## 4. R2 구현 요약

### M4

- field별 prequential likelihood-ratio e-process
- stable / transient family
- hierarchical partial pooling
- unseen context parent fallback
- machine × ball-set residual 수축
- evidence 부족 시 exact M0
- activation / deactivation `1000 / 100`
- transient windows `13 / 26 / 52 / 104`
- forced return 52회

### Metadata

- 사후시점·현재결과·schema·traceability·target mismatch global veto
- invalid metadata에서 M4 전체 weight 0

### M3

- restart-mixture e-process
- 13회 restart
- 기존 evidence/active life 208회
- detector와 post-change prediction 분리
- post-change `k_m3` grid `90 / 260 / 520`
- support 20 미만 exact M0

### 제품 계약

- M0~M4 역할 유지
- exact 6-of-45
- 6개 번호 × 5세트
- RESEARCH M0-only
- M3·M4 cap 각각 10%
- Pair-number interaction 비활성

## 5. R2 기준점

- verified head: `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow run: `28483871565` — success
- smoke artifact: `7996655664`
- unit-test artifact: `7996653569`

## 6. R3 사전 구현감사

R1 명세와 R2 실행경로를 대조해 다음 누락을 승인된 명세대로 보완했다.

1. M3 trigger draw 기록
2. trigger 후 208회 active-life 종료
3. post-change `k_m3` predictor
4. prediction runner corrected M3 연결

Threshold, effect size, cap, 평가기준은 변경하지 않았다.

## 7. R3 등록 Grid

M4:

- `k_global`: 260 / 520 / 1040
- `k_context`: 90 / 260 / 520
- `effect_clip`: 0.10 / 0.20 / 0.35

M3:

- `k_m3`: 90 / 260 / 520

총 결합 후보는 81개다.

## 8. R3 DEV 결과와 잠금

- namespace: `DEV`
- scenario: P4 regime reversal
- lift: `1.25`
- deterministic series: `200`
- draw count: `1230`
- M3 activation: `0 / 200 = 0%`
- maximum e-value: `1.2128703085422197`
- median maximum e-value: `1.0587511056557841`
- 95th percentile: `1.0885919344118067`
- 99th percentile: `1.1362731415280718`
- activation threshold: `1000`
- eligible `k_m3`: 없음
- direction trials: 0
- selected config: `null`
- pruned combined configs: `81 / 81`

판정:

```text
Gate 2-3P-R3 = NO_ELIGIBLE_CONFIG
Gate 2-3P-R4 = BLOCKED
Final distribution = M0 only
```

잠금:

- implementation commit: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run: `28489870505` — success
- unit tests: `87 PASS`
- artifact: `7998826927`
- artifact digest: `sha256:8f39fabeb249261feeb3f0b5cc054c85a60ea20ef49568135f8164b008337229`
- DEV report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`
- CAL executed: false
- SEALED executed: false

## 9. R3M 수학적 적합성 분석

P4 lift 1.25 exact 6-of-45 대안:

- favored group size: 10
- expected favored count: `1.5479558826836606`
- oracle KL: `0.024294585890841103 nats/draw`
- `log(1000) = 6.907755278982137`
- `208 × KL = 5.053273865294949`
- 208회 oracle expected evidence: 약 `156.53`

따라서 favored set과 change point를 미리 아는 oracle도 208회 기대 evidence가 threshold 1000에 도달하지 못한다.

정규근사 기준:

| activation 가설 수 | 80% power 필요 draw |
|---:|---:|
| 1 | 약 448 |
| 2 | 약 483 |
| 4 | 약 518 |
| 8 | 약 552 |
| 45 | 약 636 |

기존 최대 nominal component 수는 `45 × 8 × 16 = 5,760`으로 mixture dilution이 매우 크다.

결론:

```text
threshold 1000
+ evidence life 208
+ lift 1.25
+ power 80%
= mathematically incompatible
```

## 10. 신규 5.0 교정 명세

Threshold 1000과 R3 실패결과는 유지한다.

시간계약을 분리한다.

```text
pre-activation evidence horizon = 520 draws
post-activation active life = 208 draws
activation / deactivation = 1000 / 100
```

핵심 구조:

1. 번호별 Bernoulli betting 대신 exact 6-of-45 group likelihood-ratio
2. activation 가능한 primary hypotheses 최대 4개
3. 45개 번호별·다중 lambda 탐색은 diagnostic-only
4. past-only predict-then-bet group learning
5. restart wealth 사전등록 감쇠 schedule
6. oracle feasibility gate 선행
7. oracle 통과 후 predictable-group gate
8. 이후에만 full M3 DEV 허용
9. M4 구조 변경 없음
10. R4는 계속 BLOCKED

명세 파일:

- `reports/gate2_3p_r3m_mathematical_feasibility.md`
- `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`

## 11. 5.0 향후 Gate

### Gate 2-3P-R3M-2

사용자 승인 후 구현 가능한 범위:

1. exact fixed-size group LR
2. 520-draw oracle detector
3. threshold 1000 유지
4. deterministic oracle DEV only
5. oracle 결과 hash 잠금

아직 구현하면 안 되는 범위:

- past-only group learner
- primary 4-way full detector
- full M3 grid
- CAL
- SEALED
- 실제 데이터
- 모바일 UI

Oracle PASS 전에는 다음 구현으로 이동하지 않는다.

## 12. 금지

- 사용자 승인 전 `5.0.0-research` Python 구현
- 추가 DEV 탐색
- R4 CAL·SEALED 실행
- threshold 1000 완화
- 실패 seed·scenario 삭제
- 208회 post-activation active life 완화
- 적격하지 않은 config 임의 선택
- 실제 Walk-forward
- 사용자용 후보 생성
- 모바일 UI 개발
- main 병합

## 13. 링크

- Issue #26: `https://github.com/dpes31/predictive-algorithm/issues/26`
- R3M Draft PR #27: `https://github.com/dpes31/predictive-algorithm/pull/27`
- Issue #21: `https://github.com/dpes31/predictive-algorithm/issues/21`
- R3 Draft PR #22: `https://github.com/dpes31/predictive-algorithm/pull/22`
- R2 Draft PR #19: `https://github.com/dpes31/predictive-algorithm/pull/19`
- R1 spec PR #17: `https://github.com/dpes31/predictive-algorithm/pull/17`
