# Algorithm Integration Gate A1 Detailed Specification

상태: `SPEC COMPLETE / USER REVIEW`

작성일: 2026-07-03

작업 브랜치: `docs/algorithm-integration-a1-spec`

기준 브랜치: `feature/product-p1-release-candidate`

기준 병합 커밋: `9d6766d21e51758cca1840c8098645d0e0ee8042`

계약 버전: `research-ensemble-spec-1.0.0`

구현 후보 모델 버전: `6.0.0-research` — 예약만 하며 이번 Gate에서 활성화하지 않는다.

## 1. 목적

현재 제품의 exact 6-of-45 조합수학, deterministic seed, 5세트 optimizer와 P1 rollback 경로를 유지하면서 다음을 하나의 연구용 점수경로로 연결하기 위한 구현 명세를 고정한다.

- 과거 당첨번호에서 계산되는 M1 persistence, M2 reversal, M3 regime feature
- 사용자가 명시적으로 제공한 물리변수
- 사용자가 승인한 관점과 가설
- 불확실성 수축, component abstention, run-level abstention
- 구성요소별 contribution과 ablation

이번 Gate는 문서·계약만 작성한다. Python 구현, Walk-forward, HTML, CAL, SEALED, 모바일 및 `main` 병합을 수행하지 않는다.

## 2. 상위 잠금과 영구 금지

다음을 변경하지 않는다.

```text
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
P1 acceptance SHA-256 = a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139
data version = draws-2026.06.27-r1
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
CONTROL_M0 = existing P1 behavior
```

영구 금지:

- 외부 당첨결과 사이트 접속과 재시도
- 운영기관·방송사·제조사 등 외부기관 문의
- 새로운 공식·비공식 데이터 출처 탐색
- 사용자가 제공하지 않은 물리변수 수집 또는 추정
- B2~B5를 알고리즘 개발의 차단조건으로 복원
- 기존 실패결과·hash·report·lock·rollback 수정 또는 삭제

외부 대조는 더 이상 A1 연구·구현의 선행조건이 아니다. 기존 데이터 상태를 공식잠금으로 과장하지 않고 `auto_checked`로 유지한다.

## 3. 현재 문제 정의

현재 `product/run_prediction.py`는 45개 logits를 모두 `0.0`으로 생성한다. 과거 회차는 data hash, cutoff와 seed에만 사용되고 번호별 비균등 점수에는 사용되지 않는다.

A1은 제품 앞단에 다음 계층을 추가하도록 명세한다.

```text
past-only feature snapshot
-> historical component M1/M2/M3
-> approved hypothesis component
-> user-supplied physical component
-> uncertainty shrinkage
-> centered and clipped 45-number logits
-> exact FixedSizeDistribution(k=6)
-> existing deterministic five-set optimizer
```

## 4. 실행모드

### 4.1 CONTROL_M0

- 기존 P1 runner와 byte-level 의미를 유지한다.
- logits 45개는 모두 0이다.
- product weights는 `M0=1`, 나머지 0이다.
- 기존 seed·hash·5세트 결과를 변경하지 않는다.
- 항상 rollback 기준이다.

### 4.2 RESEARCH_ENSEMBLE

- 새 45-number score contract를 사용한다.
- `research_only=true`
- `public_release_allowed=false`
- `statistical_edge=false`
- `advantage_status="미검증 연구 점수"`
- 사용자가 명시적으로 research mode를 선택한 경우에만 실행한다.
- 기본모드는 구현 후에도 `CONTROL_M0`다.

RESEARCH_ENSEMBLE의 번호순위와 조합확률은 연구출력이며 당첨확률 개선을 주장하지 않는다.

## 5. 45-number score interface

계약 ID: `score-45-1.0.0`

### 5.1 입력

```text
target_draw_no
records ending exactly at target_draw_no - 1
data_version / data_hash
feature_contract_version
historical_config
user_input_registry
hypothesis_registry
mode
```

### 5.2 출력

정확히 번호 `1..45` 각각에 대해 다음을 반환한다.

```text
number
m1_raw / m1_normalized
m2_raw / m2_normalized
m3_raw / m3_normalized / m3_eligible
historical_contribution
hypothesis_contribution
physical_contribution
uncertainty_rate
pre_center_logit
final_logit
component_reasons
```

