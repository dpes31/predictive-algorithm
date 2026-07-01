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

1. `docs/ALGORITHM_SPEC.md`
2. `docs/NON_NEGOTIABLES.md`
3. `docs/DATA_POLICY.md`
4. `docs/VALIDATION_PROTOCOL.md`
5. `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`
6. `docs/GATE2_PREDICTABLE_GROUP_FEASIBILITY_SPEC.md`
7. `docs/GATE2_PREDICTABLE_GROUP_VALIDATION_PROTOCOL.md`
8. `reports/gate2_3p_r3_dev_lock.json`
9. `reports/gate2_3p_r3m2_oracle_dev_summary.json`
10. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
11. `handoff/PROJECT_HANDOFF.md`
12. `handoff/GATE2_PHYSICAL_PROGRESS.md`
13. `handoff/DECISION_LOG_GATE2_R3M3_SPEC.md`

## 현재 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R4: `BLOCKED`
- Gate 2-3P-R3M-1: 승인 완료
- Gate 2-3P-R3M-2 Oracle DEV: `PASS`
- Gate 2-3P-R3M-3-1 상세 명세: **완료·사용자 승인 대기**
- Gate 2-3P-R3M-3-2 구현·DEV: **미승인·미실행**
- full M3 DEV: `BLOCKED`
- CAL·SEALED: `BLOCKED`
- 실제 데이터·모바일 MVP: `BLOCKED`

현재 브랜치: `feature/r3m3-predictable-group-spec`  
기준 브랜치: `feature/gate2p-r3m2-oracle-engine`  
관련 Issue: `#30`  
현재 Draft PR: `#31`  
현재 모델: `5.0.0-research`  
Predictable-group contract: `1.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## R3 실패 잠금

- implementation: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow: `28489870505`
- report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

기존 실패 결과를 수정하지 않는다.

## Oracle PASS 잠금

- implementation: `37fd815220ccd363f019f3798366a2060872e073`
- workflow: `28493929179`
- tests: `96 PASS`
- positive activation: `91.85%`
- median delay: `241`
- null false activation: `0.08%`
- one-sided 95% upper: `0.1443001%`
- report hash: `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash: `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

Oracle PASS는 true group과 change point를 아는 수학적 상한만 확인한다.

## R3M-3-1 고정 명세

### 시간계약

- global block start: `521 + 52k`
- outer learning window: 완료된 과거 520회
- retraining: 52회마다 고정 boundary에서만
- group freeze: 다음 52회 전체
- detection horizon: 520회
- activation threshold: 1000
- post-activation active life: 208회

### 번호 점수

```text
p0 = 6/45
half-life = 104
prior strength = 52
w(t) = 2^[-age(t)/104]
p_hat = [52*p0 + sum w*x] / [52 + sum w]
score = logit(p_hat) - logit(p0)
```

점수 차이가 `1e-12` 이하이면 낮은 번호 우선이다.

### Group size 선택

- 후보: `{6,10,15}`
- internal validation: 260회 warmup 후 52회 fold 5개
- size eligible: cumulative fold log LR > 0 and positive folds >= 3
- eligible size 중 cumulative log LR 최대 선택
- `1e-12` 이내 동률이면 더 작은 size 선택
- eligible size가 없으면 `ABSTAIN`
- 선택 후 520회 전체로 번호 순위를 다시 계산하고 다음 52회 group 고정

### Seed

- main: `DEV-PG`
- bootstrap: `DEV-PG-CI`
- 기존 DEV, CAL, SEALED 사용 금지

### PASS 기준

Positive:

- availability >= 80%
- activation >= 80%
- median delay <= 520
- direction accuracy >= 80%
- direction trials >= 16000
- mean delta Log Loss > 0 and one-sided 95% lower > 0
- mean delta Brier >= 0 and one-sided 95% lower >= 0

Null:

- false activation <= 0.1%
- one-sided exact 95% upper <= 0.2%

하나라도 실패하면 `PREDICTABLE_GROUP_FAIL`이다.

## 금지사항

별도 사용자 승인 없이 다음을 수행하지 않는다.

- predictable-group Python 구현
- 추가 DEV 실행
- score, window, half-life, prior, fold, size 후보 수정
- full M3 detector 또는 grid
- Gate 2-3P-R4 CAL·SEALED
- threshold 1000 완화
- 실패 seed·scenario 삭제
- 실제 Walk-forward 또는 사용자용 후보 생성
- 모바일 UI·Supabase 개발
- main 병합

## 다음 Gate

사용자 승인 후에만 `Gate 2-3P-R3M-3-2`로 이동해 고정 명세 그대로 Python 구현과 DEV-PG 검증을 수행한다. 결과 통과 전 full M3와 R4는 계속 차단한다.

## 작업 종료 시 누적

- `AGENTS.md`
- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
