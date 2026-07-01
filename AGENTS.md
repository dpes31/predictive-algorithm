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
6. `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`
7. `reports/gate2_3p_r3_dev_lock.json`
8. `reports/gate2_3p_r3m_mathematical_feasibility.md`
9. `reports/gate2_3p_r3m2_oracle_dev_summary.json`
10. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
11. `handoff/PROJECT_HANDOFF.md`
12. `handoff/GATE2_PHYSICAL_PROGRESS.md`
13. `handoff/DECISION_LOG_GATE2_M3_FEASIBILITY.md`
14. `handoff/DECISION_LOG_GATE2_R3M2_APPROVAL.md`
15. `handoff/GATE2_R3M2_IMPLEMENTATION_START.md`

## 현재 상태

- Gate 2-3P-R3: **완료·NO_ELIGIBLE_CONFIG**
- Gate 2-3P-R4: **BLOCKED**
- Gate 2-3P-R3M-1: **승인 완료**
- Gate 2-3P-R3M-2 Oracle DEV: **PASS**
- predictable-group 학습: **별도 승인 전 BLOCKED**
- full M3 DEV: **BLOCKED**
- CAL·SEALED: **BLOCKED**
- 실제 데이터·모바일 MVP: **BLOCKED**

현재 브랜치: `feature/gate2p-r3m2-oracle-engine`  
기준 브랜치: `feature/gate2p-r3m-feasibility-spec`  
관련 Issue: `#28`  
현재 Draft PR: `#29`  
현재 모델: `5.0.0-research`  
Feature contract: `3.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## R3 잠금 결과

- decision: `NO_ELIGIBLE_CONFIG`
- implementation commit: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run: `28489870505`
- report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

이 실패 결과와 hash는 변경하지 않는다.

## R3M-2 구현 범위

구현 완료:

- exact 6-of-45 group likelihood-ratio
- favored group 사전고정 oracle detector
- pre-activation evidence horizon `520`
- activation threshold `1000`
- post-activation active life `208`
- deterministic DEV-only positive/null gate
- exact one-sided 95% binomial upper bound
- namespace·scope lock

미구현:

- past-only predictable-group learner
- primary 4-way detector
- full M3 DEV grid
- deployable M3 prediction path

## Oracle DEV 잠금 결과

- status: `ORACLE_PASS`
- implementation commit: `37fd815220ccd363f019f3798366a2060872e073`
- workflow run: `28493929179`
- unit tests: `96 PASS`
- artifact: `8000257623`
- artifact digest: `sha256:6c52c97fbd167a2f2ae22e4d225510cc419985c19e08f283dcdfbd6eaec2dafe`
- report hash: `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash: `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

Positive oracle:

- 2,000 series
- 1,837 activations
- activation rate `91.85%` — PASS against `80%`
- median activation delay `241` — PASS against `520`

Null safety:

- 10,000 series
- 8 false activations
- false activation rate `0.08%` — PASS against `0.10%`
- one-sided 95% upper `0.1443001%` — PASS against `0.20%`

Oracle PASS는 favored group과 change point를 알고 있는 수학적 상한의 가능성을 확인한 결과다. 과거 데이터만으로 그룹을 예측할 수 있음을 의미하지 않는다.

## 금지사항

별도 사용자 승인 없이 다음을 수행하지 않는다.

- predictable-group 학습 구현 또는 DEV 실행
- full M3 DEV
- Gate 2-3P-R4 CAL·SEALED
- threshold 1000 완화
- 실패 scenario·seed 삭제
- 208회 post-activation active life 완화
- 실제 Walk-forward 또는 사용자용 후보 생성
- 모바일 UI·Supabase 개발
- main 병합

## 브랜치·PR 정책

- main 직접 개발 금지
- 기능별 별도 브랜치와 Draft PR
- 사용자 검토 전 병합 금지
- 실패 결과 덮어쓰기 금지
- PR #11·#13·#15·#17·#19·#22·#27·#29 미병합 유지

## 다음 Gate

다음 단계는 별도 승인 후 `Gate 2-3P-R3M-3 predictable-group feasibility`다.

허용 예정 범위:

1. past-only training window
2. betting 시작 전 group 고정
3. group size `{6, 10, 15}`
4. lift 1.25 positive DEV
5. null 안전성 DEV
6. 방향정확도·Log Loss·Brier 평가

Oracle PASS가 full M3 또는 R4 승인을 의미하지 않는다.

## 작업 종료 시 누적

- `AGENTS.md`
- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
