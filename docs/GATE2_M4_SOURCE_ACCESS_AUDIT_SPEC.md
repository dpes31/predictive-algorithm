# Gate 2-3P-M4F-2 Source-Access Audit Specification

상태: 사용자 검토용 상세 명세  
작성일: 2026-07-01  
기준 모델: `5.0.0-research`  
M4 data feasibility contract: `1.0.0`  
Source-access audit contract: `1.0.0`  
작업 브랜치: `feature/gate2p-m4f2-source-access-spec`

## 1. 목적

Gate 2-3P-M4F-1에서 고정한 물리·운영 metadata 요건을 실제 원천기관이 충족할 수 있는지 문서로 판정한다.

이번 Gate는 다음만 수행한다.

- source-access audit 상세 명세
- 동행복권·MBC 자료요청서 초안
- field-level data dictionary 템플릿
- sample schema
- 권한·보안·timestamp 검증 체크리스트
- `SOURCE_ACCESS_PASS`, `SOURCE_ACCESS_FAIL`, `NO_DATA_PATH` 판정규칙

실제 자료요청 발송, 전화·메일 접촉, 데이터 수집·다운로드·영상추출, Python 구현, DEV, CAL, SEALED, 실제 번호 Walk-forward, 모바일 UI, main 병합은 수행하지 않는다.

## 2. 이전 상태 유지

```text
Gate 2-3P-R3M-3-2 = PREDICTABLE_GROUP_FAIL
M3 past-number path = FROZEN
Gate 2-3P-M4F-1 = APPROVED
Gate 2-3P-M4F-2 = SPECIFICATION ONLY
Full M3 DEV = BLOCKED
Gate 2-3P-R4 = BLOCKED
Final distribution = M0_ONLY
```

기존 결과와 모든 lock hash는 변경하지 않는다.

## 3. 감사 대상

### 3.1 동행복권 또는 추첨운영기관

우선 확인 대상:

- 회차별 추첨기 식별정보
- 회차별 볼 세트 식별정보
- 장비·볼 선정시각
- 장비 점검·정비·교체 이력
- 볼 세트 검사·인증·교체 이력
- 사전 테스트 횟수·상태·완료시각
- 원본 record ID와 수정이력
- 공식 결과와 분리된 metadata 저장구조

### 3.2 MBC 또는 추첨방송 운영부서

우선 확인 대상:

- 예정·실제 추첨시각
- 스튜디오·장소 식별정보
- 장비 반입·인수·준비 시각
- 리허설·사전 테스트 운영기록
- 현장 온습도·기압·전원·장비상태 기록 존재 여부
- 방송 편성 변경·지연 기록
- 원본 log와 수정이력

### 3.3 공인 측정·검교정 주체

접근 가능 시 확인 대상:

- 번호별 볼 질량·직경·진원도·마모 측정
- 측정장비 ID와 검교정 상태
- 측정 불확도
- 측정시각
- 볼 번호와 측정값을 연결하는 label mapping

## 4. 감사 원칙

1. 존재 여부와 접근권한을 분리한다.
2. “기록이 있다”는 구두 설명만으로 통과하지 않는다.
3. 필드명보다 timestamp 의미와 생성 시점을 우선 검증한다.
4. 실제 결과번호가 포함된 파일과 metadata 파일을 물리적으로 분리할 수 있어야 한다.
5. 개인 식별정보는 요청·수집하지 않는다.
6. 원본자료 대신 비식별화된 식별자와 최소필드 제공을 우선한다.
7. 장비·볼 ID는 일관된 pseudonymous ID로 대체할 수 있다.
8. 데이터 정정·덮어쓰기·삭제 이력이 보존돼야 한다.
9. 자료가 없거나 접근이 불가능한 경우 이를 실패가 아닌 `NO_DATA_PATH`로 명확히 잠근다.
10. 실제 결과를 확인한 뒤 접근기준이나 필드요건을 낮추지 않는다.

## 5. 필수 증빙 패킷

각 기관은 가능한 범위에서 다음 문서를 제공해야 한다. 이번 Gate에서는 제공을 요청하는 초안만 작성한다.

### 5.1 소유권·책임

- data owner 부서
- system owner 부서
- 실무 contact role
- 승인권자 role
- 기록 생성주체
- 기록 보존주체

