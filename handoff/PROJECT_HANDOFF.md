# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-3 합성 검증 실행 완료 · NOT PASSED · 보정안 승인 대기**  
현재 작업 브랜치: `feature/gate2-synthetic-validation`  
기준 브랜치: `feature/gate2-engine-core`  
관련 이슈: `#7 Gate 2-3 합성 null 및 positive-control 검증`  
현재 Draft PR: `#8 Gate 2-3: add synthetic null and planted-signal validation`

## 1. 프로젝트 목적

과거 로또 6/45 데이터와 이후 누적 데이터를 이용해 다음 회차의 6개 번호 조합 5세트를 생성하고, 사전 잠금 후 실제 결과와 비교하여 검증하는 연구형 확률예측 시스템입니다.

핵심 모형:

- M0 균등 무작위
- M1 지속
- M2 반전·평균회귀
- M3 구조변화

비균등 신호가 확인되지 않으면 M0으로 복귀합니다.

## 2. 승인 및 Gate 상태

- Gate 1: 승인 완료
- Gate 2-1: 명세 승인 완료
- Gate 2-2: Python 엔진 골격 승인 완료
- Gate 2-3: 합성 검증 실행 완료
- Gate 2-3 판정: **NOT PASSED**
- Gate 2-4 실제 데이터 Walk-forward: **차단**
- 최종 Gate 상태: `RESEARCH`
- 최종 사용자 적용 가중치: M0=1.0 유지

## 3. 데이터 상태

- 범위: 1~1230회
- 데이터 버전: `draws-2026.06.27-r1`
- `auto_checked`: 1,230
- `verified`: 0
- `locked`: 0
- 공식 자동 대조: 미완료
- 실제 데이터는 Gate 2-3에서 사용하지 않음

## 4. Gate 2-3 실행 범위

### 균등 null

- 캘리브레이션: 1,000개 시계열
- 독립 검증: 1,000개 시계열
- 시계열당 1,230회
- alpha: 0.001

### Positive controls

각 시나리오당 100회:

- 고정 번호 상대가중치 1.02, 1.05, 1.10
- 최근 52회 지속 과정
- 최근 52회 반전 과정
- 400·800회 구조변화
- 52회 일시적 편향 후 균등 복귀
- 번호쌍 factor 1.25, 1.5, 2.0, 3.0

### 재현성

- 모델 버전: `2.0.0-research`
- 보고서 해시: `0a479eb341f2028471483a5b4c6ca7aa2f4065be493bc04af34df25cec62d2d0`
- Full workflow run: `28427144563`
- Full workflow conclusion: `success`
- Artifact ID: `7973775000`
- Artifact SHA-256: `8fa08d4d2db0287077659e2d5ff47cb20fe69d027f93b2b71caa11a2a5947db2`

## 5. Null 결과

| 검사 | 이벤트 | 관측률 | 95% 단측 상한 |
|---|---:|---:|---:|
| 합성 Gate proxy | 1/1,000 | 0.10% | 0.4735% |
| M3 변화진단 | 0/1,000 | 0.00% | 0.2991% |
| Pair 진단 | 0/1,000 | 0.00% | 0.2991% |

해석:

- 관측 점추정은 0.1% 기준 이하
- 1,000회 표본만으로 실제 오탐률의 95% 상한이 0.1% 이하라고 확정할 수 없음
- null 억제력은 양호하지만 정식 통과 근거로는 불충분

## 6. Positive-control 결과

- 고정 번호 +2%: 탐지 0%
- 고정 번호 +5%: 탐지 0%
- 고정 번호 +10%: proxy 탐지 1%, M1 양의 점수 0%
- 지속 과정: proxy 탐지 64%, M1 양의 점수 0%
- 반전 과정: proxy 탐지 1%, M2 양의 점수 0%
- 구조변화: M3 진단 0%, M3 개선점수 0
- 일시적 변화: M3 진단 0%, M3 개선점수 0
- pair factor 1.25~3.0: pair 진단 0%
- 80% power 최소 탐지 효과크기: 없음

따라서 “심은 신호를 올바른 모형이 탐지한다”는 Gate 2-3 완료조건을 충족하지 못했습니다.

## 7. 확인된 문제

### M1·M2 과확신

현재 `η=±z` 구조가 약한 신호에 비해 지나치게 큰 확률 편차를 만들어 Log Loss와 Brier Score가 M0보다 악화됐습니다.

### M3 진단 포화

winsorized `z_shift`와 CUSUM의 최대값이 3.0에 포화됐고, null 99.9% 분위수도 3.0이 되어 구조변화 p-value를 충분히 낮출 수 없었습니다.

### Pair 진단 검정력 부족

104회 window에서 990개 번호쌍·다중 시점을 보정한 null 최대 z 분위수는 약 8.37로, factor 3.0도 탐지하지 못했습니다.

### 보고 로직 오류

M3 개선점수가 0임에도 M1·M2가 음수라 상대적으로 승자로 표시됐습니다. 향후 승리 판정은 양의 개선점수와 gate 활성화를 필수조건으로 해야 합니다.

## 8. 보정안 — 사용자 승인 필요

제안 Gate: `Gate 2-3R`

1. M1·M2에 사전고정 shrinkage/temperature sub-expert 도입
2. 예측 피처는 winsorize 유지, M3 global diagnostic은 raw statistic으로 분리
3. pair 진단은 비활성 유지 또는 장기 window·검정체계 보정
4. positive-control 승리 판정 로직 수정
5. 모델 버전 `2.1.0-research`로 증가
6. 동일 null·positive-control 전체 재실행

핵심 수식·하이퍼파라미터 변경이 포함되므로 사용자 승인 전에 구현하지 않습니다.

## 9. 금지사항

- Gate 2-4 실제 데이터 Walk-forward 실행 금지
- 1231회 후보 생성 금지
- 실패한 positive-control 삭제 금지
- 효과크기·변화시점 소급 변경 금지
- pair interaction 활성화 금지
- 실제 공개예측 금지
- UI·Supabase 개발 진행 금지

## 10. 필수 문서

1. `AGENTS.md`
2. `docs/ALGORITHM_SPEC.md`
3. `docs/GATE2_ENGINE_SPEC.md`
4. `docs/GATE2_FEATURE_CONTRACT.md`
5. `docs/GATE2_BACKTEST_PROTOCOL.md`
6. `docs/GATE2_3_EXECUTION_PLAN.md`
7. `reports/gate2_3_full_summary.md`
8. `reports/gate2_3_full_summary.json`
9. 본 파일
10. `handoff/DECISION_LOG.md`
11. `handoff/GATE2_3_WORK_LOG.md`

## 11. 주요 링크

- 저장소: `https://github.com/dpes31/predictive-algorithm`
- Gate 2-3 Issue: `https://github.com/dpes31/predictive-algorithm/issues/7`
- Gate 2-3 Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/8`
- Gate 2-3 branch: `feature/gate2-synthetic-validation`
