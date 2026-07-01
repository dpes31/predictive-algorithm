# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R3M-3-1 predictable-group 상세 명세 완료·승인 대기**  
현재 브랜치: `feature/r3m3-predictable-group-spec`  
기준 브랜치: `feature/gate2p-r3m2-oracle-engine`  
관련 Issue: #30  
현재 Draft PR: #31

## 목적

로또 6/45의 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## Gate 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R4: `BLOCKED`
- Gate 2-3P-R3M-1: 승인 완료
- Gate 2-3P-R3M-2: `ORACLE_PASS`
- Gate 2-3P-R3M-3-1: **상세 명세 완료·승인 대기**
- Gate 2-3P-R3M-3-2: 미승인·미구현·미실행
- full M3 DEV, CAL, SEALED, 실제 데이터, 모바일 MVP: 차단

현재 모델은 `5.0.0-research`, predictable-group contract는 `1.0.0`, Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`다.

## 이전 잠금

R3 실패:

- implementation `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow `28489870505`
- report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

Oracle PASS:

- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- tests `96 PASS`
- positive activation `91.85%`
- null false activation `0.08%`
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

이전 결과와 hash는 변경하지 않는다.

## R3M-3-1 고정 명세

### 학습과 freeze

- global block grid: `521 + 52k`
- outer learning window: 완료된 과거 520회
- retraining: 52회 boundary에서만
- group freeze: 다음 52회 전체
- missing/invalid window: `ABSTAIN`

### 번호 점수

```text
p0 = 6/45
half-life = 104
prior strength = 52
w(t) = 2^[-age/104]
p_hat = [52*p0 + sum(w*x)] / [52 + sum(w)]
score = logit(p_hat) - logit(p0)
```

점수 동률 `1e-12` 이내는 낮은 번호 우선이다.

### Group size

- 후보 `{6,10,15}`
- internal validation: initial 260회 + 52회 fold 5개
- eligible: cumulative fold log LR > 0 and positive folds >= 3
- eligible size 중 cumulative log LR 최대
- 동률은 작은 size 우선
- eligible size 없음: `ABSTAIN`
- 선택 후 520회 전체 점수로 final group 생성

### e-process

- exact group LR, lift 1.25
- evaluation horizon 520회
- activation threshold 1000
- post-activation active life 208회
- abstain LR 1

### DEV 계약

Positive:

- P4 regime reversal
- series 1230
- change point 615
- evaluation 625~1144
- replicates 2000

Null:

- exact uniform 6-of-45
- 동일 evaluation interval
- replicates 10000

Seed:

- `DEV-PG`
- `DEV-PG-CI`
- 기존 DEV, CAL, SEALED 금지

### PASS 기준

- group availability >= 80%
- activation rate >= 80%
- median delay <= 520
- direction accuracy >= 80%
- direction trials >= 16000
- mean delta Log Loss > 0 and one-sided lower > 0
- mean delta Brier >= 0 and one-sided lower >= 0
- null false activation <= 0.1%
- null exact one-sided upper <= 0.2%

모두 만족해야 `PREDICTABLE_GROUP_PASS`다. 하나라도 실패하면 `PREDICTABLE_GROUP_FAIL`이며 기준완화나 부분통과는 허용하지 않는다.

## 명세 파일

- `docs/GATE2_PREDICTABLE_GROUP_FEASIBILITY_SPEC.md`
- `docs/GATE2_PREDICTABLE_GROUP_VALIDATION_PROTOCOL.md`

## 현재 금지

- predictable-group Python 구현
- 추가 DEV 실행
- score/window/half-life/prior/fold/size 후보 수정
- full M3 detector 또는 grid
- R4 CAL·SEALED
- 실제 Walk-forward
- 사용자용 번호 생성
- 모바일 UI
- main 병합

## 다음 Gate

사용자 승인 후에만 `Gate 2-3P-R3M-3-2`에서 명세 그대로 Python 구현과 DEV-PG 검증을 진행한다. 결과 통과 전 full M3와 R4는 계속 차단한다.

## 링크

- Issue #30: `https://github.com/dpes31/predictive-algorithm/issues/30`
- Draft PR #31: `https://github.com/dpes31/predictive-algorithm/pull/31`
