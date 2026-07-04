# Gate 2 Implementation Plan

상태: **REVIEW CANDIDATE / Gate 2-1**  
목적: 고정 수식을 코드로 옮길 때 개발 순서·파일구조·테스트·승인시점을 명확히 한다.

---

## 1. Gate 2 전체 산출물

Gate 2는 다음 순서로 진행한다.

```text
Gate 2-1 명세 고정
→ Gate 2-2 엔진 골격·확률 정규화
→ Gate 2-3 합성 null/positive control
→ Gate 2-4 역사적 Walk-forward
→ Gate 2-5 검증보고 및 연구용 후보 생성
```

Gate 3 UI 개발은 Gate 2 검증 완료 후 진행한다.

---

## 2. Gate 2-1 — 명세 고정

현재 단계.

산출물:

- `docs/GATE2_ENGINE_SPEC.md`
- `docs/GATE2_FEATURE_CONTRACT.md`
- `docs/GATE2_BACKTEST_PROTOCOL.md`
- `docs/GATE2_IMPLEMENTATION_PLAN.md`
- Issue #3
- 별도 branch와 Draft PR
- handoff 문서 갱신

승인기준:

- 수식이 `ALGORITHM_SPEC.md`와 충돌하지 않음
- 비개발자가 목적·단계·판정 기준을 이해할 수 있음
- Codex 또는 타 AI가 추가 질문 없이 구현 가능한 수준
- 실제 미래예측 공개가 포함되지 않음

---

## 3. Gate 2-2 — 엔진 골격

### 권장 파일구조

```text
engine/
├─ __init__.py
├─ config.py
├─ contracts.py
├─ data_loader.py
├─ feature_engineering.py
├─ elementary_symmetric.py
├─ distributions.py
├─ experts/
│  ├─ __init__.py
│  ├─ uniform.py
│  ├─ persistence.py
│  ├─ reversal.py
│  └─ regime_change.py
├─ weights.py
├─ randomness_gate.py
├─ candidate_optimizer.py
├─ uncertainty.py
├─ prediction_run.py
└─ hashing.py
```

### 구현 순서

1. 데이터 계약 로더
2. 미래 데이터 차단 assertion
3. feature snapshot 생성
4. `e_6` 동적계획법
5. M0 확률분포
6. sub-expert 확률분포
7. M1~M3 내부 가중치
8. top-level shadow weight
9. gate 상태기계
10. 후보 5세트 선택
11. 출력 JSON과 해시

### 완료 테스트

- M0 모든 조합확률 동일
- 확률합 1
- 주변확률 합 6
- 동일 입력 재현
- target draw 이후 데이터 거부
- 후보 5세트 중복 없음
- gate CLOSED일 때 최종 M0

---

## 4. Gate 2-3 — 합성 검증

### 권장 파일구조

```text
simulation/
├─ uniform_lottery.py
├─ planted_bias.py
├─ regime_shift.py
├─ temporary_anomaly.py
├─ pair_interaction.py
└─ experiment_runner.py
```

### 필수 실험

- 균등 시계열 1,000개
- 고정 편향 효과크기 2%, 5%, 10%
- 지속·반전·구조변화 시나리오
- 일시적 편향 후 균등 복귀
- pair interaction

### 완료기준

- 균등 null에서 CANDIDATE 오탐 ≤0.1%
- 신호가 사라지면 M0 복귀
- planted signal 방향 오류율 보고
- 탐지 불가능한 효과크기를 숨기지 않음

---

## 5. Gate 2-4 — 역사적 Walk-forward

### 권장 파일구조

```text
backtest/
├─ runner.py
├─ baselines.py
├─ metrics.py
├─ bootstrap.py
├─ multiple_testing.py
├─ calibration.py
└─ report_builder.py
```

### 실행

```text
300회부터 1230회까지 931회 예측
```

각 회차 저장:

- 사용 가능 마지막 회차
- 피처 스냅샷 해시
- 모형별 joint probability
- sub-expert·top-level weight
- gate 상태
- 후보 5세트
- 실제 결과
- Brier·log loss·hit metric

