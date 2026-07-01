# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-r3-dev-grid`  
기준 브랜치: `feature/gate2p-r2-correction-engine`  
관련 이슈: #21  
현재 Draft PR: #22

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-1 | 승인 완료 | 100% |
| Gate 2-3P-2 | 완료 | 100% |
| Gate 2-3P-3 | NOT PASSED | 100% |
| Gate 2-3P-R1 | 승인 완료 | 100% |
| Gate 2-3P-R2 | 구현 완료·CI 통과 | 100% |
| Gate 2-3P-R3 | **완료·NO_ELIGIBLE_CONFIG** | 100% |
| Gate 2-3P-R4 | BLOCKED | 0% |
| 실제 메타데이터 파일럿 | 차단 | 0% |
| 실제 Walk-forward | 차단 | 0% |
| 모바일 MVP | 차단 | 0% |

## R2 기준점

- model `4.0.0-research`
- feature contract `3.0.0`
- verified head `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow run `28483871565`: success
- smoke artifact `7996655664`
- unit-test artifact `7996653569`

## R3 사전 구현감사

R1 명세 대비 R2 실행경로에서 다음 누락을 확인하고 승인 명세대로 보완했다.

1. M3 trigger draw 기록
2. trigger 후 208회 active-life 종료
3. `k_m3` post-change predictor
4. prediction runner corrected M3 연결

Threshold, effect size, cap, 평가기준은 변경하지 않았다.

## R3 등록 Grid

- M4: `k_global 3 × k_context 3 × effect_clip 3 = 27`
- M3: `k_m3 = 90 / 260 / 520`
- 결합 후보: 81개

## R3 DEV 결과

- namespace: DEV only
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

M3가 한 번도 활성화되지 않았으므로 post-change `k_m3`와 독립 M4 grid를 임의 선택하지 않았다.

## 실행 무결성과 잠금

- implementation commit `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run `28489870505`: success
- unit tests: 87 PASS
- artifact `7998826927`
- artifact digest `sha256:8f39fabeb249261feeb3f0b5cc054c85a60ea20ef49568135f8164b008337229`
- DEV report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`
- CAL executed: false
- SEALED executed: false

## 고정 기준

- M0~M4 역할과 6개 번호 × 5세트 유지
- M3·M4 cap 각각 10%
- activation / deactivation `1000 / 100`
- false activation 0.1%
- one-sided 95% upper 0.2%
- lift 1.25 strict detection 80%
- lift 1.50 strict detection 95%
- 기존 실패 시나리오 유지
- Pair-number interaction 비활성
- RESEARCH 최종분포 M0-only

## 현재 차단

- R4 CAL·SEALED
- threshold 완화 또는 실패 seed 제거
- 실제 데이터·모바일 UI·main 병합

## 다음 권고 단계

별도 승인 후 M3 detector의 mixture dilution과 threshold 1000, 208회 life, lift 1.25 검출력의 수학적 양립 가능성을 재설계하는 교정 명세를 먼저 작성한다. 명세 승인 전 구현이나 추가 DEV 탐색을 하지 않는다.
