# AGENTS.md

이 문서는 모든 개발 에이전트가 작업 전에 읽어야 하는 최상위 운영 규칙이다.

## 프로젝트 목적

로또 6/45 다음 회차의 정확히 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

- M0 균등 기준 유지
- M1 지속, M2 반전, M3 구조변화, M4 물리·운영 증거 역할 유지
- 근거 부족 시 exact M0
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패 결과와 불확실성 보존
- 제품 출력은 6개 번호 × 5세트

## 필수 읽기

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
12. `handoff/GATE2_R3_DEV_START.md`

## 현재 상태

- Gate 2-3P-3: NOT PASSED
- Gate 2-3P-R1: 승인 완료
- Gate 2-3P-R2: 구현 완료·CI 통과
- Gate 2-3P-R3: 사용자 승인 완료·DEV 평가 진행 중
- Gate 2-3P-R4: 별도 승인 전 차단
- 실제 메타데이터·Walk-forward·모바일 MVP: 차단

현재 브랜치: `feature/gate2p-r3-dev-grid`  
기준 브랜치: `feature/gate2p-r2-correction-engine`  
관련 Issue: `#21`  
현재 모델: `4.0.0-research`  
Feature contract: `3.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## R2 최신 기준점

- verified head: `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow run: `28483871565` — success
- smoke artifact: `7996655664`
- unit-test artifact: `7996653569`
- canonical data, compile, unit tests, deterministic smoke, research/public guards: PASS

이는 구현 무결성과 재현성 검증이며 예측력 검증이 아니다.

## R3 사전 구현감사

R1 명세와 R2 구현을 대조해 다음 누락을 확인했고 현재 브랜치에서 보완했다.

1. M3 trigger draw 기록
2. trigger 후 208회 active life 종료
3. `k_m3` post-change predictor
4. prediction runner의 corrected M3 연결

검증 threshold와 효과크기는 변경하지 않는다.

## R3 Grid

- M4 `k_global`: `260 / 520 / 1040`
- M4 `k_context`: `90 / 260 / 520`
- M4 `effect_clip`: `0.10 / 0.20 / 0.35`
- M3 `k_m3`: `90 / 260 / 520`
- 결합 후보: 81개

선택은 DEV namespace에서만 수행한다. lift-1.25 방향정확도 제약과 null 오탐 우선 규칙을 유지한다. 적격 config가 없으면 임의 선택하지 않고 `NO_ELIGIBLE_CONFIG`를 기록한다.

## 금지사항

- CAL 또는 SEALED 실행
- threshold 완화
- 실패 scenario·seed 삭제
- 실제 Walk-forward 또는 사용자용 후보 생성
- 모바일 UI·Supabase 개발
- main 병합

## 브랜치·PR 정책

- main 직접 개발 금지
- 기능별 별도 브랜치와 Draft PR
- 사용자 검토 전 병합 금지
- 실패한 결과 덮어쓰기 금지
- PR #11·#13·#15·#17·#19 미병합 유지

## 다음 Gate

R3 DEV 결과와 선택 config 또는 `NO_ELIGIBLE_CONFIG`를 commit hash와 함께 잠근다. 적격 config가 있을 때만 사용자 별도 승인 후 R4로 이동한다.

## 작업 종료 시 누적

- `AGENTS.md`
- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
