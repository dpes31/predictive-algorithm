# Gate 2 Feature Contract v1.0.0

상태: **REVIEW CANDIDATE / Gate 2-1**  
목적: 모든 특징량의 의미·계산창·표준화·결측처리·사용모형을 고정하여 미래 데이터 누출과 임의 피처 추가를 방지한다.

---

## 1. 공통 원칙

회차 t를 예측할 때 모든 특징은 `D_{t-1}`만 이용한다.

```text
feature(i, t) = f(draws 1 ... t-1)
```

금지:

- 회차 t 결과 사용
- 전체 데이터 평균·표준편차를 과거 시점에 소급 사용
- 백테스트 결과를 본 뒤 유리한 window 추가
- 번호 순서를 연속적인 수치거리로 해석
- 보너스번호를 본번호 출현과 혼합

번호별 표준화는 예측 시점의 45개 번호 횡단면 또는 이론적 null 분포로만 계산한다.

---

## 2. 기본 상수

```text
p0 = 6 / 45
prior_concentration κ = 90
recent windows W = {10, 30, 52, 104}
change windows = {52 vs previous 52, 104 vs previous 104}
EWMA half-life = 26 draws
winsorization range = [-3, +3]
minimum history for prediction = 299 draws
first outer prediction = draw 300
```

상수 변경은 모델 버전 변경과 사용자 승인이 필요하다.

---

## 3. 장기 수축 출현률

번호 i가 1~t-1회에 포함된 횟수:

```text
c_i,long(t) = Σ_(s=1..t-1) y_i,s
```

Beta prior:

```text
α0 = κ · p0
β0 = κ · (1 - p0)
```

사후평균:

```text
p_i,long(t)
= [α0 + c_i,long(t)] / [α0 + β0 + (t-1)]
```

표준화:

```text
z_i,long(t)
= clip(
    [p_i,long(t) - p0] / sqrt[p0(1-p0)/(κ+t-1)],
    -3,
    +3
  )
```

용도:

- M1 `E1,long`
- 진단용 장기 편향

주의: Beta 근사는 번호별 주변분포 특징을 위한 수축도구이며 최종 조합확률은 아니다.

---

## 4. 최근 출현률

각 window W에 대해:

```text
c_i,W(t) = Σ_(s=t-W..t-1) y_i,s
p_i,W(t) = c_i,W(t) / W
```

이론적 표준화:

```text
z_i,W(t)
= clip(
    [p_i,W(t) - p0] / sqrt[p0(1-p0)/W],
    -3,
    +3
  )
```

생성 피처:

```text
z_recent_10
z_recent_30
z_recent_52
z_recent_104
```

용도:

- 양의 방향: M1
- 음의 방향: M2

---

## 5. 추세 피처

단기와 중기의 차이:

```text
z_trend_10_52(i,t)
= clip([z_i,10(t) - z_i,52(t)] / sqrt(2), -3, +3)
```

중기와 장기의 차이:

```text
z_trend_30_104(i,t)
= clip([z_i,30(t) - z_i,104(t)] / sqrt(2), -3, +3)
```

용도:

- 양의 방향: M1 지속
- 음의 방향: M2 반전

---

## 6. 미출현 간격 피처

회차 t 직전 번호 i의 연속 미출현 회수:

```text
g_i(t) = number of consecutive draws before t with y_i,s = 0
```

균등 독립 주변모형에서 geometric gap의 평균과 표준편차:

```text
μ_gap = (1-p0)/p0
σ_gap = sqrt(1-p0)/p0
```

표준화:

```text
z_gap(i,t) = clip([g_i(t)-μ_gap]/σ_gap, -3, +3)
```

용도:

- M2 gap sub-expert
- 설명용 진단

주의: gap이 길다는 이유만으로 출현확률이 높아진다고 가정하지 않는다. 사전예측 성능이 없으면 가중치는 감소한다.

---

## 7. 구조변화 피처

### 7.1 52회 구간 변화

최근 52회와 그 직전 52회의 출현률 차이:

```text
p_i,recent52(t) = mean(y_i,t-52 ... y_i,t-1)
p_i,prior52(t)  = mean(y_i,t-104 ... y_i,t-53)
```

```text
z_shift_52(i,t)
= clip(
    [p_i,recent52(t)-p_i,prior52(t)]
    / sqrt[2p0(1-p0)/52],
    -3,
    +3
  )
```

### 7.2 104회 구간 변화

```text
z_shift_104(i,t)
= clip(
    [p_i,recent104(t)-p_i,prior104(t)]
    / sqrt[2p0(1-p0)/104],
    -3,
    +3
  )
```

용도:

- M3 shift sub-experts

---

## 8. EWMA 피처

번호별 지수가중 평균:

```text
α_EWMA = 1 - exp[-ln(2)/26]
EWMA_i,t = α_EWMA y_i,t-1 + (1-α_EWMA) EWMA_i,t-1
```

초기값:

```text
EWMA_i,1 = p0
```

장기 사후평균과의 차이:

```text
z_ewma_minus_long(i,t)
= cross_sectional_zscore(EWMA_i,t - p_i,long(t))
```

45개 번호 횡단면 평균과 표준편차로 계산하고 `[-3,+3]`으로 제한한다.

용도:

- M3 EWMA sub-expert

