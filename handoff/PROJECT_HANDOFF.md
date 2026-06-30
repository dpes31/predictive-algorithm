# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-2 Python 엔진 골격 구현 완료 · CI 및 사용자 검토 대기**  
현재 작업 브랜치: `feature/gate2-engine-core`  
기준 브랜치: `feature/gate2-engine-spec`  
관련 이슈: `#5 Gate 2-2 Python 예측 엔진 골격 및 수학적 정합성 검증`

## 1. 프로젝트 목적

과거 로또 6/45 데이터와 이후 누적 데이터를 이용해 다음 회차의 6개 번호 조합 5세트를 생성하고, 사전 잠금 후 실제 결과와 비교하여 검증하는 연구형 확률예측 시스템입니다.

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
- 인수인계 Markdown을 작업마다 누적
- Gate 1 승인 완료
- Gate 2-1 명세 승인 완료
- `auto_checked` 데이터는 연구용 백테스트에만 사용
- 실제 미래예측 공개와 데이터 잠금은 공식 검증 완료 후 진행

## 3. 데이터 상태

- 범위: 1~1230회
- 데이터 버전: `draws-2026.06.27-r1`
- 구조·체크섬·파생 데이터·재현성 검사: 통과
- `auto_checked`: 1,230
- `verified`: 0
- `locked`: 0
- 공식 자동 대조: 미완료

## 4. Gate 2-2 구현 완료 항목

### 확률 엔진

- `engine/elementary_symmetric.py`
  - 6차 elementary symmetric polynomial 정규화
  - exact inclusion marginal 계산
- `engine/distributions.py`
  - exact fixed-size product distribution
  - finite mixture distribution
  - k-best 조합 탐색

### 데이터·피처

- 미래 회차 cutoff assertion
- 연구용과 공개용 데이터 상태 분리
- 장기 수축 출현률
- 최근 10·30·52·104회 편차
- 단기·중기 추세
- 미출현 간격
- 52·104회 구조변화 차이
- EWMA
- CUSUM
- 엔트로피 진단
- 결정론적 feature snapshot hash

### M0~M3

- M0 균등모형
- M1 지속 sub-expert 7종
- M2 반전·평균회귀 sub-expert 7종
- M3 구조변화 sub-expert 4종
- M3 change gate는 Gate 2-3 null calibration 전까지 0
- pair interaction은 비활성화

### 가중치·게이트

- bounded sequential loss update
- CLOSED / RESEARCH / CANDIDATE / PROMOTED 상태기계
- RESEARCH 최종분포는 M0=1
- CANDIDATE 비균등 비중 최대 30%
- PROMOTED는 공식 잠금·prospective 조건 필요

### 후보와 출력

- 결정론적 5세트 후보 생성
- 동일 입력·버전·설정 seed
- prediction hash
- `research_only: true`
- `public_release_allowed: false`
- 95% 구간은 Gate 2-3 전까지 `pending`, 임의 생성 금지

## 5. 테스트 및 CI

추가 테스트:

- 작은 상태공간 확률합 1
- 주변확률 합이 pick count와 일치
- M1~M3 주변확률 합 6
- 미래 데이터 차단
- unlocked auto_checked 공개예측 차단
- 피처 유한성·범위·해시 재현
- 한 회차 가중치 폭증 제한
- Gate 상태별 비중 제한
- 후보 5세트 고유성·재현성·커버리지
- 연구용 안전 필드

GitHub Actions:

- Gate 1 데이터 무결성 재검사
- 전체 unittest
- 합성 균등 smoke 2회 실행
- 두 JSON byte 단위 비교
- 연구용 안전 필드 assertion
- smoke artifact 업로드

로컬 독립 실행에서는 18개 초기 테스트가 통과했으며, 저장소에는 추가 계약 테스트를 포함했습니다. 최종 판정은 GitHub Actions 결과를 기준으로 합니다.

## 6. 이번 단계에서 하지 않은 것

- 전체 300~1230회 Walk-forward
- 1,000개 균등 null simulation
- planted positive-control
- M3 change gate calibration
- 95% uncertainty interval
- pair interaction 활성화
- 실제 1231회 공개후보
- HTML UI 연결
- Supabase 연결

## 7. Gate 2-3 다음 작업

Gate 2-2 승인 후 별도 브랜치에서 진행합니다.

1. 균등 null 시계열 반복실험
2. 2%·5%·10% 고정 편향
3. 지속·반전·구조변화 synthetic signal
4. 일시적 편향 후 M0 복귀
5. M3 change gate null calibration
6. 오탐률·탐지력·탐지지연 측정
7. pair interaction 진단만 수행

## 8. 주요 위험

- 현재 M1·M2 계수 규모는 승인 명세의 `±z`를 그대로 사용하므로 Gate 2-3에서 합성 탐지력과 calibration을 반드시 확인해야 함
- 역사적 데이터는 untouched holdout이 아님
- 후보 다양화는 near-tie 범위에서만 허용되어야 함
- 공식 데이터 잠금 전 public prediction 금지
- uncertainty interval은 아직 없음

## 9. 작업 재개 시 필수 순서

1. `AGENTS.md`
2. `docs/ALGORITHM_SPEC.md`
3. `docs/NON_NEGOTIABLES.md`
4. `docs/DATA_POLICY.md`
5. `docs/GATE2_ENGINE_SPEC.md`
6. `docs/GATE2_FEATURE_CONTRACT.md`
7. `docs/GATE2_BACKTEST_PROTOCOL.md`
8. `docs/GATE2_IMPLEMENTATION_PLAN.md`
9. `docs/GATE2_ENGINE_CORE_REVIEW.md`
10. 본 파일
11. `handoff/DECISION_LOG.md`
12. `handoff/WORK_LOG.md`

## 10. 주요 링크

- 저장소: `https://github.com/dpes31/predictive-algorithm`
- Gate 2-1 Issue: `https://github.com/dpes31/predictive-algorithm/issues/3`
- Gate 2-1 Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/4`
- Gate 2-2 Issue: `https://github.com/dpes31/predictive-algorithm/issues/5`
- Gate 2-2 branch: `feature/gate2-engine-core`
