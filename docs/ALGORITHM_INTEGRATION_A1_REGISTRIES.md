# Algorithm Integration A1 Registry Contracts

상태: `SPEC COMPLETE / USER REVIEW`

계약 버전:

```text
hypothesis-registry-1.0.0
user-input-registry-1.0.0
user-physical-adapter-1.0.0
```

## 1. 목적

사용자가 제공한 관점과 물리변수를 임의 해석이나 추가 수집 없이 재현 가능한 입력계약으로 고정한다.

모든 active entry는 사용자가 승인한 내용만 포함한다. 외부 검색, 기관 문의, 모델의 자동 추정으로 registry를 채우지 않는다.

## 2. 공통 registry envelope

모든 registry는 다음 필드를 가진다.

```json
{
  "registry_type": "hypothesis | user_input",
  "contract_version": "...",
  "registry_version": "...",
  "status": "DRAFT | APPROVED | RETIRED",
  "approved_by": "user",
  "approved_at": "ISO-8601 or null",
  "entries": [],
  "registry_hash": "sha256"
}
```

규칙:

- `APPROVED`가 아닌 registry는 RESEARCH_ENSEMBLE에 사용할 수 없다.
- entry 순서는 hash 계산 전에 `entry_id`로 정렬한다.
- float는 canonical JSON으로 직렬화한다.
- registry 내용이 한 글자라도 변경되면 version과 hash를 변경한다.
- 기존 승인 registry를 덮어쓰지 않고 새 version을 만든다.

## 3. user input entry

필수 필드:

```json
{
  "entry_id": "UPI-0001",
  "name": "...",
  "classification": "NUMBER_LEVEL | BALL_SET_LEVEL | DRAW_LEVEL | STATIC_ASSUMPTION | NON_DISCRIMINATIVE_REFERENCE",
  "value_type": "NUMBER_VECTOR | SCALAR | CATEGORY | MAPPING | TIME_SERIES",
  "unit": "... or null",
  "value": null,
  "number_mapping": null,
  "applicable_draws": {"from": null, "to": null},
  "source_type": "USER_SUPPLIED",
  "user_statement_reference": "literal summary",
  "supplied_at": "ISO-8601",
  "approved_for_scoring": false,
  "allowed_hypothesis_ids": [],
  "missing_policy": "ZERO_AND_FLAG | ABSTAIN_COMPONENT | ABSTAIN_RUN",
  "entry_hash": "sha256"
}
```

### 3.1 분류 규칙

`NUMBER_LEVEL`

- 번호 1..45에 대응하는 값 또는 명시적 부분집합 mapping이 존재한다.
- 직접 번호점수로 변환할 수 있는 유일한 기본 분류다.

`BALL_SET_LEVEL`

- 볼 세트별 값이다.
- 해당 회차의 볼 세트와 번호 mapping이 사용자가 제공된 경우에만 번호점수 가능하다.

`DRAW_LEVEL`

- 회차 전체에 공통인 값이다.
- 단독으로는 번호순위를 만들 수 없다.
- 승인된 hypothesis의 strength 또는 regime 조건만 조절할 수 있다.

`STATIC_ASSUMPTION`

- 일반 물리조건 또는 모델 가정이다.
- simulation 또는 설명에만 사용한다.
- 직접 contribution은 0이다.

`NON_DISCRIMINATIVE_REFERENCE`

- 모든 번호에 동일하게 적용되어 순위를 만들 수 없는 참고값이다.
- 예: 번호별 실측 차이가 없는 공통 nominal 무게.
- 직접 contribution은 반드시 0이다.

### 3.2 미제공값 처리

- missing을 0, 평균 또는 모델 추정값으로 임의 대체하지 않는다.
- `ZERO_AND_FLAG`: contribution 0, diagnostics 기록
- `ABSTAIN_COMPONENT`: 해당 physical/hypothesis component 전체 0
- `ABSTAIN_RUN`: RESEARCH_ENSEMBLE 전체 CONTROL_M0 fallback

## 4. hypothesis entry

필수 필드:

```json
{
  "hypothesis_id": "HYP-0001",
  "version": "1.0.0",
  "status": "DRAFT | ACTIVE | DIAGNOSTIC | RETIRED",
  "statement": "사용자 관점의 명확한 문장",
  "rationale": "검증되지 않은 가설임을 포함한 설명",
  "source_type": "USER_APPROVED",
  "input_entry_ids": [],
  "transform_type": "LINEAR_NUMBER_SCORE | SIGNED_NUMBER_SCORE | RANK_BUCKET | DRAW_STRENGTH_MODIFIER | BALL_SET_NUMBER_MAP | ADDITIVE_PROJECTION",
  "formula": "machine-readable expression id",
  "parameters": {},
  "expected_direction": "POSITIVE | NEGATIVE | USER_DEFINED",
  "applicable_scope": {},
  "required": false,
  "minimum_support": 0.0,
  "single_hypothesis_cap": 0.10,
  "missing_policy": "ZERO_AND_FLAG | ABSTAIN_COMPONENT | ABSTAIN_RUN",
  "contradiction_policy": "SHRINK | ABSTAIN | FLAG_ONLY",
  "approved_by": "user",
  "approved_at": "ISO-8601 or null",
  "hypothesis_hash": "sha256"
}
```

### 4.1 상태

- `DRAFT`: 문서화만 됐으며 실행 금지
- `ACTIVE`: 사용자가 수식과 방향까지 승인했으며 실행 가능
- `DIAGNOSTIC`: contribution 0, diagnostics만 생성
- `RETIRED`: 신규 실행 금지, 과거 hash 재현용으로 보존

