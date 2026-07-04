# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-m4f2-source-access-spec`  
기준 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`  
관련 Issue: #34  
현재 Draft PR: #35

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-R3M-3-2 | PREDICTABLE_GROUP_FAIL | 100% |
| M3 past-number path | FROZEN | 100% |
| Gate 2-3P-M4F-1 | 승인 완료 | 100% |
| Gate 2-3P-M4F-2 | **상세 명세 완료·승인 대기** | 100% |
| 실제 source audit | NOT_EVALUATED | 0% |
| Gate 2-3P-M4F-3 | BLOCKED | 0% |
| Gate 2-3P-M4F-4 | BLOCKED | 0% |
| Gate 2-3P-M4F-5 | BLOCKED | 0% |
| CAL·SEALED | BLOCKED | 0% |
| 실제 번호·모바일 | BLOCKED | 0% |

## M4F-2 완료 산출물

- audit specification
- decision rules
- authority/security/timestamp checklist
- field dictionary template
- JSON Schema and dummy record
- 기관별 미발송 자료구조 문의서 2종
- AGENTS and handoff synchronization

## Hard criteria

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

## 판정규칙

```text
path-ending evidence confirmed -> NO_DATA_PATH
H1~H8 all PASS             -> SOURCE_ACCESS_PASS
all H known and any FAIL   -> SOURCE_ACCESS_FAIL
otherwise                  -> AUDIT_INCOMPLETE
```

- PASS는 실제 데이터 수집 승인이 아님
- FAIL은 기준완화 없이 실패항목을 보존
- NO_DATA_PATH는 공식적인 부재·복구불가·최종 접근불가 확인이 필요
- 무응답은 AUDIT_INCOMPLETE이며 NO_DATA_PATH가 아님

## Evidence

```text
E0_UNVERIFIED
E1_DOCUMENTED
E2_SAMPLED
E3_SYSTEM_VERIFIED
```

최종 PASS에는 각 hard criterion 최소 E2가 필요하며 핵심 timestamp와 audit trail은 E3 또는 동등한 공식증빙이 필요하다.

## Schema lock

Sample schema는 다음을 강제한다.

- outcome fields excluded
- additional properties rejected
- provenance required
- availability class required
- correction status and record hash required
- personal information prohibited
- dummy record is synthetic only

## 현재 판정

```text
M4F-2 = SPEC COMPLETE / APPROVAL PENDING
Actual source status = NOT_EVALUATED
External contact = NOT_PERFORMED
Data received = false
M4F-3 and later = BLOCKED
Final distribution = M0 only
```

## 다음 단계

다음은 `M4F-2A request package finalization`이다. 발신주체·연구주체·보존기간·수신부서·권한조건을 확정하고 최종 문안만 잠근다. 외부 전달은 별도 승인 전 금지한다.
