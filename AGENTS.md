# AGENTS.md

이 문서는 Codex 및 모든 AI 개발 에이전트가 작업 시작 전에 반드시 읽어야 하는 최상위 운영 규칙입니다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 제품과 검증대상은 로또번호 예측기다.

핵심 원칙:

- M0 균등 무작위 기준모형 유지
- M1 지속, M2 반전, M3 구조변화 유지
- M4 물리·운영 증거모형 연구계약 보존
- 신호 미확인 시 M0 복귀
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패와 불확실성 보존
- 최종 제품 출력은 6개 번호 × 5세트

## 2. 작업 전 필수 읽기

1. `docs/ALGORITHM_SPEC.md`
2. `docs/NON_NEGOTIABLES.md`
3. `docs/DATA_POLICY.md`
4. `docs/VALIDATION_PROTOCOL.md`
5. `docs/GATE2_ENGINE_SPEC.md`
6. `docs/GATE2_FEATURE_CONTRACT.md`
7. `docs/GATE2_BACKTEST_PROTOCOL.md`
8. `reports/gate2_3_full_summary.md`
9. `reports/gate2_3r_full_summary.md`
10. `docs/GATE2_PHYSICAL_EVIDENCE_SPEC.md`
11. `docs/GATE2_PHYSICAL_DATA_SCHEMA.md`
12. `docs/GATE2_PHYSICAL_VALIDATION_PROTOCOL.md`
13. `docs/GATE2_PHYSICAL_ENGINE_REVIEW.md`
14. `reports/gate2_3p3_full_summary.md`
15. `reports/gate2_3p3_result_manifest.json`
16. `handoff/GATE2_PHYSICAL_PROGRESS.md`
17. `handoff/PROJECT_HANDOFF.md`
18. `handoff/DECISION_LOG_GATE2_PHYSICAL_VALIDATION.md`

## 3. 현재 Gate

- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- Gate 2-3P-1: 사용자 승인 완료
- Gate 2-3P-2: 사용자 승인 완료
- Gate 2-3P-3: **NOT PASSED**
- Gate 2-3P-R: 사용자 결정 대기
- Gate P-1: 실제 메타데이터 파일럿 차단
- Gate 2-4P: 실제 Walk-forward 차단
- 모바일 UI: 차단

현재 브랜치: `feature/gate2p3-validation`  
현재 Draft PR: #15  
현재 모델: `3.0.0-research`  
현재 Gate state: `RESEARCH`  
현재 최종 적용분포: `M0 only`  
현재 deployable M4 weight: `0`

## 4. Gate 2-3P-3 결과

실험 규모:

- maxT calibration 10,000
- model null calibration 4,000
- independent null validation 5,000
- positive controls 12,000
- robustness 6,000
- total 37,000

실행:

- workflow run `28451343507`
- 20 shards and aggregate: success
- report hash `b59cc753eda4058f0b55a685a136da01a327dd6b6b7fc33b10fd4758dfc36948`

판정:

- proxy false activation 0.1%, upper 0.205288% — upper criterion fail
- M3 false activation 0.16% — criterion fail
- lift 1.25 strict detection: all six scenarios below 80%
- strongest machine scenario: 24.2%
- regime-reversal M3 activation: 0.2%
- post-draw-error activation: 2.6%
- signal-decay return within 208 draws: 65.8%

## 5. 결과 해석

- CI/workflow는 성공했다.
- 통계 검증은 실패했다.
- 모든 알고리즘 개발이 불가능하다는 판정이 아니다.
- `3.0.0-research` 구조가 사전등록된 오탐·탐지력 기준을 충족하지 못했다.
- 동일 버전을 재실행하거나 임계값만 완화해서 통과시키지 않는다.

## 6. 사용자 승인 전 금지

- Gate 2-3P-R 구현
- 기존 M4 weight·shrinkage·context 결합 변경
- M3 detector 변경
- 효과크기·통과기준 변경
- 실패 seed·시나리오 삭제
- 동일 검증을 유리한 seed로 반복
- 실제 과거번호 Walk-forward
- 실제 미래후보 공개
- Pair interaction 예측 활성화
- M4 10% cap 완화
- 모바일 UI·Supabase 개발
- `통계적 우위 없음` 표시 제거

## 7. 보정 명세 후보

다음은 진단 후보이며 사용자 승인 전 확정하지 않는다.

- field별 sequential evidence weighting
- null-calibrated sparsity·abstention
- hierarchical partial pooling
- stable-context와 transient-context expert 분리
- invalid timestamp global veto
- M3 change detector 재설계
- explicit signal decay·M0 return
- 신규 모델 버전과 동일 규모 재검증

## 8. 브랜치와 PR

- main 직접 개발 금지
- 기능별 별도 브랜치
- Draft PR
- 사용자 검토 전 병합 금지
- 기존 실패 버전과 보고서 덮어쓰기 금지
- PR #11·#13·#15 미병합 상태 유지

## 9. 연구·공개정책

- 연구 출력: `research_only: true`
- 공개 허용: `public_release_allowed: false`
- 합성검증 실패로 Gate P-1 이동 금지
- 실제 Walk-forward 통과 전 확률 우위 주장 금지
- 실제 후보 5세트 공개 금지

## 10. 다음 사용자 결정

권고: Gate 2-3P-3 NOT PASSED 결과를 승인하고, Gate 2-3P-R 보정 명세 작성 여부를 결정한다.

승인 전 새 알고리즘 코드나 재검증을 실행하지 않는다.

## 11. 작업 종료 시 누적

- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정사항 로그
- Draft PR 설명
- CI run·artifact·failure 기록

## 12. 사용자 보고

- 검증 실행 성공과 모델 통과 여부를 구분
- 단계별 진척도 표시
- 완료·미착수·차단 구분
- 5세트 제품 목표 유지 여부 명시
- 실패 항목과 다음 보정 논리를 수치로 제시
