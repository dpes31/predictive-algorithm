# Gate 2-3P-M4F-1 Source and Variable Registry

상태: 사전등록 후보목록  
작성일: 2026-07-01  
Contract: `m4-data-feasibility-1.0.0`

## 1. 판정 코드

```text
P0_PRIMARY       실제 M4 primary 후보
P1_DIAGNOSTIC    진단·품질검사용
P2_ACCESS_NEEDED 운영기관 원기록 접근 필요
P3_EXCLUDED      사전 제외
```

Availability:

```text
A0 = prediction_lock_at 이전 이용 가능
A1 = prediction_lock_at 이후, draw 이전
A2 = draw 이후
A3 = outcome-derived
```

A0만 향후 제품 입력 후보다.

## 2. Stable variable registry

| 변수 | 인과 가설 | 우선 출처 | 공개 접근 | 최소 지원 | 초기 판정 |
|---|---|---|---|---:|---|
| machine_id | 장비별 공기흐름·마모 차이 | 운영기관 signed log | 확인 필요 | level당 104 | P2_ACCESS_NEEDED |
| machine_model_id | 세대·구조 차이 | 자산원장·제조사 문서 | 제한적 | level당 104 | P2_ACCESS_NEEDED |
| machine_serial_hash | 동일 개체 추적 | 자산원장 | 비공개 예상 | level당 104 | P2_ACCESS_NEEDED |
| machine_draws_since_service | 정비 후 상태 변화 | 유지보수 원장 | 비공개 예상 | 260 total | P2_ACCESS_NEEDED |
| machine_cumulative_draw_count | 사용 누적효과 | 운영원장 | 비공개 예상 | 520 total | P2_ACCESS_NEEDED |
| ball_set_id | 볼 세트별 물리편차 | 선정·출고 원장 | 확인 필요 | level당 104 | P2_ACCESS_NEEDED |
| ball_set_generation | 제조·교체 regime | 인증서·자산원장 | 제한적 | level당 104 | P2_ACCESS_NEEDED |
| ball_set_draws_since_certification | 인증 후 마모 | 인증·사용원장 | 비공개 예상 | 260 total | P2_ACCESS_NEEDED |
| machine_ball_set_id | 장비×볼 상호작용 | 위 두 원장 결합 | 비공개 예상 | cell당 52 | P2_ACCESS_NEEDED |
| venue_id | 장소·설비 차이 | MBC 공식 편성·운영기록 | 공개 가능 | level당 104 | P1_DIAGNOSTIC |

## 3. Ball-level measurement registry

| 변수 | 단위 | 요구조건 | 초기 판정 |
|---|---:|---|---|
| ball_number | 1~45 | 물리 측정치와 label 연결 | P2_ACCESS_NEEDED |
| mass_mg | mg | 공인계측기·불확도 포함 | P2_ACCESS_NEEDED |
| diameter_mm | mm | 공인계측기·불확도 포함 | P2_ACCESS_NEEDED |
| roundness_error_mm | mm | 반복측정·검교정 | P2_ACCESS_NEEDED |
| surface_wear_grade | ordinal | 사전 고정 판정기준 | P2_ACCESS_NEEDED |
| measured_at | timestamp | 실제 사용회차 이전 | P2_ACCESS_NEEDED |

45개 번호 중 하나라도 누락되면 해당 ball set measurement snapshot은 무효다.

## 4. Transient variable registry

| 변수 | 관측창 | 우선 출처 | 공개 접근 | 초기 판정 |
|---|---|---|---|---|
| indoor_temperature_c | draw 전 60~0분 | 현장 교정센서 | 비공개 | P2_ACCESS_NEEDED |
| indoor_humidity_pct | draw 전 60~0분 | 현장 교정센서 | 비공개 | P2_ACCESS_NEEDED |
| indoor_pressure_hpa | draw 전 60~0분 | 현장 교정센서 | 비공개 | P2_ACCESS_NEEDED |
| warmup_duration_sec | 장비 가동~draw | 장비 log | 비공개 | P2_ACCESS_NEEDED |
| mixing_duration_sec | 혼합 시작~추출 | 장비 log | 비공개 | P2_ACCESS_NEEDED |
| airflow_setting | draw 전 설정 | 장비 log | 비공개 | P2_ACCESS_NEEDED |
| power_voltage_v | draw 전 10분 평균 | 전원 logger | 비공개 | P2_ACCESS_NEEDED |
| power_frequency_hz | draw 전 10분 평균 | 전원 logger | 비공개 | P2_ACCESS_NEEDED |
| vibration_rms | draw 전 10분 평균 | 현장 sensor | 비공개 | P2_ACCESS_NEEDED |
| pre_draw_test_count | 준비과정 | 운영 log | 비공개 | P2_ACCESS_NEEDED |
| pre_draw_test_pass_fail | 준비과정 | 운영 log | 비공개 | P2_ACCESS_NEEDED |
| pre_draw_test_completed_at | 준비과정 | 운영 log | 비공개 | P2_ACCESS_NEEDED |
| schedule_delay_sec | 예정시각 대비 | MBC 공식 공지·방송기록 | 공개 가능 | P1_DIAGNOSTIC |