전역 출력:

```text
active_components
abstained_components
run_abstained
run_abstention_reasons
component_caps
component_support
feature_snapshot_hash
user_input_hash
hypothesis_registry_hash
score_config_hash
score_vector_hash
```

### 5.3 공통 불변조건

- 45개 번호가 정확히 한 번씩 존재한다.
- 모든 값은 finite다.
- 미래 회차 데이터가 하나라도 포함되면 hard fail한다.
- 각 component score는 cross-sectional mean 0으로 정규화한다.
- 정규화된 component는 `[-1, 1]`로 clip한다.
- 최종 logits의 평균은 부동소수점 허용오차 `1e-12` 이내에서 0이다.
- 최종 logits는 `[-0.35, 0.35]`로 clip한다.
- 같은 입력·버전·registry·config는 동일 score vector와 hash를 생성한다.

## 6. 과거 당첨번호 feature contract

현재 `engine/feature_engineering.py`의 leakage-safe feature를 재사용한다.

### 6.1 M1 persistence feature

```text
z_recent_10
z_recent_30
z_recent_52
z_recent_104
z_long
z_trend_10_52
z_trend_30_104
```

M1 sub-expert는 해당 feature의 부호를 그대로 사용한다.

### 6.2 M2 reversal feature

```text
-z_recent_10
-z_recent_30
-z_recent_52
-z_recent_104
-z_trend_10_52
-z_trend_30_104
+z_gap
```

M2는 persistence와 별도 component로 유지한다. 같은 feature를 상쇄시키기 위해 고정 50:50 평균하지 않는다.

### 6.3 M3 regime feature

```text
z_shift_52
z_shift_104
z_ewma_minus_long
signed_cusum_score
```

M3는 다음 조건에서만 eligible이다.

```text
change evidence is pre-target only
change gate is calibrated by an already registered method
change gate is active
no post-draw field is present
```

조건을 충족하지 않으면 `M3_ABSTAIN`이며 M3 contribution은 정확히 0이다.

과거 `PREDICTABLE_GROUP_FAIL` 모델의 threshold, window, half-life, prior, fold, group-size를 변경해 M3 eligibility를 만들지 않는다. 해당 모델은 A1 입력으로 사용하지 않는다.

### 6.4 M1·M2·M3 family weight

고정 임의가중치 대신 기존 bounded sequential loss update를 사용한다.

각 과거 시점에서 target 이전 데이터만으로 각 family의 exact combination log loss를 계산하고 M0 baseline과 비교한다. 기존 `engine/weights.py`의 다음 고정식을 재사용한다.

```text
difference = clip(loss_family - loss_M0, -5, 5)
raw_weight = previous_weight^0.995 * exp(-0.10 * difference)
raw_weight = max(0.01, raw_weight)
normalized_weight = raw_weight / sum(raw_weights)
```

규칙:

- 최소 history는 기존 `299`를 유지한다.
- 각 시점의 weight는 해당 시점 결과를 보기 전에 고정한다.
- M3가 abstain이면 M3 weight를 0으로 만들고 M1·M2 사이에서만 정규화한다.
- 현재 target의 결과는 weight 계산에 사용하지 않는다.
- loss sequence와 최종 family weights는 hash 대상이다.

### 6.5 historical component

각 family의 번호별 mixture marginal이 아니라 number logit vector를 동일 공간에서 합성한다.

```text
H_i = w_M1 * normalize(M1_i)
    + w_M2 * normalize(M2_i)
    + w_M3 * normalize(M3_i)
```

`H_i`는 다시 mean-center 후 `[-1,1]`로 clip한다.

Historical component 전체 기여상한은 다음과 같다.

```text
historical_budget = 0.60
```

## 7. 사용자 관점 component

사용자 관점은 자유서술을 코드에 직접 삽입하지 않는다. 승인된 hypothesis registry entry만 실행 가능하다.

```text
U_i = sum(active hypothesis contribution for number i)
```

규칙:

