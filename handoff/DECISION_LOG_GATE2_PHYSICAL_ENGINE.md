# Gate 2 Physical Engine Decision Record

## D-020 — Gate 2-3P-2 구현 완료 및 재검증 전 차단 유지

- 결정일: 2026-06-30
- 사용자 승인:
  - Gate 2-3P-1 명세 승인
  - 모델 버전 `3.0.0-research` 승인
  - Gate 2-3P-2 Python 구현 승인

### 구현 결정

1. 기존 M0~M3와 5세트 출력을 유지한다.
2. M4는 추첨 전에 관측 가능한 물리·운영 context만 사용한다.
3. metadata는 출처·관측시각·사전가용성·confidence를 필수로 한다.
4. 추첨 후 관측값·현재 회차 결과·inferred 데이터는 prediction 기여를 금지한다.
5. M4는 균등 prior 기반 강한 shrinkage를 사용한다.
6. context support가 20 미만이거나 metadata 품질이 낮으면 uniform fallback한다.
7. M4 최종 비중은 초기 10%를 넘지 않는다.
8. M3는 단일 familywise maxT 검정을 사용한다.
9. maxT calibration이 10,000개 미만이면 M3 activation을 금지한다.
10. RESEARCH 상태 최종분포는 M0=100%를 유지한다.

### 구현 산출물

- `engine/physical_metadata.py`
- `engine/experts/physical_evidence.py`
- `engine/maxt_gate.py`
- `engine/prediction_run.py`
- `engine/randomness_gate.py`
- `simulation/physical_scenarios.py`
- `scripts/run_gate2_physical_smoke.py`
- physical·maxT·leakage·integration tests

### 검증

- GitHub Actions run: `28444499045`
- conclusion: success
- unit tests: pass
- deterministic smoke: pass
- smoke report hash: `d6f504ccbc964a72fd2e870e0ae1c933a07241b4cb16a868436e1455d218a7f7`
- physical artifact digest: `sha256:8134f362de8e9c06f90fcd04586b27871ec4f5cfa84eba952e6036799e836253`

### 해석

- Gate 2-3P-2 성공은 코드와 계약이 작동한다는 의미다.
- 예측력과 오탐률은 아직 검증되지 않았다.
- unrelated metadata에서도 finite-sample M4 분포는 비균등해질 수 있으므로 Gate 2-3P-3가 필수다.
- 단일 ball-set holdout의 Log Loss가 M0보다 나빴던 결과를 삭제하지 않는다.

### 결정

- Gate 2-3P-2를 구현 완료 상태로 기록한다.
- Gate state는 `RESEARCH`로 유지한다.
- 최종 적용분포는 `M0 only`로 유지한다.
- Gate 2-3P-3은 사용자 승인 전 실행하지 않는다.
- 실제 데이터 Walk-forward·실제 후보 공개·모바일 UI는 계속 차단한다.
