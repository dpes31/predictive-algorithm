# AGENTS.md

이 문서는 Codex 및 모든 AI 개발 에이전트가 작업 시작 전에 반드시 읽어야 하는 최상위 운영 규칙입니다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 제품과 검증대상은 로또번호 예측기다.

핵심 원칙:

- M0 균등 기준 유지
- M1 지속, M2 반전, M3 구조변화, M4 물리·운영 증거 역할 유지
- 신호 미확인 시 M0 복귀
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패와 불확실성 보존
- 최종 제품 출력은 6개 번호 × 5세트

## 2. 필수 읽기

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
13. `reports/gate2_3p3_full_summary.md`
14. `reports/gate2_3p3_result_manifest.json`
15. `docs/GATE2_PHYSICAL_CORRECTION_SPEC.md`
16. `docs/GATE2_PHYSICAL_CORRECTION_VALIDATION.md`
17. `docs/GATE2_PHYSICAL_CORRECTION_IMPLEMENTATION_PLAN.md`
18. `handoff/GATE2_PHYSICAL_PROGRESS.md`
19. `handoff/PROJECT_HANDOFF.md`
20. `handoff/DECISION_LOG_GATE2_PHYSICAL_CORRECTION.md`

## 3. 현재 Gate

- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- Gate 2-3P-1: 승인 완료
- Gate 2-3P-2: 승인 완료
- Gate 2-3P-3: NOT PASSED, 결과 승인 완료
- Gate 2-3P-R1: 명세 완료, 사용자 검토 대기
- Gate 2-3P-R2: 구현 차단
- Gate 2-3P-R3: 개발 검수 차단
- Gate 2-3P-R4: sealed validation 차단
- Gate P-1: 실제 메타데이터 파일럿 차단
- Gate 2-4P: 실제 Walk-forward 차단
- 모바일 UI: 차단

현재 브랜치: `feature/gate2p3-correction-spec`  
현재 Draft PR: #17  
현재 적용 모델: `3.0.0-research` 실패 동결  
제안 모델: `4.0.0-research`  
현재 Gate state: `RESEARCH`  
현재 최종 적용분포: `M0 only`  
현재 deployable M4 weight: `0`

## 4. Gate 2-3P-3 실패 근거

- proxy false activation 0.100000%, upper 0.205288%
- M3 false activation 0.160000%
- irrelevant metadata activation 0.120048%
- lift 1.25 strict detection 0.0%~24.2%
- post-draw-error activation 2.6%
- signal-decay return within 208 draws 65.8%

## 5. Gate 2-3P-R1 제안

### M4

- field별 prequential likelihood-ratio e-process
- stable / transient family 분리
- activation evidence 1000
- deactivation evidence 100
- evidence 부족 시 exact M0 abstention
- hierarchical partial pooling
- interaction residual 강한 수축
- transient restart 13·26·52·104
- M4 deployable cap 10%

### Metadata

다음 하나라도 있으면 M4 global veto:

- post-draw timestamp
- current result field
- schema mismatch
- verified source traceability 없음
- required field contradiction
- future metadata

### M3

- maxT 폐기 제안
- 번호·betting fraction·restart mixture e-process
- trigger 1000 / deactivation 100
- detector와 post-change prediction 분리
- 최대 trigger life 208회

### Validation

- DEV / CAL / SEALED seed 분리
- sealed manifest 사전 commit
- PASS/FAIL 72,000 series
- 한 개 mandatory check 실패 시 NOT PASSED

## 6. 유지 기준

- exact 6-of-45 distribution
- 6개 번호 × 5세트
- M0~M4 상위 역할
- RESEARCH M0-only
- CANDIDATE M0 최소 70%
- M3 최대 10%
- M4 최대 10%
- false activation 0.1%
- one-sided 95% upper 0.2%
- lift 1.25 strict detection 80%
- lift 1.50 strict detection 95%
- 기존 실패 시나리오·효과크기 유지
- Pair interaction 예측 비활성

## 7. 사용자 승인 전 금지

- `4.0.0-research` 코드 구현
- hyperparameter grid 실행
- calibration·sealed validation
- threshold 완화
- 실패 scenario·seed 삭제
- 실제 과거번호 Walk-forward
- 실제 미래후보 공개
- M4 cap 완화
- 모바일 UI·Supabase 개발
- `통계적 우위 없음` 제거

## 8. Version·branch 정책

- `3.0.0-research` 실패결과 덮어쓰기 금지
- main 직접 개발 금지
- 기능별 별도 브랜치와 Draft PR
- 사용자 검토 전 병합 금지
- PR #11·#13·#15·#17 미병합 유지

## 9. 중단 원칙

`4.0.0-research`가 sealed validation에 실패하면 동일 synthetic suite에서 추가 구조·파라미터 튜닝을 중단한다.

새로운 외부 물리데이터가 확보되기 전 비균등 로또 예측연구를 재개하지 않는다.

## 10. 다음 사용자 결정

다음 세 가지 승인 후 R2 구현을 시작한다.

1. Gate 2-3P-R1 보정 아키텍처
2. 모델 버전 `4.0.0-research`
3. sealed validation과 실패 시 중단 원칙

## 11. 작업 종료 시 누적

- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정 로그
- Draft PR 설명
- 테스트·실패·차단사항