- 단일 hypothesis의 절대 기여상한은 `0.10`이다.
- 전체 hypothesis component의 절대 기여상한은 `0.25`다.
- 입력이 없거나 조건을 충족하지 못하면 해당 hypothesis만 abstain한다.
- `required=true` hypothesis 입력이 없으면 RESEARCH_ENSEMBLE 전체가 abstain한다.
- 수식·방향·parameter·input mapping을 registry 밖에서 변경할 수 없다.
- registry 변경은 version과 hash를 변경한다.

상세 registry 계약은 `docs/ALGORITHM_INTEGRATION_A1_REGISTRIES.md`를 따른다.

## 8. 사용자 제공 물리변수 component

계약 ID: `user-physical-adapter-1.0.0`

허용 입력은 사용자가 직접 제공하고 registry에 승인한 값뿐이다.

입력분류:

```text
NUMBER_LEVEL
BALL_SET_LEVEL
DRAW_LEVEL
STATIC_ASSUMPTION
NON_DISCRIMINATIVE_REFERENCE
```

점수 규칙:

- `NUMBER_LEVEL`: 번호별 값이 존재할 때만 cross-sectional score 생성 가능
- `BALL_SET_LEVEL`: 번호와 ball-set mapping이 함께 승인된 경우에만 번호점수 가능
- `DRAW_LEVEL`: 모든 번호에 공통이면 직접 순위를 만들 수 없고 hypothesis strength modifier만 가능
- `STATIC_ASSUMPTION`: simulation·설명용이며 직접 점수 0
- `NON_DISCRIMINATIVE_REFERENCE`: 직접 점수 0

공통 nominal 공 무게처럼 45개 번호에 동일한 값은 정확히 0 contribution이다.

번호별 값의 기본 변환:

```text
centered_i = value_i - mean(value_1..value_45)
scale = population standard deviation
z_i = 0 if scale == 0 else centered_i / scale
normalized_i = clip(z_i / 3, -1, 1)
```

방향은 사용자가 승인한 hypothesis entry에서만 결정한다. adapter가 물리적 인과 방향을 임의로 선택하지 않는다.

기여상한:

```text
single physical field <= 0.05
total physical component <= 0.15
```

물리입력이 없거나 비차별적이어도 historical component는 실행할 수 있다. diagnostics에는 `PHYSICAL_ABSTAIN` 사유를 남긴다.

## 9. 통합점수와 uncertainty

번호 i의 사전 점수:

```text
raw_i = 0.60 * H_i + U_i + P_i
```

여기서:

```text
abs(U_i aggregate) <= 0.25
abs(P_i aggregate) <= 0.15
```

누락된 component의 budget은 다른 component에 자동 재분배하지 않는다. 입력이 부족할수록 logit 강도가 자연스럽게 작아진다.

### 9.1 support

각 component는 `support in [0,1]`을 반환한다.

- historical support: 유효 history와 sequential loss coverage
- hypothesis support: registry 조건과 required input 충족률
- physical support: 차별적 번호 coverage와 사용자 승인 mapping 충족률

### 9.2 disagreement

활성 component 중 raw 합계의 부호와 반대되는 절대 기여비율을 `disagreement_i in [0,1]`로 계산한다.

### 9.3 uncertainty shrinkage

```text
support_i = weighted mean of active component support
uncertainty_i = min(0.75,
                    0.35 * (1 - support_i)
                  + 0.40 * disagreement_i)
shrunk_i = raw_i * (1 - uncertainty_i)
```

이후 45개 `shrunk_i`를 mean-center하고 `[-0.35,0.35]`로 clip하여 `final_logit_i`를 만든다.

## 10. abstention

### 10.1 component abstention

다음 경우 해당 component만 0으로 만든다.

- 입력 미제공
- registry 미승인
- number-discriminative mapping 부재
- support 기준 미달
- M3 gate inactive
- 비finite 계산

비finite 계산은 diagnostics만 남기고 계속하는 것이 아니라 구현 오류로 hard fail한다.

### 10.2 run-level abstention

RESEARCH_ENSEMBLE은 다음 경우 CONTROL_M0로 완전 fallback한다.

