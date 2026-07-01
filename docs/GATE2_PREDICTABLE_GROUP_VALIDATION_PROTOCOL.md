# Gate 2-3P-R3M-3 Predictable-Group Validation Protocol

상태: 사용자 검토용 사전등록 검증계약  
작성일: 2026-07-01  
모델: `5.0.0-research`

## 고정 learner

- outer window: 520
- half-life: 104
- prior strength: 52
- internal validation: 260 warmup + 5 folds x 52
- group sizes: 6, 10, 15
- betting block: 52
- evaluation horizon: 520
- lift: 1.25
- activation threshold: 1000
- active life: 208

이번 Gate에는 hyperparameter grid가 없다.

## 실행 규모

- positive P4 series: 2,000
- null series: 10,000
- bootstrap resamples: 10,000
- namespace: `DEV-PG`, `DEV-PG-CI` only

## Positive PASS

다음을 모두 만족해야 한다.

```text
group availability >= 0.80
activation rate >= 0.80
median activation delay <= 520
direction accuracy >= 0.80
direction trials >= 16000
mean delta Log Loss > 0
one-sided 95% lower delta Log Loss > 0
mean delta Brier >= 0
one-sided 95% lower delta Brier >= 0
```

Abstain block은 availability에는 실패로 반영하고 Log Loss와 Brier delta는 0으로 반영한다.

## Null PASS

다음을 모두 만족해야 한다.

```text
false activation rate <= 0.001
one-sided exact 95% upper <= 0.002
```

Upper bound는 R3M-2와 동일한 one-sided Clopper-Pearson 방식이다.

## Unit-test PASS

다음 항목이 모두 통과해야 DEV를 실행할 수 있다.

- score formula
- score tie lower-number rule
- fold boundaries
- group-size eligibility
- group-size tie smaller-size rule
- no eligible size -> ABSTAIN
- 52-draw group freeze
- fixed retraining boundary
- leakage rejection
- invalid window -> ABSTAIN
- exact LR null expectation = 1
- abstain LR = 1
- namespace rejection for CAL and SEALED
- deterministic reproduction
- active life 208 preservation

## Aggregate decision

모든 positive, null, unit-test, scope-lock 조건을 통과하면:

```text
PREDICTABLE_GROUP_PASS
```

하나라도 실패하면:

```text
PREDICTABLE_GROUP_FAIL
```

부분통과, 조건부통과, 기준완화는 허용하지 않는다.

## Scope lock

Canonical report에서 다음이 모두 false여야 한다.

- full M3 DEV executed
- CAL executed
- SEALED executed
- real data executed
- mobile work executed
- public release allowed
- main merge performed

Final distribution은 `M0_ONLY`여야 한다.

## 필수 보고

- size 6, 10, 15 선택 block 수
- abstain block 수
- size별 eligible count
- fold positive-count 분포
- CV score 평균과 quantile
- activation rate와 delay
- direction hits와 trials
- Log Loss와 Brier 평균 및 lower bound
- null false activation과 exact upper bound
- seed manifest hash
- implementation, workflow, artifact, report, lock hash

특정 size의 결과가 낮다는 이유로 사후 제외하지 않는다.

## Stop condition

어느 통과기준이라도 실패하거나 leakage, seed 비재현, hash 불일치, scope 위반이 발견되면 full M3로 이동하지 않는다.

PASS하더라도 primary 4-way mixture, full M3 DEV, CAL, SEALED, 실제 데이터, 모바일 UI, main 병합은 별도 승인 전까지 차단한다.
