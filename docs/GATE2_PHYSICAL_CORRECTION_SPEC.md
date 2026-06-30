# Gate 2-3P-R Correction Architecture Specification

상태: 사용자 검토용 고정 명세  
작성일: 2026-07-01  
기준 브랜치: `feature/gate2p3-validation`  
작업 브랜치: `feature/gate2p3-correction-spec`  
제안 모델 버전: `4.0.0-research`  
제안 Feature contract: `3.0.0`  
Physical metadata schema: `1.0.0` 유지

## 1. 목적

Gate 2-3P-3에서 확인된 다음 실패를 구조적으로 보정한다.

1. 무관한 메타데이터에도 M4가 비균등분포를 생성하고 활성화한 문제
2. 볼 세트·상호작용처럼 표본이 분산되는 신호가 과도하게 희석된 문제
3. 안정적 조건과 일시적 조건을 같은 메모리 구조로 처리한 문제
4. 신호 종료 후 M0 복귀가 느린 문제
5. 일부 사후시점 오류가 있어도 M4가 계속 작동한 문제
6. M3 maxT가 오탐 제어와 구조변화 탐지력을 동시에 확보하지 못한 문제

이번 보정은 검증기준을 낮추지 않는다. 실패 시나리오·효과크기·M0 안전정책·6개 번호 × 5세트 출력도 유지한다.

## 2. 버전 정책

`3.0.0-research`는 실패 버전으로 동결한다.

이번 변경은 다음 이유로 breaking architecture change다.

- M4 단일 평균결합을 field별 evidence-gated 구조로 교체
- M4 내부를 stable / transient sub-expert로 분리
- M3 maxT를 anytime-valid e-process change detector로 교체
- 전체 metadata global veto 추가
- calibration·sealed validation 분리

따라서 제안 버전은 다음과 같다.

