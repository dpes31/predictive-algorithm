# Gate 2 Physical Metadata Schema

상태: 검토용 고정 명세  
스키마 버전: `1.0.0`

## 1. 원칙

물리·운영 데이터는 값 자체보다 **언제 알 수 있었는지, 어디에서 왔는지, 얼마나 신뢰할 수 있는지**를 함께 저장한다.

모든 필드는 다음 공통 메타데이터를 가진다.

```json
{
  "value": null,
  "status": "unknown",
  "source_type": "none",
  "source_url": null,
  "observed_at": null,
  "available_before_draw": false,
  "confidence": 0.0,
  "notes": null
}
```

## 2. 상태값

- `unknown`: 확인 불가
- `reported`: 기사·후기·방송 설명에서 언급
- `observed`: 영상·공개자료에서 직접 관측
- `verified`: 복수 독립 출처 또는 공식 기록으로 확인
- `inferred`: 영상·시기 정보로 추론, 모델 입력 기본 금지

`inferred`는 exploratory 분석에는 저장할 수 있지만 예측 입력에는 기본적으로 사용하지 않는다.

## 3. 출처 유형

- `official_document`
- `official_broadcast`
- `official_webpage`
- `press_report`
- `observer_report`
- `manual_video_review`
- `machine_extracted_video`
- `none`

## 4. 회차 레코드

```json
{
  "draw_no": 1231,
  "draw_datetime": "2026-07-04T20:35:00+09:00",
  "metadata_version": "1.0.0",
  "machine": {
    "machine_id": {},
    "machine_generation": {},
    "maintenance_event_id": {},
    "draws_since_maintenance": {}
  },
  "ball_set": {
    "ball_set_id": {},
    "ball_generation": {},
    "set_use_count_before_draw": {},
    "draws_since_full_replacement": {}
  },
  "environment": {
    "temperature_c": {},
    "humidity_percent": {},
    "air_pressure_setting": {},
    "mixing_duration_seconds": {}
  },
  "pre_draw_tests": {
    "test_count": {},
    "test_draw_sequences": {},
    "published_before_draw": {}
  },
  "historical_order_features": {
    "machine_number_mean_rank": {},
    "ball_set_number_mean_rank": {},
    "recent_number_rank_shift": {}
  },
  "regime": {
    "machine_regime_id": {},
    "ball_regime_id": {},
    "operating_procedure_regime_id": {}
  }
}
```

## 5. 실제 결과 레코드와 분리

물리 메타데이터와 당첨결과는 별도 파일·테이블로 유지한다.

- `draw_metadata`: 추첨 전 관측 정보
- `draw_results`: 추첨 후 본번호·보너스·배출순서

예측 엔진은 target 회차에 대해 `draw_metadata[target]`와 `draw_results[1..target-1]`만 읽을 수 있다.

## 6. 배출순서

현재 회차의 배출순서는 결과 데이터다.

```json
{
  "draw_no": 1231,
  "ordered_numbers": [3, 11, 18, 27, 36, 44],
  "bonus_number": 9,
  "extraction_timestamps": null
}
```

사용 가능 범위:

- target 이전 회차의 순서 통계: 사용 가능
- target 회차 순서: 예측 입력 금지

## 7. 사전 모의추첨

사전 모의추첨 결과는 다음 조건을 모두 만족할 때만 production-grade feature 후보가 된다.

1. 본추첨 전에 실제로 수행됨
2. 결과가 본추첨 전에 기록·확인 가능함
3. 본추첨과 동일 장비·볼 세트 사용 여부 확인 가능
4. 원자료와 시각이 보존됨

본추첨 후 공개된 회고성 정보는 historical exploratory feature로만 분리한다.

## 8. 신뢰도 기본값

- official_document / verified: 1.00
- official_broadcast / observed: 0.90
- official_webpage / observed: 0.90
- press_report / reported: 0.60
- observer_report / reported: 0.40
- manual_video_review / observed: 0.70
- machine_extracted_video / observed: 성능검증 전 0.50
- inferred: 0.00 for prediction
- unknown: 0.00

신뢰도는 임의로 상향하지 않는다.

## 9. 완전성 지표

회차별로 다음을 계산한다.

```text
required_field_completeness
weighted_reliability
pre_draw_availability_rate
source_traceability_rate
```

M4 활성 최소조건 제안:

- pre-draw availability 100%
- required field completeness 70% 이상
- weighted reliability 0.70 이상
- source traceability 90% 이상

기준 미달이면 해당 회차 M4 비중은 0이다.

## 10. 검증 규칙

- draw_no 중복 금지
- observed_at은 draw_datetime보다 늦을 수 있으나, 늦으면 prediction feature 금지
- available_before_draw=true인데 observed_at이 draw 이후면 validation 실패
- confidence 범위 0~1
- verified 상태는 source_url 또는 official record ID 필수
- set_use_count_before_draw는 현재 회차 사용을 포함하지 않음
- current draw result를 metadata에 포함하면 미래누출로 실패
