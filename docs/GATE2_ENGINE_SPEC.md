# Gate 2 Predictive Engine Specification v1.0.0

상태: **REVIEW CANDIDATE / Gate 2-1**  
기준 알고리즘: `docs/ALGORITHM_SPEC.md` v1.0.0  
적용 데이터: 1~1230회 `auto_checked` 연구용 데이터  
금지 범위: 실제 미래예측 공개, 공식 데이터 잠금, Supabase 이전

---

## 1. 목적

Gate 2 엔진은 회차 `t` 직전까지의 데이터만 이용해 다음 회차의 조합확률을 계산하고, 6개 번호 조합 5세트를 생성하며, 같은 절차를 과거 회차에 반복 적용해 균등 무작위 기준보다 재현 가능한 우위가 있는지 검증한다.

이 엔진은 단순 출현빈도 추천기가 아니다. 다음 네 모형을 동시에 운영한다.

- M0: 균등 무작위
- M1: 지속
- M2: 반전·평균회귀
- M3: 구조변화

비균등 신호가 확인되지 않으면 M0으로 복귀한다.

---

## 2. 데이터 사용정책

### 연구용 허용

- 1~1230회 `auto_checked` 데이터로 피처 계산
- 합성데이터 검증
- 과거 Walk-forward 백테스트
- 연구용 후보 5세트 생성

### 금지

- `auto_checked` 데이터를 공식 확정 데이터로 표현
- 공식 검증 전 실제 미래예측을 공개·잠금
- 1231회 이후 결과를 1231회 예측에 사용
- 전체 데이터를 본 뒤 과거 시점의 하이퍼파라미터를 소급 변경

---

## 3. 기본 정의

- 번호 집합: `N = {1, ..., 45}`
- 회차 t의 실제 당첨조합: `Y_t`, `|Y_t| = 6`
- 예측 시점 정보: `D_{t-1}`
- 특정 번호의 포함 여부:

```text
y_i,t = 1  if i ∈ Y_t
        = 0  otherwise
```

- 균등 번호 주변확률:

```text
p0 = 6 / 45
```

- 균등 조합확률:

```text
P0(S) = 1 / C(45,6)
```

보너스번호는 저장·표시하지만 Gate 2 v1의 학습목표와 평가대상에서 제외한다.

---

## 4. 조합확률 표현

번호별 양의 가중치:

```text
q_i,t,r = exp(η_i,t,r)
```

상태·모형 r에서 6개 조합 S의 확률:

```text
P_r,t(S)
= ∏_(i∈S) q_i,t,r / e_6(q_1,t,r, ..., q_45,t,r)
```

`e_6`는 45개 가중치의 6차 elementary symmetric polynomial이다.

이 표현의 장점:

- 정확히 6개가 선택되는 구조를 보존
- 8,145,060개 조합의 확률합이 정확히 1
- 번호별 점수를 조합확률로 변환 가능
- pair interaction이 0인 v1에서 동적계획법으로 정규화 가능

### Pair interaction

기준 수식의 `γ_i,j,t,r` 항은 제거하지 않는다. 다만 Gate 2 최초 구현에서는 다음 이유로 0에 고정한다.

- 990개 번호쌍 대비 표본 부족
- 다중검정과 과적합 위험
- pair 항이 포함된 정확 정규화 비용 증가

활성화 조건:

1. 합성 positive-control에서 탐지 성능 확인
2. FDR 보정 통과
3. 독립 구간 재현
4. 사용자 승인과 모델 MINOR 버전 증가

---

## 5. M0 — 균등 무작위모형

```text
η_i,t,0 = 0
q_i,t,0 = 1
P_0,t(S) = 1 / C(45,6)
```

역할:

- 기준확률
- 무신호 상태의 최종 출력
- 비균등모형 과적합 방지
- 모든 성능 비교의 기준

M0는 어떤 경우에도 삭제하지 않는다.

---

## 6. M1 — 지속모형

목적: 최근 또는 장기 편차가 다음 회차에도 같은 방향으로 이어지는 가설을 평가한다.

M1은 단일 고정계수 모델이 아니라 사전 고정된 sub-expert의 혼합이다.

```text
E1,10  : +z_recent_10
E1,30  : +z_recent_30
E1,52  : +z_recent_52
E1,104 : +z_recent_104
E1,long: +z_long
E1,trend-short: +z_trend_10_52
E1,trend-mid  : +z_trend_30_104
```

