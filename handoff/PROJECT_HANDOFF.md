# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R3 DEV 평가 진행 중**  
현재 브랜치: `feature/gate2p-r3-dev-grid`  
기준 브랜치: `feature/gate2p-r2-correction-engine`  
관련 Issue: #21  
Draft PR: 생성 예정

## 1. 목적

로또 6/45 다음 회차에 대해 정확히 6개 번호 조합 5세트를 출력하는 연구형 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## 2. Gate 상태

- Gate 2-3 / 2-3R: NOT PASSED
- Gate 2-3P-1: 승인 완료
- Gate 2-3P-2: 완료
- Gate 2-3P-3: NOT PASSED
- Gate 2-3P-R1: 승인 완료
- Gate 2-3P-R2: 구현 완료·CI 통과
- Gate 2-3P-R3: **사용자 승인·DEV 평가 진행 중**
- Gate 2-3P-R4: 별도 승인 전 차단
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
- canonical data, compile, unit tests, deterministic smoke, research/public guards: PASS

## 6. R3 사전 구현감사

R1 명세와 R2 실행경로를 대조하여 다음 누락을 확인했다.

1. M3 trigger draw 기록 누락
2. trigger 후 208회 종료 처리 누락
3. post-change `k_m3` predictor 누락
4. prediction runner의 corrected M3 연결 누락

R3 브랜치에서 승인 명세에 맞춰 구현했다. 기준과 threshold는 변경하지 않았다.

## 7. R3 평가 계약

M4 grid:

- `k_global`: 260 / 520 / 1040
- `k_context`: 90 / 260 / 520
- `effect_clip`: 0.10 / 0.20 / 0.35

M3 grid:

- `k_m3`: 90 / 260 / 520

결합 후보는 81개다.

선택 순서:

1. DEV namespace만 사용
2. P4 lift 1.25 M3 mandatory 방향 제약 확인
3. 적격할 때만 M4 null false activation 우선 평가
4. 동률이면 큰 prior와 작은 clip 선택
5. 적격 config가 없으면 `NO_ELIGIBLE_CONFIG`와 implementation hash를 잠금

## 8. 금지

- main 병합
- CAL·SEALED 실행
- 기준 완화
- 실패 seed 또는 scenario 삭제
- 실제 Walk-forward
- 사용자용 후보 생성
- 모바일 UI 개발

## 9. 다음 작업

DEV 200개 P4 lift-1.25 series로 M3 mandatory preflight를 실행한다. 적격하면 M4 27개 grid를 평가한다. 적격하지 않으면 81개 결합 config 전체를 선택 불가로 판정하고 R4를 계속 차단한다.

## 10. 링크

- Issue #21: `https://github.com/dpes31/predictive-algorithm/issues/21`
- R2 Draft PR #19: `https://github.com/dpes31/predictive-algorithm/pull/19`
- R1 spec PR #17: `https://github.com/dpes31/predictive-algorithm/pull/17`
