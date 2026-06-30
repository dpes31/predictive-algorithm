# AGENTS.md

이 문서는 Codex 및 모든 AI 개발 에이전트가 작업 시작 전에 반드시 읽어야 하는 최상위 운영 규칙입니다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 제품과 검증대상은 로또번호 예측기다.

핵심 원칙:

- M0 균등 무작위 기준모형 유지
- M1 지속, M2 반전, M3 구조변화 유지
- M4 물리·운영 증거모형은 승인 후 추가
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
13. `handoff/GATE2_PHYSICAL_PROGRESS.md`
14. `handoff/PROJECT_HANDOFF.md`
15. `handoff/DECISION_LOG.md`

## 3. 현재 Gate

- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- Gate 2-3P-1: 명세 완료, 사용자 검토 대기
- Gate 2-3P-2: 구현 차단
- Gate 2-3P-3: 재검증 차단
- Gate P-1: 실제 메타데이터 파일럿 차단
- Gate 2-4P: 실제 Walk-forward 차단
- 모바일 UI: 차단

현재 브랜치: `feature/gate2-physical-evidence-spec`

## 4. Gate 2-3P-1 제안 변경

사용자 승인 대기:

1. M4 물리·운영 증거모형 추가
2. M3를 단일 maxT omnibus 검정으로 변경
3. 모델 버전 `3.0.0-research`
4. Feature contract `2.0.0`
5. Physical metadata schema `1.0.0`

승인 전 Python 엔진 코드를 변경하지 않는다.

## 5. M4 입력 원칙

- target draw 이전에 알 수 있는 데이터만 사용
- 현재 회차 배출순서는 결과이므로 입력 금지
- 본추첨 후 공개된 정보를 사전 데이터처럼 사용 금지
- 출처·observed_at·available_before_draw·confidence 필수
- 결측·inferred는 기본 기여 0
- 장비·볼 교체 후 과거 효과 자동 감쇠
- 데이터 완전성·신뢰도 미달 시 M4 비중 0

## 6. M3 maxT 원칙

- 사전등록된 raw shift·CUSUM·entropy deviation만 사용
- 전체 forecast origin 최대통계량으로 familywise null 보정
- 별도 Holm 중복 적용 금지
- calibration 최소 10,000
- alpha 0.001 유지

## 7. 변경 금지

사용자 승인 없이 다음을 변경하지 않는다.

- M0 제거
- M1·M2·M3 역할 변경
- M4 구현
- M3 maxT 구현
- 모델 버전 증가
- 통과 기준 완화
- 실패 시나리오 삭제
- 실제 과거번호 Walk-forward
- 실제 미래후보 공개
- Pair interaction 예측 활성화
- 모바일 UI·Supabase 개발

## 8. 브랜치와 PR

- main 직접 개발 금지
- 기능별 별도 브랜치
- Draft PR
- 사용자 검토 전 병합 금지
- 기존 실패 버전과 보고서 덮어쓰기 금지

## 9. 연구·공개정책

- 연구 출력: `research_only: true`
- 공개 허용: `public_release_allowed: false`
- 공식 데이터 검증 전 잠금·공개 금지
- 합성검증 통과는 실제 예측력 증명이 아님
- 실제 메타데이터 Walk-forward 통과 전 확률 우위 주장 금지

## 10. 작업 종료 시 누적

- `handoff/PROJECT_HANDOFF.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 결정사항 로그
- Draft PR 설명
- 테스트·실패·차단사항

## 11. 사용자 보고

- 현재 단계가 개발인지 검증인지 명시
- 단계별 진척도 표시
- 완료·미착수·차단 구분
- 실제 번호 5세트 출력 구조 유지 여부 명시
- 다음 승인사항 한 번에 제시
