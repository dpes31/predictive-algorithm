# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-r3-dev-grid`  
기준 브랜치: `feature/gate2p-r2-correction-engine`  
관련 이슈: #21  
Draft PR: 생성 예정

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-1 | 승인 완료 | 100% |
| Gate 2-3P-2 | 완료 | 100% |
| Gate 2-3P-3 | NOT PASSED | 100% |
| Gate 2-3P-R1 | 승인 완료 | 100% |
| Gate 2-3P-R2 | 구현 완료·CI 통과 | 100% |
| Gate 2-3P-R3 | **사용자 승인·DEV 실행 준비 중** | 55% |
| Gate 2-3P-R4 | 차단 | 0% |
| 실제 메타데이터 파일럿 | 차단 | 0% |
| 실제 Walk-forward | 차단 | 0% |
| 모바일 MVP | 차단 | 0% |

## R2 최신 검증 기준점

- model `4.0.0-research`
- feature contract `3.0.0`
- verified head `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow run `28483871565`: success
- smoke artifact `7996655664`
- unit-test artifact `7996653569`
- canonical data, compile, unit tests, deterministic smoke, research/public guards: PASS

## R3 사전 구현감사 및 보완

R1 명세와 R2 코드를 대조해 다음 누락을 확인했다.

1. M3 trigger draw 기록
2. trigger 후 208회 active-life 종료
3. `k_m3` post-change predictor
4. prediction runner의 corrected M3 연결

R3 브랜치에서 승인된 구조 그대로 구현했다. threshold와 효과크기는 변경하지 않았다.

## R3 등록 Grid

- M4: `k_global 3 × k_context 3 × effect_clip 3 = 27`
- M3: `k_m3 = 90 / 260 / 520`
- 결합 후보: 81개
- 선택 우선순위: mandatory lift-1.25 방향 제약 → null false activation → 큰 prior·작은 clip
- 적격 후보가 없으면 `NO_ELIGIBLE_CONFIG`

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

## 현재 실행 제한

- DEV namespace만 허용
- CAL·SEALED 실행 금지
- 실제 데이터·모바일 UI·main 병합 금지

## 다음 작업

M3 mandatory preflight를 DEV 200개 시리즈로 실행한다. M3가 lift 1.25에서 적격하지 않으면 M4 grid와 무관하게 결합 81개 모두 적격 불가이므로 임의 config를 선택하지 않는다. 적격할 때만 M4 27개 grid 평가로 진행한다.
