# Algorithm Integration Gate A1 Acceptance and Rollback Contract

상태: `SPEC COMPLETE / IMPLEMENTATION NOT AUTHORIZED`

계약: `research-ensemble-spec-1.0.0`

## 1. 목적

후속 Algorithm Integration Gate A2 구현이 명세를 준수하는지 판정할 고정 기준을 정의한다. 이번 A1에서는 테스트·실행·판정을 수행하지 않는다.

## 2. 판정 상태

```text
A1_SPEC_COMPLETE
A2_IMPLEMENTATION_PASS
A2_IMPLEMENTATION_FAIL
A2_IMPLEMENTATION_BLOCKED
```

- `A1_SPEC_COMPLETE`: A1 문서·report·lock이 일치하고 사용자 승인 대기
- `A2_IMPLEMENTATION_PASS`: I1~I24 전부 PASS
- `A2_IMPLEMENTATION_FAIL`: 평가된 기준 중 하나 이상 FAIL
- `A2_IMPLEMENTATION_BLOCKED`: 사용자 승인 입력 또는 필수 기존 코드가 없어 평가 불가능

Conditional PASS와 waiver는 없다.

## 3. 구현 통과기준 I1~I24

### 계약·범위

```text
I1  integration contract가 research-ensemble-spec-1.0.0과 일치
I2  구현 브랜치가 승인된 A1 spec commit을 base로 사용
I3  Python 구현·테스트 외 Walk-forward/HTML/CAL/SEALED/mobile/main 변경 0
I4  외부접속·외부기관 문의·새 출처탐색 코드 또는 workflow 0
```

### CONTROL_M0 보존

```text
I5  CONTROL_M0 output이 P1 canonical case와 byte-identical
I6  CONTROL_M0 seed/config/model/prediction hash 의미가 P1과 동일
I7  RESEARCH_ENSEMBLE 미지정 시 default mode가 CONTROL_M0
```

### 45-number score

```text
I8  번호 1..45가 정확히 한 번씩 존재
I9  모든 component와 final logit이 finite
I10 component mean-centering과 [-1,1] clip 통과
I11 final logits mean 0 오차 <= 1e-12, 범위 [-0.35,0.35]
I12 동일 입력 5회 반복 및 Python 3.11/3.12 score_vector_hash 동일
```

### 과거 feature와 누출

```text
I13 input_last_draw == target_draw_no - 1 강제
I14 target 이상 회차, 누락 target-1, duplicate, false cutoff 모두 hard fail
I15 M1/M2 feature 명칭·부호가 A1 고정값과 일치
I16 sequential family weight가 target 결과 없이 prequential하게 계산
I17 M3 inactive/unapproved이면 exact zero contribution
I18 frozen PREDICTABLE_GROUP_FAIL parameter와 report/hash 변경 0
```

### registry와 physical adapter

```text
I19 DRAFT/DIAGNOSTIC/RETIRED hypothesis가 active score에 영향 0
I20 registry 밖 입력·미승인 source·hash mismatch hard fail
I21 모든 번호에 동일한 physical scalar/vector contribution이 exact zero
I22 single hypothesis <=0.10, hypothesis aggregate <=0.25,
    single physical field <=0.05, physical aggregate <=0.15,
    historical budget <=0.60
```

### diagnostics·ablation·rollback

```text
I23 component contribution 합, uncertainty shrink, final logit 재계산 가능
I24 모든 지정 ablation 생성 가능하고 실패 시 CONTROL_M0 rollback 가능
```

## 4. 필수 negative fixtures

후속 구현은 최소 다음 negative case를 독립적으로 검증한다.

1. 44개 또는 46개 number score
2. duplicate number key
3. number 0 또는 46
4. NaN/infinity component
5. target draw record 포함
6. target-1 record 누락
7. duplicate historical draw
8. unapproved hypothesis ACTIVE 위조
9. registry hash 위조
10. user input source type 위조
11. physical adapter가 common scalar에 nonzero score 생성
12. single hypothesis cap 0.10 초과
13. hypothesis aggregate 0.25 초과
14. physical field cap 0.05 초과
15. physical aggregate 0.15 초과
16. historical budget 0.60 초과
17. M3 inactive 상태에서 nonzero contribution
18. required hypothesis input 누락
19. all components abstain인데 research output 생성
20. CONTROL_M0 결과 변경
21. external URL 또는 network client dependency 추가
22. prior report/lock 변경

