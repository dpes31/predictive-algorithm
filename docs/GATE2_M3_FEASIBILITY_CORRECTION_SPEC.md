# Gate 2-3P-R3M M3 Feasibility Correction Specification

상태: 사용자 검토용 신규 교정 명세  
작성일: 2026-07-01  
기준 브랜치: `feature/gate2p-r3-dev-grid`  
작업 브랜치: `feature/gate2p-r3m-feasibility-spec`  
기준 모델: `4.0.0-research`  
제안 모델: `5.0.0-research`  
Feature contract: `3.0.0` 유지  
Physical metadata schema: `1.0.0` 유지

## 1. 목적

Gate 2-3P-R3에서 확인된 `NO_ELIGIBLE_CONFIG`를 파라미터 완화 없이 구조적으로 해결할 수 있는지 명세한다.

유지 조건:

- activation threshold `1000`
- deactivation threshold `100`
- R3 실패 결과와 모든 seed 보존
- lift 1.25 strict detection target `80%`
- false activation target `0.1%`
- one-sided 95% upper bound `0.2%`
- M3 deployable cap `10%`
- RESEARCH final distribution `M0 only`
- 정확히 6개 번호 × 5세트 출력
- 미래 데이터 누출 금지

이번 명세는 Python 구현, 추가 DEV, CAL, SEALED를 포함하지 않는다.

## 2. 수학적 판정

다음 기존 계약은 양립하지 않는다.

```text
threshold 1000
AND evidence life 208 draws
AND lift 1.25
AND detection power 80%
```

P4 lift 1.25 exact 6-of-45 대안에서 oracle KL은 회차당 `0.024294585890841103 nats`다.

```text
208 * KL = 5.053273865294949
log(1000) = 6.907755278982137
```

따라서 favored set과 change point를 정확히 아는 oracle도 208회 기대 evidence가 threshold에 못 미친다. 기존 45 × 8 × restart 균등 mixture는 이보다 더 큰 dilution을 발생시킨다.

상세 계산은 `reports/gate2_3p_r3m_mathematical_feasibility.md`에 고정한다.

## 3. 버전 결정

`4.0.0-research`는 R3 `NO_ELIGIBLE_CONFIG` 상태로 동결한다.

다음 변경은 breaking architecture change다.

- 번호별 독립 betting mixture를 exact fixed-size group LR로 교체
- detector evidence horizon과 post-activation active life 분리
- activation 가능한 primary hypothesis와 diagnostic-only hypothesis 분리
- oracle feasibility gate 선행
- past-only predict-then-bet group construction 추가

따라서 제안 모델 버전은 다음이다.

