# Gate 2 Physical Validation Decision Record

## D-021 — Gate 2-3P-3 전체 합성검증 NOT PASSED

- 결정일: 2026-06-30
- 사용자 승인:
  - Gate 2-3P-2 구현 승인
  - Gate 2-3P-3 전체 합성 null/positive-control 재검증 승인
- 모델: `3.0.0-research`
- 브랜치: `feature/gate2p3-validation`
- Issue: #14
- Draft PR: #15

### 실행

- M3 maxT null calibration: 10,000
- M4 model null calibration: 4,000
- independent null validation: 5,000
- positive controls: 12,000
- robustness: 6,000
- total: 37,000 synthetic series
- deterministic shards: 20

### 실행 무결성

- workflow run: `28451343507`
- workflow conclusion: success
- all shards: success
- aggregate: success
- head SHA: `56f5ace469ee42a1b5743029092585724819796b`
- summary artifact: `7983755657`
- artifact digest: `sha256:58526bd3b6f9a178575092f0affdb29d115139bd9dd1210dac04ef768dbe7ca7`
- report hash: `b59cc753eda4058f0b55a685a136da01a327dd6b6b7fc33b10fd4758dfc36948`

### Null 결과

- proxy false activation: 5/5,000 = 0.100000%
- proxy one-sided 95% upper: 0.205288%
- M3 false activation: 8/5,000 = 0.160000%
- M3 one-sided 95% upper: 0.283731%

판정:

- observed proxy rate criterion: PASS at boundary
- proxy upper-bound criterion: FAIL
- M3 false-activation criterion: FAIL
- irrelevant-metadata criterion: FAIL

### Positive-control 결과 — lift 1.25

- ball set strict detection: 0.8%
- machine strict detection: 24.2%
- machine × ball strict detection: 0.8%
- regime reversal strict detection: 0.0%
- temporary environment strict detection: 0.0%
- pretest shared strict detection: 0.4%

사전등록 목표는 각 시나리오 80% 이상이었다. 모두 미달했다.

### Robustness

통과:

- missingness 증가에 따른 confidence 증가 없음
- independent pretest activation 없음
- direction reversal 208 draws 이내 적응

실패:

- post-draw-error activation 2.6%
- signal-decay return within 208 draws 65.8%
- M3 regime-reversal activation 0.2%

### 결정

```text
Gate 2-3P-3 = NOT PASSED
Gate state = RESEARCH
Final deployable distribution = M0 only
M4 deployable weight = 0
```

### 의미

- 코드·CI 실행 실패가 아니다.
- 전체 검증은 계획대로 완료됐다.
- `3.0.0-research` 모델이 사전등록된 오탐·탐지력 기준을 충족하지 못했다.
- 모든 향후 알고리즘 개발이 불가능하다는 판정은 아니다.
- 동일 버전의 임계값 완화 또는 seed 선별 재실행은 금지한다.

### 차단

- Gate P-1 실제 메타데이터 예측 파일럿
- Gate 2-4P 실제 Walk-forward
- 실제 미래 번호 5세트 공개
- 모바일 예측 UI 활성화
- M4 비중 0 초과 적용

### 다음 권고

사용자 승인 후 `Gate 2-3P-R` 보정 명세만 작성한다. 검토 후보:

1. field별 sequential evidence weighting
2. null-calibrated abstention
3. hierarchical partial pooling
4. stable/transient context 분리
5. invalid timestamp global veto
6. M3 detector 재설계
7. signal decay와 M0 return 강화
8. 신규 버전과 동일 규모 재검증 계약
