# Gate 2-3P-R3M-3 Predictable-Group Feasibility Specification

상태: 사용자 검토용 상세 명세  
작성일: 2026-07-01  
기준 모델: `5.0.0-research`  
Predictable-group contract: `1.0.0`  
작업 브랜치: `feature/r3m3-predictable-group-spec`  
기준 브랜치: `feature/gate2p-r3m2-oracle-engine`

## 1. 목적

Gate 2-3P-R3M-2 Oracle DEV PASS는 favored group과 변화시점을 알고 있을 때 threshold 1000, detection horizon 520, lift 1.25가 검출 가능함을 확인했다.

이번 Gate는 미래 결과를 보지 않고 과거 당첨번호만으로 다음 52회에 사용할 favored group을 사전에 구성할 수 있는지 검증하기 위한 계약을 고정한다.

이번 작업은 명세만 포함한다. Python 구현, DEV 실행, full M3, CAL, SEALED, 실제 데이터, 모바일 UI, main 병합을 포함하지 않는다.

## 2. 유지되는 상위 계약

- model version: `5.0.0-research`
- exact 6-of-45 distribution
- activation threshold: `1000`
- post-activation active life: `208 draws`
- pre-activation detection horizon: `520 draws`
- lift: `1.25`
- M3 deployable cap: `10%`
- false activation target: `0.1%`
- one-sided 95% upper target: `0.2%`
- final distribution: `M0 only`
- 제품 출력: 6개 번호 × 5세트
- 미래 데이터 누출 금지
- R3 실패결과와 R3M-2 Oracle lock 보존

## 3. Gate 분할

현재 단계는 다음과 같이 분리한다.

```text
Gate 2-3P-R3M-3-1 = detailed specification
Gate 2-3P-R3M-3-2 = future Python implementation and DEV execution
```

R3M-3-1 승인 전 R3M-3-2로 이동하지 않는다.

## 4. 데이터 범위

이 Gate는 번호 이력만 사용한다.

허용 입력:

- 완료된 과거 draw number
- 완료된 과거 당첨번호 6개
- 사전등록된 block boundary

금지 입력:

- 현재 betting block의 결과
- target draw 결과
- 실제 또는 합성 change point를 learner 입력으로 전달
- true favored group
- 추첨기, 볼 세트, 온습도 등 M4 metadata
- CAL 또는 SEALED seed
- 결과를 본 뒤 생성한 feature

과거 draw가 누락, 중복, 범위 오류, 6개 고유번호 조건 위반이면 해당 52회 block은 `ABSTAIN` 처리한다. 보간이나 임의 대체는 금지한다.

## 5. 시간 구조

### 5.1 Global block grid

모든 retraining 시점은 사전에 고정한다.

```text
block_start(k) = 521 + 52k,  k = 0,1,2,...
block_end(k) = block_start(k) + 51
```

첫 모델은 완료된 과거 520회가 존재할 때만 만들 수 있다.

### 5.2 Outer learning window

Betting block 시작을 `b`라 하면 학습창은 정확히 다음이다.

```text
W_b = draws [b-520, ..., b-1]
length = 520 completed draws
```

창 길이는 조정하지 않는다. 260, 1040 등 다른 outer window는 이번 Gate에서 평가하지 않는다.

### 5.3 Group freeze

`b` 직전에 group size와 번호 group을 확정한다.

```text
freeze_time < b
frozen interval = [b, ..., b+51]
```

52회 betting block 도중 group, group size, score, lift를 수정하지 않는다.

### 5.4 Retraining

재학습은 다음 block boundary에서만 수행한다.

```text
b, b+52, b+104, ...
```

중간 재학습, 성과 악화 후 즉시 교체, 사후 restart는 금지한다.

## 6. 번호별 점수식

번호 `n`과 block start `b`에 대해:

```text
x(n,t) = 1  if number n is included in draw t
         0  otherwise
p0 = 6 / 45
half_life = 104 draws
prior_strength = 52
age(t) = b - 1 - t
w(t) = 2 ^ (-age(t) / 104)
```

