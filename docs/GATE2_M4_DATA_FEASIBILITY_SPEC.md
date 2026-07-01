# Gate 2-3P-M4F-1 Physical and Operational Data Feasibility Specification

상태: 사용자 검토용 상세 명세  
작성일: 2026-07-01  
기준 모델: `5.0.0-research`  
M4 data feasibility contract: `1.0.0`  
작업 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`

## 1. 목적

Gate 2-3P-R3M-3-2에서 과거 번호 이력만 사용하는 predictable-group 경로는 `PREDICTABLE_GROUP_FAIL`로 잠겼다. 이번 Gate는 해당 M3 경로를 동결하고, 추첨 전에 관측 가능한 물리·운영 변수만으로 M4 연구를 진행할 수 있는지 데이터 측면에서 사전 판정하기 위한 계약을 고정한다.

이번 Gate는 명세 작성만 포함한다. Python 구현, 추가 DEV 탐색, 데이터 수집, CAL, SEALED, 실제 번호 Walk-forward, 사용자용 번호 생성, 모바일 UI, main 병합을 포함하지 않는다.

## 2. 상위 상태와 동결

다음 상태를 유지한다.

```text
Gate 2-3P-R3M-3-2 = PREDICTABLE_GROUP_FAIL
M3 past-number path = FROZEN
Full M3 DEV = BLOCKED
Gate 2-3P-R4 = BLOCKED
Final distribution = M0_ONLY
```

기존 R3 실패, R3M-2 Oracle PASS, R3M-3 predictable-group FAIL의 commit, workflow, report hash, lock hash를 변경하지 않는다.

## 3. 핵심 원칙

1. 변수는 물리적 또는 운영상 인과경로가 설명되어야 한다.
2. 예측에 사용되는 값은 `prediction_lock_at` 이전에 실제로 이용 가능해야 한다.
3. 추첨 전 관측이라도 판매마감·예측잠금 이후에만 알 수 있는 값은 배포용 입력이 아니다.
4. 결과 공개 이후 생성·수정된 값은 금지한다.
5. 공식 출처, 원본 timestamp, 변경이력, draw 연결키가 없는 값은 prediction-eligible이 아니다.
6. 결측을 결과나 주변 회차로 보간하지 않는다.
7. 데이터가 일정한 상수이거나 변동이 거의 없으면 설명변수로 채택하지 않는다.
8. 공공데이터로 직접 측정할 수 없는 실내·장비 상태를 외부 날씨로 대체해 동일 변수처럼 취급하지 않는다.
9. 데이터 확보 실패는 모델 실패와 동일하게 기록하며, 임의 추정값으로 보완하지 않는다.

## 4. 시간 필드 계약

각 metadata record는 다음 시각을 분리해 저장해야 한다.

```text
draw_scheduled_at       공식 예정 추첨시각
draw_actual_at          실제 추첨 개시시각
observed_at             센서·기록이 현상을 관측한 시각
recorded_at             원 시스템에 저장된 시각
available_at            모델 운영자가 해당 값을 이용할 수 있게 된 시각
source_published_at     외부 출처가 공개한 시각
ingested_at             연구 저장소에 수집된 시각
prediction_lock_at      해당 회차 예측 입력을 동결한 시각
```

시간대는 `Asia/Seoul`과 UTC를 함께 기록한다. 원본 timezone이 없으면 verified로 승격하지 않는다.

### 4.1 이용 가능성 등급

```text
A0_DEPLOYABLE:
available_at <= prediction_lock_at

A1_RESEARCH_ONLY:
prediction_lock_at < available_at < draw_actual_at

A2_POST_DRAW:
available_at >= draw_actual_at

