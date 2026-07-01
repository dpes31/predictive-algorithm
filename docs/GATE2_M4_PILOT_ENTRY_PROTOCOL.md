# Gate 2-3P-M4F Pilot Entry and Control Protocol

상태: 사용자 검토용 사전등록 계약  
작성일: 2026-07-01  
Contract: `m4-data-feasibility-1.0.0`

## 1. 목적

실제 물리·운영 metadata를 모델에 연결하기 전에 source access, timestamp, coverage, leakage, synthetic control 조건을 순서대로 통과하도록 한다. 어느 단계도 자동으로 다음 단계를 승인하지 않는다.

## 2. Gate sequence

```text
M4F-1  specification
M4F-2  source-access audit and data dictionary review
M4F-3  ingestion-only shadow pilot
M4F-4  synthetic null and positive controls
M4F-5  retrospective metadata evidence pilot
M4F-6  future CAL/SEALED specification
```

현재 승인범위는 M4F-1 문서화까지다.

## 3. M4F-2 source-access audit entry

M4F-2로 이동하려면 다음 문서가 존재해야 한다.

- data owner and contact role
- lawful research-use permission
- field-level data dictionary
- historical coverage statement
- timestamp semantics
- update and correction policy
- source-record identifier format
- personal or sensitive data exclusion confirmation
- sample schema without outcome fields

접근 가능성에 대한 구두 설명만으로는 통과하지 않는다.

## 4. M4F-2 PASS criteria

모두 만족해야 `SOURCE_ACCESS_PASS`다.

```text
machine_id or ball_set_id historical source exists
AND at least 520 consecutive draws are potentially linkable
AND selection/observation timestamps exist
AND source records have immutable identifiers
AND correction history can be preserved
AND outcome fields can be physically separated
AND research use is authorized
```

machine과 ball set 중 최소 하나의 stable primary field가 위 조건을 만족해야 한다. 외부 날씨와 방송시간만 확보된 경우에는 `SOURCE_ACCESS_FAIL`이다.

## 5. M4F-3 ingestion-only shadow pilot

목적은 schema와 timestamp 운영만 검증하는 것이다.

```text
consecutive draws = 26
prediction or evidence calculation = prohibited
outcome join during collection = prohibited
```

각 회차에서 metadata를 prediction lock 전에 별도 immutable snapshot으로 저장한다.

### 5.1 Shadow PASS

- 26/26 draw linkage 성공
- required timestamp 100%
- source reference 100%
- checksum reproduction 100%
- schema validation 100%
- outcome payload contamination 0건
- post-lock mutation 0건
- duplicate/conflicting core field 0건

하나라도 실패하면 `INGESTION_SHADOW_FAIL`이다.

## 6. Synthetic null controls

M4F-4에서 다음 null cell을 모두 실행한다.

### N0 Exact uniform

- outcomes: exact uniform 6-of-45
- metadata: 실제 또는 합성 context sequence
- expected: no evidence growth

### N1 Block permutation

- metadata를 52회 block 내부에서 outcome과 독립적으로 permutation
- marginal distribution과 missingness는 보존

### N2 Time-shift leakage trap

- metadata를 one-draw lead, post-draw timestamp, outcome payload와 함께 주입
- expected: global veto 100%, M4 weight 0

### N3 Irrelevant external proxy

- KMA-like weather sequence를 outcome과 독립 생성
- expected: no activation

### N4 Constant and high-cardinality field

- constant venue field
- nearly unique record identifier
- expected: prediction-ineligible or abstain

### N5 Missing-not-at-random

- missingness를 machine, ball set, schedule delay와 연관
- expected: quality gate fail or diagnostic-only

### 6.1 Null PASS

모든 null cell에서 다음을 만족해야 한다.

```text
false activation rate <= 0.001
one-sided exact 95% upper <= 0.002
post-draw global veto rate = 1.000
outcome contamination acceptance = 0
constant/high-cardinality field weight = 0
```

## 7. Synthetic positive controls

### P1 Stable machine effect

- favored group size: 10
- lift: 1.25 and 1.50
- stable duration: at least 520 draws
- context support: at least 104 per machine level

### P2 Stable ball-set effect

- favored group size: 10
- lift: 1.25 and 1.50
- ball-set level support: at least 104

### P3 Machine x ball-set interaction

- residual interaction only
- interaction cell support: at least 52
- main effects present and prediction-eligible

