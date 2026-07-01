# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-r2-correction-engine`  
기준 브랜치: `feature/gate2p3-correction-spec`  
관련 이슈: #18  
현재 Draft PR: #19

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-1 | 승인 완료 | 100% |
| Gate 2-3P-2 | 완료 | 100% |
| Gate 2-3P-3 | NOT PASSED | 100% |
| Gate 2-3P-R1 | 승인 완료 | 100% |
| Gate 2-3P-R2 | **구현 완료·CI 통과** | 100% |
| Gate 2-3P-R3 | unit/smoke 완료, DEV 검수 미착수 | 40% |
| Gate 2-3P-R4 | 차단 | 0% |
| 실제 메타데이터 파일럿 | 차단 | 0% |
| 실제 Walk-forward | 차단 | 0% |
| 모바일 MVP | 차단 | 0% |

## R2 구현

- model `4.0.0-research`
- feature contract `3.0.0`
- field별 log-domain e-process
- stable / transient M4
- hierarchical partial pooling
- machine × ball-set residual shrinkage
- metadata global veto
- exact-M0 abstention
- 1000 / 100 hysteresis
- transient window 13 / 26 / 52 / 104
- M3 restart-mixture change e-process
- 208회 최대 수명
- RESEARCH 최종분포 M0-only
- exact 6-of-45와 5세트 출력 유지
- DEV / CAL / SEALED namespace 분리

## CI 결과

- run `28483762170`: success
- head `6f264309a8e5cd5ee076cd235ff76c3684bcb5cc`
- canonical data: PASS
- compile: PASS
- full unit tests: PASS
- deterministic smoke twice: PASS
- research-only guard: PASS
- public-release guard: PASS
- smoke artifact `7996617074`
- smoke digest `sha256:e82f74246d3983b2653b465b55fcd475c5f0ea382eb46c1eefe95a529aa197af`
- unit-test artifact `7996615246`

## 고정 기준

- M0~M4 역할과 6개 번호 × 5세트 유지
- M3·M4 cap 각각 10%
- false activation 0.1%
- one-sided 95% upper 0.2%
- lift 1.25 strict detection 80%
- lift 1.50 strict detection 95%
- 기존 실패 시나리오 유지
- Pair-number interaction 비활성

## 다음 단계

Gate 2-3P-R3에서 DEV namespace만 사용해 허용 grid를 평가하고 config hash를 잠근다. R4 sealed validation은 별도 승인 전 실행하지 않는다.
