# Algorithm Integration Gate A3 Evaluation Specification

상태: `SPEC COMPLETE / EVALUATION NOT AUTHORIZED`

계약: `research-ensemble-evaluation-spec-1.0.0`

작업 브랜치: `docs/algorithm-integration-a3-evaluation-spec`

기준 브랜치: `feature/product-p1-release-candidate`

기준 커밋: `901ececb1add7f55879b6efb744d435fdbc31ced`

## 1. 목적

A2에서 구현된 `RESEARCH_ENSEMBLE`을 실제 평가하기 전에 CONTROL_M0 대비 retrospective prequential 평가설계를 고정한다. A3는 명세 전용 Gate이며 평가 Python 구현, 실제 Walk-forward, parameter 탐색, 실제 사용자 entry 활성화, HTML, CAL, SEALED, 모바일 및 `main` 병합을 수행하지 않는다.

## 2. 상위 잠금

```text
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
P1 acceptance SHA-256 = a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139
A1 contract = research-ensemble-spec-1.0.0
A2 contract = research-ensemble-implementation-1.0.0
A2 tested commit = 15b7eccf6547abc3b12c5d7fc119547768ebda6e
A2 final PR head = bcd0787a517e7801a5bbb9c7def77195286f7d92
A2 merge commit = 901ececb1add7f55879b6efb744d435fdbc31ced
rollback mode = CONTROL_M0
model version = 6.0.0-research
```

A4는 A2의 feature windows, half-life, prequential weight update, contribution caps, uncertainty rule, final logit cap, candidate optimizer와 seed contract를 결과에 따라 변경하지 않는다. 변경이 필요하면 기존 결과를 보존하고 새 contract와 사용자 승인을 받아야 한다.

## 3. 고정 데이터와 target sequence

```text
dataset = data/draws.json
draw range = 1..1230
record count = 1230
data version = draws-2026.06.27-r1
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification status = auto_checked
officially locked = false
minimum history = 299
warm-up targets = 300..351
confirmatory targets = 352..1230
confirmatory target count = 879
```

Warm-up 300..351은 historical family weight support를 만드는 데만 사용하고 성능 집계에서 제외한다. Confirmatory sequence는 352부터 1230까지 누락 없이 오름차순으로 고정한다.

## 4. target-1 cutoff

각 target `t`에서 feature와 weight 입력은 정확히 draw 1..t-1이다. draw t 결과는 prediction과 distribution이 고정된 뒤 metric 계산에만 전달한다.

다음은 hard fail이다.

- feature, weight, registry, seed 또는 candidate 생성에 draw t 이상 사용
- t-1 누락
- duplicate 또는 non-contiguous history
- target sequence 변경
- target별 cutoff hash 불일치

## 5. 고정 평가 프로파일

Primary profile:

```text
profile_id = A3-EMPTY-REGISTRY-HISTORICAL-V1
mode = RESEARCH_ENSEMBLE
ablation_id = ENSEMBLE_FULL
user input registry = approved empty registry
hypothesis registry = approved empty registry
physical adapter = empty
M3 evidence = absent and inactive
```

따라서 confirmatory profile의 active nonuniform component는 M1과 M2 historical layer뿐이다.

CONTROL_M0는 기존 Product P1 exact uniform 6-of-45 distribution과 byte-semantic rollback path다.

## 6. 평가 lane

A4는 다음 10개 고정 lane을 생성한다.

1. `CONTROL_M0`
2. `HISTORICAL_ONLY`
3. `HYPOTHESIS_ONLY`
4. `PHYSICAL_ONLY`
5. `ENSEMBLE_FULL`
6. `ENSEMBLE_MINUS_M1`
7. `ENSEMBLE_MINUS_M2`
8. `ENSEMBLE_MINUS_M3`
9. `ENSEMBLE_MINUS_HYPOTHESES`
10. `ENSEMBLE_MINUS_PHYSICAL`