각 sub-expert의 조합분포를 계산하고, M1 내부 가중치는 과거 사전예측 log score로만 순차 갱신한다.

```text
P_M1,t = Σ_m a_m,t · P_E1,m,t
Σ_m a_m,t = 1
```

고빈도 번호가 미래에도 유리하다고 가정하지 않는다. M1은 경쟁 가설 중 하나일 뿐이다.

---

## 7. M2 — 반전·평균회귀모형

목적: 최근 편차가 약화되거나 반대 방향으로 전환되는 가설을 평가한다.

```text
E2,10  : -z_recent_10
E2,30  : -z_recent_30
E2,52  : -z_recent_52
E2,104 : -z_recent_104
E2,trend-short: -z_trend_10_52
E2,trend-mid  : -z_trend_30_104
E2,gap: +z_gap
```

`z_gap`은 장기 미출현 번호가 반드시 출현한다는 의미가 아니다. 균등 시행에서는 예측력이 없어야 하며, 실제 사전예측 성능이 없으면 M2 가중치가 감소한다.

```text
P_M2,t = Σ_m b_m,t · P_E2,m,t
Σ_m b_m,t = 1
```

---

## 8. M3 — 구조변화모형

목적: 최근 데이터 생성구조가 장기 상태와 달라졌다는 가설을 평가한다.

초기 sub-expert:

```text
E3,shift-52  : z_shift_52_vs_previous_52
E3,shift-104 : z_shift_104_vs_previous_104
E3,ewma      : z_ewma_minus_long
E3,cusum     : signed_cusum_score
```

M3은 변화가 있다고 단정하지 않는다. global change gate가 약하면 M3 분포는 M0 쪽으로 수축한다.

```text
η_i,t,M3 = g_change,t · η_raw_i,t,M3
0 ≤ g_change,t ≤ 1
```

---

## 9. Sub-expert 가중치 갱신

각 sub-expert는 회차 t-1에 실제 결과 `Y_{t-1}`에 부여했던 joint probability로 평가한다.

```text
loss_m,t-1 = -log P_m,t-1(Y_t-1)
```

지수가중 갱신:

```text
raw_a_m,t = a_m,t-1^δ · exp[-λ · clipped(loss_m,t-1 - loss_M0,t-1)]
a_m,t = raw_a_m,t / Σ_j raw_a_j,t
```

초기 고정값:

```text
δ = 0.995
λ = 0.10
loss difference clipping = [-5, +5]
minimum sub-expert weight before normalization = 0.01
```

목적:

- 한 회차의 우연한 적중으로 가중치 폭증 방지
- 최근 성능을 반영하되 장기 안정성 유지
- 동일 입력에서 결정론적 재현

상수 변경은 하이퍼파라미터 변경이므로 모델 MINOR 버전과 사용자 승인이 필요하다.

---

## 10. Top-level M0~M3 가중치

Shadow ensemble 가중치:

```text
u_r,t ∝ u_r,t-1^δ · exp[-λ · clipped(loss_r,t-1 - loss_M0,t-1)]
Σ_r u_r,t = 1
```

최종 사용 가중치는 무작위성 게이트 상태에 따라 결정한다.

### Gate CLOSED

```text
w_0,t = 1
w_1,t = w_2,t = w_3,t = 0
```

후보 5세트는 균등분포에서 결정론적으로 생성하며 `통계적 우위 없음`으로 표시한다.

### Gate RESEARCH

- M1~M3는 shadow prediction과 백테스트에만 사용
- 사용자 공개 확률에는 영향 없음

### Gate CANDIDATE

역사적 백테스트에서 승격기준을 충족했으나 미래 검증 전인 상태.

```text
w_0,t ≥ 0.70
Σ_(r=1..3) w_r,t ≤ 0.30
```

연구보고서에서만 비균등 혼합 결과를 표시한다.

### Gate PROMOTED

사전등록된 미래 검증까지 통과한 상태.

```text
w_0,t ≥ 0.25
```

공식 검증 데이터가 잠긴 경우에만 실제 예측 공개에 사용할 수 있다.

---

## 11. 무작위성 게이트

게이트는 번호별 단일 p-value가 아니라 다음 증거를 통합한다.

1. Joint log score 개선
2. Number-level Brier score 개선
3. Calibration 비열화 여부
4. 2개 이상 시간구간에서 방향 재현
5. 다중검정 보정
6. 합성 null에서 오탐률
7. 합성 planted-bias에서 탐지력