실명이나 개인 연락처는 최종 감사보고서에 저장하지 않고 role만 기록한다.

### 5.2 데이터 사전

- field name
- business definition
- data type
- unit
- allowed values
- null meaning
- generation system
- observed/recorded/available timestamp 의미
- correction rule
- retention period
- source record identifier

### 5.3 역사적 범위

- 최초 기록 회차와 날짜
- 마지막 기록 회차와 날짜
- 연속 회차 수
- 누락 회차 목록
- 시스템 변경·마이그레이션 기간
- 장비·볼 식별체계 변경일

### 5.4 Timestamp 의미

- clock source
- timezone
- server clock synchronization 방식
- timestamp precision
- timestamp가 생성되는 event
- 수기 입력 가능 여부
- 사후 수정 가능 여부
- 수정 전 timestamp 보존 여부

### 5.5 정정·변경 이력

- append-only 여부
- update/delete 가능 여부
- before/after value 보존 여부
- correction reason
- corrected_at
- corrected_by role
- immutable audit ID

### 5.6 접근·법적 권한

- 연구사용 허용 여부
- 제3자 제공 가능 여부
- 저장 위치 제한
- 국외이전 제한
- 재배포 제한
- 보존기간
- 파기 의무
- 결과 공개 제한
- 기관 보안심사 필요 여부

### 5.7 샘플 구조

- outcome field가 제거된 3~10개 dummy record
- 실제 개인·보안정보가 없는 schema-only sample
- source-record ID 형식
- timestamp 형식
- correction record 예시

## 6. Audit evidence level

```text
E0_UNVERIFIED
구두 설명, 비공식 메모, 출처 불명

E1_DOCUMENTED
기관 공식 답변 또는 데이터 사전

E2_SAMPLED
비식별 sample schema와 record 구조 확인

E3_SYSTEM_VERIFIED
원 시스템 설명, audit trail, timestamp·정정 구조 확인
```

판정에 필요한 최소수준:

- source existence: E1 이상
- timestamp semantics: E1 이상
- immutable ID and correction history: E2 이상
- outcome separation: E2 이상
- 520회 coverage: E1 공식 범위표 이상
- 최종 `SOURCE_ACCESS_PASS`: 모든 hard item E2 이상, 핵심 timestamp·audit trail은 E3 또는 이에 준하는 공식 증빙

## 7. 감사 단계

### Step A — 기관·시스템 식별

- data owner 확인
- source system name 확인
- 운영기관과 방송사 간 데이터 책임경계 확인

### Step B — 필드 존재 감사

필수 stable source 중 하나 이상이 존재해야 한다.

```text
machine_id historical source
OR ball_set_id historical source
```

외부 날씨·방송시간만 존재하면 primary source로 인정하지 않는다.

### Step C — 역사적 범위 감사

- 연속 520회 잠재 결합 가능 여부
- 누락·시스템변경 구간
- ID 체계의 일관성
- 회차별 선택시각 존재 여부

### Step D — Timestamp 감사

- observed_at
- recorded_at
- available_at
- source_published_at
- draw_scheduled_at
- draw_actual_at
- correction timestamps

A0/A1/A2/A3 분류가 가능한지 확인한다.

### Step E — 누출·분리 감사

- metadata payload에서 winning numbers 제거 가능
- draw order·bonus 제거 가능
- 결과 공개 후 생성된 값 구분 가능
- 사후 수정 record 식별 가능

### Step F — 권한·보안 감사

- lawful research use
- 최소권한
- 암호화 전송
- 저장기간
- 파기
- 재배포 금지
- 보안사고 통지

### Step G — 판정

정해진 hard criteria에 따라 단일 final status를 부여한다.

## 8. Hard criteria

### H1 Primary source existence

다음 중 하나 이상:

- 회차별 machine_id source
- 회차별 ball_set_id source
- 번호별 certified ball measurement source

### H2 Historical coverage

- 최소 520개 연속 회차 잠재 결합
- draw_no/date mapping 가능
- source system migration gap 설명 가능

### H3 Timestamp integrity

- 선택·관측·기록·이용가능·추첨시각 구분
- timezone 확인
- 사후수정 여부 확인
- prediction-lock 전 이용가능성 판정 가능

### H4 Immutable identity and correction history

