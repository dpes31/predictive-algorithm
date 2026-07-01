# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-M4F-1 data feasibility specification 완료·승인 대기**  
현재 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`  
기준 브랜치: `feature/r3m3-predictable-group-engine`  
관련 Issue: #33

## 목적

로또 6/45의 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## Gate 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R3M-2: `ORACLE_PASS`
- Gate 2-3P-R3M-3-2: `PREDICTABLE_GROUP_FAIL`
- M3 past-number path: **FROZEN**
- Gate 2-3P-M4F-1: **명세 완료·승인 대기**
- Gate 2-3P-M4F-2: 미승인·미실행
- full M3 DEV: `BLOCKED`
- Gate 2-3P-R4: `BLOCKED`
- CAL·SEALED·실제 데이터·모바일 MVP: `BLOCKED`

현재 모델은 `5.0.0-research`, M4 data feasibility contract는 `1.0.0`, Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`다.

## Predictable-group 실패 잠금

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests `105 PASS`
- artifact `8002526507`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

이 결과를 유지하며 M3 past-number learner는 추가 튜닝하지 않는다.

## M4F-1 문서

- `docs/GATE2_M4_DATA_FEASIBILITY_SPEC.md`
- `docs/GATE2_M4_SOURCE_VARIABLE_REGISTRY.md`
- `docs/GATE2_M4_PILOT_ENTRY_PROTOCOL.md`
- `reports/gate2_m4f1_public_source_feasibility.md`

## 시간·누출 계약

각 metadata record는 다음을 분리한다.

- observed_at
- recorded_at
- available_at
- source_published_at
- ingested_at
- prediction_lock_at
- draw_actual_at

Availability:

```text
A0_DEPLOYABLE     available_at <= prediction_lock_at
A1_RESEARCH_ONLY prediction_lock_at < available_at < draw_actual_at
A2_POST_DRAW      available_at >= draw_actual_at
A3_OUTCOME_DERIVED
```

A0만 향후 제품 입력 후보다. A2/A3는 금지하며 required field 혼입 시 global veto다.

## 변수 범위

Primary stable 후보:

- machine identity, model, generation, service age, use count
- ball-set identity, generation, certification age, use count
- machine × ball-set context
- label-preserving certified ball mass, diameter, roundness, wear

Primary transient 후보:

- local indoor temperature, humidity, pressure
- warmup, mixing duration, airflow
- power voltage/frequency, vibration
- pre-draw test count, pass/fail, completion time

Diagnostic-only:

- KMA ASOS/AWS outdoor weather
- MBC official schedule and schedule-change notices
- official video double transcription

Excluded:

- 개인 identity
- 판매·구매·검색량
- 방송 연출요소
- 비물리적 달력특성
- outcome fields와 사후 영상추정
- 제3자·OCR 단독 추정

## Coverage와 최소 표본

Retrospective pilot hard minimum:

- 520 consecutive linked draws
- draw linkage 100%
- machine 또는 ball-set coverage 95% 이상
- selection timestamp coverage 95% 이상
- source traceability 99% 이상
- core stable weighted reliability 0.95 이상
- stable context level당 104회
- interaction cell당 52회
- transient field 260회, retained bin당 52회

26회 shadow phase는 ingestion·timestamp 검증만 수행하며 예측력 검증을 금지한다.

## Source hierarchy

- Grade A: operator/broadcaster signed logs, certified measurements, local sensors
- Grade B: official MBC, 동행복권, KMA and government public data
- Grade C: double-reviewed official-video/manual transcription, diagnostic-only
- Grade D: third-party or inferred sources, rejected

공개 공식원천만으로는 machine, ball-set, ball measurement, pre-draw operations, indoor sensor의 520회 primary archive가 확인되지 않았다. 운영기관 또는 방송사 원기록 접근경로가 없으면 M4 pilot은 `NO_DATA_PATH`다.

## Synthetic controls

Mandatory null:

- exact uniform
- block permutation
- time-shift leakage trap
- irrelevant weather proxy
- constant/high-cardinality field
- missing-not-at-random

Null 기준:

- false activation <= 0.1%
- one-sided 95% upper <= 0.2%
- post-draw veto 100%
- outcome contamination acceptance 0

Mandatory positive:

- stable machine lift 1.25/1.50
- stable ball-set lift 1.25/1.50
- machine × ball interaction
- transient environment 104/208회
- missing/noisy metadata
- regime replacement

## Actual pilot entry

모든 hard gate를 충족해야 `REAL_METADATA_PILOT_ENTRY_PASS`다.

- lawful source access
- 520 consecutive draws
- core coverage and reliability PASS
- at least two retained context levels, each 104 draws
- A0 coverage 90% 이상 for deployable analysis
- outcome contamination 0
- mandatory null PASS
- P1 machine 또는 P2 ball-set lift 1.25 PASS

Conditional PASS는 없다.

## Gate sequence

```text
M4F-1 specification
M4F-2 source-access audit and data dictionary
M4F-3 26-draw ingestion-only shadow
M4F-4 synthetic controls
M4F-5 retrospective metadata evidence pilot
M4F-6 future CAL/SEALED specification
```

현재 M4F-1만 완료됐다.

## 현재 금지

- 자료요청 발송
- scraping·영상추출·OCR
- 센서설치·데이터수집
- Python 구현
- 추가 DEV·synthetic 실행
- 실제 metadata import
- CAL·SEALED
- 실제 번호 Walk-forward
- 사용자용 번호 생성
- 모바일 UI
- main 병합

## 다음 단계

사용자 승인 후 `Gate 2-3P-M4F-2`에서 source-access audit 상세 명세와 자료요청서 초안만 작성한다. 실제 요청 발송과 데이터 수집은 별도 승인 전 금지한다.