```text
model_version = 5.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

## 4. 변경되지 않는 상위 구조

- M0: 균등 무작위 기준
- M1: 지속
- M2: 반전·평균회귀
- M3: 구조변화
- M4: 물리·운영 증거
- exact 6-of-45 distribution
- 6개 번호 × 5세트
- Pair-number interaction 예측 비활성
- RESEARCH 상태에서는 최종분포 M0=100%
- 실제 데이터·모바일 개발 차단

M4 구조와 4.0 실패 결과는 이번 명세에서 변경하지 않는다.

## 5. 시간계약 분리

기존 `208`은 detector evidence 누적기간과 활성 후 사용기간을 동시에 의미했다. 이를 분리한다.

### 5.1 Pre-activation evidence horizon

```text
H_detect = 520 draws
```

- threshold 1000을 넘기기 위한 evidence 누적 상한
- 13회 restart grid 기준 40개 interval
- 52회 macro block 기준 10개 block
- P4 post-change 615회 범위 안에서 평가 가능
- activation 전에는 M3 prediction weight 0

### 5.2 Post-activation active life

```text
H_active = 208 draws
```

- activation 이후 M3 prediction을 사용할 수 있는 최대기간
- 208회 경과 시 강제 M0 복귀
- detector evidence history와 deployable predictor life를 혼동하지 않음

### 5.3 Deactivation

다음 중 하나면 즉시 M3 abstain이다.

```text
E_M3 < 100
OR completed-block ΔLogLoss <= 0
OR completed-block ΔBrier < 0
OR active_age >= 208
```

## 6. Exact group likelihood-ratio

번호별 Bernoulli 근사 대신 exact fixed-size distribution을 사용한다.

Favored group `F`, group size `m`, lift `r`에 대해:

```text
Q_F,r(S) = r ^ |S ∩ F| / Z(F, r)
P0(S) = 1 / C(45, 6)
LR_t(F, r) = Q_F,r(S_t) / P0(S_t)
```

정규화 상수:

```text
Z(F, r) = Σ_k C(m,k) C(45-m,6-k) r^k
```

조건:

- `F`와 `r`은 결과 공개 전에 고정
- 현재 회차 결과로 group을 수정하지 않음
- LR clipping 금지
- log-domain 계산
- exact 6-of-45 normalization 필수

## 7. Hypothesis 계층

모든 가설을 동일 평균하지 않는다.

```text
M3 hypotheses
├── Primary activation hypotheses: 최대 4개
└── Diagnostic-only hypotheses: activation 권한 없음
```

### 7.1 Primary hypotheses

Primary는 activation threshold에 참여한다.

최대 4개만 허용하며 각 가설은 사전등록한다.

1. stable favored-group continuation
2. stable favored-group reversal
3. metadata-aligned regime transition
4. past-only learned structural group

초기 wealth:

```text
w_h >= 0.25 for active four-way contract
Σ_h w_h = 1
```

4개보다 많은 가설을 activation mixture에 넣지 않는다. 후보가 부족하면 남는 wealth를 기존 primary에 사전등록 비율로 재배분한다.

### 7.2 Diagnostic-only hypotheses

다음은 탐색·설명 목적으로 계산할 수 있으나 activation에 사용할 수 없다.

- 45개 개별 번호 방향
- 전체 betting-fraction grid
- 결과 후 생성된 그룹
- 낮은 support의 임시 그룹
- 사전등록되지 않은 interaction

Diagnostic 결과를 보고 primary를 교체하면 해당 실험은 무효다.

## 8. Predict-then-bet group construction

실제 구조변화 group을 미리 알 수 없으므로 group learning과 betting을 분리한다.

### 8.1 Training window

각 restart origin `r` 이전의 과거 데이터만 사용한다.

```text
training_end < betting_start
```

허용 group sizes:

```text
m ∈ {6, 10, 15}
```

과거-only score로 상위 `m`개 번호를 선택하고 group을 betting 시작 전에 고정한다.

### 8.2 Evaluation window

고정된 group은 이후 데이터에 대해서만 LR을 누적한다.

```text
E_h,t = Π_{s=betting_start..t} LR_s(F_h, r_h)
```

Evaluation 도중 group 재학습 금지다. 새로운 group은 다음 사전등록 restart에서 별도 process로 시작한다.

### 8.3 Leakage barrier

- target draw 포함 금지
- current result 포함 금지
- change point 사후확정 금지
- sealed seed로 group dictionary 생성 금지
- diagnostic winner를 primary로 승격 금지

## 9. Restart와 wealth allocation

Restart interval은 13회를 유지한다.

모든 restart를 단순 균등 평균하지 않는다.

### 9.1 Alpha-wealth schedule

Restart `j`의 wealth는 사전등록 감쇠 schedule을 사용한다.

```text
v_j ∝ 1 / (j + 1)^2
Σ_j v_j = 1
```

최근 restart에 충분한 wealth를 부여하되 전체 mixture는 e-valid하게 유지한다.

### 9.2 Primary mixture

```text
E_M3,t = Σ_h w_h Σ_j v_j E_h,j,t
```

조건:

- `w_h`, `v_j`는 결과 전 고정
- dynamic winner-take-all 금지
- max e-value를 그대로 activation에 사용 금지
- mixture 전체가 threshold 1000을 넘어야 함

## 10. Oracle feasibility gate

일반 detector 구현 전에 oracle gate를 반드시 통과해야 한다.

### 10.1 Oracle contract

- favored group known
- change point known
- exact LR
- threshold 1000
- H_detect 520
- lift 1.25
- deterministic DEV seeds only

### 10.2 Oracle PASS

```text
activation rate >= 80%
AND median activation delay <= 520
AND null false activation <= 0.1%
AND one-sided 95% upper <= 0.2%
```

Oracle gate 실패 시:

```text
STOP
no group-learning implementation
no full detector grid
no CAL
no SEALED
```

## 11. Predictable-group feasibility gate

Oracle 통과 후 past-only learned group을 평가한다.

PASS 조건:

```text
lift 1.25 activation >= 80%
direction accuracy >= 80%
mean ΔLogLoss > 0
mean ΔBrier >= 0
null false activation criteria PASS
```

Group learning 실패 시 M3는 deployable candidate가 될 수 없다.

## 12. Full M3 DEV gate

Oracle과 predictable-group gate를 통과한 후에만 primary 4-way + restart mixture를 평가한다.

허용 config는 후속 구현 명세에서 별도 고정하며 이번 문서에서는 grid를 만들지 않는다.

선택 우선순위:

1. null false activation 최소
2. lift 1.25 strict detection 80% 이상
3. activation delay 최소
4. ΔLogLoss 최대
5. 더 단순한 hypothesis dictionary

적격 config가 없으면 다시 `NO_ELIGIBLE_CONFIG`다.

## 13. R4 진입조건

Gate 2-3P-R4는 다음이 모두 충족될 때만 별도 승인 가능하다.

- 5.0 Python 구현 완료
- unit tests PASS
- oracle DEV PASS
- predictable-group DEV PASS
- full M3 DEV PASS
- config와 implementation commit hash 잠금
- CAL/SEALED namespace 미사용 확인
- 사용자 별도 승인

현재 R4는 계속 `BLOCKED`다.

## 14. 중단조건

다음 중 하나면 M3 비균등 연구를 중단한다.

1. 520회 oracle gate 실패
2. exact LR에서도 lift 1.25 80% 미달
3. null false activation 기준을 만족시키면 positive power가 붕괴
4. primary hypothesis를 4개 이하로 제한할 수 없음
5. past-only group learning이 방향정확도 80% 미달

중단 시 최종분포는 M0 only이며 M4와 실제 물리데이터 연구는 별도 Gate로만 재개할 수 있다.

## 15. 현재 결정

- R3 `NO_ELIGIBLE_CONFIG` 승인 기록
- R4 차단 유지
- threshold 1000 유지
- 208회는 post-activation active life로 유지
- detector evidence horizon 520 제안
- 제안 모델 `5.0.0-research`
- Python 구현 미승인
- 추가 DEV 미승인
- CAL·SEALED 미승인
- 실제 데이터·모바일 개발 차단
