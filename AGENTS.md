# AGENTS.md

이 문서는 Codex 및 모든 AI 개발 에이전트가 작업 시작 전에 반드시 읽어야 하는 최상위 운영 규칙입니다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 제품과 검증대상은 로또번호 예측기다.

핵심 원칙:

- M0 균등 무작위 기준모형 유지
- M1 지속, M2 반전, M3 구조변화 유지
- M4 물리·운영 증거모형 유지
- 신호 미확인 시 M0 복귀
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패와 불확실성 보존
- 최종 출력은 6개 번호 × 5세트

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
14. `handoff/GATE2_PHYSICAL_PROGRESS.md`
15. `handoff/PROJECT_HANDOFF.md`
16. `handoff/DECISION_LOG_GATE2_PHYSICAL.md`

## 3. 현재 Gate

- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- Gate 2-3P-1: 사용자 승인 완료
- Gate 2-3P-2: 구현 완료, 사용자 검토 대기
- Gate 2-3P-3: 사용자 승인 전 차단
- Gate P-1: 실제 메타데이터 파일럿 차단
- Gate 2-4P: 실제 Walk-forward 차단
- 모바일 UI: 차단

현재 브랜치: `feature/gate2p2-engine`  
현재 Draft PR: #13  
현재 모델: `3.0.0-research`  
현재 Gate state: `RESEARCH`  
현재 최종 적용분포: `M0 only`

## 4. Gate 2-3P-2 구현 상태

완료:

- physical metadata contract·validator
- source·timestamp·pre-draw availability·confidence validation
- current-result leakage 차단
- M4 contextual shrinkage expert
- quality·support 미달 uniform fallback
- M3 single maxT calibrator
- M0~M4 prediction integration
- M4 weight cap 10%
- physical synthetic scenarios
- deterministic smoke·unit tests·CI

최신 성공 workflow:

- run `28444499045`
- head `e9f0dc303f596b8db52f2f6193581978944db401`
- unit tests pass
- physical smoke pass
- research-only contract pass

## 5. M4 입력 원칙

- target draw 이전에 알 수 있는 데이터만 사용
- 현재 회차 배출순서는 결과이므로 입력 금지
- 본추첨 후 공개된 정보를 사전 데이터처럼 사용 금지
- 출처·observed_at·available_before_draw·confidence 필수
- 결측·inferred·unknown은 prediction 기여 0
- metadata 품질 미달 시 uniform fallback
- context support 최소 20
- M4 최종 비중 최대 10%

## 6. M3 maxT 원칙

- 사전등록된 raw shift·CUSUM·entropy deviation만 사용
- 전체 forecast origin 최대통계량으로 familywise null 보정
- 별도 Holm 중복 적용 금지
- calibration 최소 10,000
- alpha 0.001 유지
- calibration 부족 시 M3 비활성

## 7. Gate 2-3P-3 승인 전 금지

- 전체 null·positive 대규모 실행
- 통과 기준 변경
- 효과크기·시나리오 삭제
- 실패 seed 제외
- 실제 과거번호 Walk-forward
- 실제 미래후보 공개
- Pair interaction 예측 활성화
- M4 10% cap 완화
- 모바일 UI·Supabase 개발
- `통계적 우위 없음` 표시 제거

## 8. 브랜치와 PR

- main 직접 개발 금지
- 기능별 별도 브랜치
- Draft PR
- 사용자 검토 전 병합 금지
- 기존 실패 버전과 보고서 덮어쓰기 금지
- PR #11·#13 모두 미병합 상태 유지

## 9. 연구·공개정책

- 연구 출력: `research_only: true`
- 공개 허용: `public_release_allowed: false`
- 합성 smoke는 예측력 증명이 아님
- Gate 2-3P-3 통과 후에도 실제 metadata Walk-forward가 필요함
- 실제 Walk-forward 통과 전 확률 우위 주장 금지

## 10. 다음 승인 후 작업

Gate 2-3P-3:

1. maxT null 10,000
2. model null 4,000
3. independent null 5,000
4. positive scenario·effect size별 500
5. missingness·misclassification·regime robustness
6. strict PASS / NOT PASSED 판정

## 11. 작업 종료 시 누적

- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정사항 로그
- Draft PR 설명
- CI run·artifact·failure 기록

## 12. 사용자 보고

- 현재 단계가 개발인지 검증인지 명시
- 단계별 진척도 표시
- 완료·미착수·차단 구분
- 5세트 출력 유지 여부 명시
- smoke와 통계검증을 구분
- 다음 승인사항 한 번에 제시
