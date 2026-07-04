# Gate 2-3P-R3M-3 Specification Decision Record

## D-031 — Oracle PASS 승인

사용자는 Gate 2-3P-R3M-2의 Oracle DEV PASS와 구현·결과 잠금을 승인했다.

고정 기준:

- model `5.0.0-research`
- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

## D-032 — Predictable-group 학습계약

- outer window: 520
- half-life: 104
- prior strength: 52
- score: shrunken weighted inclusion log-odds minus uniform log-odds
- retraining: fixed 52-draw boundary
- group freeze: following 52 draws
- invalid window: ABSTAIN

## D-033 — Group-size 선택

- candidates: 6, 10, 15
- internal fit prefix: 260
- validation: five chronological 52-draw folds
- eligible if cumulative fold log LR > 0 and at least 3 folds positive
- select maximum cumulative log LR
- tie within `1e-12`: smaller size
- number-score tie within `1e-12`: lower number
- no eligible size: ABSTAIN

## D-034 — DEV 계약

Positive:

- P4 regime reversal
- 2,000 series
- draw count 1,230
- evaluation 625 through 1,144

Null:

- exact uniform 6-of-45
- 10,000 series
- same evaluation interval

Seed namespaces:

- `DEV-PG`
- `DEV-PG-CI`

Existing DEV, CAL, SEALED namespaces are prohibited.

## D-035 — PASS 기준

Positive:

- availability >= 80%
- activation >= 80%
- median delay <= 520
- direction accuracy >= 80%
- direction trials >= 16,000
- mean delta Log Loss > 0
- one-sided 95% lower delta Log Loss > 0
- mean delta Brier >= 0
- one-sided 95% lower delta Brier >= 0

Null:

- false activation <= 0.1%
- exact one-sided 95% upper <= 0.2%

모두 충족해야 `PREDICTABLE_GROUP_PASS`다. 하나라도 실패하면 `PREDICTABLE_GROUP_FAIL`이다.

## D-036 — 현재 차단

현재 상태:

```text
Gate 2-3P-R3M-3-1 = SPEC COMPLETE / APPROVAL PENDING
Gate 2-3P-R3M-3-2 = BLOCKED
Full M3 DEV = BLOCKED
Gate 2-3P-R4 = BLOCKED
Final distribution = M0 only
```

현재 작업에서는 Python 구현, DEV 실행, full M3, CAL, SEALED, 실제 데이터, 모바일 UI, main 병합을 수행하지 않았다.