### 4.2 transform contract

`LINEAR_NUMBER_SCORE`

```text
score_i = direction * normalized(input_i)
```

`SIGNED_NUMBER_SCORE`

```text
score_i = approved sign map(number i) * normalized(input_i)
```

`RANK_BUCKET`

- 사용자가 승인한 fixed bucket boundary만 사용한다.
- 결과를 보고 boundary를 변경하지 않는다.

`DRAW_STRENGTH_MODIFIER`

- 번호 간 순위를 새로 만들지 않는다.
- 다른 approved number-level score의 강도만 `[0,1]` 범위에서 축소한다.
- 1보다 크게 증폭할 수 없다.

`BALL_SET_NUMBER_MAP`

- 사용자 제공 ball-set ID와 number mapping이 모두 필요하다.
- mapping이 없으면 abstain한다.

`ADDITIVE_PROJECTION`

- pair/group 관점을 45개 번호 additive score로 투영하는 식이 명시돼야 한다.
- 조합별 별도 상호작용확률은 A1 v1에서 허용하지 않는다.

### 4.3 기여상한

```text
single hypothesis absolute cap <= 0.10
all active hypotheses aggregate absolute cap <= 0.25
```

- entry cap 합이 0.25를 넘으면 registry validation fail이다.
- cap은 empirical result를 본 뒤 늘리지 않는다.
- `DIAGNOSTIC` entry의 cap은 0이다.

## 5. physical adapter mapping

Physical field entry는 추가로 다음을 가진다.

```json
{
  "field_id": "PHY-0001",
  "input_entry_id": "UPI-0001",
  "normalization": "CROSS_SECTIONAL_Z_CLIP_3 | USER_FIXED_SCALE | NONE",
  "direction_source": "HYPOTHESIS_ONLY",
  "field_cap": 0.05,
  "number_discriminative": false,
  "adapter_status": "ACTIVE | ZERO_REFERENCE | ABSTAIN"
}
```

검증:

- `direction_source`는 항상 `HYPOTHESIS_ONLY`다.
- adapter 코드가 무거운 공이 유리/불리하다는 방향을 임의 선택할 수 없다.
- 45개 값의 분산이 0이면 `ZERO_REFERENCE`다.
- 부분 번호 mapping은 미매핑 번호를 추정하지 않는다.
- 부분 mapping을 허용하려면 hypothesis에 명시된 missing policy를 적용한다.
- field cap은 최대 0.05, aggregate physical cap은 최대 0.15다.

## 6. 승인되지 않은 값 차단

다음은 hard fail이다.

- registry에 없는 input entry가 active payload에 존재
- `source_type`이 `USER_SUPPLIED`가 아님
- hypothesis가 참조하지 않는 physical direction
- 승인시각 없는 ACTIVE hypothesis
- hash 불일치
- 1..45 밖의 number key
- 중복 number key
- NaN, infinity 또는 unit 불일치
- 사용자가 제공하지 않은 값을 default로 생성

## 7. 사용자 관점의 최초 등록 절차

A2 구현 전 별도 문서 검토로 다음을 수행한다.

1. 기존 대화·저장소에 명시적으로 남은 사용자 관점 후보를 수집한다.
2. 문장을 임의 확장하지 않고 literal summary로 작성한다.
3. 각 관점이 번호점수를 만들 수 있는지 분류한다.
4. 필요한 입력이 실제로 사용자 제공 범위에 있는지 확인한다.
5. 수식·방향·cap·missing policy를 사용자에게 제시한다.
6. 사용자가 승인한 entry만 `ACTIVE`로 변경한다.
7. 승인 registry version과 hash를 잠근다.

이번 A1 Gate에서는 실제 사용자 관점 entry를 임의 생성하거나 ACTIVE로 승인하지 않는다.

## 8. 예시 — 비차별적 공통값

```json
{
  "entry_id": "UPI-BALL-NOMINAL-WEIGHT",
  "classification": "NON_DISCRIMINATIVE_REFERENCE",
  "value_type": "SCALAR",
  "source_type": "USER_SUPPLIED",
  "approved_for_scoring": false,
  "missing_policy": "ZERO_AND_FLAG"
}
```

이 entry는 기록·simulation 설명에는 사용할 수 있지만 번호 ranking contribution은 0이다.

## 9. 예시 — 번호별 사용자 제공값

번호별 값이 실제 제공된 경우에만 다음 구조를 사용할 수 있다.

```json
{
  "entry_id": "UPI-NUMBER-PHYSICAL-VECTOR-V1",
  "classification": "NUMBER_LEVEL",
  "value_type": "NUMBER_VECTOR",
  "number_mapping": {"1": 0.0, "2": 0.0},
  "source_type": "USER_SUPPLIED",
  "approved_for_scoring": true,
  "allowed_hypothesis_ids": ["HYP-EXAMPLE"],
  "missing_policy": "ABSTAIN_COMPONENT"
}
```

위 값은 형식 예시이며 실제 사용자 입력으로 간주하지 않는다.

## 10. hash

```text
entry_hash = SHA256(canonical entry without entry_hash)
registry_hash = SHA256(contract_version, registry_version, sorted entry_hashes)
user_input_hash = registry_hash of approved user inputs
hypothesis_registry_hash = registry_hash of approved hypotheses
physical_adapter_config_hash = SHA256(sorted adapter mappings)
```

이 hash들은 RESEARCH_ENSEMBLE score vector와 prediction hash에 반드시 포함한다.
