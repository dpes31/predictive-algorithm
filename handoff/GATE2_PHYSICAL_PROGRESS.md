# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p-r3m2-oracle-engine`  
기준 브랜치: `feature/gate2p-r3m-feasibility-spec`  
관련 이슈: #28  
현재 Draft PR: #29

## 진행률

| 단계 | 상태 | 진척도 |
|---|---|---:|
| Gate 2-3P-R3 | NO_ELIGIBLE_CONFIG | 100% |
| Gate 2-3P-R4 | BLOCKED | 0% |
| Gate 2-3P-R3M-1 | 승인 완료 | 100% |
| Gate 2-3P-R3M-2 | **구현 완료·ORACLE_PASS** | 100% |
| Gate 2-3P-R3M-3 | 별도 승인 전 차단 | 0% |
| full M3 DEV | 차단 | 0% |
| CAL·SEALED | 차단 | 0% |
| 실제 데이터·모바일 | 차단 | 0% |

## Oracle DEV 결과

- model `5.0.0-research`
- detection horizon `520`
- activation threshold `1000`
- active life `208`
- positive series `2000`
- positive activated `1837`
- positive rate `0.9185` — PASS
- median delay `241` — PASS
- null series `10000`
- null activations `8`
- null rate `0.0008` — PASS
- null one-sided upper `0.001443000578280491` — PASS

## 잠금

- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- tests `96 PASS`
- artifact `8000257623`
- artifact digest `sha256:6c52c97fbd167a2f2ae22e4d225510cc419985c19e08f283dcdfbd6eaec2dafe`
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

## 판정

```text
Oracle DEV = PASS
R3M-3 = BLOCKED pending approval
Full M3 DEV = BLOCKED
R4 = BLOCKED
Final distribution = M0 only
```

## 다음 단계

별도 승인 후 Gate 2-3P-R3M-3 feasibility만 진행한다. full M3, CAL, SEALED, 실제 데이터, 모바일 UI, main 병합은 계속 차단한다.
