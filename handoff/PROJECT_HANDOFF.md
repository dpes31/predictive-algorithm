# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-1 예측 엔진 명세 작성 완료 · 사용자 검토 대기**  
현재 작업 브랜치: `feature/gate2-engine-spec`  
기준 브랜치: `feature/gate1-governance-foundation`  
관련 이슈: `#3 Gate 2-1 예측 엔진 명세 및 백테스트 계약 고정`  
현재 Draft PR: `#4 Gate 2-1: freeze predictive engine and backtest specification`

## 1. 프로젝트 목적

과거 로또 6/45 데이터와 이후 누적 데이터를 이용해 다음 회차의 6개 번호 조합 5세트를 생성하고, 추첨 전에 잠근 뒤 실제 결과와 비교하여 검증하는 연구형 확률예측 앱을 개발합니다.

핵심 모형:

- M0 균등 무작위
- M1 지속
- M2 반전·평균회귀
- M3 구조변화

비균등 신호가 확인되지 않으면 M0으로 복귀합니다.

## 2. 사용자 확정사항

- 출력: 6개 번호 조합 5세트
- 성공목표: 6개 적중 가능성 → 최고 일치 개수 → 다양성 → 군중 회피
- 신호가 없어도 후보 제공, 단 `통계적 우위 없음` 표시
- 군중 회피 영향 최대 5%
- 사용자 95% 구간, 모델 승격 99.9%
- Python 예측, HTML은 잠금 JSON 표시
- 상세 분석 기본 숨김
- 인수인계 Markdown을 작업마다 누적
- Gate 1 승인 완료
- 현재 `auto_checked` 데이터는 연구용 백테스트에 사용
- 실제 미래예측 공개와 데이터 잠금은 공식 검증 완료 후 진행

## 3. Gate 1 상태

- 데이터 범위: 1~1230회
- 데이터 버전: `draws-2026.06.27-r1`
- 구조·체크섬·파생 데이터·재현성 검사: 통과
- 데이터셋 SHA-256: `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- 공식 자동 대조: 미완료
- `auto_checked`: 1,230
- `verified`: 0
- `locked`: 0
- Vercel Preview 모바일 검수: 통과

## 4. Gate 2-1 완료 항목

### 문서

- `docs/GATE2_ENGINE_SPEC.md`
- `docs/GATE2_FEATURE_CONTRACT.md`
- `docs/GATE2_BACKTEST_PROTOCOL.md`
- `docs/GATE2_IMPLEMENTATION_PLAN.md`
- `docs/GATE2_REVIEW_GUIDE.md`

### 핵심 설계

- 정확히 6개가 선택되는 조합확률을 elementary symmetric polynomial로 정규화
- M0~M3와 sub-expert 구조 정의
- 지속과 반전을 별도 경쟁가설로 유지
- pair interaction은 계약상 유지하되 초기값 0
- 무작위성 gate 상태: CLOSED / RESEARCH / CANDIDATE / PROMOTED
- 역사적 데이터만으로 PROMOTED 금지
- 300~1230회 Walk-forward 고정
- Block A/B/C 고정
- Joint Log Loss를 1차 지표로 고정
- Brier·Calibration·후보 일치성과를 보조지표로 고정
- 균등 null 1,000개와 planted positive-control 정의
- Moving-block bootstrap·Holm 보정 정의
- 동일 입력 결정론적 seed와 출력 해시 정의

## 5. Gate 2-1 검토 필요사항

사용자가 확인할 핵심:

1. M0~M3 역할이 기존 논의와 일치하는지
2. 최근 신호의 지속과 반전이 독립 가설로 유지되는지
3. 신호가 없을 때 최종분포가 M0인지
4. 역사적 백테스트만으로 검증완료라고 하지 않는지
5. 실제 미래예측 공개가 공식 검증 이후인지
6. 후보 5세트에서 정확히 6개 적중확률이 1순위인지

## 6. Gate 2-2 다음 작업

Gate 2-1 승인 후 새 구현 브랜치에서 진행합니다.

1. `engine/` 패키지 골격
2. 데이터 cutoff assertion
3. 피처 스냅샷
4. elementary symmetric polynomial DP
5. M0 분포
6. M1~M3 sub-expert
7. 순차 가중치
8. randomness gate 상태기계
9. 후보 5세트 최적화
10. 출력 JSON·해시
11. 단위테스트와 CI

Gate 2-2에서는 아직 전체 역사적 백테스트나 UI를 완료하지 않습니다. 먼저 수학적 정합성과 합성 smoke test를 검증합니다.

## 7. 주요 위험

- 공식 데이터 잠금 미완료
- 역사적 데이터가 완전한 untouched holdout이 아님
- 작은 우연 패턴이 sub-expert weight를 움직일 위험
- 990개 pair interaction의 과적합 위험
- 후보 5세트 다양화가 1차 확률목표를 침해할 위험
- 계산속도를 이유로 조합분포를 독립 Bernoulli 근사로 바꿀 위험

## 8. 작업 재개 시 필수 순서

1. `AGENTS.md`
2. `docs/ALGORITHM_SPEC.md`
3. `docs/NON_NEGOTIABLES.md`
4. `docs/GATE2_ENGINE_SPEC.md`
5. `docs/GATE2_FEATURE_CONTRACT.md`
6. `docs/GATE2_BACKTEST_PROTOCOL.md`
7. `docs/GATE2_IMPLEMENTATION_PLAN.md`
8. `docs/GATE2_REVIEW_GUIDE.md`
9. 본 파일
10. `handoff/DECISION_LOG.md`
11. `handoff/WORK_LOG.md`

## 9. 주요 링크

- 저장소: `https://github.com/dpes31/predictive-algorithm`
- Gate 1 Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/2`
- Gate 2-1 Issue: `https://github.com/dpes31/predictive-algorithm/issues/3`
- Gate 2-1 Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/4`
- Gate 2-1 branch: `feature/gate2-engine-spec`