```text
model_version = 4.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

## 3. 변경되지 않는 상위 구조

- M0: 균등 무작위 기준
- M1: 과거 번호 지속
- M2: 반전·평균회귀
- M3: 구조변화
- M4: 물리·운영 증거
- 정확히 6개 번호를 선택하는 fixed-size product distribution
- 다음 회차 후보 5세트 출력
- Pair interaction 예측 비활성
- RESEARCH 상태 최종분포 M0=100%
- CANDIDATE 상태 전체 비균등 비중 최대 30%
- M4 초기 deployable 비중 최대 10%
- `통계적 우위 없음` 표시
- 미래 데이터 누출 금지

## 4. 실패 원인과 직접 보정 매핑

| Gate 2-3P-3 실패 | 4.0 보정 |
|---|---|
| 무관변수 활성 0.120048% | field별 e-process + global abstention |
| 볼 세트 strict detection 0.8% | hierarchical partial pooling |
| machine × ball 0.8% | interaction 전용 계층과 최소지원 계약 |
| temporary environment 0% | transient expert와 restart mixture |
| M0 복귀 65.8% | expiry·restart·hard return 계약 |
| post-draw-error 활성 2.6% | metadata global veto |
| M3 오탐 0.16%, 탐지 0.2% | anytime-valid change e-process |

## 5. M4 전체 구조

M4는 더 이상 모든 field logits를 동일 평균으로 합치지 않는다.

```text
M4
├── M4-S: stable physical context
└── M4-T: transient operational context
```

상위 인터페이스에서는 계속 `M4` 하나로 보이지만 내부적으로 두 family의 증거를 독립 계산한다.

### 5.1 Stable family

- machine.machine_id
- machine.machine_generation
- ball_set.ball_set_id
- ball_set.ball_generation
- regime.machine_regime_id
- regime.ball_regime_id
- interaction.machine_ball_set_id

특성:

- 동일 regime 안에서 장기 누적
- regime 교체 시 이전 세부효과를 직접 상속하지 않음
- 상위 field 효과를 통해서만 부분적으로 상속
- 일반적인 지수감쇠를 사용하지 않음

### 5.2 Transient family

- environment.temperature_band
- environment.humidity_band
- environment.air_pressure_band
- pre_draw_tests.condition_id
- mixing_duration_band
- 기타 사전등록된 단기 운영조건

특성:

- restart mixture 사용
- 유효 시작점 후보: 최근 13·26·52·104회
- 오래된 증거가 자동으로 지배하지 못함
- 104회 동안 신규 증거가 없으면 family evidence를 1로 복귀

## 6. Field별 prequential evidence e-process

각 field `j`는 다른 field와 독립적으로 번호분포 `Q[j,t]`를 만든다.

예측 대상 회차 결과 `S_t`가 공개되기 전에 `Q[j,t]`를 고정한다.

Field별 1-step likelihood ratio:

```text
LR[j,t] = Q[j,t](S_t) / P0(S_t)
```

누적 stable e-process:

```text
E_stable[j,t] = product(s <= t) LR[j,s]
```

Transient e-process는 사전등록 restart 시점별 process의 균등 mixture다.

```text
E_transient[j,t] = mean(r in restart_set) product(s=r..t) LR[j,s]
```

조건:

- 모든 `Q[j,t]`는 과거 데이터만 사용
- 결과 공개 후 field 선택 금지
- LR clipping 금지
- underflow 방지를 위한 log-domain 계산만 허용
- 결측 또는 품질 미달 회차는 `LR=1`

## 7. Null-calibrated abstention

M4는 기본적으로 균등분포를 반환한다.

Family evidence:

```text
E_S,t = mean(j in stable_fields) E_stable[j,t]
E_T,t = mean(j in transient_fields) E_transient[j,t]
E_M4,t = 0.5 * E_S,t + 0.5 * E_T,t
```

Activation 기준:

```text
E_M4,t >= 1000
AND 최근 완료 macro block의 M4 Δ Log Loss > 0
AND 최근 완료 macro block의 M4 Δ Brier >= 0
AND metadata global veto = false
```

Activation 전:

```text
P4,t = P0
M4 status = ABSTAIN
```

Activation 후에도 evidence가 약화되면 즉시 abstain한다.

```text
E_M4,t < 100
OR 최근 2개 완료 block 중 하나라도 Δ Log Loss <= 0
→ P4,t = P0
```

`1000`과 `100`은 activation / deactivation hysteresis다. 결과를 본 뒤 변경하지 않는다.

## 8. Field weight

M4가 활성화된 경우에만 field weight를 계산한다.

```text
raw_weight[j,t] = max(0, log(E[j,t]))
```

Family 내부 정규화:

```text
w[j,t] = raw_weight[j,t] / sum_k raw_weight[k,t]
```

추가 제한:

- 단일 field 최대 50%
- interaction field 최대 25%
- transient family 전체 최대 40%
- evidence `E[j,t] <= 1`인 field의 weight는 0
- active field가 없으면 M4 전체 abstain

최종 M4 logits:

```text
eta4[i,t] = center_i(
    family_weight_S * sum(j in S) w[j,t] * eta[j,i,t]
  + family_weight_T * sum(j in T) w[j,t] * eta[j,i,t]
)
```

Family weight는 `log(E_S)`와 `log(E_T)`의 양의 부분을 정규화해 계산한다.

## 9. Hierarchical partial pooling

각 field의 context별 번호효과를 독립 빈도로 계산하지 않는다.

### 9.1 두 단계 수축

번호 균등 기준:

```text
p0 = 6 / 45
```

Field-level 포함확률:

```text
p_field[j,i]
= (k_global * p0 + y_field[j,i]) / (k_global + n_field[j])
```

Context-level 포함확률:

```text
p_context[j,c,i]
= (k_context * p_field[j,i] + y_context[j,c,i])
  / (k_context + n_context[j,c])
