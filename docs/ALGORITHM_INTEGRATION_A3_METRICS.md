# Algorithm Integration Gate A3 Metrics Contract

상태: `SPEC COMPLETE / METRICS NOT RUN`

계약: `research-ensemble-evaluation-spec-1.0.0`

## 1. Primary metric

Confirmatory target은 352..1230이다. 실제 6개 번호 집합을 `Y_t`, lane m의 target 이전 정보 기반 exact distribution을 `P_m(.|H_t-1)`로 둔다.

```text
JLS_m,t = ln P_m(Y_t | H_t-1)
d_t = JLS_ENSEMBLE_FULL,t - JLS_CONTROL_M0,t
primary estimate = mean(d_t)
```

CONTROL_M0는 모든 조합에 대해 `1 / C(45,6)`이다. Higher joint log score가 더 좋다.

```text
H0: E[d_t] <= 0
H1: E[d_t] > 0
```

## 2. Primary inference

```text
method = circular moving-block bootstrap
block length = 52 targets
replicates = 10000
alpha = 0.05
alternative = one-sided greater
seed = deterministic hash of contract, data hash, target sequence and PRIMARY_MBB
```

879개 `d_t`를 원형 moving blocks로 resample한다. One-sided 95% lower bound는 bootstrap replicate mean의 5th percentile이다.

```text
primary statistical pass = mean(d_t) > 0 and lower bound > 0
```

NaN, infinity, zero outcome probability, target 누락 또는 replicate 수 불일치는 hard fail이다.

## 3. Marginal Brier

번호 i의 inclusion probability를 `p_m,t,i`, 실제 indicator를 `y_t,i`로 둔다.

```text
Brier_m,t = (1/45) * sum_i (p_m,t,i - y_t,i)^2
Brier gain_t = Brier_CONTROL_M0,t - Brier_ENSEMBLE_FULL,t
```

Positive gain이 연구 lane 우위다. Guardrail은 `mean Brier gain >= 0`이다. Brier는 primary criterion을 대체하지 않는다.

## 4. Calibration diagnostics

879 x 45개의 predicted inclusion probability를 안정 정렬해 10개 equal-count bin으로 나눈다. 동률은 target, number 오름차순으로 처리한다.

각 bin에서 mean prediction, empirical inclusion rate, absolute gap과 weighted ECE를 기록한다. 각 target의 inclusion probability 합이 정확히 6인지 독립 검증한다. Calibration은 진단값이며 단독 PASS 기준이 아니다.

## 5. Temporal stability

고정 구간:

```text
Q1 = 352..571
Q2 = 572..791
Q3 = 792..1011
Q4 = 1012..1230
```

각 구간 mean `d_t`를 계산한다.

```text
positive quarters >= 3 of 4
final cumulative joint log-score difference > 0
```

구간 경계는 결과를 보고 변경하지 않는다.

## 6. Ablation metrics

10개 lane 각각에 대해 다음을 산출한다.

- CONTROL_M0 대비 mean joint log-score difference
- one-sided block-bootstrap p-value
- mean marginal Brier gain
- quarter means
- final cumulative difference

Component necessity contrasts:

```text
C1 = ENSEMBLE_FULL - ENSEMBLE_MINUS_M1
C2 = ENSEMBLE_FULL - ENSEMBLE_MINUS_M2
```

C1·C2는 Holm family-wise alpha 0.05를 적용한다. CONTROL_M0를 제외한 9개 research lane 비교도 별도 diagnostic family로 Holm correction한다. Diagnostic significance는 overall PASS 판정을 만들거나 뒤집지 않는다.

## 7. Equivalence assertions

Empty-registry profile에서 canonical distribution hash로 다음을 검증한다.

```text
ENSEMBLE_FULL == HISTORICAL_ONLY
ENSEMBLE_FULL == ENSEMBLE_MINUS_M3
ENSEMBLE_FULL == ENSEMBLE_MINUS_HYPOTHESES
ENSEMBLE_FULL == ENSEMBLE_MINUS_PHYSICAL
HYPOTHESIS_ONLY == CONTROL_M0
PHYSICAL_ONLY == CONTROL_M0
```

적용 가능한 lane은 score-vector hash도 비교한다. Candidate sets, seed와 prediction hash는 equivalence 대상이 아니다.

## 8. Candidate diagnostics

5세트의 matching-number count, 최고 match, 평균 match와 exact-set match를 기록할 수 있다. 이는 기술통계이며 PASS 기준에 사용하지 않는다.

## 9. Multiple-comparison policy

- Confirmatory family: ENSEMBLE_FULL vs CONTROL_M0 한 개, correction 없음
- Component family: C1·C2, Holm correction
- Diagnostic family: 9개 lane-vs-M0, Holm correction
- 사후 metric·subgroup·target subset은 exploratory로만 표시

## 10. Missing policy

879개 target 중 primary row 하나라도 누락되면 aggregate decision을 확정하지 않는다. 부분 결과는 보존한다.

## 11. Canonical fields

Target row:

```text
target_draw_no
input_last_draw
lane_id
joint_log_score
joint_log_score_delta_vs_m0
marginal_brier
marginal_brier_gain_vs_m0
score_vector_hash
distribution_hash
cutoff_hash
metric_row_hash
```

Aggregate report:

```text
primary_mean_delta
primary_lower_95_one_sided
primary_bootstrap_p_value
mean_brier_gain
quarter_means
positive_quarter_count
final_cumulative_delta
component_contrasts
holm_adjusted_results
equivalence_results
calibration_diagnostics
```