### P4 Transient environment effect

- favored group size: 10
- duration: 104 and 208 draws
- restart candidates: 13, 26, 52, 104
- signal end followed by null period

### P5 Measurement noise and missingness

- timestamp-valid noise
- 10%, 30%, 50% missingness
- measurement misclassification 5% and 15%

### P6 Regime replacement

- machine or ball-set retirement and replacement
- old context effect must not be directly inherited

## 8. Positive-control PASS

Mandatory lift 1.25 criteria:

```text
direction accuracy >= 0.80
strict activation rate >= 0.80
median activation delay <= 520
mean delta Log Loss > 0
mean delta Brier >= 0
```

Mandatory lift 1.50 criteria:

```text
direction accuracy >= 0.95
strict activation rate >= 0.95
median activation delay <= 260
mean delta Log Loss > 0
mean delta Brier >= 0
```

Transient signal termination:

```text
M4 returns to exact M0 within 52 draws
```

Robustness cells are reported separately. Missingness 50% may fail detection but must not create unsafe false activation.

## 9. Actual retrospective pilot entry

M4F-5에 진입하려면 다음 hard gate를 모두 통과해야 한다.

### 9.1 Source and legal

- `SOURCE_ACCESS_PASS`
- data-use permission documented
- no prohibited personal data
- source correction policy available

### 9.2 Historical data

- 520 consecutive linked draws
- draw linkage 100%
- machine_id coverage at least 95% or ball_set_id coverage at least 95%
- selection timestamp coverage at least 95%
- source traceability at least 99%
- no ambiguous core joins

### 9.3 Reliability

- core stable weighted reliability at least 0.95
- no prediction field below 0.90
- Grade D source count zero
- Grade C primary field count zero unless separately approved

### 9.4 Context variation

At least one primary field must satisfy:

```text
at least two retained context levels
AND each retained level support >= 104
```

Interaction analysis additionally requires cell support at least 52.

### 9.5 Timestamp and leakage

- availability class assigned for 100% of supplied records
- A2/A3 primary records zero
- A0 coverage at least 90% for deployable analysis
- outcome payload contamination zero
- global-veto unit tests 100% pass

### 9.6 Synthetic controls

- all mandatory null cells pass
- P1 or P2 lift 1.25 pass
- all scope-lock checks pass

모든 조건을 충족해야:

```text
REAL_METADATA_PILOT_ENTRY_PASS
```

하나라도 실패하면:

```text
REAL_METADATA_PILOT_ENTRY_FAIL
```

Conditional PASS는 허용하지 않는다.

## 10. Actual pilot evaluation policy

실제 metadata pilot은 연구용이며 다음을 사전 고정한다.

- no model selection on actual outcomes
- no threshold adjustment
- no field deletion because of poor outcome performance
- no field addition after outcome inspection
- all field eligibility decided before evaluation
- actual pilot output remains M0-only unless a later Gate explicitly changes state
- actual pilot failure is permanently retained

## 11. Actual pilot stop conditions

다음 중 하나면 즉시 중단한다.

1. outcome leakage 발견
2. core source timestamp 위조·사후생성 가능성
3. legal permission 불명확
4. 520회 연속자료 미달
5. core coverage 기준 미달
6. reliability 기준 미달
7. context variation 부족
8. synthetic null failure
9. artifact or source hash 불일치
10. undocumented source correction

## 12. Current public-data conclusion

공개 공식 MBC 자료는 방송시각, 일정변경, 공식 영상과 참관절차를 확인하는 데 유효하다. 공식 KMA ASOS/AWS는 외부 환경 시계열을 제공한다. 그러나 두 공개원천만으로는 machine, ball set, certified ball measurement, pre-draw operational log, local indoor environment의 520회 primary archive를 구성할 수 없다.

따라서 실제 M4 pilot의 최우선 선행조건은 운영기관 또는 방송사 원기록 접근 가능성 확인이다. 해당 접근이 불가능하면 M4 primary evidence pilot은 `NO_DATA_PATH`로 종료한다.

## 13. Scope lock

M4F-1 결과로 다음을 실행하지 않는다.

- data request transmission
- scraping or video extraction
- Python implementation
- synthetic execution
- actual metadata import
- CAL
- SEALED
- actual-number Walk-forward
- product predictions
- mobile UI
- main merge