Pre-draw test 번호열 자체는 이번 contract에서 제외한다.

## 5. External proxy registry

| 변수 | 공식 출처 | 결합방식 | 위험 | 초기 판정 |
|---|---|---|---|---|
| outdoor_temperature | KMA ASOS/AWS | venue 인접지점·시간 | 실내 대체오류 | P1_DIAGNOSTIC |
| outdoor_humidity | KMA ASOS/AWS | venue 인접지점·시간 | HVAC로 차단 가능 | P1_DIAGNOSTIC |
| outdoor_pressure | KMA ASOS/AWS | venue 인접지점·시간 | 실내 직접측정 아님 | P1_DIAGNOSTIC |
| wind/precipitation | KMA ASOS/AWS | venue 인접지점·시간 | 기전 약함 | P1_DIAGNOSTIC |
| scheduled_broadcast_time | MBC 공식 프로그램 | draw_no/date | 일정 변수 | P1_DIAGNOSTIC |
| schedule_change_notice | MBC 공식 공지 | draw_no/date | 공개시각 확인 필요 | P1_DIAGNOSTIC |
| VOD published metadata | MBC 공식 VOD | draw_no/date | 사후 공개 | P1_DIAGNOSTIC, A2 |

KMA 지점은 기간별 위치 변경이 있을 수 있으므로 지점 위경도 이력을 함께 보존한다.

## 6. Excluded registry

| 변수군 | 제외사유 |
|---|---|
| 진행자·게스트·참관인 identity | 인과기전 없음·개인정보 |
| 판매액·잭팟·검색량 | 물리 추첨과 직접 기전 없음 |
| 구매자 선택패턴 | 당첨 물리과정과 무관 |
| 방송 자막·카메라·의상 | 물리기전 없음 |
| 음력·사주·별자리 | 검증 가능한 물리기전 없음 |
| winning numbers·bonus·draw order | outcome leakage |
| 결과 공개 후 영상 추정값 | A2/A3 leakage |
| 제3자 블로그 정보 | source authority 부족 |
| OCR 단독 장비식별 | 오류·재현성 부족 |

## 7. Source registry

### S-A1 Lottery operator signed logs

대상:
- machine selection
- ball-set selection
- inspection
- maintenance
- test execution
- exact timestamps

Prediction eligibility: 잠재적으로 가능. 접근협의 필요.

### S-A2 Broadcaster operational logs

대상:
- studio/venue
- scheduled and actual draw times
- rehearsal and preparation timestamps
- equipment handoff records

Prediction eligibility: 필드별 available_at에 따라 A0 또는 A1.

### S-A3 Certified measurement records

대상:
- ball mass, diameter, roundness
- machine calibration
- sensor calibration

Prediction eligibility: 원본 인증서와 label mapping이 있으면 가능.

### S-B1 MBC official public pages

확인 가능한 범위:
- 정규 방송시각
- 방송시간 변경공지
- 공식 영상·회차일자
- 참관 준비과정 및 상암사옥 일정

제한:
- 구조화된 machine/ball/pretest 장기 archive가 아님.

### S-B2 KMA official ASOS/AWS

확인 가능한 범위:
- 시간·분·일 관측
- 온도, 습도, 기압 등
- 지점정보와 위치이력

제한:
- 실내 장비환경의 proxy일 뿐 직접측정이 아님.

### S-C1 Double-reviewed official-video transcription

요건:
- 독립 추출자 2명
- frame timestamp
- 원본 URL과 hash
- 일치율 99% 이상

기본 판정: diagnostic-only.

## 8. Source-access audit 질문지

운영기관·방송사 자료사전 검토 시 다음을 확인한다.

1. 회차별 machine_id와 ball_set_id가 기록되는가.
2. 선택시각과 외부 이용가능시각이 분리되는가.
3. historical archive가 520회 이상 존재하는가.
4. 장비·볼 교체와 정비이력이 보존되는가.
5. pre-draw test 횟수·상태·시각이 기록되는가.
6. 실내 센서 원시자료가 존재하는가.
7. ball number별 인증 측정값이 존재하는가.
8. 기록 수정이력과 원본 hash를 제공할 수 있는가.
9. 결과번호가 같은 payload에 혼입되는가.
10. 연구·저장·재배포 권한 범위는 무엇인가.

한 항목이라도 답변을 추정으로 채우지 않는다.