---

## 9. CUSUM 피처

중심화 관측:

```text
x_i,s = y_i,s - p0
```

고정 drift allowance:

```text
k = 0.25 · sqrt[p0(1-p0)]
```

최근 상태:

```text
Cplus_i,t  = max(0, Cplus_i,t-1 + x_i,t-1 - k)
Cminus_i,t = min(0, Cminus_i,t-1 + x_i,t-1 + k)
```

signed score:

```text
cusum_raw_i,t = Cplus_i,t + Cminus_i,t
signed_cusum_score_i,t = cross_sectional_zscore(cusum_raw_i,t)
```

`[-3,+3]`으로 제한한다.

용도:

- M3 CUSUM sub-expert

---

## 10. Global entropy diagnostic

window W의 전체 번호 질량:

```text
r_i,W(t) = c_i,W(t) / (6W)
```

정규화 엔트로피:

```text
H_W(t) = -Σ_i r_i,W(t) log r_i,W(t) / log(45)
```

window:

```text
W ∈ {52, 104}
```

용도:

- 무작위성 gate 진단
- 특정 번호의 직접 추천점수로 사용 금지

판정은 이론값 하나가 아니라 동일 길이 균등 6/45 Monte Carlo null 분포의 percentile로 계산한다.

---

## 11. 회차 간 중복 진단

연속 두 회차의 중복 수:

```text
overlap_t = |Y_t ∩ Y_t-1|
```

lag L 평균 중복:

```text
mean_overlap_L = mean(|Y_s ∩ Y_s-L|)
L ∈ {1,2,...,20}
```

용도:

- 독립성 gate 진단
- 번호 직접점수로 사용 금지

다중 lag의 최대편차는 permutation familywise test로 평가한다.

---

## 12. Pair interaction diagnostic

특정 번호쌍 `(i,j)`의 window W 동시출현 횟수:

```text
c_i,j,W(t) = Σ I(i∈Y_s and j∈Y_s)
```

균등모형에서 특정 쌍의 한 회차 동시포함확률:

```text
p_pair0 = C(43,4) / C(45,6) = 1/66
```

표준화:

```text
z_pair_i,j,W
= [c_i,j,W/W - p_pair0] / sqrt[p_pair0(1-p_pair0)/W]
```

기본 window:

```text
W = 104
```

Gate 2 최초 구현에서는 분석·positive-control 검증만 수행하며 `γ_i,j = 0`으로 유지한다.

---

## 13. Global change gate

M3 수축계수 `g_change,t`는 다음 진단의 사전고정 결합으로 계산한다.

입력:

- max absolute `z_shift_52`
- max absolute `z_shift_104`
- entropy null percentile
- CUSUM aggregate percentile

각 입력을 균등 Monte Carlo null의 tail probability로 변환한다.

```text
evidence_k = max(0, 1 - 2·tail_probability_k)
```

결합:

```text
g_change,t = median(evidence_1, ..., evidence_4)
```

단, 다중검정 보정 후 유의하지 않으면:

```text
g_change,t = 0
```

M3은 이 값만큼 M0에서 멀어질 수 있다.

---

## 14. 결측 및 초기구간 처리

- `t < 300`: 외부 Walk-forward 평가에서 제외
- window 길이가 부족한 특징: 사용하지 않고 해당 sub-expert weight를 0으로 설정
- 번호가 아직 한 번도 나오지 않은 경우 gap은 `t-1`로 계산하되 winsorize
- 횡단면 표준편차가 0이면 해당 z-score 전부 0
- NaN 또는 infinite 발생 시 실행 실패

결측값을 0으로 조용히 대체하지 않는다. 위 규칙에 명시된 경우만 0을 사용한다.

---

## 15. Feature snapshot 출력

각 예측 시점마다 다음을 저장한다.

```json
{
  "target_draw_no": 1231,
  "input_last_draw": 1230,
  "data_version": "draws-2026.06.27-r1",
  "feature_contract_version": "1.0.0",
  "number_features": {
    "1": {
      "z_long": 0.0,
      "z_recent_10": 0.0,
      "z_recent_30": 0.0,
      "z_recent_52": 0.0,
      "z_recent_104": 0.0,
      "z_trend_10_52": 0.0,
      "z_trend_30_104": 0.0,
      "z_gap": 0.0,
      "z_shift_52": 0.0,
      "z_shift_104": 0.0,
      "z_ewma_minus_long": 0.0,
      "signed_cusum_score": 0.0
    }
  },
  "global_features": {
    "entropy_52": 0.0,
    "entropy_104": 0.0,
    "change_gate": 0.0
  },
  "snapshot_hash": "sha256"
}
```

모든 값은 예측 시점 기준으로 저장하여 이후 코드 변경 시 비교 가능하게 한다.

---

## 16. 피처 추가 정책

새 피처는 다음 조건을 모두 충족해야 한다.

1. 물리적·통계적 가설 명시
2. 미래 데이터 없이 계산 가능
3. 균등 null에서 기대 동작 정의
4. planted positive-control 정의
5. 다중검정 포함
6. 기존 피처 대비 중복성 평가
7. 사용자 승인
8. feature contract MINOR 버전 증가

백테스트 성능이 좋아 보인다는 이유만으로 피처를 추가하지 않는다.
