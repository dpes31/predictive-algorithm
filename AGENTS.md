# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽는다.

## 프로젝트 목적

로또 6/45 다음 회차의 정확히 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

- M0 균등 기준 유지
- M1 지속, M2 반전, M3 구조변화, M4 물리·운영 증거 역할 유지
- 근거 부족 시 exact M0
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패 결과와 불확실성 보존
- 제품 출력은 6개 번호 × 5세트

## 필수 읽기

1. `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`
2. `docs/GATE2_PREDICTABLE_GROUP_FEASIBILITY_SPEC.md`
3. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`
4. `docs/GATE2_M4_DATA_FEASIBILITY_SPEC.md`
5. `docs/GATE2_M4_SOURCE_VARIABLE_REGISTRY.md`
6. `docs/GATE2_M4_PILOT_ENTRY_PROTOCOL.md`
7. `reports/gate2_m4f1_public_source_feasibility.md`
8. `handoff/PROJECT_HANDOFF.md`
9. `handoff/GATE2_PHYSICAL_PROGRESS.md`
10. `handoff/DECISION_LOG_GATE2_M4F1_SPEC.md`

## 현재 상태

- Gate 2-3P-R3: `NO_ELIGIBLE_CONFIG`
- Gate 2-3P-R3M-2 Oracle DEV: `PASS`
- Gate 2-3P-R3M-3-2: `PREDICTABLE_GROUP_FAIL`
- M3 past-number path: **FROZEN**
- Gate 2-3P-M4F-1: **상세 명세 완료·사용자 승인 대기**
- Gate 2-3P-M4F-2: 미승인·미실행
- full M3 DEV: `BLOCKED`
- Gate 2-3P-R4: `BLOCKED`
- CAL·SEALED: `BLOCKED`
- 실제 데이터·모바일 MVP: `BLOCKED`

현재 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`  
기준 브랜치: `feature/r3m3-predictable-group-engine`  
관련 Issue: `#33`  
현재 모델: `5.0.0-research`  
M4 data feasibility contract: `1.0.0`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

## Predictable-group 실패 잠금

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests `105 PASS`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

과거 번호 이력만 사용하는 M3 predictable-group 경로는 추가 튜닝 없이 동결한다.

## M4F-1 핵심 계약

### 시간과 누출

각 record는 `observed_at`, `recorded_at`, `available_at`, `source_published_at`, `ingested_at`, `prediction_lock_at`, `draw_actual_at`을 분리한다.

```text
A0_DEPLOYABLE     available_at <= prediction_lock_at
A1_RESEARCH_ONLY prediction_lock_at < available_at < draw_actual_at
A2_POST_DRAW      available_at >= draw_actual_at
A3_OUTCOME_DERIVED
```

A0만 향후 제품 입력 후보다. A2/A3는 금지이며 required field 혼입 시 global veto다.

### Primary stable 후보

- machine identity, model, generation, service age, usage count
- ball-set identity, generation, certification age, usage count
- machine × ball-set context
- number-preserving certified ball mass, diameter, roundness, wear

### Primary transient 후보

- local indoor temperature, humidity, pressure
- machine warmup and mixing duration
- airflow, power voltage/frequency, vibration
- pre-draw test count, pass/fail, completion timestamp

### Diagnostic-only 후보

- KMA ASOS/AWS outdoor weather
- official MBC schedule, schedule changes, VOD metadata
- double-reviewed official-video transcription

### 사전 제외

- 개인 identity와 인적 특성
- 판매액, 당첨금, 검색량, 구매패턴
- 방송 자막·카메라·의상
- 음력·사주·별자리
- winning numbers, bonus, draw order
- 사후 영상추정과 제3자 출처

## Reliability와 coverage

Reliability score:

```text
source authority       0.35
timestamp integrity    0.25
measurement directness 0.20
immutability           0.10
join certainty         0.10
```

- 0.90 이상: prediction-eligible candidate
- 0.75~0.90: diagnostic-only
- 0.75 미만: reject
- core stable weighted reliability: 0.95 이상

Retrospective pilot 최소조건:

- 연속 520회
- draw linkage 100%
- machine 또는 ball-set coverage 95% 이상
- selection timestamp coverage 95% 이상
- source traceability 99% 이상
- stable context level당 104회
- interaction cell당 52회
- transient field 260회, bin당 52회

## Gate sequence

```text
M4F-1 specification
M4F-2 source-access audit
M4F-3 26-draw ingestion-only shadow
M4F-4 synthetic null/positive controls
M4F-5 retrospective metadata evidence pilot
M4F-6 future CAL/SEALED specification
```

현재 M4F-1만 완료됐다.

## Actual pilot hard entry

모두 충족해야 `REAL_METADATA_PILOT_ENTRY_PASS`다.

- lawful source access documented
- 520 consecutive linked draws
- core coverage and reliability PASS
- at least two retained context levels, each 104 draws
- A0 coverage 90% 이상 for deployable analysis
- outcome contamination 0
- mandatory synthetic null PASS
- P1 machine 또는 P2 ball-set lift 1.25 positive control PASS

Conditional PASS는 허용하지 않는다.

## 공개원천 현재 결론

공식 MBC 공개원천은 방송일정·변경공지·영상·참관절차를 제공하고, KMA는 ASOS/AWS 외부환경을 제공한다. 그러나 공개원천만으로 회차별 machine, ball set, certified measurements, pre-draw logs, local indoor sensor의 520회 primary archive는 확인되지 않았다.

따라서 운영기관 또는 방송사 원기록 접근경로가 없으면 M4 primary pilot은 `NO_DATA_PATH`로 종료한다.

## 금지사항

별도 사용자 승인 없이 다음을 수행하지 않는다.

- data owner에게 요청 발송
- scraping·영상추출·OCR
- 센서설치 또는 데이터 수집
- Python schema·ingestion 구현
- 추가 DEV 또는 synthetic 실행
- 실제 metadata import·결합
- CAL·SEALED
- 실제 번호 Walk-forward
- 사용자용 번호 생성
- 모바일 UI·Supabase 개발
- main 병합

## 다음 Gate

사용자 승인 후에만 `Gate 2-3P-M4F-2 source-access audit` 명세·자료요청서 작성으로 이동한다. 실제 요청 발송과 데이터 수집은 M4F-2에서도 별도 승인 전 금지한다.

## 작업 종료 시 누적

- `AGENTS.md`
- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 출처·한계·차단사항