```

Context logit:

```text
eta[j,c,i] = center_i(
    clip(logit(p_context[j,c,i]) - logit(p0), -b_j, b_j)
)
```

### 9.2 Hyperparameter 선택

다음 grid만 허용한다.

```text
k_global ∈ {260, 520, 1040}
k_context ∈ {90, 260, 520}
b_j ∈ {0.10, 0.20, 0.35}
```

선택 규칙:

1. 개발용 synthetic seed에서만 선택
2. 목적함수: null false activation 최소화 우선
3. 제약: lift 1.25 방향정확도 80% 이상
4. 동률이면 더 큰 prior와 더 작은 effect clip 선택
5. 선택 결과를 implementation commit hash와 함께 잠금
6. calibration·sealed validation 결과를 본 뒤 재선택 금지

## 10. Interaction context

`machine × ball_set`은 독립 flat context로 학습하지 않는다.

```text
eta_interaction[m,b,i]
= eta_machine[m,i]
+ eta_ball[b,i]
+ delta_interaction[m,b,i]
```

`delta_interaction`은 0을 중심으로 강하게 수축한다.

활성 최소조건:

- 해당 조합 weighted support >= 52
- machine과 ball_set 주효과 모두 prediction-eligible
- interaction field e-value > 1

미충족 시 interaction residual은 0이다.

## 11. Metadata global veto

다음 중 하나라도 발견되면 해당 회차 M4 전체를 균등분포로 강제한다.

- supplied field의 `observed_at > draw_datetime`
- `available_before_draw=true`인데 timestamp 없음
- 현재 회차 winning numbers·ordered numbers·bonus 포함
- schema version 불일치
- verified인데 source traceability 없음
- required field에 모순된 복수 값 존재
- target draw 이후 metadata 포함

Global veto 결과:

```text
P4,t = P0
M4 status = INVALID_METADATA
M4 field weights = all zero
```

Optional field의 단순 결측·unknown은 global veto가 아니라 해당 field만 제외한다.

## 12. Stable / transient expiry와 M0 복귀

### Stable

- regime ID 변경 시 context residual 초기화
- field-level parent effect만 유지
- 새 context support 20 미만이면 해당 context distribution은 field-level parent로만 구성

### Transient

- restart mixture의 가장 최근 13·26·52·104회만 유지
- 104회 동안 `E_T < 1`이면 transient family weight 0
- 신호 종료 후 208회 이내 `P4=P0` 복귀율 80% 이상 요구

### Global hard return

다음 조건이면 M4는 최소 52회 동안 강제 abstain한다.

```text
최근 완료 block Δ Log Loss <= 0
AND 최근 완료 block Δ Brier < 0
```

강제 abstain 중에도 shadow evaluation은 계속하지만 deployable M4 weight는 0이다.

## 13. M3 재설계

기존 maxT p-value detector를 폐기하고 anytime-valid mixture e-process로 교체한다.

### 13.1 입력

각 번호 `i`의 포함지표:

```text
X[i,t] ∈ {0,1}
p0 = 6/45
```

Betting fraction grid:

```text
lambda ∈ {-0.20, -0.10, -0.05, -0.02, 0.02, 0.05, 0.10, 0.20}
```

번호·방향·restart별 process:

```text
E[i,lambda,r,t]
= product(s=r..t) (1 + lambda * (X[i,s] - p0))
```

모든 factor는 음수가 되지 않는 grid만 사용한다.

### 13.2 Global mixture

Restart 후보는 13회 간격으로 생성하고 최근 104개 restart만 유지한다.

```text
E_M3,t = mean(i, lambda, r) E[i,lambda,r,t]
```

Mixture e-process이므로 별도 Holm 보정을 적용하지 않는다.

Activation:

```text
E_M3,t >= 1000
```

Deactivation:

```text
E_M3,t < 100
OR trigger 후 208회 경과
```

### 13.3 Detection과 prediction 분리

- `E_M3`는 change 존재 여부만 결정
- 번호 방향은 trigger 이후의 post-change M3 prediction expert가 계산
- detector 결과를 직접 logits로 사용하지 않음
- trigger 전 M3 distribution은 P0
- trigger 후에도 post-change support 20 미만이면 P0

## 14. M3 post-change prediction

Trigger 시점 `tau` 이후 번호별 포함률을 균등 prior에 수축한다.

```text
p_post[i,t]
= (k_m3 * p0 + y_post[i,t]) / (k_m3 + n_post)
```

```text
k_m3 ∈ {90, 260, 520}
```

선택은 개발용 seed에서만 수행하고 sealed validation 전 잠근다.

Post-change logits:

```text
eta3[i,t] = center_i(
    clip(logit(p_post[i,t]) - logit(p0), -0.20, 0.20)
)
```

M3 trigger 종료 또는 208회 경과 시 P0로 복귀한다.

## 15. M0~M4 최종 결합

RESEARCH:

```text
w0 = 1.0
w1 = w2 = w3 = w4 = 0
```

CANDIDATE 이후에만 shadow evidence를 deployable weight 후보로 변환한다.

고정 상한:

- M0 최소 70%
- M3 최대 10%
- M4 최대 10%
- M1+M2+M3+M4 합계 최대 30%

M3 또는 M4가 abstain이면 해당 weight는 0이고 잔여질량은 M0로 이동한다.

## 16. 개발·검증 데이터 분리

### Development seeds

- hyperparameter grid 선택
- 코드 디버깅
- smoke
- PASS/FAIL 판정에 사용 금지

### Calibration seeds

- field e-process null behavior 확인
- M3 implementation sanity calibration
- final threshold 변경에 사용 금지
- threshold는 이 명세의 1000/100을 유지

### Sealed validation seeds

- 최종 PASS/NOT PASSED에만 사용
- 첫 실행 전 seed manifest hash를 저장
- 실행 후 코드·config 수정 금지
- 실패 seed 제외 금지

## 17. 제품 출력 유지

최종 사용자 결과 형식은 변경하지 않는다.

```text
다음 회차 예측
1세트: 6개 번호
2세트: 6개 번호
3세트: 6개 번호
4세트: 6개 번호
5세트: 6개 번호
```

추가 연구정보:

- M0~M4 shadow weights
- M3 e-value와 상태
- M4 stable/transient e-value
- active field와 field weight
- metadata quality·global veto
- data cutoff·seed·prediction hash
- `통계적 우위 없음`

## 18. 구현 금지사항

- e-value threshold 완화
- failed scenario 삭제
- lift 1.25 기준 삭제
- 결과를 본 뒤 field 분류 변경
- calibration seed를 development에 재사용
- sealed validation 재실행 후 최선 seed 선택
- M4 10% cap 완화
- Pair interaction 번호쌍 모델 활성화
- 실제 과거번호 Walk-forward 선행
- 실제 미래후보 공개

## 19. 다음 단계

이 명세 승인 후에만 다음을 진행한다.

1. Gate 2-3P-R2: Python 구현
2. Gate 2-3P-R3: unit·smoke·development synthetic 검수
3. Gate 2-3P-R4: sealed full synthetic validation
4. 통과 시 Gate P-1 실제 메타데이터 100회 feasibility pilot
5. 실패 시 동일 synthetic 시나리오 기반 추가 파라미터 조정 중단

## 20. 중단 원칙

`4.0.0-research`가 sealed validation에 실패하면 다음을 적용한다.

- 동일 데이터·동일 시나리오에서 5번째 구조수정 금지
- 새로운 외부 물리정보나 새로운 측정가능 데이터가 확보되기 전 비균등 로또 예측연구 중단
- M0 기반 5세트 생성기는 연구·기록 목적으로만 유지
- 일반 의사결정 엔진으로의 확장은 별도 실제 라벨 데이터 프로젝트에서 재정의
