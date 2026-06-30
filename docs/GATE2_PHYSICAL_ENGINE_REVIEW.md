# Gate 2-3P-2 Physical Evidence Engine Review

상태: 구현 완료 · 사용자 검토 대기  
모델 버전: `3.0.0-research`  
브랜치: `feature/gate2p2-engine`  
Draft PR: #13

## 1. 구현 목적

기존 로또 6/45 예측기의 M0~M3와 6개 번호 × 5세트 출력을 유지하면서, 추첨 전에 알 수 있는 물리·운영 조건을 M4 증거채널로 추가했다.

이번 Gate는 **엔진 구현과 smoke 검증**이다. 실제 예측력의 통계검증은 Gate 2-3P-3에서 수행한다.

## 2. 주요 코드

### `engine/physical_metadata.py`

- 물리 메타데이터 parsing·validation
- 출처·관측시각·사전가용성·confidence 검증
- 결과 필드와 미래 데이터 차단
- completeness·reliability·traceability 계산

### `engine/experts/physical_evidence.py`

- M4 contextual shrinkage expert
- 동일 추첨기·볼 세트·regime의 과거 결과만 집계
- 강한 균등 prior 수축
- 지원 표본 부족 또는 품질 미달 시 균등분포 반환

### `engine/maxt_gate.py`

- M3 단일 maxT omnibus 검정
- 전체 origin·진단을 하나의 null 최대통계량으로 보정
- plus-one empirical p-value
- 10,000개 calibration 전에는 activation 차단

### `engine/prediction_run.py`

- M0~M4 혼합
- M4 메타데이터 optional 입력
- RESEARCH 상태 최종분포 M0-only
- M4 candidate weight cap 10%
- 5개 후보 세트 출력 유지

### `simulation/physical_scenarios.py`

- 무관 메타데이터
- 볼 세트별 편향
- 추첨기별 편향
- regime reversal
- 30% 결측 시나리오

### `scripts/run_gate2_physical_smoke.py`

- deterministic implementation smoke
- 실제 데이터 미사용
- statistical validation 미완료 명시

## 3. 안전장치

- target 회차보다 늦은 결과·메타데이터 금지
- current ordered numbers·winning numbers·bonus 입력 금지
- 추첨 후 관측값을 pre-draw로 표시하면 validation 실패
- inferred·unknown은 예측기여 0
- 필수 메타데이터 품질 미달 시 M4 균등 fallback
- RESEARCH 상태 M4 최종가중치 0
- CANDIDATE 상태에서도 M4 최대 10%
- public release 차단

## 4. 테스트

GitHub Actions run `28444499045`가 성공했다.

- canonical data validation: pass
- unit test suite: pass
- deterministic smoke twice: pass
- research-only contract: pass
- public-release prohibition: pass

추가된 테스트:

- post-draw leakage rejection
- result-field rejection
- inferred evidence exclusion
- duplicate metadata rejection
- M4 active·uniform fallback
- deterministic physical generation
- maxT resolution·full contract
- M4 prediction integration
- M4 deployment cap

## 5. Smoke 결과 해석

Smoke는 각 scenario의 마지막 1개 target만 계산한다. 이 값으로 탐지력이나 예측력을 판단하지 않는다.

관찰:

- machine·regime·missingness sample은 실행 가능
- unrelated sample에서도 finite-sample 차이로 M4 distribution이 비균등해질 수 있음
- ball-set sample 한 건은 M0보다 Log Loss가 나빴음

따라서 M4는 코드가 작동하지만 아직 유효한 예측모형으로 승인되지 않았다. Gate 2-3P-3의 대규모 null 검증이 필수다.

## 6. 승인 후 다음 단계

Gate 2-3P-3에서 다음을 실행한다.

- M3 maxT null calibration 10,000
- 전체 model null calibration 4,000
- independent null validation 5,000
- positive control별 500
- missingness·misclassification·regime robustness
- strict detection·Log Loss·Brier·calibration 평가

통과 전에는 실제 과거번호 Walk-forward와 모바일 화면 개발을 시작하지 않는다.
