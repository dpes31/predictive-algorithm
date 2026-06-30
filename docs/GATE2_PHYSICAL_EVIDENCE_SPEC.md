# Gate 2-3P-1 Physical Evidence Model Specification

상태: 검토용 고정 명세  
작성일: 2026-06-30  
기준 브랜치: `feature/gate2-synthetic-validation-r1`  
작업 브랜치: `feature/gate2-physical-evidence-spec`  
제안 모델 버전: `3.0.0-research`

## 1. 목적

기존 로또 6/45 예측기의 목적과 출력은 변경하지 않는다.

- 다음 회차 6개 번호 조합 5세트 출력
- 1~45 번호별 상대 포함확률 산출
- 동일 입력·버전에서 동일 결과
- 신호 미확인 시 M0 균등모형 복귀
- 검증 전 `통계적 우위 없음`

이번 확장은 과거 당첨번호만 사용하는 M0~M3에 **추첨 전에 관측 가능한 물리·운영 증거채널 M4**를 추가한다.

## 2. 변경되지 않는 구조

- M0: 균등 무작위
- M1: 번호 이력의 지속
- M2: 반전·평균회귀
- M3: 구조변화
- 정확히 6개를 선택하는 fixed-size product distribution
- 동적 모형 가중치
- 후보 5세트 최적화
- 군중 회피 영향 최대 5%
- Pair interaction 예측 비활성
- 미래 데이터 누출 금지
- 연구용 출력과 공개용 출력 분리

## 3. 신규 M4 정의

M4는 물리·운영 조건이 번호별 상대 포함확률을 반복적으로 변화시키는지 평가한다.

전체 혼합분포:

```text
P_t(S) = sum(r=0..4) w[r,t] * P_r,t(S)
```

M4 조합분포:

```text
P_4,t(S) proportional to exp(sum(i in S) eta_4[i,t])
```

번호별 logit:

```text
eta_4[i,t] = sum(j) reliability[j,t] * beta[j,i,t] * x[j,t]
```

제약:

- `x[j,t]`는 공식 추첨 결과가 공개되기 전에 관측 가능해야 한다.
- `reliability[j,t]`는 0~1이며 결측이면 0이다.
- 번호별 효과 `beta[j,i,t]`는 번호 전체 평균이 0이 되도록 중심화한다.
- 모든 효과에는 강한 0 수축을 적용한다.
- 표본이 부족하면 M4는 균등분포에 수렴한다.
- 장비·볼 교체 후 기존 효과는 자동 감쇠한다.
- 결과를 본 뒤 특정 변수·번호·기간을 선택하지 않는다.

## 4. M4 증거 그룹

### 4.1 장비

- 추첨기 ID
- 추첨기 세대·교체 구간
- 정비 또는 부품 교체 이벤트
- 정비 후 경과 회차

### 4.2 볼 세트

- 볼 세트 ID
- 볼 세대·전면 교체 구간
- 해당 세트의 사용 횟수 — 추첨 전 기준
- 교체 후 경과 회차
- 번호별 실측 무게·직경·구형도 — 실제 공개 자료가 있을 때만

### 4.3 운영조건

- 당일 사용 세트 선정 결과
- 혼합시간·추첨기 설정값 — 추첨 전 공개될 때만
- 온도·습도 — 실측값과 시각이 있을 때만
- 사전 모의추첨 결과 — 본추첨 전에 공개·기록된 경우에만

### 4.4 과거 배출순서 요약

현재 회차의 배출순서는 결과이므로 입력할 수 없다. 다음만 허용한다.

- 동일 볼 세트의 과거 번호별 평균 배출순위
- 동일 장비의 과거 번호별 평균 배출순위
- 최근 N회 배출순위 변화
- 모두 예측 대상 회차 이전 데이터만 사용

## 5. 금지되는 변수

- 본추첨 후 확인된 현재 회차 배출순서
- 본추첨 후 게시된 정보를 마치 사전 공개된 것처럼 사용
- 출처 없이 추정한 볼 세트 ID
- 기사에 나온 일반 규격을 회차별 실제 측정값으로 대체
- 미래 교체·정비 이력
- 결과와 상관이 큰 기간·번호만 사후 선택

## 6. M3 검정 보정

기존 `1,000 null + 4개 Holm + alpha 0.001`은 M3 활성화가 수학적으로 불가능했다.

M3는 사전등록된 단일 maxT omnibus 통계량으로 변경한다.

```text
T_t = max(
  standardized raw shift-52,
  standardized raw shift-104,
  standardized raw CUSUM,
  standardized entropy deviation
)
```

Null 시계열마다 모든 forecast origin의 최대 `T`를 저장하고, 단일 empirical p-value를 계산한다.

```text
p = (1 + count(null_max_T >= observed_T)) / (B + 1)
```

- 별도 Holm 보정을 다시 적용하지 않는다.
- familywise error는 null series의 전체-origin 최대통계량으로 제어한다.
- calibration B는 최소 10,000으로 고정한다.
- alpha 0.001은 완화하지 않는다.

## 7. 모델 가중치 안전장치

- RESEARCH 상태 최종 적용분포는 계속 M0=1이다.
- 합성검증을 통과해도 실제 데이터 Walk-forward 전에는 M4를 공개후보에 반영하지 않는다.
- CANDIDATE 상태에서 M1~M4 전체 비균등 비중 합계는 최대 30%다.
- M4 단독 비중 상한은 초기 10%다.
- M4 데이터 완전성 또는 신뢰도가 기준 미달이면 M4 비중은 0이다.

## 8. 5세트 출력 계약

최종 제품 출력은 유지한다.

```text
다음 회차 예측
1세트: 번호 6개
2세트: 번호 6개
3세트: 번호 6개
4세트: 번호 6개
5세트: 번호 6개
```

연구정보:

- 번호별 기준 포함확률
- 모델 추정 포함확률
- M0~M4 가중치
- 물리변수 데이터 완전성
- 물리변수 신뢰도
- 통계적 우위 상태
- 데이터 cutoff와 prediction hash

## 9. 버전 정책

M4 추가와 M3 검정 변경은 major 변경이다.

제안:

```text
model_version = 3.0.0-research
feature_contract_version = 2.0.0
physical_data_schema_version = 1.0.0
```

기존 `2.1.0-research` 결과와 실패 기록은 변경하지 않는다.

## 10. 다음 단계

이 명세 승인 후에만 다음을 구현한다.

1. 물리 메타데이터 계약과 validator
2. M4 hierarchical shrinkage expert
3. M3 maxT calibration
4. 물리변수 synthetic scenario generator
5. null·positive-control 전체 재검증
