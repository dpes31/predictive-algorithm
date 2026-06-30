# Gate 2-3P Validation Protocol

상태: 검토용 고정 명세  
작성일: 2026-06-30

## 1. 목적

M4가 실제 관계가 있을 때만 번호별 확률을 변화시키고, 무관·결측·오류 데이터에서는 M0으로 복귀하는지 검증한다.

Gate 2-3P는 실제 과거 당첨번호를 사용하지 않는 합성검증이다.

## 2. 검증 순서

### Gate 2-3P-1 — 명세

- M4 수식
- 메타데이터 스키마
- M3 maxT 검정
- 합성 시나리오
- 통과·중단 기준

### Gate 2-3P-2 — 구현

- metadata validator
- M4 expert
- missingness·reliability 처리
- maxT calibrator
- synthetic generator
- deterministic report

### Gate 2-3P-3 — 전체 합성검증

- null calibration
- independent null validation
- positive controls
- negative controls
- 오류·결측·regime 시나리오

## 3. Null 시나리오

### N0. 완전 균등

물리변수와 번호 결과가 독립이다.

### N1. 무관한 메타데이터

볼 세트·추첨기·온습도 값은 변하지만 결과와 관계가 없다.

### N2. 결측 의존성

메타데이터 결측률이 시기와 장비에 따라 달라지지만 번호 결과와는 독립이다.

### N3. 측정오차

관측값에 잡음이 있지만 결과와 관계가 없다.

### N4. 잘못된 ID

볼 세트 ID 일부가 오분류되지만 결과와 관계가 없다.

### N5. 교체 이벤트만 존재

장비·볼 세트 교체는 있으나 번호확률은 균등하다.

## 4. Positive-control 시나리오

### P1. 볼 세트별 번호효과

5개 볼 세트별로 서로 다른 번호군에 상대가중치를 부여한다.

사전고정 효과크기:

```text
1.05 / 1.10 / 1.25 / 1.50
```

### P2. 추첨기별 번호효과

두 장비에서 서로 다른 번호군이 유리하도록 설정한다.

### P3. 장비 × 볼 세트 상호작용

상호작용은 M4 내부의 사전등록 contextual effect로만 평가하며 번호쌍 interaction과 구분한다.

### P4. 교체 후 방향 전환

교체 전과 후의 번호효과 방향을 반대로 설정한다. M3가 교체시점을 감지하고 M4가 새 조건에 적응해야 한다.

### P5. 일시적 환경효과

사전 공개된 환경변수 구간에서만 약한 번호효과가 발생하고 이후 사라진다.

### P6. 사전 모의추첨 신호

모의추첨과 본추첨이 공통 latent condition을 공유하는 경우와 완전히 독립인 경우를 각각 생성한다.

## 5. Robustness 시나리오

- metadata 10% / 30% / 50% 결측
- confidence 과대평가 10% / 30%
- ID 오분류 5% / 15%
- observed_at 오류
- regime change 직후 데이터 부족
- 과거에는 유효했으나 이후 관계 소멸
- 관계 방향 반전

## 6. 실험 규모

### M3 maxT calibration

- 10,000 null series
- 각 series 1,230 draws
- 전체 forecast origin의 maxT 사용

### 전체 모델 null calibration

- 4,000 series

### 독립 null validation

- 5,000 series

### Positive controls

- 시나리오·효과크기별 500 series

### Smoke

- 20 calibration / 20 validation / positive 5

## 7. 평가 지표

- familywise false activation rate
- one-sided 95% upper confidence limit
- M4 strict detection rate
- M3 activation rate
- matched-context direction accuracy
- Log Loss improvement vs M0
- Brier improvement vs M0
- calibration error
- detection delay
- regime adaptation delay
- M0 return delay
- missingness degradation curve
- minimum detectable effect

## 8. Strict success 정의

M4 시나리오 성공은 다음을 모두 만족해야 한다.

1. M4 mean delta Log Loss > 0
2. M4 mean delta Brier >= 0
3. M4가 M1·M2·M3보다 엄격히 우수
4. 최소 2개 macro block에서 양의 Log Loss 개선
5. 효과 방향 정확도 80% 이상
6. 사전등록 효과크기 1.25에서 strict detection 80% 이상
7. 신호가 사라진 뒤 M0 복귀

M3 시나리오는 추가로 maxT p <= 0.001을 요구한다.

## 9. Null 통과 기준

- 전체 proxy 관측 오탐률 <= 0.1%
- one-sided 95% upper <= 0.2%
- M3 maxT 관측 오탐률 <= 0.1%
- 무관한 물리변수에서 M4 평균 가중치 증가 없음
- 결측·오분류가 증가할수록 확신이 증가하지 않음

`95% upper <= 0.1%`는 계산량이 지나치게 커질 수 있으므로 연구 승격 기준과 별도 관리한다. 공개 승격 전에는 더 큰 prospective validation이 필요하다.

## 10. 통과 후에도 허용되지 않는 것

합성검증 통과는 실제 로또 예측력 증명이 아니다.

통과 후 허용:

- 실제 메타데이터 수집 파일럿
- 연구용 Walk-forward 설계

통과 후에도 금지:

- 실제 미래예측 공개
- 확률 우위 주장
- 데이터 잠금
- M4 비중 상한 해제

## 11. 중단 기준

다음 중 하나면 Gate 2-3P를 NOT PASSED로 판정한다.

- null proxy 오탐률 초과
- M4가 무관변수에 반응
- 1.25 contextual effect에서 strict detection 80% 미달
- M3 maxT가 구조변화를 탐지하지 못함
- 결측 증가 시 확신 증가
- 미래 데이터 누출 테스트 실패

실패 결과는 삭제하지 않고 새 버전에서만 수정한다.
