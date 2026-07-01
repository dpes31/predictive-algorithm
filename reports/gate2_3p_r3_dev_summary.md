# Gate 2-3P-R3 DEV Evaluation Summary

최종 갱신: 2026-07-01  
모델: `4.0.0-research`  
Feature contract: `3.0.0`  
Namespace: `DEV` only

## Decision

**NO_ELIGIBLE_CONFIG**

Gate 2-3P-R3의 mandatory preflight에서 P4 regime-reversal, lift 1.25 시나리오가 M3 activation threshold `1000`에 도달하지 못했다. 등록된 `k_m3 = 90 / 260 / 520` 모두 방향정확도 평가 trial이 0이므로 적격하지 않다.

따라서 M4의 27개 grid와 결합한 81개 configuration 전체를 선택 불가로 판정한다. 임의 config는 선택하지 않는다.

## Locked implementation

- implementation commit: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run: `28489870505`
- workflow conclusion: `success`
- artifact: `7998826927`
- artifact digest: `sha256:8f39fabeb249261feeb3f0b5cc054c85a60ea20ef49568135f8164b008337229`
- DEV report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

## Evaluation scope

- scenario: `p4_regime_reversal`
- effect size: `1.25`
- replicates: `200`
- draw count: `1230`
- registered M3 grid: `3`
- registered M4 grid: `27`
- combined configurations: `81`

## Result

- activated series: `0 / 200`
- activation rate: `0.0%`
- max e-value: `1.2128703085422197`
- median max e-value: `1.0587511056557841`
- 95th percentile: `1.0885919344118067`
- 99th percentile: `1.1362731415280718`
- eligible `k_m3`: none
- selected config: `null`
- pruned combined configurations: `81 / 81`

## Interpretation

이번 결과는 실행 실패가 아니다. 전체 unit test 87개와 DEV runner가 정상 완료됐다. 실패 원인은 사전등록된 M3 detector가 lift 1.25 구조변화 신호에서 activation threshold에 전혀 근접하지 못한 통계적 검출력 부족이다.

`k_m3`는 detector activation 이후의 post-change predictor 수축값이므로, detector가 한 번도 활성화되지 않은 상태에서 `k_m3` 또는 M4 grid를 선택하는 것은 의미가 없다.

## Gate state

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R4: `BLOCKED`
- CAL executed: `false`
- SEALED executed: `false`
- actual-data walk-forward: `BLOCKED`
- public candidates: `BLOCKED`
- mobile MVP: `BLOCKED`
- final distribution: `M0 only`

## Stop rule

현재 승인 계약에 따라 R4 sealed validation은 실행하지 않는다. 동일 synthetic suite에서 threshold 완화, 실패 seed 제거, 효과크기 변경 또는 임의 config 선택을 하지 않는다.
