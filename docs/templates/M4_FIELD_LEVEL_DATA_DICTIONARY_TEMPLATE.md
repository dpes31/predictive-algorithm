# M4 Field-Level Data Dictionary Template

상태: 빈 템플릿  
Contract: `m4-source-access-1.0.0`

기관이 보유한 실제 field를 이 템플릿에 맞춰 기술한다. 값이 확인되지 않은 항목은 추정하지 않고 `UNKNOWN`으로 남긴다.

## 1. Dataset-level information

| 항목 | 입력값 |
|---|---|
| institution_name | |
| data_owner_department | |
| system_owner_department | |
| source_system_name | |
| dataset_name | |
| dataset_version | |
| first_draw_no | |
| last_draw_no | |
| first_recorded_at | |
| last_recorded_at | |
| retention_period | |
| correction_policy_reference | |
| lawful_use_reference | |
| security_classification | |
| outcome_fields_physically_separated | YES / NO / UNKNOWN |
| sample_schema_hash | |
| completed_by_role | |
| completed_at | |

## 2. Field dictionary

아래 표는 field마다 한 행씩 작성한다.

| column | required description |
|---|---|
| field_id | dictionary 내부 고유 ID |
| field_name | 원 시스템 field명 |
| canonical_name | 연구 schema의 표준 field명 |
| family | stable / ball_measurement / transient / provenance / timestamp / quality |
| business_definition | 현업 의미 |
| causal_rationale | 추첨 물리·운영과의 가설적 인과경로 |
| source_system | 생성 원시스템 |
| source_table_or_log | 원 table·log·document |
| source_record_id_field | 원본 record ID field |
| data_type | string / integer / number / boolean / timestamp / enum / object |
| unit | SI 또는 원 단위 |
| precision | 소수점·timestamp precision |
| allowed_values | enum 또는 범위 |
| null_allowed | YES / NO |
| null_meaning | unknown / not measured / not applicable / redacted 등 |
| generation_event | 어떤 사건에서 생성되는가 |
| observed_at_source | 관측시각 출처 |
| recorded_at_source | 저장시각 출처 |
| available_at_source | 이용가능시각 출처 |
| source_published_at_source | 외부 공개시각 출처 |
| timezone | 원본 timezone |
| clock_source | NTP·장비시계·수기 등 |
| manually_editable | YES / NO |
| correction_history_available | YES / NO |
| immutable_identifier | YES / NO |
| historical_first_draw | 최초 보유 회차 |
| historical_last_draw | 최종 보유 회차 |
| estimated_coverage_pct | 추정하지 말고 공식 산출값만 기재 |
| missing_draws_reference | 누락 목록 문서 |
| availability_class_possible | A0 / A1 / A2 / A3 판정 가능 여부 |
| contains_outcome_information | YES / NO |
| contains_personal_information | YES / NO |
| security_class | public / internal / confidential / restricted |
| proposed_access_role | 접근 가능 role |
| transfer_format | CSV / JSON / database extract / other |
| correction_rule | 정정 절차 |
| retention_rule | 보존·파기 절차 |
| evidence_level | E0 / E1 / E2 / E3 |
| reliability_source_authority | 0.00~0.35 |
| reliability_timestamp_integrity | 0.00~0.25 |
| reliability_measurement_directness | 0.00~0.20 |
| reliability_immutability | 0.00~0.10 |
| reliability_join_certainty | 0.00~0.10 |
| reliability_total | 0.00~1.00 |
| initial_eligibility | prediction_candidate / diagnostic_only / reject |
| exclusion_reason | 제외 시 사유 |
| notes | 추가 설명 |

## 3. Required core rows

아래 canonical field는 존재 여부 자체를 반드시 기록한다. 존재하지 않으면 행을 삭제하지 말고 `source_system=NOT_AVAILABLE`로 남긴다.

### Draw identity and time

- `draw.operator_id`
- `draw.draw_no`
- `draw.draw_date`
- `draw.draw_scheduled_at`
- `draw.draw_actual_at`
- `draw.prediction_lock_at`
- `draw.venue_id`

### Provenance

- `provenance.source_record_id`
- `provenance.source_system`
- `provenance.recorded_at`
- `provenance.available_at`
- `provenance.ingested_at`
- `provenance.record_hash`
- `provenance.correction_id`

### Machine

- `machine.machine_id`
- `machine.model_id`
- `machine.generation`
- `machine.last_service_at`
- `machine.draws_since_service`
- `machine.cumulative_draw_count`
- `machine.selection_observed_at`
- `machine.selection_available_at`

### Ball set

- `ball_set.ball_set_id`
- `ball_set.generation`
- `ball_set.last_certified_at`
- `ball_set.draws_since_certification`
- `ball_set.cumulative_draw_count`
- `ball_set.selection_observed_at`
- `ball_set.selection_available_at`

### Pre-draw operations

- `pre_draw_tests.test_count`
- `pre_draw_tests.pass_count`
- `pre_draw_tests.fail_count`
- `pre_draw_tests.condition_id`
- `pre_draw_tests.completed_at`
- `operations.warmup_duration_sec`
- `operations.mixing_duration_sec`
- `operations.airflow_setting`

### Local environment

- `environment.indoor_temperature_c`
- `environment.indoor_relative_humidity_pct`
- `environment.indoor_air_pressure_hpa`
- `environment.sensor_id`
- `environment.window_start_at`
- `environment.window_end_at`
- `environment.sensor_calibration_id`

### Ball-level measurement

- `ball_measurement.ball_set_id`
- `ball_measurement.ball_number`
- `ball_measurement.mass_mg`
- `ball_measurement.diameter_mm`
- `ball_measurement.roundness_error_mm`
- `ball_measurement.surface_wear_grade`
- `ball_measurement.measurement_device_id`
- `ball_measurement.measurement_uncertainty`
- `ball_measurement.measured_at`

## 4. Field decision worksheet

각 field의 최종 감사결과를 다음 형식으로 기록한다.

| canonical_name | exists | 520-draw coverage | timestamp semantics | outcome separation | evidence level | reliability | final field status |
|---|---|---|---|---|---|---:|---|
| example | YES/NO | PASS/FAIL/UNKNOWN | PASS/FAIL/UNKNOWN | PASS/FAIL/UNKNOWN | E0-E3 | 0.00 | candidate/diagnostic/reject |

## 5. Completion rules

- 빈칸을 임의 추정값으로 채우지 않는다.
- `UNKNOWN`은 FAIL과 구분해 기록한다.
- 기관의 원 field명과 canonical field명을 모두 보존한다.
- 하나의 원 field를 여러 canonical field로 복제하지 않는다.
- timestamp가 수기 입력이면 반드시 표시한다.
- outcome field가 포함되면 해당 field와 payload 전체의 분리 가능성을 기록한다.
- 개인식별 field는 값 예시를 첨부하지 않는다.
- sample value는 synthetic dummy만 허용한다.
