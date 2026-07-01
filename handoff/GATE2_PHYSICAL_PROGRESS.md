# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/r3m3-predictable-group-spec`  
기준 브랜치: `feature/gate2p-r3m2-oracle-engine`  
관련 이슈: #30  
현재 Draft PR: #31

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-R3 | NO_ELIGIBLE_CONFIG | 100% |
| Gate 2-3P-R4 | BLOCKED | 0% |
| Gate 2-3P-R3M-1 | 승인 완료 | 100% |
| Gate 2-3P-R3M-2 | ORACLE_PASS | 100% |
| Gate 2-3P-R3M-3-1 | **상세 명세 완료·승인 대기** | 100% |
| Gate 2-3P-R3M-3-2 | 미승인·미실행 | 0% |
| full M3 DEV | 차단 | 0% |
| CAL·SEALED | 차단 | 0% |
| 실제 데이터·모바일 | 차단 | 0% |

## Oracle 기준점

- model `5.0.0-research`
- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- positive activation `91.85%`
- null false activation `0.08%`
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

## R3M-3-1 고정값

- outer learning window `520`
- half-life `104`
- prior strength `52`
- initial internal fit `260`
- validation folds `5 x 52`
- group sizes `{6,10,15}`
- betting block `52`
- detection horizon `520`
- activation threshold `1000`
- active life `208`
- main namespace `DEV-PG`
- bootstrap namespace `DEV-PG-CI`

## PASS 기준

- availability >= 80%
- activation >= 80%
- median delay <= 520
- direction accuracy >= 80%
- direction trials >= 16000
- mean and one-sided lower delta Log Loss > 0
- mean delta Brier >= 0 and one-sided lower >= 0
- null false activation <= 0.1%
- null exact upper <= 0.2%

모든 기준을 통과해야 `PREDICTABLE_GROUP_PASS`다.

## 현재 판정

```text
R3M-3-1 = SPEC COMPLETE / APPROVAL PENDING
R3M-3-2 = BLOCKED
Full M3 DEV = BLOCKED
R4 = BLOCKED
Final distribution = M0 only
```

## 다음 단계

사용자 승인 후 R3M-3-2에서 고정 명세 그대로 Python 구현과 DEV-PG 검증만 진행한다. full M3, CAL, SEALED, 실제 데이터, 모바일 UI, main 병합은 계속 차단한다.
