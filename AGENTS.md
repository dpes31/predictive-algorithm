# AGENTS.md

이 문서는 모든 개발 에이전트가 작업 전에 읽어야 하는 최상위 운영 규칙이다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 정확히 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

핵심 원칙:

- M0 균등 기준 유지
- M1 지속, M2 반전, M3 구조변화, M4 물리·운영 증거 역할 유지
- 근거 부족 시 exact M0
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패 결과와 불확실성 보존
- 제품 출력은 6개 번호 × 5세트

## 2. 필수 읽기

1. `docs/ALGORITHM_SPEC.md`
2. `docs/NON_NEGOTIABLES.md`
3. `docs/DATA_POLICY.md`
4. `docs/VALIDATION_PROTOCOL.md`
5. `docs/GATE2_PHYSICAL_CORRECTION_SPEC.md`
6. `docs/GATE2_PHYSICAL_CORRECTION_VALIDATION.md`
7. `docs/GATE2_PHYSICAL_CORRECTION_IMPLEMENTATION_PLAN.md`
8. `reports/gate2_3p3_full_summary.md`
9. `handoff/GATE2_PHYSICAL_PROGRESS.md`
10. `handoff/PROJECT_HANDOFF.md`
11. `handoff/GATE2_CORRECTION_IMPLEMENTATION_START.md`

## 3. 현재 상태

- Gate 2-3P-3: NOT PASSED
- Gate 2-3P-R1: 사용자 승인 완료
- Gate 2-3P-R2: **구현 완료·CI 통과**
- Gate 2-3P-R3: DEV 검수 미착수
- Gate 2-3P-R4: sealed validation 차단
- 실제 메타데이터 파일럿: 차단
- 실제 Walk-forward: 차단
- 모바일 UI: 차단

현재 브랜치: `feature/gate2p-r2-correction-engine`  
현재 Draft PR: #19  
현재 모델: `4.0.0-research`  
Feature contract: `3.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## 4. 구현된 교정 구조

### M4

- field별 log-domain e-process
- stable / transient family
- hierarchical partial pooling
- unseen context parent fallback
- machine × ball-set residual shrinkage
- activation / deactivation 1000 / 100
- exact-M0 abstention
- transient window 13 / 26 / 52 / 104
- forced return 52회

### Metadata

다음은 M4 global veto다.

- post-draw timestamp
- current-result field
- schema mismatch
- verified source traceability 없음
- target draw mismatch

### M3

- restart-mixture change e-process
- 45개 번호
- 고정 betting-fraction grid
- 13회 restart
- 최대 life 208회
- detector와 방향점수 분리

## 5. 유지 기준

- exact 6-of-45
- 6개 번호 × 5세트
- RESEARCH M0-only
- CANDIDATE M0 최소 70%
- M3 최대 10%
- M4 최대 10%
- false activation 0.1%
- one-sided 95% upper 0.2%
- lift 1.25 strict detection 80%
- lift 1.50 strict detection 95%
- 기존 실패 시나리오·효과크기 유지
- Pair-number interaction 비활성

## 6. CI 기준

R2 완료 CI run: `28483762170`

- canonical data PASS
- compile PASS
- full unit tests PASS
- deterministic smoke twice PASS
- research-only guard PASS
- public-release guard PASS

## 7. 현재 금지

별도 승인 없이 다음을 수행하지 않는다.

- R3 DEV grid 실행
- CAL 또는 SEALED namespace 실행
- threshold 완화
- 실패 scenario·seed 삭제
- 실제 과거번호 Walk-forward
- 실제 후보 공개
- M3·M4 cap 완화
- 모바일 UI·Supabase 개발
- main 병합

## 8. 브랜치·PR 정책

- main 직접 개발 금지
- 기능별 별도 브랜치와 Draft PR
- 사용자 검토 전 병합 금지
- 실패한 `3.0.0-research` 결과 덮어쓰기 금지
- PR #11·#13·#15·#17·#19 미병합 유지

## 9. 다음 Gate

Gate 2-3P-R3에서 DEV namespace만 사용하여 허용 grid를 평가하고 선택 config와 commit hash를 잠근다. R4 sealed validation은 별도 승인 전 실행하지 않는다.

## 10. 중단 원칙

`4.0.0-research`가 sealed validation에 실패하면 동일 synthetic suite의 추가 튜닝을 중단한다. 새로운 외부 물리데이터가 확보되기 전 비균등 예측연구를 재개하지 않는다.

## 11. 작업 종료 시 누적

- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