단일 confirmatory comparison은 `ENSEMBLE_FULL` 대 `CONTROL_M0`다.

Empty-registry profile에서 다음 distribution equivalence를 요구한다.

- `ENSEMBLE_FULL == HISTORICAL_ONLY`
- `ENSEMBLE_FULL == ENSEMBLE_MINUS_M3`
- `ENSEMBLE_FULL == ENSEMBLE_MINUS_HYPOTHESES`
- `ENSEMBLE_FULL == ENSEMBLE_MINUS_PHYSICAL`
- `HYPOTHESIS_ONLY == CONTROL_M0`
- `PHYSICAL_ONLY == CONTROL_M0`

위 equivalence는 score vector와 exact probability distribution에 적용한다. `ablation_id`가 identity와 seed에 포함되므로 candidate sets, seed와 prediction hash의 lane 간 동일성은 요구하지 않는다.

## 7. 실제 사용자 lane 차단

실제 hypothesis 또는 physical value가 포함된 lane은 별도 registry Gate 전까지 실행하지 않는다. 실행 조건은 literal user statement, formula, direction, cap, missing policy, APPROVED registry version, user approval과 registry hash lock이다.

미승인 lane 상태:

```text
LANE_BLOCKED_UNAPPROVED_USER_INPUT
```

이 차단은 empty-registry historical evaluation을 차단하지 않는다.

## 8. 실행 순서

각 confirmatory target에서 다음 순서를 고정한다.

1. dataset, version, hash와 cutoff 검증
2. CONTROL_M0 distribution 생성
3. A2 score bundle과 10개 lane 생성
4. 모든 prediction identity와 distribution hash 고정
5. draw t outcome을 metric 함수에 전달
6. target-level metric row와 diagnostics 기록
7. canonical ordering으로 저장

## 9. 재현성

```text
supported runtimes = Python 3.11, Python 3.12
full repeats per runtime >= 2
network dependency = forbidden
canonical target ordering = ascending
```

runtime과 repeat 간 target sequence, score vector hash, distribution hash, metric-row hash, aggregate metrics, decision과 evaluation manifest hash가 동일해야 한다. Clock와 workflow run ID는 metric 및 decision hash에 포함하지 않는다.

## 10. metric hierarchy

- Primary: joint log-score difference versus CONTROL_M0
- Secondary: marginal Brier difference, calibration diagnostics, temporal stability
- Diagnostic: 10개 ablation, component contribution, deterministic five-set hit counts

정의와 통계판정은 `docs/ALGORITHM_INTEGRATION_A3_METRICS.md`를 따른다. Candidate hit count는 PASS 기준이 아니다.

## 11. evidence와 hash

A4는 최소 다음을 독립 재계산하고 저장한다.

```text
data_hash
target_sequence_hash
lane_manifest_hash
A2_model_source_hash
score_config_hash
per_target_cutoff_hash
per_target_score_vector_hash
per_target_distribution_hash
per_target_metric_row_hash
metric_rows_hash
aggregate_metrics_hash
multiple_comparison_report_hash
evaluation_manifest_hash
decision_hash
```

기존 저장값을 신뢰하지 않고 재계산한다. 하나라도 불일치하면 중단하고 evidence를 보존한다.

## 12. 해석 제한

A4가 PASS해도 다음은 유지한다.

```text
research_only = true
public_release_allowed = false
statistical_edge = false
advantage_status = retrospective research evaluation only
```

A4 PASS는 고정 retrospective sequence의 사전 등록 criterion 통과만 의미한다. 당첨확률 향상, prospective validation, CAL·SEALED 통과 또는 제품 승격을 의미하지 않는다.

## 13. 다음 Gate

A3 완료상태는 `A3_SPEC_COMPLETE`다. 다음 단계는 별도 사용자 승인 후의 `Algorithm Integration Gate A4`, contract `research-ensemble-evaluation-implementation-1.0.0`이다.