- source_record_id 존재
- correction 전후 보존
- 삭제·덮어쓰기 추적 가능

### H5 Outcome separation

- winning numbers, bonus, draw order를 metadata 제공물에서 물리적으로 제외 가능
- outcome-derived field를 식별·제외 가능

### H6 Research authorization

- 연구 사용의 서면 허용 가능
- 저장·보존·파기 조건 합의 가능
- 개인·민감정보 없이 제공 가능

### H7 Security feasibility

- 승인된 secure transfer 가능
- at-rest encryption 가능
- access log 가능
- least-privilege 운영 가능

### H8 Field-level traceability

- 각 field의 source system, business definition, timestamp semantics, null meaning 확인 가능

## 9. Final status 규칙

### 9.1 `SOURCE_ACCESS_PASS`

다음을 모두 만족할 때만 부여한다.

```text
H1 PASS
AND H2 PASS
AND H3 PASS
AND H4 PASS
AND H5 PASS
AND H6 PASS
AND H7 PASS
AND H8 PASS
AND no unresolved critical contradiction
```

추가 조건:

- machine 또는 ball_set의 stable primary source가 포함돼야 함
- 외부 날씨·방송시간만으로는 PASS 불가
- 실제 데이터 제공 승인이 아니라 M4F-3 shadow 설계에 진입할 수 있는 접근 타당성 PASS임

### 9.2 `SOURCE_ACCESS_FAIL`

원천기록 또는 접근경로는 존재하지만 하나 이상의 hard criterion이 현재 충족되지 않을 때 부여한다.

예:

- 520회가 아닌 300회만 존재
- source ID는 있으나 timestamp 의미가 불명확
- 연구사용은 가능하지만 outcome 분리가 불가능
- field dictionary가 불완전
- secure transfer 또는 audit log가 준비되지 않음

`SOURCE_ACCESS_FAIL`은 실패항목과 remediation 가능 여부를 기록한다. 기준완화는 금지한다.

### 9.3 `NO_DATA_PATH`

다음 중 하나가 공식적으로 확인될 때 부여한다.

- machine·ball_set·ball measurement 원기록이 존재하지 않음
- 기록은 존재했으나 520회 범위를 복구할 수 없음
- timestamp 또는 회차연결키가 원천적으로 생성되지 않음
- outcome과 metadata를 분리할 수 없는 구조이며 재추출도 불가능
- data owner가 연구제공을 최종적으로 허용할 수 없다고 공식 답변
- 원본기관을 식별할 수 없고 책임기관 간 이관도 불가능
- 공개 proxy 외에는 primary physical/operational source가 없음

`NO_DATA_PATH`에서는 추가 scraping·영상추정으로 primary source를 대체하지 않는다.

### 9.4 Interim status

자료가 아직 회신되지 않았거나 증빙이 부족한 동안은:

```text
AUDIT_INCOMPLETE
```

`AUDIT_INCOMPLETE`는 final status가 아니며 PASS로 간주하지 않는다.

## 10. Critical contradiction

다음 중 하나는 즉시 FAIL 또는 NO_DATA_PATH 검토대상이다.

- 동일 회차 machine_id 충돌
- ball_set_id와 선정원장 불일치
- available_at이 draw 이후인데 pre-draw로 표시
- timestamp가 대량 동일값 또는 사후 일괄생성
- source ID 재사용
- 수정 전 기록이 보존되지 않음
- sample payload에 outcome field 포함
- 기관 답변과 sample schema가 모순

## 11. 감사 산출물

M4F-2 실제 감사가 승인될 경우 다음을 생성한다.

- institution response register
- evidence index
- field dictionary
- source system map
- coverage matrix
- timestamp semantics matrix
- security and permission matrix
- contradiction log
- final decision record
- source evidence hash manifest

이번 Gate에서는 템플릿만 작성하며 실제 값을 채우지 않는다.

## 12. Scope lock

현재 작업에서는 다음을 수행하지 않는다.

- 요청서 발송
- 기관 접촉
- 데이터 열람·다운로드
- scraping·OCR·영상추출
- Python schema validation
- shadow ingestion
- synthetic controls
- actual metadata pilot
- CAL·SEALED
- 실제 번호 Walk-forward
- 모바일 UI
- main 병합