모든 negative fixture는 예상된 exception code 또는 fallback reason을 가져야 한다.

## 5. 필수 positive fixtures

1. historical-only RESEARCH_ENSEMBLE
2. M1 우세 prequential weight 예시
3. M2 우세 prequential weight 예시
4. M3 inactive abstention 예시
5. 승인된 number-level user input 예시
6. 비차별적 physical value zero contribution 예시
7. hypothesis missing `ZERO_AND_FLAG` 예시
8. hypothesis missing `ABSTAIN_COMPONENT` 예시
9. required input 누락 run fallback 예시
10. full ensemble contribution 재계산 예시
11. 10개 ablation ID deterministic 예시
12. CONTROL_M0 canonical regression fixture

예시는 synthetic fixture일 수 있으나 실제 예측력 증거로 표현하지 않는다.

## 6. 재현성 계약

후속 A2 구현은 다음을 만족한다.

```text
supported Python = 3.11, 3.12
repeats per runtime >= 5
canonical JSON serialization fixed
random source = deterministic seed only
network access = forbidden
clock value excluded from score_vector_hash and prediction_hash
```

`generated_at` 변경은 score vector, candidate sets, seed와 prediction hash를 변경하지 않는다.

다음 변경은 각 hash를 반드시 변경한다.

- target draw
- data hash
- feature snapshot
- user input registry
- hypothesis registry
- score config
- mode
- ablation ID
- model source

## 7. output contract

RESEARCH_ENSEMBLE 필수 최상위 필드:

```text
schema_version
integration_contract_version
mode_requested
mode_effective
fallback_applied
fallback_reasons
target_draw_no
input_last_draw
research_only
public_release_allowed
statistical_edge
advantage_status
candidate_sets
score_vector
component_summary
ablation_summary
versions
hashes
seed
limitations
```

고정 disclosure:

```text
research_only = true
public_release_allowed = false
statistical_edge = false
advantage_status = 미검증 연구 점수
```

CONTROL_M0는 기존 P1 output schema를 변경하지 않는다.

## 8. hash 재계산

검증 harness는 저장된 값을 신뢰하지 않고 다음을 독립 재계산한다.

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

하나라도 불일치하면 `A2_IMPLEMENTATION_FAIL`이다.

## 9. prior failure freeze 검증

다음 파일과 잠금값은 A2 diff 및 hash 비교 대상이다.

```text
reports/gate2_3p3_full_summary.md
reports/gate2_3p_r3_dev_lock.json
reports/gate2_3p_r3m2_oracle_dev_lock.json
reports/gate2_3p_r3m3_predictable_group_dev_lock.json
reports/product_p1_acceptance.json
reports/product_p1_acceptance_lock.json
```

A2는 과거 실패결과를 수정하거나 성공으로 재분류할 수 없다.

## 10. rollback manifest 요구사항

A2 구현 시 다음을 별도 manifest로 기록한다.

```text
spec_base_commit
implementation_branch
implementation_commit
P1_rollback_anchor
CONTROL_M0_entrypoint
new_research_entrypoint
files_added
files_modified
files_forbidden_to_modify
revert_command_or_commit
failure_report_path
```

rollback은 A2 변경만 제거하고 P1과 과거 연구이력을 보존해야 한다.

## 11. 중단규칙

다음 중 하나가 발생하면 구현검증을 중단하고 evidence를 보존한다.

- CONTROL_M0 regression
- future-data leakage
- unapproved input activation
- network access dependency
- prior lock mutation
- nondeterministic score or candidates
- component cap bypass
- hash mismatch

실패 후 같은 결과를 PASS로 만들기 위한 parameter 수정은 별도 사용자 승인과 새 contract version 없이는 금지한다.

## 12. A1 명세 승인조건

A1 명세 자체는 다음 D1~D10을 충족해야 `A1_SPEC_COMPLETE`다.

```text
D1  score-45 contract 정의
D2  M1/M2/M3 통합과 M3 abstention 정의
D3  user-only physical adapter 정의
D4  hypothesis registry와 승인절차 정의
D5  CONTROL_M0 / RESEARCH_ENSEMBLE 분리
D6  uncertainty와 abstention 정의
D7  contribution과 ablation 정의
D8  version/hash/rollback 정의
D9  I1~I24 구현 통과기준 정의
D10 금지범위와 다음 승인경계 정의
```

A1 사용자 승인 전 A2를 시작하지 않는다.
