# Gate 2-3 Work Log

- 작업일: 2026-06-30
- 작업 브랜치: `feature/gate2-synthetic-validation`
- 기준 브랜치: `feature/gate2-engine-core`
- 사용자 승인: Gate 2-2 승인, Gate 2-3 합성 null/positive-control 검증 진행
- 관련 이슈: #7
- Draft PR: #8

## 1. 구현

- exact fixed-size weighted sampler
- fixed bias, persistence, reversal, regime shift, temporary anomaly, pair-factor scenarios
- block-aligned incremental diagnostics
- familywise-over-origins null calibration
- Holm correction and M3 change-gate calculation
- exact blockwise M0/M1/M2/M3 probability probe
- independent null score calibration
- synthetic proxy decision
- exact one-sided Clopper-Pearson upper confidence bound
- JSON and Markdown report generation
- smoke and full experiment workflows
- immutable distribution normalizer caching for execution performance

## 2. 테스트 및 실행

### Smoke

- Workflow: `Gate 2 synthetic validation`
- Run ID: `28427144648`
- Conclusion: success
- canonical data validation: success
- all unit tests: success
- synthetic smoke: success

### Full experiment

- Workflow: `Gate 2 synthetic full experiment`
- Run ID: `28427144563`
- Job ID: `84232864723`
- Conclusion: success
- null calibration: 1,000 series
- independent null validation: 1,000 series
- positive controls: 100 series per scenario
- draws per series: 1,230
- alpha: 0.001

### Artifact

- Name: `gate2-3-full-experiment`
- Artifact ID: `7973775000`
- Artifact digest: `sha256:8fa08d4d2db0287077659e2d5ff47cb20fe69d027f93b2b71caa11a2a5947db2`
- Report hash: `0a479eb341f2028471483a5b4c6ca7aa2f4065be493bc04af34df25cec62d2d0`

## 3. Null 결과

- Gate proxy: 1/1,000, 0.10%
- Gate proxy one-sided 95% upper: 0.4735%
- M3 diagnostic: 0/1,000
- M3 diagnostic one-sided 95% upper: 0.2991%
- Pair diagnostic: 0/1,000
- Pair diagnostic one-sided 95% upper: 0.2991%

점추정 기준 0.1% 이하였으나, 1,000개 시계열로 95% upper bound 0.1% 이하를 입증하지 못했습니다.

## 4. Positive-control 결과

- fixed +2%: M1 positive score 0%, proxy 0%
- fixed +5%: M1 positive score 0%, proxy 0%
- fixed +10%: M1 positive score 0%, proxy 1%
- persistence: M1 positive score 0%, proxy 64%
- reversal: M2 positive score 0%, proxy 1%
- regime shift: M3 diagnostic 0%, M3 improvement 0
- temporary anomaly: M3 diagnostic 0%, M3 improvement 0
- pair factor 1.25 / 1.5 / 2 / 3: pair diagnostic 0%
- 80% power minimum detectable fixed lift: none
- 80% power minimum detectable pair factor: none

## 5. 발견된 문제

### M1·M2 amplitude

고정 수식 `η=±z`가 약한 신호에 비해 과확신 분포를 만들어 proper score를 악화시켰습니다.

### M3 saturation

winsorized 진단의 null 99.9% 분위수가 3.0에 포화돼 M3가 활성화될 수 없었습니다.

### Pair power

104회 window에서 990개 pair와 여러 origin을 보정한 최대 z null 기준이 약 8.37로 높아 factor 3도 탐지하지 못했습니다.

### Reporting

M3 score 0이 음수인 M1·M2보다 상대적으로 높아 승리율 100%로 표시되는 오류를 확인했습니다. 탐지 성공으로 해석하지 않으며 보고서에서 정정했습니다.

## 6. 판정

```text
Gate 2-3: NOT PASSED
Gate state: RESEARCH
Final distribution: M0 only
Gate 2-4: blocked
```

## 7. 보정 제안 — 미승인

- M1·M2 shrinkage/temperature sub-experts
- M3 raw diagnostic separation
- pair diagnostic redesign or continued exclusion
- strict positive-control winner definition
- proposed version: `2.1.0-research`

프로젝트 규칙에 따라 사용자 승인 전 위 변경을 구현하지 않습니다.

## 8. 금지 범위 유지

- 실제 1~1230회 Walk-forward 미실행
- 1231회 후보 미생성
- pair interaction 예측모형 비활성
- 실제 공개예측 미허용
- Supabase 및 UI 미연결
- 실패 결과 삭제 또는 효과크기 소급 변경 금지
