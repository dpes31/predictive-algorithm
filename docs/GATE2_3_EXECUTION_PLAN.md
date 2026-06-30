# Gate 2-3 Synthetic Validation Execution Plan

상태: 사용자 승인 완료  
승인일: 2026-06-30  
기준 브랜치: `feature/gate2-engine-core`

## 목적

Gate 2-2 엔진이 균등 무작위 데이터에서 허위 신호를 만들지 않는지, 그리고 사전에 정의한 편향이 존재할 때 올바른 방향과 모형으로 탐지하는지 검증한다.

## 검증층

### A. Diagnostic calibration

- uniform 6/45 null series
- entropy 52/104
- shift 52/104
- EWMA deviation
- CUSUM aggregate
- pair 104 diagnostic
- empirical tail probability
- Holm-adjusted global change gate

### B. Planted positive controls

- fixed number bias: relative lift 1.02 / 1.05 / 1.10
- persistence signal
- reversal signal
- regime changes at 400 / 800
- temporary 52-draw anomaly and return to uniform
- pair interaction diagnostic

## 기본 실험 수

- null full experiment: minimum 1,000 series × 1,230 draws
- positive controls: scenario별 사전고정 반복 수
- CI smoke: 축약 반복 수

## 핵심 지표

- false activation rate
- exact binomial confidence interval
- detection power
- false sign rate
- detection delay
- return-to-M0 delay
- minimum detectable effect size
- M1/M2/M3 matched-model ranking

## 중요한 통계적 한계

1,000개 null series에서 오탐이 0건이어도 95% 단측 상한은 약 0.3%다. 따라서 관측 오탐률 0%를 근거로 `≤0.1%가 확정되었다`고 표현하지 않는다.

- point estimate 기준: 1/1000 단위
- 엄격한 95% upper bound ≤0.1% 입증에는 최소 약 2,995개의 무오탐 반복이 필요
- Gate 2-3 보고서는 관측값과 불확실성 상한을 함께 제시

## 금지

- 합성결과를 본 뒤 효과크기·변화시점·threshold 변경
- 2%·5% 신호가 탐지되지 않았다는 결과 삭제
- pair interaction을 예측모형에 활성화
- 실제 1~1230회 Walk-forward 실행
- 1231회 실제 후보 생성
- 합성데이터 통과를 실제 로또 예측력으로 표현