가중 posterior inclusion probability:

```text
p_hat(n,b) =
  [52*p0 + sum_{t=b-520}^{b-1} w(t)*x(n,t)]
  / [52 + sum_{t=b-520}^{b-1} w(t)]
```

번호 점수:

```text
score(n,b) = logit(p_hat(n,b)) - logit(p0)
logit(p) = log[p / (1-p)]
```

규칙:

- score clipping 금지
- 표준화, winsorization, 번호별 보정 금지
- half-life 104와 prior strength 52 고정
- pair interaction 사용 금지
- physical metadata 사용 금지

## 7. 번호 순위와 동률 처리

번호는 다음 순서로 정렬한다.

1. `score(n,b)` 내림차순
2. 점수 차이가 `1e-12` 이하이면 번호 오름차순

Group cutoff에서 동률이 발생해도 같은 규칙을 적용한다. 무작위 tie-break는 금지한다.

## 8. Group size 후보

허용 group size는 정확히 다음 세 개다.

```text
M = {6, 10, 15}
```

다른 크기는 생성하거나 평가하지 않는다.

## 9. Chronological internal validation

Group size는 target betting block을 사용하지 않고 outer learning window 내부의 과거-only 검증으로 선택한다.

### 9.1 Fold 구조

Outer window 520회를 다음처럼 사용한다.

```text
initial fit prefix = 260 draws
validation folds = 5
fold length = 52 draws
```

Fold `q = 0,...,4`의 validation 시작:

```text
v_q = b - 260 + 52q
validation_q = [v_q, ..., v_q+51]
training_q = [b-520, ..., v_q-1]
```

Training length는 순서대로 260, 312, 364, 416, 468회다.

### 9.2 Fold group

각 fold 시작 직전에 `training_q`만 사용해 번호 점수를 계산한다. 점수식은 제6절과 동일하며 가능한 prefix 길이만 사용한다.

각 `m`에 대해 상위 `m`개 번호를 `F(q,m)`으로 고정하고 다음 52회에 exact group likelihood-ratio를 계산한다.

```text
L(q,m) = sum over validation_q of log LR(draw | F(q,m), lift=1.25)
```

### 9.3 Size eligibility

Group size `m`은 다음을 모두 만족해야 한다.

```text
sum_q L(q,m) > 0
positive_fold_count(m) >= 3 of 5
```

여기서 positive fold는 `L(q,m) > 0`인 fold다. 값이 정확히 0이면 positive로 세지 않는다.

### 9.4 Size selection

Eligible size 중 다음 값을 최대화한다.

```text
CV_score(m) = sum_q L(q,m)
```

동률 규칙:

1. CV score 차이가 `1e-12` 이하이면 더 작은 group size 선택
2. 따라서 우선순위는 6, 10, 15

Eligible size가 없으면 해당 betting block은 `ABSTAIN`이다.

## 10. Final group construction

선택된 size를 `m*`라 한다.

Outer learning window 520회 전체를 사용해 제6절 score를 다시 계산하고 상위 `m*`개 번호를 final group `F_b`로 고정한다.

```text
F_b is fixed before draw b
```

Final group을 만든 뒤 내부 CV를 다시 계산하거나 size를 변경하지 않는다.

## 11. Betting distribution

Non-abstain block은 R3M-2에서 구현된 exact fixed-size alternative를 사용한다.

```text
Q_b(S) proportional to 1.25 ^ |S intersect F_b|
P0(S) = 1 / C(45,6)
LR_b,t = Q_b(S_t) / P0(S_t)
```

Abstain block:

```text
Q_b = P0
LR_b,t = 1
M3 weight = 0
```

## 12. Predictable e-process

Evaluation episode은 520회, 즉 52회 block 10개로 구성한다.

```text
E_0 = 1
E_t = product of predictable LR values through t
activation if E_t >= 1000
```

Group은 각 block 시작 전에 과거만으로 고정되므로 null에서 predictable e-process 조건을 유지한다.

