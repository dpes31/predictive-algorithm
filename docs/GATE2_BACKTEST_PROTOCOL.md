# Gate 2 Walk-forward Backtest Protocol v1.0.0

상태: **REVIEW CANDIDATE / Gate 2-1**  
목적: 과거 데이터를 이용한 모델 검증이 미래 데이터 누출·기간선택·지표선택·하이퍼파라미터 과적합으로 변질되지 않도록 평가 절차를 고정한다.

---

## 1. 검증의 기본 원칙

회차 t 예측은 반드시 1회부터 t-1회까지만 사용한다.

```text
1~299회 → 300회 예측
1~300회 → 301회 예측
...
1~1229회 → 1230회 예측
```

첫 외부 평가 회차는 300회로 고정한다.

이유:

- 최대 208회 구조변화 window 확보
- 최소한의 장기 수축 통계 확보
- 초기구간 불안정성 완화

---

## 2. 역사적 데이터의 지위

현재 1~1230회 데이터는 이미 여러 형태로 관찰·분석되었으므로 완전히 untouched한 holdout으로 간주하지 않는다.

따라서 역사적 백테스트의 역할은 다음으로 제한한다.

- 구현 오류 탐지
- 기준모형 대비 탐색적 성능 평가
- 합성데이터와 실제데이터 동작 비교
- `CANDIDATE` 상태 판단

최종 `PROMOTED` 판정은 사전등록 이후의 미래 회차가 필요하다.

---

## 3. 사전지정 평가구간

전체 외부 Walk-forward:

```text
300회 ~ 1230회
```

시간 안정성 확인을 위한 사전지정 블록:

```text
Block A: 300 ~ 609
Block B: 610 ~ 919
Block C: 920 ~ 1230
```

세 블록은 비슷한 길이로 고정한다. 결과를 본 뒤 경계를 변경하지 않는다.

판정:

- 전체구간 개선
- 최소 2개 블록에서 같은 방향
- 특정 1개 블록에 성능이 집중되지 않음

---

## 4. 비교 기준모형

### B0 — 균등 조합분포

```text
P(S) = 1 / C(45,6)
```

가장 중요한 기준이다.

### B1 — 누적 고빈도

예측시점까지 누적 출현률 상위 번호 중심.

### B2 — 최근 52회 고빈도

최근 52회 출현률 상위 번호 중심.

### B3 — 최근 52회 저빈도

최근 52회 출현률 하위 번호 중심.

### B4 — Gap 중심

미출현 간격 상위 번호 중심.

### B5 — 직전 회차 재사용

직전 당첨번호 6개를 핵심 후보로 사용.

### B6 — 균형형 휴리스틱

홀짝·저고·합계를 과거 중앙구간에 맞추는 규칙 기반 조합.

모든 기준모형은 동일한 5세트 출력 형식과 결정론적 seed를 사용한다.

---

## 5. 확률예측 핵심지표

### 5.1 Joint Log Loss

실제 당첨조합 `Y_t`에 대한 손실:

```text
LL_t = -log P_t(Y_t)
```

기준 대비 개선:

```text
ΔLL_t = LL_M0,t - LL_model,t
```

양수이면 모델이 M0보다 우수하다.

가장 중요한 1차 지표다.

### 5.2 Number-level Brier Score

번호별 주변예측확률 `p_i,t`:

```text
BS_t = (1/45) Σ_i (p_i,t - y_i,t)^2
```

기준 대비 개선:

```text
ΔBS_t = BS_M0,t - BS_model,t
```

양수이면 모델이 우수하다.

### 5.3 Calibration

전체 `(i,t)` 예측을 사전고정 bin으로 나눈다.

```text
bins = [0, .05, .10, .125, .14, .16, .20, .30, 1]
```

보고:

- Expected Calibration Error
- calibration intercept
- calibration slope
- 예측확률 범위

모델이 log score를 개선하더라도 calibration이 명확히 악화되면 승격하지 않는다.

---

## 6. 후보 5세트 결과지표

각 후보 세트 k와 실제 조합의 일치 수:

```text
hit_k,t = |S_k,t ∩ Y_t|
```

회차별 지표:

```text
max_hit_t = max_k hit_k,t
mean_hit_t = mean_k hit_k,t
```

누적 보고:

- 평균 `max_hit`
- 평균 `mean_hit`
- 3개 이상 일치 회차 비율
- 4개 이상 일치 회차 비율
- 5개 이상 일치 회차 비율
- 6개 적중 횟수
- 후보 5세트의 평균 중복수
- 후보 5세트의 번호 union 크기

정확히 6개 적중은 희귀하므로 단독 승격지표로 사용하지 않는다.

---

## 7. 균등 5세트 포트폴리오 비교

한 번 생성한 무작위 5세트와 비교하면 분산이 크다.

따라서 각 회차에 대해 균등분포 기반 5세트 포트폴리오를 사전고정 seed로 최소 10,000회 시뮬레이션한다.

비교:

- 모델 `max_hit`의 균등 percentile
- 모델 `mean_hit`의 균등 percentile
- 3개 이상 일치 확률의 균등 기대범위
- 후보 union과 overlap의 균등범위

