# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R3M-2 Oracle DEV PASS**  
현재 브랜치: `feature/gate2p-r3m2-oracle-engine`  
기준 브랜치: `feature/gate2p-r3m-feasibility-spec`  
관련 Issue: #28  
현재 Draft PR: #29

## 목적

로또 6/45의 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## Gate 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R4: `BLOCKED`
- Gate 2-3P-R3M-1: 승인 완료
- Gate 2-3P-R3M-2: 구현 완료·`ORACLE_PASS`
- Gate 2-3P-R3M-3: 별도 승인 전 차단
- full M3 DEV: 차단
- CAL·SEALED: 차단
- 실제 데이터·모바일 MVP: 차단

현재 모델은 `5.0.0-research`, Feature contract는 `3.0.0`, Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`다.

## R3 실패 잠금

- implementation: `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow: `28489870505`
- report hash: `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash: `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

기존 실패 결과는 변경하지 않는다.

## R3M-2 구현

- exact 6-of-45 group likelihood-ratio
- 520회 oracle evidence horizon
- activation threshold `1000`
- post-activation active life `208`
- deterministic DEV namespace
- positive/null Oracle Gate
- one-sided 95% binomial upper bound
- scope lock

## Oracle DEV 결과

Positive:

- 2,000 series
- 1,837 activated
- activation rate `0.9185` — PASS
- median activation delay `241` — PASS

Null:

- 10,000 series
- 8 false activations
- false activation rate `0.0008` — PASS
- one-sided 95% upper `0.001443000578280491` — PASS

Oracle PASS는 사전에 고정된 oracle 가설의 수학적 가능성을 확인한 결과다. 과거 데이터만으로 그룹을 구성할 수 있다는 의미는 아니다.

## 실행 무결성과 잠금

- implementation commit: `37fd815220ccd363f019f3798366a2060872e073`
- workflow run: `28493929179`
- unit tests: `96 PASS`
- artifact: `8000257623`
- artifact digest: `sha256:6c52c97fbd167a2f2ae22e4d225510cc419985c19e08f283dcdfbd6eaec2dafe`
- report hash: `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash: `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

결과 파일:

- `reports/gate2_3p_r3m2_oracle_dev_summary.json`
- `reports/gate2_3p_r3m2_oracle_dev_lock.json`

## 차단사항

별도 사용자 승인 없이 다음을 진행하지 않는다.

- predictable-group 학습
- primary 4-way detector
- full M3 DEV
- R4 CAL·SEALED
- threshold 완화
- 실패 seed·scenario 삭제
- 실제 Walk-forward
- 모바일 UI
- main 병합

## 다음 Gate

다음 단계는 `Gate 2-3P-R3M-3 predictable-group feasibility`다. 별도 승인 후 past-only training, betting 전 group 고정, group size `{6, 10, 15}`, positive/null DEV, 방향정확도·Log Loss·Brier 평가만 진행한다.

## 링크

- Issue #28: `https://github.com/dpes31/predictive-algorithm/issues/28`
- Draft PR #29: `https://github.com/dpes31/predictive-algorithm/pull/29`
