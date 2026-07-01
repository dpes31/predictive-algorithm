# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R3 완료 · NO_ELIGIBLE_CONFIG**  
현재 브랜치: `feature/gate2p-r3-dev-grid`  
기준 브랜치: `feature/gate2p-r2-correction-engine`  
관련 Issue: #21  
현재 Draft PR: #22

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
- 실제 메타데이터 파일럿: 차단
- 실제 Walk-forward: 차단
- 모바일 MVP: 차단

현재 Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`, deployable M3·M4 weight는 0이다.

## 3. 동결 버전

```text
model_version = 4.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

실패한 `3.0.0-research` 결과와 보고서는 변경하지 않는다.

## 4. R2 구현

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
- 13회 restart, 최대 active life 208회
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

## 5. R2 최신 CI

- verified head: `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow run: `28483871565` — success
- smoke artifact: `7996655664`
- unit-test artifact: `7996653569`

## 6. R3 사전 구현감사

R1 명세와 R2 실행경로를 대조해 다음 누락을 확인하고 승인된 명세대로 보완했다.

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

## 8. R3 DEV 결과

Mandatory preflight:

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

M3 detector가 mandatory lift 1.25 신호에서 한 번도 활성화되지 않았으므로, detector 이후에만 작동하는 `k_m3`와 독립 M4 grid를 임의 선택하지 않았다.

## 9. 실행 무결성과 잠금

- implementation commit: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run: `28489870505` — success
- unit tests: `87 PASS`
- artifact: `7998826927`
- artifact digest: `sha256:8f39fabeb249261feeb3f0b5cc054c85a60ea20ef49568135f8164b008337229`
- DEV report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`
- CAL executed: false
- SEALED executed: false

결과 파일:

- `reports/gate2_3p_r3_dev_summary.md`
- `reports/gate2_3p_r3_dev_summary.json`
- `reports/gate2_3p_r3_dev_lock.json`

## 10. 금지

- R4 CAL·SEALED 실행
- threshold·효과크기 소급 완화
- 실패 seed 또는 scenario 삭제
- 적격하지 않은 config 임의 선택
- 실제 Walk-forward
- 사용자용 후보 생성
- 모바일 UI 개발
- main 병합

## 11. 다음 권고 단계

R4를 실행하지 않는다. 별도 승인 후 M3 detector의 mixture dilution, activation threshold 1000, 208회 process life와 lift 1.25 검출력의 수학적 양립 가능성을 먼저 분석하는 신규 교정 명세를 작성한다. 명세 승인 전 Python 구현이나 추가 DEV 탐색을 진행하지 않는다.

## 12. 링크

- Issue #21: `https://github.com/dpes31/predictive-algorithm/issues/21`
- R3 Draft PR #22: `https://github.com/dpes31/predictive-algorithm/pull/22`
- R2 Draft PR #19: `https://github.com/dpes31/predictive-algorithm/pull/19`
- R1 spec PR #17: `https://github.com/dpes31/predictive-algorithm/pull/17`
