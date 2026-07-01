# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`  
기준 브랜치: `feature/r3m3-predictable-group-engine`  
관련 Issue: #33

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-R3 | NO_ELIGIBLE_CONFIG | 100% |
| Gate 2-3P-R3M-2 | ORACLE_PASS | 100% |
| Gate 2-3P-R3M-3-2 | PREDICTABLE_GROUP_FAIL | 100% |
| M3 past-number path | FROZEN | 100% |
| Gate 2-3P-M4F-1 | **상세 명세 완료·승인 대기** | 100% |
| Gate 2-3P-M4F-2 | 미승인·미실행 | 0% |
| Gate 2-3P-M4F-3 | 차단 | 0% |
| Gate 2-3P-M4F-4 | 차단 | 0% |
| Gate 2-3P-M4F-5 | 차단 | 0% |
| CAL·SEALED | 차단 | 0% |
| 실제 번호·모바일 | 차단 | 0% |

## M3 실패 잠금

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

과거 번호 이력 learner는 추가 튜닝 없이 동결한다.

## M4F-1 고정값

### Time and leakage

- A0 deployable: available before prediction lock
- A1 research-only: after lock, before draw
- A2 post-draw: prohibited
- A3 outcome-derived: prohibited

### Minimum data

- ingestion shadow: 26 consecutive draws, no prediction
- retrospective pilot: 520 consecutive linked draws
- stable level support: 104
- interaction cell support: 52
- transient total support: 260
- transient bin support: 52

### Coverage

- draw linkage 100%
- machine or ball-set 95%+
- selection timestamp 95%+
- source traceability 99%+
- A0 coverage 90%+ for deployable analysis
- core stable reliability 0.95+

### Sources

- Grade A: operator/broadcaster logs, certified measurements, local sensors
- Grade B: official MBC, 동행복권, KMA public data
- Grade C: double-reviewed official-video extraction, diagnostic-only
- Grade D: rejected

### Actual pilot entry

All hard gates are mandatory. Conditional PASS is prohibited.

```text
SOURCE_ACCESS_PASS
+ 520 linked draws
+ coverage/reliability PASS
+ context variation PASS
+ leakage PASS
+ mandatory null PASS
+ machine or ball-set positive control PASS
= REAL_METADATA_PILOT_ENTRY_PASS
```

## 공개원천 결론

공개 MBC·동행복권·KMA 원천은 방송일정·공식결과·외부기상 확인에는 유효하다. 그러나 machine, ball set, certified measurement, pre-draw operations, local indoor sensor의 520회 primary archive는 공개원천만으로 확인되지 않았다.

원기록 접근경로가 없으면 `NO_DATA_PATH`다.

## 현재 판정

```text
M4F-1 = SPEC COMPLETE / APPROVAL PENDING
M4F-2 and later = BLOCKED
Full M3 DEV = BLOCKED
R4 = BLOCKED
Final distribution = M0 only
```

## 다음 단계

사용자 승인 후 M4F-2에서 source-access audit 상세 명세와 자료요청서 초안만 작성한다. 실제 요청 발송·데이터 수집·Python 구현은 별도 승인 전 금지한다.