A3_OUTCOME_DERIVED:
값 또는 timestamp가 당첨번호·추첨순서·보너스번호에서 생성됨
```

- A0만 향후 배포형 M4 입력 후보가 된다.
- A1은 물리적 타당성 진단에만 사용하며 제품 예측에는 사용할 수 없다.
- A2와 A3는 모델 입력 금지다.
- A2/A3가 required field에 혼입되면 metadata global veto를 발생시킨다.

## 5. Draw 연결 계약

Metadata는 다음 복합키로 회차에 연결한다.

```text
operator_id
draw_no
draw_date
draw_scheduled_at
draw_actual_at
venue_id
source_record_id
```

필수 조건:

- `draw_no`와 `draw_date`가 공식 결과와 일치
- 동일 source record가 둘 이상의 회차에 연결되지 않음
- actual draw timestamp 오차가 60초 이내이거나 공식 변경공지로 설명됨
- 일정 변경 회차는 별도 exception record 보유
- 연결이 추정이면 `join_status=ambiguous`로 두고 prediction-eligible에서 제외

## 6. 변수 family

M4는 stable과 transient 두 family를 유지한다.

### 6.1 Stable physical family

- `machine.machine_id`
- `machine.model_id`
- `machine.generation`
- `machine.serial_hash`
- `machine.commissioned_at`
- `machine.last_service_at`
- `machine.draws_since_service`
- `machine.cumulative_draw_count`
- `ball_set.ball_set_id`
- `ball_set.generation`
- `ball_set.commissioned_at`
- `ball_set.retired_at`
- `ball_set.cumulative_draw_count`
- `ball_set.draws_since_certification`
- `interaction.machine_ball_set_id`

### 6.2 Ball-level certified measurement family

번호별 물리차이를 직접 검토하려면 다음과 같은 label-preserving 측정값이 필요하다.

- `ball.number`
- `ball.mass_mg`
- `ball.diameter_mm`
- `ball.roundness_error_mm`
- `ball.surface_wear_grade`
- `ball.measurement_device_id`
- `ball.measurement_uncertainty`
- `ball.measured_at`

번호와 물리 측정치의 연결이 제거되거나 측정 불확도가 없으면 이 family는 사용할 수 없다.

### 6.3 Transient operational family

- `environment.indoor_temperature_c`
- `environment.indoor_relative_humidity_pct`
- `environment.indoor_air_pressure_hpa`
- `environment.sensor_id`
- `environment.window_start_at`
- `environment.window_end_at`
- `machine.warmup_duration_sec`
- `machine.mixing_duration_sec`
- `machine.airflow_setting`
- `machine.power_voltage_v`
- `machine.power_frequency_hz`
- `machine.vibration_rms`
- `pre_draw_tests.test_count`
- `pre_draw_tests.pass_count`
- `pre_draw_tests.fail_count`
- `pre_draw_tests.condition_id`
- `pre_draw_tests.completed_at`
- `draw.schedule_delay_sec`

### 6.4 Diagnostic-only external proxy family

- nearest KMA ASOS/AWS temperature
- nearest KMA ASOS/AWS humidity
- nearest KMA ASOS/AWS pressure
- precipitation, wind, outdoor conditions
- official broadcast scheduled time and schedule-change notice

외부 기상은 스튜디오 실내 장비환경의 직접 측정값이 아니므로 local sensor와 동일 field로 합치지 않는다. 외부 기상은 초기에는 `diagnostic_only=true`다.

## 7. 사전 제외 변수

다음은 M4 primary variable로 사용하지 않는다.

- 진행자, 황금손, 참관인, 경찰관, 제작진 개인 식별정보
- 성별, 연령, 인적 특성
- 판매액, 당첨금, 구매량, 검색량, 커뮤니티 언급량
- 방송 자막·카메라 각도·의상·대본
- 음력, 사주, 별자리 및 비물리적 달력 특성
- 당첨번호, 보너스번호, 추첨순서
- 추첨영상에서 결과 공개 이후 역산한 장비상태
- 사후 보정된 timestamp
- 출처 없는 수기 추정값

Pre-draw test에서 나온 번호열은 별도 보안·누출 검토 전까지 primary input에서 제외한다. 테스트 횟수, 통과상태, 시간, 조건만 허용한다.

## 8. Source hierarchy

### Grade A — 원 운영시스템 직접기록

- 동행복권 또는 추첨운영기관의 signed machine log
- MBC 추첨운영 signed log
- 장비·볼 세트 출고·선정·점검·유지보수 원장
- 공인 측정·검교정 성적서
- 현장 센서 원시데이터

요건:

- immutable record ID
- 원본 timestamp
- 담당 시스템 또는 서명주체
- 수정이력
- 회차 연결키

### Grade B — 공식 공개 원천

- 동행복권 공식 공지·보도자료
- MBC 공식 편성·방송시간 변경공지·추첨영상 metadata
- 기상청 ASOS/AWS 공식 관측자료
- 정부 공공데이터 API

Grade B는 공개 사실 확인에는 사용할 수 있으나, 장비 내부상태를 직접 측정하지 않은 proxy는 diagnostic-only다.

### Grade C — 이중검수 수기 추출

- 공식 영상에서 두 명이 독립 추출한 장비 식별표시
- 공식 문서 PDF의 수기 구조화

요건:

- double entry
- disagreement log
- frame/time reference
- 원본 hash

Grade C는 기본적으로 diagnostic-only이며 prediction-eligible 승격에는 별도 승인과 99% 이상의 독립 일치율이 필요하다.

### Grade D — 제3자 또는 추정

- 블로그, 커뮤니티, 비공식 영상
- 이미지 추정, OCR 단독 결과
- 출처가 재현되지 않는 설명

Grade D는 모델 입력 금지다.

## 9. Reliability score

각 record는 다음 점수를 합산한다.

```text
source_authority       0.00 ~ 0.35
timestamp_integrity    0.00 ~ 0.25
measurement_directness 0.00 ~ 0.20
immutability           0.00 ~ 0.10
join_certainty         0.00 ~ 0.10
--------------------------------
reliability_score      0.00 ~ 1.00
```

판정:

```text
>= 0.90  prediction-eligible candidate
0.75-0.90 diagnostic-only
< 0.75   reject
```

Core stable fields의 weighted mean reliability는 0.95 이상이어야 pilot entry가 가능하다.

## 10. 결측과 모순 처리

### 10.1 결측

- missing은 `unknown`으로 저장
- forward fill, backward fill, 평균대체 금지
- 동일 장비의 이전 회차 값을 현재 회차에 자동 복사 금지
- 결측 field는 해당 field LR=1
- required core field 결측이면 해당 회차 M4 전체는 `ABSTAIN`

### 10.2 모순

다음은 global veto다.

- 동일 회차에 machine_id 또는 ball_set_id가 복수로 충돌
- observed_at 또는 available_at이 draw 이후
- available-before-lock 표기와 timestamp 불일치
- 공식 schedule change를 반영하지 않은 draw timestamp
- source record가 사후 수정됐으나 이전 버전이 없음
- 당첨결과가 metadata payload에 포함

## 11. Coverage 기준

### 11.1 Core stable coverage

Retrospective evidence pilot 진입에는 연속 520회 구간에서 다음이 필요하다.

```text
draw linkage coverage                     = 100%
machine_id coverage                       >= 95%
ball_set_id coverage                      >= 95%
machine/ball selection timestamp coverage >= 95%
source traceability                       >= 99%
A0 or A1 availability classification      = 100%
```

A0 deployable 분석은 별도로 A0 coverage 90% 이상이어야 한다.

### 11.2 Transient coverage

```text
local indoor environment coverage >= 80%
pre-draw operational log coverage >= 80%
valid sensor calibration coverage >= 95% of supplied sensor rows
```

외부 KMA proxy coverage가 높더라도 local sensor coverage를 대체하지 않는다.

### 11.3 Missingness bias

Field missingness가 다음과 연관되면 prediction-eligible에서 제외한다.

- machine or ball-set context
- schedule delay
- maintenance event
- prior draw result
- current outcome

Missingness model의 예측 AUC가 0.60 이상이면 비무작위 결측으로 표시하고 별도 보정 명세 전까지 diagnostic-only로 둔다.

## 12. 최소 필요 표본

### 12.1 Data ingestion qualification

운영·timestamp·schema 파이프라인만 확인하는 shadow phase:

```text
minimum consecutive draws = 26
required timestamp compliance = 100%
core field coverage = 100%
```

이 단계에서는 예측력 주장과 e-process 계산을 금지한다.

### 12.2 Retrospective M4 evidence pilot

```text
minimum consecutive linked draws = 520
minimum stable context support = 104 draws per retained level
minimum machine x ball-set interaction support = 52 draws per retained cell
minimum transient field total support = 260 draws
minimum transient bin support = 52 draws
```

식별 가능한 변동이 필요하므로 retained field에는 최소 두 개의 context level 또는 명확한 regime transition이 있어야 한다. 단일 상수 field는 제외한다.

### 12.3 Ball-level measurements

- 각 사용 ball set의 45개 번호 전체 측정
- 측정 누락 0개
- 동일 측정장비 또는 교차교정 기록
- 측정시각이 사용회차 이전
- 최소 두 개 ball set 또는 한 세트의 두 개 이상 인증시점

## 13. Public-source feasibility snapshot

2026-07-01 기준 공개 공식원천으로 확인 가능한 범위:

- MBC 공식 페이지: 정규 방송시각, 방송시간 변경공지, 추첨영상, 참관절차와 MBC 상암사옥 일정
- 기상청 기상자료개방포털: ASOS/AWS 시간·분·일 관측과 지점정보
- 동행복권 공식 페이지·보도자료: 추첨사업자와 공식 추첨 관련 공지

현재 공개 공식원천만으로는 회차별 machine_id, ball_set_id, ball-level measurement, pre-draw test log, local indoor sensor log의 장기 구조화 archive를 확인할 수 없다. 따라서 M4 primary pilot은 운영기관 또는 방송사 원기록 접근협의가 선행되지 않으면 진입할 수 없다.

## 14. Gate 분할

```text
Gate 2-3P-M4F-1 = data feasibility specification
Gate 2-3P-M4F-2 = source-access audit and data dictionary review
Gate 2-3P-M4F-3 = ingestion-only shadow pilot
Gate 2-3P-M4F-4 = synthetic null/positive control implementation
Gate 2-3P-M4F-5 = retrospective metadata evidence pilot
```

각 단계는 별도 사용자 승인 없이는 진행하지 않는다.

## 15. 현재 금지

- 데이터 제공 요청 발송
- 웹 scraping 또는 영상 추출
- 센서 설치·수집
- Python schema·ingestion 구현
- synthetic DEV 실행
- 실제 metadata 결합
- CAL·SEALED
- 실제 번호 Walk-forward
- 사용자용 번호 생성
- 모바일 UI
- main 병합