### 비교

- B0~B6 기준모형
- 균등 포트폴리오 10,000회 시뮬레이션
- Block A/B/C
- Moving-block bootstrap
- Holm 보정

### 결과 해석

- 역사적 데이터는 탐색적
- CANDIDATE 여부만 판단
- PROMOTED 선언 금지

---

## 6. Gate 2-5 — 검증보고 및 연구용 후보

Gate 2-4 결과를 바탕으로 다음을 제출한다.

### 기술보고

- 수식과 코드 매핑표
- 테스트 결과
- 합성 null·positive control
- Walk-forward 성능
- 기준모형 비교
- 다중검정 결과
- calibration
- Gate 상태

### 비개발자 보고

첫 화면 순서:

1. 결론: 우위 있음/없음
2. 무엇과 비교했는지
3. 평균적으로 얼마나 달랐는지
4. 특정 기간에만 잘했는지
5. 과적합 검사를 통과했는지
6. 다음 단계

### 연구용 1231회 후보

- 공식 공개·잠금 아님
- `research_only: true`
- gate CLOSED면 M0 기반 후보
- gate CANDIDATE면 M0 70% 이상 혼합 유지
- `통계적 우위 없음`을 숨기지 않음

---

## 7. 테스트 구조

```text
tests/
├─ test_data_cutoff.py
├─ test_feature_contract.py
├─ test_elementary_symmetric.py
├─ test_probability_normalization.py
├─ test_uniform_model.py
├─ test_expert_models.py
├─ test_weight_update_limits.py
├─ test_randomness_gate.py
├─ test_candidate_optimizer.py
├─ test_reproducibility.py
├─ test_synthetic_null.py
├─ test_synthetic_positive.py
└─ test_walk_forward_contract.py
```

실패하면 다음 단계로 이동하지 않는다.

---

## 8. CI 작업

```text
.github/workflows/gate2-engine.yml
```

단계:

1. Python 환경
2. Gate 1 데이터 검증
3. 단위 테스트
4. 합성 smoke test
5. 확률 정규화 검사
6. 미래 데이터 누출 검사
7. 결정론적 재실행 해시 비교
8. 축약 Walk-forward smoke test
9. 보고서 아티팩트 생성

전체 931회 백테스트와 1,000개 합성 시계열은 별도 수동 workflow로 실행한다.

---

## 9. 모델 버전

Gate 2 최초 연구엔진:

```text
model_version = 2.0.0-research
feature_contract_version = 1.0.0
backtest_protocol_version = 1.0.0
```

버전 변경:

- PATCH: 수식 결과가 변하지 않는 오류·성능 개선
- MINOR: 승인된 sub-expert·피처·보조진단 추가
- MAJOR: M0~M3 구조·목적함수·승격기준 변경

과거 실행은 새 버전으로 덮어쓰지 않는다.

---

## 10. 구현 중 금지사항

- 전체 8,145,060 조합을 매 회차 무차별 반복 계산해 성능문제를 만든 뒤 근사식으로 몰래 교체
- 편의를 위해 45개 번호를 독립 Bernoulli로 최종 샘플링
- 모델 결과를 보고 window 변경
- M0를 단순 benchmark 파일로만 두고 최종 혼합에서 제거
- pair interaction을 검증 없이 활성화
- 후보 UI부터 먼저 개발
- 백테스트가 좋게 나오도록 seed 변경
- 실패 결과 삭제

---

## 11. 사용자 검토 포인트

Gate 2-1에서 사용자가 확인할 내용은 코드가 아니라 다음 의사결정이다.

- M0~M3 역할이 기존 논의와 일치하는지
- 최근신호의 지속과 반전이 별도 가설로 유지되는지
- 무신호일 때 M0로 복귀하는지
- 역사적 백테스트만으로 검증완료라고 하지 않는지
- 실제 미래예측 공개가 공식 검증 이후로 제한되는지
- 5세트 선택에서 6개 적중확률이 1순위인지

승인 후 Gate 2-2 코드 구현으로 이동한다.