동일 회차에서 모델과 기준은 common random numbers를 사용한다.

---

## 8. 합성데이터 Negative Control

완전 균등 6/45 데이터를 최소 1,000개 시계열로 생성한다.

각 시계열 길이:

```text
1230 draws
```

검증 항목:

- M1~M3가 지속적으로 M0보다 우수하다고 오판하지 않는지
- gate `CANDIDATE` 오탐률
- sub-expert weight 폭주
- calibration
- pair diagnostic 오탐

통과 기준:

```text
CANDIDATE false activation rate ≤ 0.1%
```

---

## 9. 합성데이터 Positive Control

다음 planted signal을 각각 생성한다.

### P1 — 고정 번호편향

일부 번호의 가중치를 약하게 증가.

```text
relative weight lift = {1.02, 1.05, 1.10}
```

### P2 — 지속 신호

특정 구간 동안 최근 편차가 유지되도록 생성.

### P3 — 평균회귀 신호

과도한 최근 편차가 다음 구간에서 반대방향으로 약화되도록 생성.

### P4 — 구조변화

특정 회차 이후 번호가중치 변경.

```text
change points = {400, 800}
```

### P5 — 일시적 변화

52회 동안만 편향 후 균등으로 복귀.

### P6 — Pair interaction

특정 번호쌍의 동시출현 가중치 증가.

검증:

- 올바른 모형이 상대적으로 높은 weight를 얻는지
- 탐지 지연시간
- 신호 종료 후 M0 복귀시간
- false sign rate
- 최소 탐지가능 효과크기

---

## 10. 통계적 비교

### 10.1 Paired Moving-block Bootstrap

대상:

```text
ΔLL_t
ΔBS_t
```

고정 block length:

```text
52 draws
```

반복:

```text
20,000 bootstrap samples
```

보고:

- 평균 개선
- 95%, 99.9% 구간
- `P(Δ > 0)`

### 10.2 One-sided Block Permutation

귀무가설:

```text
모델과 M0의 사전예측 손실 차이 평균 ≤ 0
```

block length 52를 유지한 부호·블록 순열검정을 사용한다.

### 10.3 다중검정

사전지정 비교:

- M1 vs M0
- M2 vs M0
- M3 vs M0
- shadow ensemble vs M0

Holm-Bonferroni로 familywise error를 보정한다.

승격 기준:

```text
adjusted one-sided p ≤ 0.001
```

---

## 11. Gate 상태 판정

### CLOSED

기본 상태. 최종 결과는 M0.

### RESEARCH

M1~M3 shadow 평가 진행.

### CANDIDATE

다음 조건을 모두 충족:

1. 전체구간 평균 `ΔLL > 0`
2. Bayesian bootstrap `P(ΔLL > 0) ≥ 0.999`
3. Holm-adjusted p ≤ 0.001
4. Brier score 악화 없음
5. Block A/B/C 중 최소 2개에서 `ΔLL > 0`
6. Negative-control false activation ≤ 0.1%
7. 특정 1개 sub-expert에 성과 80% 이상 집중되지 않음

역사적 데이터만으로는 `PROMOTED`가 될 수 없다.

### PROMOTED

다음 조건을 모두 충족:

1. 공식 검증 데이터
2. 최소 52회 prospective 예측
3. 사전등록된 모델 변경 없음
4. anytime-valid e-value ≥ 1000
5. calibration 악화 없음
6. 데이터·코드·예측 잠금 감사 통과

---

## 12. 중단 및 하향 규칙

다음 중 하나면 gate를 한 단계 하향한다.

- 최근 52회 평균 `ΔLL < 0`
- calibration slope가 사전허용범위 `[0.8, 1.2]`를 벗어남
- 데이터 누출 발견
- 재현성 해시 불일치
- 공식 데이터 정정으로 결과 변경
- null simulation 오탐률 기준 초과

데이터 누출 또는 예측 사후수정이 발견되면 해당 모델 버전은 폐기하고 전체 결과에 표시한다.

---

## 13. 결과보고 계약

`reports/gate2_backtest_summary.json`:

```json
{
  "model_version": "2.0.0-research",
  "data_version": "draws-2026.06.27-r1",
  "evaluation_draws": [300, 1230],
  "gate_state": "RESEARCH",
  "joint_log_loss": {},
  "brier_score": {},
  "calibration": {},
  "candidate_metrics": {},
  "block_results": {},
  "multiple_testing": {},
  "null_control": {},
  "positive_controls": {},
  "advantage_status": "통계적 우위 없음",
  "report_hash": "sha256"
}
```

비개발자용 Markdown 보고서는 다음을 먼저 보여준다.

1. 균등모형 대비 우위 있음/없음
2. 데이터 구간
3. 1차 지표 결과
4. 과적합·누출 검사
5. Gate 상태
6. 다음 결정

---

## 14. 금지되는 보고방식

- 가장 잘 맞은 회차만 제시
- 4개·5개 일치 1회로 검증 주장
- 실패 모델 삭제
- 역사적 구간을 결과 후 재분할
- 유리한 지표만 선택
- 보정 전 p-value 제시
- `CANDIDATE`를 검증 완료로 표현
- `통계적 우위 없음`을 숨김
