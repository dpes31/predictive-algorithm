# Gate 2-3P-M4F-2 Authority, Security, and Timestamp Verification Checklist

상태: 빈 감사 템플릿  
작성일: 2026-07-01  
Contract: `m4-source-access-1.0.0`

각 항목은 `PASS`, `FAIL`, `UNKNOWN`, `NOT_APPLICABLE` 중 하나로 기록한다. `UNKNOWN`은 PASS로 계산하지 않는다.

## 1. Authority and lawful use

| ID | 확인항목 | 판정 | 증빙 ID | 비고 |
|---|---|---|---|---|
| A-01 | data owner 부서가 공식 확인됨 | | | |
| A-02 | system owner 부서가 공식 확인됨 | | | |
| A-03 | 자료 제공 승인권자 role이 확인됨 | | | |
| A-04 | 기록 생성주체와 보존주체가 구분됨 | | | |
| A-05 | 연구사용 목적이 서면 허용 가능함 | | | |
| A-06 | 제3자 제공·재위탁 조건이 명시됨 | | | |
| A-07 | 저장 위치와 국외이전 제한이 확인됨 | | | |
| A-08 | 보존기간과 파기 의무가 확인됨 | | | |
| A-09 | 결과 공개·인용 제한이 확인됨 | | | |
| A-10 | 개인정보·민감정보 없이 제공 가능함 | | | |
| A-11 | 장비·볼 ID의 가명화가 허용됨 | | | |
| A-12 | 기관의 보안심사·NDA 절차가 확인됨 | | | |

Critical items: A-01, A-03, A-05, A-08, A-10.

## 2. Source existence and historical coverage

| ID | 확인항목 | 판정 | 증빙 ID | 비고 |
|---|---|---|---|---|
| S-01 | 회차별 machine_id 원천 존재 | | | |
| S-02 | 회차별 ball_set_id 원천 존재 | | | |
| S-03 | 번호별 ball measurement 원천 존재 | | | |
| S-04 | machine 또는 ball_set 중 최소 하나 존재 | | | |
| S-05 | 최소 520개 연속 회차가 잠재 결합 가능 | | | |
| S-06 | 최초·최종 보유 회차가 공식 확인됨 | | | |
| S-07 | 누락 회차 목록이 제공 가능함 | | | |
| S-08 | 시스템 변경·마이그레이션 이력이 확인됨 | | | |
| S-09 | ID 체계 변경일과 mapping이 확인됨 | | | |
| S-10 | draw_no·draw_date 연결키가 존재 | | | |
| S-11 | source_record_id가 존재 | | | |
| S-12 | 동일 record ID 재사용 여부를 검사 가능 | | | |

Critical items: S-04, S-05, S-10, S-11.

## 3. Outcome separation and leakage

| ID | 확인항목 | 판정 | 증빙 ID | 비고 |
|---|---|---|---|---|
| L-01 | metadata payload에서 winning numbers 제거 가능 | | | |
| L-02 | bonus number 제거 가능 | | | |
| L-03 | draw order 제거 가능 | | | |
| L-04 | 결과 공개 후 파생 field 식별 가능 | | | |
| L-05 | 결과 DB와 metadata DB가 논리적 또는 물리적으로 분리됨 | | | |
| L-06 | sample schema에 outcome field가 없음 | | | |
| L-07 | test number sequence를 제외 가능 | | | |
| L-08 | post-draw 수정 record를 식별 가능 | | | |
| L-09 | outcome join은 별도 승인된 evaluation 단계에서만 가능 | | | |
| L-10 | 기관 제공단계에서 outcome contamination 검사가 가능 | | | |

Critical items: L-01, L-02, L-03, L-04, L-06.

## 4. Timestamp semantics

| ID | 확인항목 | 판정 | 증빙 ID | 비고 |
|---|---|---|---|---|
| T-01 | draw_scheduled_at 의미가 정의됨 | | | |
| T-02 | draw_actual_at 의미가 정의됨 | | | |
| T-03 | observed_at 의미가 정의됨 | | | |
| T-04 | recorded_at 의미가 정의됨 | | | |
| T-05 | available_at 의미가 정의됨 | | | |
| T-06 | source_published_at 의미가 정의됨 | | | |
| T-07 | correction timestamp 의미가 정의됨 | | | |
| T-08 | 원본 timezone이 확인됨 | | | |
| T-09 | UTC 변환규칙이 확인됨 | | | |
| T-10 | timestamp precision이 확인됨 | | | |
| T-11 | clock source가 확인됨 | | | |
| T-12 | NTP 또는 동기화 정책이 확인됨 | | | |
| T-13 | clock drift·skew 허용범위가 확인됨 | | | |
| T-14 | 수기 timestamp 입력 가능 여부가 확인됨 | | | |
| T-15 | timestamp 사후수정 가능 여부가 확인됨 | | | |
| T-16 | 수정 전 timestamp가 보존됨 | | | |
| T-17 | A0/A1/A2/A3 분류가 record별 가능함 | | | |
| T-18 | machine·ball selection 시각이 존재 | | | |
| T-19 | pre-draw test 완료시각이 존재 | | | |
| T-20 | 실제 추첨시각의 공식 근거가 존재 | | | |

Critical items: T-02, T-03, T-04, T-05, T-08, T-15, T-16, T-17.

## 5. Timestamp consistency tests

향후 sample이 제공될 경우 다음 논리검사를 수행한다. 이번 Gate에서는 실행하지 않는다.