- history가 299회 미만
- input last draw가 target-1이 아님
- 미래 데이터 혼입
- data hash 또는 contract hash 불일치
- 미승인 입력이나 hypothesis가 active로 표시됨
- required hypothesis 입력 누락
- 모든 비균등 component가 abstain
- 최종 max absolute logit이 `1e-12` 미만
- score vector에 NaN 또는 infinity 존재

fallback 결과에는 원래 요청 mode와 fallback 사유를 모두 기록한다.

## 11. exact distribution과 5세트

RESEARCH_ENSEMBLE은 다음 분포를 사용한다.

```text
FixedSizeDistribution(logits=final_logits, pick_count=6)
```

- exact elementary symmetric normalization을 유지한다.
- 후보 universe와 deterministic optimizer는 기존 엔진을 사용한다.
- joint probability와 lift는 실제 final distribution에서 계산한다.
- near-tie와 diversity 정책을 변경하지 않는다.
- pair·group interaction은 A1 v1에서 조합확률을 직접 수정하지 않는다.
- pair·group hypothesis는 번호별 additive projection이 명시된 경우에만 사용 가능하다.

## 12. contribution diagnostics

각 번호와 후보세트에 다음을 제공한다.

```text
historical contribution
M1/M2/M3 family contribution
hypothesis contribution by hypothesis_id
physical contribution by field_id
uncertainty shrink amount
final logit
candidate probability
candidate diversity selection effect
```

후보세트 contribution은 포함된 6개 번호의 component logit 합과 optimizer의 diversity 선택 사유를 분리한다.

## 13. ablation contract

동일 target과 동일 frozen input을 대상으로 다음 ablation ID를 지원하도록 구현한다.

```text
CONTROL_M0
HISTORICAL_ONLY
HYPOTHESIS_ONLY
PHYSICAL_ONLY
ENSEMBLE_FULL
ENSEMBLE_MINUS_M1
ENSEMBLE_MINUS_M2
ENSEMBLE_MINUS_M3
ENSEMBLE_MINUS_HYPOTHESES
ENSEMBLE_MINUS_PHYSICAL
```

각 ablation은 별도 `ablation_hash`와 derived seed를 사용한다. ablation 결과를 full ensemble 결과로 가장하지 않는다.

A1 명세 단계에서는 ablation을 실행하지 않는다.

## 14. version과 hash

고정 계약:

```text
integration_contract_version = research-ensemble-spec-1.0.0
score_contract_version = score-45-1.0.0
hypothesis_registry_contract = hypothesis-registry-1.0.0
physical_adapter_contract = user-physical-adapter-1.0.0
output_schema_version = research-ensemble-output-1.0.0
```

RESEARCH_ENSEMBLE 필수 hash:

```text
data_hash
feature_snapshot_hash
historical_loss_sequence_hash
historical_weight_hash
user_input_hash
hypothesis_registry_hash
physical_adapter_config_hash
score_config_hash
score_vector_hash
ablation_manifest_hash
model_source_hash
prediction_hash
```

Research seed:

```text
SHA256(
  integration_contract_version,
  data_hash,
  feature_snapshot_hash,
  user_input_hash,
  hypothesis_registry_hash,
  score_config_hash,
  target_draw_no,
  mode,
  ablation_id
)
```

CONTROL_M0 seed와 prediction hash는 기존 P1 계약을 유지한다.

## 15. rollback

Rollback anchor:

```text
base merge commit = 9d6766d21e51758cca1840c8098645d0e0ee8042
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
fallback mode = CONTROL_M0
```

구현 결함이나 acceptance 실패 시:

- A1 구현 브랜치만 revert한다.
- P1 runner·report·lock을 수정하지 않는다.
- CONTROL_M0를 기본모드로 유지한다.
- 실패 report와 hash를 삭제하지 않는다.
- 새 계약이 필요하면 version을 올리고 별도 Gate를 연다.

## 16. 구현 경계

사용자 별도 승인 후에만 다음 구현 Gate로 이동한다.

```text
Algorithm Integration Gate A2
scope = Python implementation and unit tests only
```

A2 승인 전 금지:

- Python 파일 생성·수정
- 실제 또는 과거 Walk-forward
- hyperparameter 탐색
- CAL·SEALED
- HTML·모바일 UI
- `main` 병합
