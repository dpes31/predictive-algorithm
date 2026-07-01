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
9. `reports/gate2_3p_r3_dev_summary.md`
10. `reports/gate2_3p_r3_dev_lock.json`
11. `reports/gate2_3p_r3m_mathematical_feasibility.md`
12. `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`
13. `handoff/GATE2_PHYSICAL_PROGRESS.md`
14. `handoff/PROJECT_HANDOFF.md`
15. `handoff/GATE2_CORRECTION_IMPLEMENTATION_START.md`
16. `handoff/GATE2_R3_DEV_START.md`
17. `handoff/DECISION_LOG_GATE2_M3_FEASIBILITY.md`

## 현재 상태

- Gate 2-3P-3: NOT PASSED
- Gate 2-3P-R1: 승인 완료
- Gate 2-3P-R2: 구현 완료·CI 통과
- Gate 2-3P-R3: **완료·NO_ELIGIBLE_CONFIG**
- Gate 2-3P-R4: **BLOCKED**
- Gate 2-3P-R3M-1: **수학적 적합성 분석·교정 명세 완료, 사용자 승인 대기**
- 실제 메타데이터·Walk-forward·모바일 MVP: 차단

현재 브랜치: `feature/gate2p-r3m-feasibility-spec`  
기준 브랜치: `feature/gate2p-r3-dev-grid`  
관련 Issue: `#26`  
현재 Draft PR: `#27`  
현재 동결 모델: `4.0.0-research`  
제안 모델: `5.0.0-research`  
Feature contract: `3.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## R3 잠금 결과

- namespace: `DEV`
- mandatory scenario: P4 regime reversal, lift `1.25`
- deterministic series: `200`
- M3 activation: `0 / 200`
- maximum e-value: `1.2128703085422197`
- activation threshold: `1000`
- eligible `k_m3`: 없음
- direction trials: `0`
- pruned combined configs: `81 / 81`
- decision: `NO_ELIGIBLE_CONFIG`
- selected config: `null`
- implementation commit: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow run: `28489870505` — success
- unit tests: `87 PASS`
- DEV report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`
- CAL executed: false
- SEALED executed: false

R3 실패 결과와 hash는 변경하지 않는다.

## R3M 수학적 판정

다음 네 조건은 동시에 양립하지 않는다.

```text
activation threshold 1000
+ pre-activation evidence life 208 draws
+ lift 1.25
+ strict detection power 80%
```

P4 exact 6-of-45 대안의 oracle KL은 회차당 `0.024294585890841103 nats`다.

```text
208 * KL = 5.053273865294949
log(1000) = 6.907755278982137
```

Favored set과 change point를 아는 oracle도 208회 기대 evidence가 threshold 1000에 미달한다. 기존 45 numbers × 8 betting fractions × restart mixture는 추가 dilution을 발생시킨다.

## 5.0 제안 구조

Threshold와 R3 실패결과는 유지한다.

```text
pre-activation evidence horizon = 520 draws
post-activation active life = 208 draws
activation / deactivation = 1000 / 100
```

- exact 6-of-45 group likelihood-ratio
- activation 가능한 primary hypothesis 최대 4개
- 나머지 가설은 diagnostic-only
- past-only predict-then-bet group construction
- oracle feasibility gate 선행
- oracle 통과 후 predictable-group gate
- 이후에만 full M3 DEV grid 허용
- M4 구조는 변경하지 않음

제안 모델 `5.0.0-research`는 아직 승인·구현되지 않았다.

## 금지사항

별도 사용자 승인 없이 다음을 수행하지 않는다.

- `5.0.0-research` Python 구현
- 추가 DEV 탐색
- Gate 2-3P-R4 CAL·SEALED 실행
- threshold 1000 완화
- 실패 scenario·seed 삭제
- 208회 post-activation active life 완화
- 적격하지 않은 config 임의 선택
- 실제 Walk-forward 또는 사용자용 후보 생성
- 모바일 UI·Supabase 개발
- main 병합

## 브랜치·PR 정책

- main 직접 개발 금지
- 기능별 별도 브랜치와 Draft PR
- 사용자 검토 전 병합 금지
- 실패한 결과 덮어쓰기 금지
- PR #11·#13·#15·#17·#19·#22·#27 미병합 유지

## 다음 Gate

다음 단계는 사용자 승인 후 Gate 2-3P-R3M-2로 이동해 `5.0.0-research`의 oracle feasibility engine과 exact group LR만 먼저 구현하는 것이다.

구현 순서:

1. exact fixed-size group LR
2. 520-draw oracle detector
3. threshold 1000 유지
4. oracle DEV gate만 실행
5. oracle PASS 전에는 predictable-group·full M3 구현 금지
6. CAL·SEALED 계속 차단

## 작업 종료 시 누적

- `AGENTS.md`
- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