| ID | 논리조건 | 예상조치 |
|---|---|---|
| TC-01 | observed_at <= recorded_at | 위반 시 contradiction |
| TC-02 | recorded_at <= available_at 또는 지연사유 존재 | 위반 시 설명 요구 |
| TC-03 | machine selection observed_at < draw_actual_at | 위반 시 A2/invalid |
| TC-04 | ball selection observed_at < draw_actual_at | 위반 시 A2/invalid |
| TC-05 | pre_draw_tests.completed_at < draw_actual_at | 위반 시 invalid |
| TC-06 | prediction-eligible이면 available_at <= prediction_lock_at | 위반 시 A1/A2 |
| TC-07 | source_published_at이 있으면 원 게시물 timestamp와 일치 | 위반 시 source integrity fail |
| TC-08 | corrected_at >= original recorded_at | 위반 시 contradiction |
| TC-09 | previous_record_hash가 실제 이전 version과 일치 | 위반 시 immutability fail |
| TC-10 | draw_actual_at 변경 시 공식 exception record 존재 | 없으면 join fail |
| TC-11 | 동일 source_record_id의 timestamp 역행 없음 | 위반 시 audit fail |
| TC-12 | 대량 record의 timestamp 일괄생성 여부 탐지 | 발견 시 E0/E1로 강등 |

## 6. Security controls

| ID | 확인항목 | 판정 | 증빙 ID | 비고 |
|---|---|---|---|---|
| SEC-01 | 전송채널이 승인됨 | | | |
| SEC-02 | 전송 중 암호화 | | | |
| SEC-03 | 저장 시 암호화 | | | |
| SEC-04 | 암호키 관리책임이 정의됨 | | | |
| SEC-05 | least-privilege role이 정의됨 | | | |
| SEC-06 | 사용자별 접근계정 사용 | | | |
| SEC-07 | 접근로그 보존 | | | |
| SEC-08 | 다운로드·반출로그 보존 | | | |
| SEC-09 | 원자료 복제 제한 | | | |
| SEC-10 | 개인기기 저장 금지 | | | |
| SEC-11 | 승인되지 않은 클라우드 업로드 금지 | | | |
| SEC-12 | 백업 범위와 파기정책 확인 | | | |
| SEC-13 | 연구종료 후 파기증빙 가능 | | | |
| SEC-14 | 보안사고 통지절차 확인 | | | |
| SEC-15 | 재배포·공개 제한 확인 | | | |
| SEC-16 | source ID 가명화 가능 | | | |
| SEC-17 | 개인정보 field 제거 확인 | | | |
| SEC-18 | sample record가 synthetic 또는 비식별임 | | | |

Critical items: SEC-01, SEC-02, SEC-03, SEC-05, SEC-07, SEC-13, SEC-17.

## 7. Data integrity and corrections

| ID | 확인항목 | 판정 | 증빙 ID | 비고 |
|---|---|---|---|---|
| I-01 | 원본 record가 immutable ID를 가짐 | | | |
| I-02 | record hash 생성 가능 | | | |
| I-03 | append-only 또는 version history 존재 | | | |
| I-04 | correction reason 보존 | | | |
| I-05 | correction role 보존 | | | |
| I-06 | correction timestamp 보존 | | | |
| I-07 | 이전 값과 새 값 모두 보존 | | | |
| I-08 | 삭제 record의 tombstone 또는 이력 존재 | | | |
| I-09 | schema version 보존 | | | |
| I-10 | source system migration mapping 존재 | | | |
| I-11 | checksum 재현 가능 | | | |
| I-12 | 동일 extract 재생성 시 hash 비교 가능 | | | |

Critical items: I-01, I-03, I-07, I-09.

## 8. Field-level minimum documentation

각 primary candidate field는 다음이 모두 PASS여야 한다.

- business definition
- source system
- source record ID
- data type and unit
- null meaning
- generation event
- timestamp semantics
- correction rule
- historical coverage
- outcome contamination flag
- security classification
- evidence level
- reliability components

하나라도 UNKNOWN이면 prediction-eligible로 분류하지 않는다.

## 9. Decision worksheet

### 9.1 Hard criteria summary

| Hard criterion | Required checklist groups | Final result |
|---|---|---|
| H1 Primary source existence | S-01~S-04 | |
| H2 Historical coverage | S-05~S-10 | |
| H3 Timestamp integrity | T critical items | |
| H4 Immutable ID and corrections | I critical items | |
| H5 Outcome separation | L critical items | |
| H6 Research authorization | A critical items | |
| H7 Security feasibility | SEC critical items | |
| H8 Field traceability | field dictionary completion | |

### 9.2 Final decision

```text
SOURCE_ACCESS_PASS
SOURCE_ACCESS_FAIL
NO_DATA_PATH
AUDIT_INCOMPLETE
```

- 모든 H1~H8 PASS: `SOURCE_ACCESS_PASS`
- source/path는 존재하나 하나 이상 FAIL: `SOURCE_ACCESS_FAIL`
- primary source 부재·복구불가·최종 제공불가: `NO_DATA_PATH`
- 증빙 미회신 또는 UNKNOWN 잔존: `AUDIT_INCOMPLETE`

## 10. Sign-off template

| role | name or role ID | decision | signed_at | evidence hash |
|---|---|---|---|---|
| audit preparer | | | | |
| data owner reviewer | | | | |
| security reviewer | | | | |
| research approver | | | | |

개인 실명은 외부공개 보고서에서 role ID로 치환할 수 있다.