상태 전환:

```text
CLOSED → RESEARCH
```

- 엔진 구현 및 shadow 평가 시작 시 기본상태

```text
RESEARCH → CANDIDATE
```

- Bayesian bootstrap P(Δ log score > 0) ≥ 0.999
- Holm 보정 one-sided p ≤ 0.001
- Brier score 악화 없음
- 사전지정 역사구간 2개에서 같은 방향
- null simulation false activation ≤ 0.1%

```text
CANDIDATE → PROMOTED
```

- 최소 52회 prospective prediction
- anytime-valid e-value ≥ 1000
- calibration 악화 없음
- 공식 검증 데이터 사용

조건 미충족 또는 성능 악화 시 이전 상태로 하향한다.

---

## 12. 최종 혼합분포

```text
P_t(S)
= w_0,t P_0,t(S)
+ w_1,t P_M1,t(S)
+ w_2,t P_M2,t(S)
+ w_3,t P_M3,t(S)
```

제약:

```text
w_r,t ≥ 0
Σ_r w_r,t = 1
```

모든 구성분포와 최종 혼합분포는 전체 조합에 대해 합이 1이어야 한다.

---

## 13. 후보 5세트 선택

정확히 6개 적중 사건에서 서로 다른 조합은 상호배타적이므로 5세트의 1등 확률은 다음 합이다.

```text
P(any exact hit) = Σ_(k=1..5) P_t(S_k)
```

### 1차 목표

서로 다른 조합 중 `P_t(S)`가 높은 상위 후보를 확보한다.

### 2차 목표

5번째 조합 확률의 99% 이상인 near-tie 후보군 안에서 다음을 최적화한다.

```text
1. 최대 일치번호 성과의 시뮬레이션 기대값
2. 후보 간 과도한 번호 중복 최소화
3. 전체 번호 커버리지
4. 군중 회피 보조점수
```

군중 회피는 2차 목적함수 기여도의 5%를 초과할 수 없다.

M0에서 모든 조합확률이 같으므로 결정론적 seed를 이용해 다양성이 높은 5세트를 선택한다.

---

## 14. 재현성

실행 seed:

```text
seed = SHA256(
  data_version
  + model_version
  + target_draw_no
  + engine_config_hash
)
```

동일한 입력·버전·설정에서는 다음이 같아야 한다.

- 피처 스냅샷
- 모형 가중치
- 조합확률 순위
- 후보 5세트
- 보고서 해시

---

## 15. 입력 계약

```json
{
  "target_draw_no": 1231,
  "data_version": "draws-2026.06.27-r1",
  "model_version": "2.0.0-research",
  "records": "data/draws.json",
  "data_usage": "research_backtest_only",
  "last_available_draw": 1230
}
```

검증:

- `last_available_draw < target_draw_no`
- 사용 레코드에 target 이후 회차 없음
- 데이터 해시 기록
- 보너스번호 학습 제외

---

## 16. 출력 계약

```json
{
  "target_draw_no": 1231,
  "model_version": "2.0.0-research",
  "data_version": "draws-2026.06.27-r1",
  "gate_state": "CLOSED",
  "advantage_status": "통계적 우위 없음",
  "model_weights": {
    "M0": 1.0,
    "M1": 0.0,
    "M2": 0.0,
    "M3": 0.0
  },
  "shadow_weights": {
    "M0": 0.0,
    "M1": 0.0,
    "M2": 0.0,
    "M3": 0.0
  },
  "candidate_sets": [
    {
      "rank": 1,
      "numbers": [1, 2, 3, 4, 5, 6],
      "joint_probability": 0.0,
      "lift_vs_uniform": 1.0,
      "credible_interval_95": [0.0, 0.0]
    }
  ],
  "generated_at": "ISO-8601",
  "input_last_draw": 1230,
  "seed": "sha256",
  "prediction_hash": "sha256",
  "public_release_allowed": false
}
```

예시 숫자는 스키마 설명용이며 실제 후보가 아니다.

---

## 17. 구현 불변조건

1. 미래 데이터 누출 없음
2. M0 제거 금지
3. M1~M3 shadow 평가 항상 수행
4. gate가 CLOSED면 최종 공개분포는 M0
5. 확률합 1
6. 동일 입력 재현
7. 후보 5세트 서로 다름
8. pair 항 기본 0
9. 군중 회피 영향 5% 이하
10. `auto_checked` 데이터 결과는 연구용으로만 표시
