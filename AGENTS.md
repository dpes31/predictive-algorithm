# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽는다.

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

1. `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`
2. `docs/GATE2_PREDICTABLE_GROUP_FEASIBILITY_SPEC.md`
3. `docs/GATE2_PREDICTABLE_GROUP_VALIDATION_PROTOCOL.md`
4. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
5. `reports/gate2_3p_r3m3_predictable_group_dev_summary.json`
6. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`
7. `handoff/PROJECT_HANDOFF.md`
8. `handoff/GATE2_PHYSICAL_PROGRESS.md`
9. `handoff/DECISION_LOG_GATE2_R3M3_RESULT.md`

## 현재 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R3M-2 Oracle DEV: `PASS`
- Gate 2-3P-R3M-3-1: 승인 완료
- Gate 2-3P-R3M-3-2: **구현 완료·PREDICTABLE_GROUP_FAIL**
- full M3 DEV: `BLOCKED`
- Gate 2-3P-R4: `BLOCKED`
- CAL·SEALED: `BLOCKED`
- 실제 데이터·모바일 MVP: `BLOCKED`

현재 브랜치: `feature/r3m3-predictable-group-engine`  
기준 브랜치: `feature/r3m3-predictable-group-spec`  
현재 Draft PR: `#32`  
현재 모델: `5.0.0-research`  
Predictable-group contract: `1.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## Oracle 잠금

- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- positive activation `91.85%`
- null false activation `0.08%`
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

Oracle PASS는 true group과 change point를 아는 수학적 상한만 확인한다.

## Predictable-group 구현

고정 계약 그대로 구현했다.

- outer window `520`
- half-life `104`
- prior strength `52`
- internal validation `260 + 5 x 52`
- group sizes `{6,10,15}`
- group freeze `52`
- detection horizon `520`
- threshold `1000`
- active life `208`
- namespaces `DEV-PG`, `DEV-PG-CI`

## DEV-PG 결과 잠금

- status `PREDICTABLE_GROUP_FAIL`
- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests `105 PASS`
- artifact `8002526507`
- artifact digest `sha256:8ba3958b1dcd45dac6ee436b9911f39281138287cd212fc1591283f985d1c6b1`
- seed hash `5fa4ab0038468a38f7a06a41928752c1a444ba9a17eef64e10a2d3d64cc69038`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

Positive:

- availability `33.66%` — FAIL
- activation `1.35%` — FAIL
- median delay `421` — PASS
- direction accuracy `78.6839%` — FAIL
- direction trials `6,732` — FAIL
- mean/lower delta Log Loss negative — FAIL
- mean/lower delta Brier negative — FAIL

Null:

- false activation `0.01%` — PASS
- one-sided 95% upper `0.04743%` — PASS

## 해석

Null 안전성은 유지됐지만 과거 번호 이력만으로 P4 reversal favored group을 충분히 사전 예측하지 못했다. 가용성, 검출력, 방향정확도와 예측효용이 사전기준에 미달했다.

결과를 본 뒤 threshold, window, half-life, prior, fold, group size 또는 effect를 수정하지 않는다.

## 금지사항

별도 사용자 승인 없이 다음을 수행하지 않는다.

- 추가 DEV 탐색 또는 하이퍼파라미터 튜닝
- full M3 detector 또는 grid
- Gate 2-3P-R4 CAL·SEALED
- threshold 1000 완화
- 실패 seed·scenario 삭제
- 실제 Walk-forward 또는 사용자용 후보 생성
- 모바일 UI·Supabase 개발
- main 병합

## 다음 Gate

다음 단계는 Python 수정이 아니라 실패 원인 분석과 연구방향 결정 명세다. 과거 번호만 사용하는 M3 predictable-group 연구를 중단할지, 물리·운영 선행변수 M4를 중심으로 별도 Gate를 설계할지 사용자 승인이 필요하다.

## 작업 종료 시 누적

- `AGENTS.md`
- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
