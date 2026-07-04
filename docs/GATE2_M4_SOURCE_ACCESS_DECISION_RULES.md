# Gate 2-3P-M4F-2 Source-Access Decision Rules

상태: 사전등록 판정규칙  
Contract: `m4-source-access-1.0.0`

## 1. 목적

Source-access 감사결과를 사후 해석 없이 단일 상태로 결정한다. 판정순서와 우선순위를 변경하지 않는다.

## 2. 입력

판정은 다음 8개 hard criterion과 path-ending evidence를 입력으로 사용한다.

```text
H1 primary source existence
H2 historical coverage
H3 timestamp integrity
H4 immutable identity and correction history
H5 outcome separation
H6 research authorization
H7 security feasibility
H8 field-level traceability
```

각 H는 `PASS`, `FAIL`, `UNKNOWN` 중 하나다.

Path-ending evidence:

```text
P1 primary records do not exist
P2 required historical range is irrecoverable
P3 timestamp or draw linkage was never generated and cannot be reconstructed
P4 metadata and outcome cannot be separated and cannot be re-extracted
P5 lawful research access is finally and formally prohibited
P6 responsible source institution cannot be identified or assumes no ownership
P7 only diagnostic public proxies exist
```

각 P는 `CONFIRMED`, `NOT_CONFIRMED`, `UNKNOWN` 중 하나다.

## 3. Evidence requirements

- H1~H8의 PASS에는 최소 E2 evidence가 필요하다.
- H3·H4의 핵심항목에는 E3 또는 이에 준하는 공식 시스템 증빙이 필요하다.
- Path-ending evidence의 CONFIRMED에는 최소 E1 공식답변이 필요하다.
- 구두설명, 비공식 게시물, 추정은 CONFIRMED로 인정하지 않는다.

## 4. Decision precedence

다음 순서대로 한 번만 판정한다.

### Rule 1 — `NO_DATA_PATH`

다음 중 하나라도 CONFIRMED이면:

```text
P1 OR P2 OR P3 OR P4 OR P5 OR P6 OR P7
```

최종판정:

```text
NO_DATA_PATH
```

단, P5는 관련 data owner와 승인권자의 최종 공식답변이어야 한다. 담당부서 미확인 또는 1차 문의 미회신은 P5가 아니다.

### Rule 2 — `SOURCE_ACCESS_PASS`

Rule 1이 적용되지 않고 다음을 모두 만족하면:

```text
H1=PASS
AND H2=PASS
AND H3=PASS
AND H4=PASS
AND H5=PASS
AND H6=PASS
AND H7=PASS
AND H8=PASS
```

최종판정:

```text
SOURCE_ACCESS_PASS
```

PASS는 실제 데이터 수집 승인이나 예측력 통과가 아니다. M4F-3 ingestion-only shadow 설계를 요청할 자격만 의미한다.

### Rule 3 — `SOURCE_ACCESS_FAIL`

Rule 1과 Rule 2가 적용되지 않고 다음을 모두 만족하면:

```text
all H values are known
AND at least one H=FAIL
AND primary source/access path still exists
```

최종판정:

```text
SOURCE_ACCESS_FAIL
```

FAIL은 기준을 낮추지 않는다. 각 FAIL 항목을 `REMEDIABLE` 또는 `NON_REMEDIABLE`로 표시하지만, 재감사는 별도 승인 없이 수행하지 않는다.

### Rule 4 — `AUDIT_INCOMPLETE`

Rule 1~3이 적용되지 않으면:

```text
AUDIT_INCOMPLETE
```

다음 사례가 포함된다.

- 기관 미회신
- 담당부서 미확인
- 증빙 없이 구두설명만 존재
- 하나 이상의 H 또는 P가 UNKNOWN
- sample schema 미제공
- timestamp 의미 미확인

`AUDIT_INCOMPLETE`는 PASS나 FAIL로 간주하지 않는다.

## 5. Decision matrix

| Path-ending confirmed | H1~H8 모두 PASS | 모든 H known, 일부 FAIL | 판정 |
|---|---|---|---|
| YES | any | any | NO_DATA_PATH |
| NO | YES | NO | SOURCE_ACCESS_PASS |
| NO | NO | YES | SOURCE_ACCESS_FAIL |
| NO/UNKNOWN | NO | NO | AUDIT_INCOMPLETE |

## 6. 기관별 결합판정

동행복권과 MBC를 각각 감사한 후 전체 M4 source status를 판정한다.

### 6.1 기관별 상태

```text
DONGHAENG_STATUS
MBC_STATUS
MEASUREMENT_PROVIDER_STATUS
```

### 6.2 전체 PASS

다음이 모두 필요하다.

```text
at least one institution = SOURCE_ACCESS_PASS for machine or ball-set stable source
AND timestamp responsibility boundaries are documented
AND no institution-level critical contradiction remains
```

한 기관이 stable source와 timestamp를 모두 보유하면 다른 기관의 PASS는 필수가 아니다. 다만 실제 추첨시각과 방송운영 timestamp의 책임경계는 문서화돼야 한다.

### 6.3 전체 FAIL

- primary source path는 존재하지만 기관 간 책임경계·권한·보안·timestamp 중 hard criterion이 FAIL
- 어느 기관도 complete PASS를 만들지 못했으나 remediation 가능성이 존재

### 6.4 전체 NO_DATA_PATH

- 모든 식별 가능한 책임기관에서 primary source 부재 또는 최종 제공불가가 확인
- 공개 proxy만 존재
- 520회 archive가 어느 기관에도 없고 복구불가

## 7. No-response policy

실제 요청 발송이 별도 승인된 이후에만 적용한다.

- 승인된 공식 채널로 1차 요청
- 최소 10영업일 대기
- 동일 내용 1회 재문의
- 최소 10영업일 추가 대기

두 번의 무응답만으로 `NO_DATA_PATH`를 판정하지 않는다. 상태는 `AUDIT_INCOMPLETE`로 유지한다.

## 8. Contradiction precedence

다음 critical contradiction은 H3, H4 또는 H5를 FAIL로 만든다.

- pre-draw 표시값이 draw 후 생성
- source ID 재사용
- correction 전 record 미보존
- sample payload에 outcome field 포함
- 기관별 timestamp 정의 상충
- machine 또는 ball-set ID가 같은 회차에서 충돌

모순이 source 구조상 해결 불가능하다는 공식증빙이 있으면 `NO_DATA_PATH` 검토대상이 된다.

## 9. Locked outputs

최종 감사 시 다음을 잠근다.

- institution status
- H1~H8 values
- P1~P7 values
- evidence index hash
- field dictionary hash
- sample schema hash
- checklist hash
- contradiction log hash
- final decision
- decision timestamp
- decision lock hash

## 10. Current status

이번 Gate에서는 실제 감사입력이 없으므로 판정은 실행하지 않는다.

```text
Gate 2-3P-M4F-2 = SPEC COMPLETE / APPROVAL PENDING
Actual source status = NOT_EVALUATED
Requests sent = false
Data received = false
```