- max component 선택 금지
- 결과 후 best group 선택 금지
- LR clipping 금지
- threshold 완화 금지
- abstain 시 evidence를 1로 유지

Activation 후 active state는 최대 208회지만 이 Gate에서는 deployable prediction을 공개하지 않는다.

## 13. Positive DEV scenario contract

사전등록 positive cell:

```text
scenario = P4 regime reversal
series length = 1230
change point = 615
post-change true favored group = 36..45
lift = 1.25
evaluation origin = 625
evaluation interval = [625, 1144]
positive replicates = 2000
```

Evaluation origin 625는 change point 이후 첫 global 52-grid boundary다. Harness의 평가구간 정의에만 사용하고 learner 입력에는 전달하지 않는다.

## 14. Null DEV scenario contract

```text
scenario = exact uniform 6-of-45
series length = 1230
evaluation origin = 625
evaluation interval = [625, 1144]
null replicates = 10000
```

Positive와 동일한 training, fold, restart, abstain 규칙을 사용한다.

## 15. Seed namespace

R3, R3M-2 Oracle, CAL, SEALED seed와 완전히 분리한다.

Main DEV seed material:

```text
Gate2-3P-R3M-3|5.0.0-research|DEV-PG|
{cell}|{scenario}|{effect}|{replicate}
```

Bootstrap seed material:

```text
Gate2-3P-R3M-3|5.0.0-research|DEV-PG-CI|
{metric}|{replicate_set_hash}
```

허용 namespace:

- `DEV-PG`
- `DEV-PG-CI`

금지 namespace:

- 기존 `DEV`
- `CAL`
- `SEALED`

Seed 목록과 SHA-256 hash를 결과물에 고정한다.

## 16. 방향 정확도

Positive scenario의 non-abstain block마다 predicted exact distribution의 번호별 marginal을 계산한다.

True favored set을 `F*`라 할 때:

```text
mean marginal on F* > mean marginal on complement
```

이면 direction hit다. 같으면 miss다.

```text
direction_accuracy = direction_hits / non_abstain_blocks
```

Abstain block은 direction denominator에 넣지 않지만 별도 availability metric으로 불이익을 받는다.

## 17. Log Loss와 Brier

모든 evaluation draw를 포함한다. Abstain draw는 M0와 동일하므로 delta는 0이다.

```text
delta_log_loss(t) = log Q_t(S_t) - log P0(S_t)
```

번호 marginal Brier:

```text
Brier(P,t) = (1/45) * sum_n [P(n included)-x(n,t)]^2
delta_brier(t) = Brier(P0,t) - Brier(Q_t,t)
```

Series별 520회 평균을 먼저 계산한 뒤 2,000 series 평균을 보고한다.

## 18. Confidence interval rule

Positive series-level mean delta의 one-sided 95% lower bound는 deterministic percentile bootstrap으로 계산한다.

- resamples: `10000`
- sampling unit: complete series
- replacement: yes
- lower bound: empirical 5th percentile
- quantile: nearest-rank
- seed namespace: `DEV-PG-CI`

Bootstrap 결과를 보고 score, window, group size 규칙을 수정하면 실험은 무효다.

## 19. Required reports

향후 R3M-3-2 실행 시 반드시 다음을 기록한다.

- code commit and workflow run
- complete seed-list hash
- positive/null report hash
- group availability
- size 6/10/15/abstain 선택 분포
- fold eligibility 분포
- activation rate and delay
- direction hits/trials
- mean delta Log Loss and lower bound
- mean delta Brier and lower bound
- null false activation and exact upper bound
- all scope-lock flags

## 20. 현재 차단

이 명세 승인 전과 R3M-3-2 결과 통과 전 다음을 진행하지 않는다.

- predictable-group Python 구현
- additional DEV
- primary 4-way full detector
- full M3 grid
- R4 CAL·SEALED
- 실제 데이터
- 사용자용 번호 생성
- 모바일 UI
- main 병합
