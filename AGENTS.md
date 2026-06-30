# AGENTS.md

이 문서는 Codex 및 모든 AI 개발 에이전트가 작업 시작 전에 반드시 읽어야 하는 최상위 운영 규칙입니다.

## 1. 프로젝트 목적

이 프로젝트는 로또 6/45 데이터를 이용해 다음 회차의 6개 번호 조합 5세트를 생성하고, 사전 잠금 후 실제 결과와 비교하는 연구형 확률예측 시스템입니다.

핵심 원칙:

- M0 균등 무작위 기준모형을 항상 유지
- M1 지속, M2 반전, M3 구조변화 가설을 분리 평가
- 신호가 확인되지 않으면 M0으로 복귀
- 미래 데이터 누출 금지
- 동일 입력·버전·seed에서 동일 결과 재현
- 실패와 불확실성을 삭제하거나 은폐하지 않음

## 2. 작업 전 필수 읽기 순서

1. `docs/ALGORITHM_SPEC.md`
2. `docs/NON_NEGOTIABLES.md`
3. `docs/DATA_POLICY.md`
4. `docs/VALIDATION_PROTOCOL.md`
5. `docs/GATE2_ENGINE_SPEC.md`
6. `docs/GATE2_FEATURE_CONTRACT.md`
7. `docs/GATE2_BACKTEST_PROTOCOL.md`
8. `docs/GATE2_IMPLEMENTATION_PLAN.md`
9. `docs/GATE2_3R_APPROVAL.md`
10. `docs/GATE2_3R_MODEL_AMENDMENT.md`
11. `reports/gate2_3_full_summary.md`
12. `reports/gate2_3r_full_summary.md`
13. `reports/gate2_3r_full_summary.json`
14. `handoff/PROJECT_HANDOFF.md`
15. `handoff/DECISION_LOG.md`
16. `handoff/GATE2_3R_WORK_LOG.md`

읽지 않고 코드를 변경하지 마십시오.

## 3. 현재 Gate 상태

- Gate 0: 완료
- Gate 1: 사용자 승인 완료
- Gate 2-1: 사용자 승인 완료
- Gate 2-2: 사용자 승인 완료
- Gate 2-3: NOT PASSED
- Gate 2-3R: **NOT PASSED**
- Gate 2-4: **차단**
- Gate 2-5: 차단
- Gate 3: 차단
- Gate 4: 미진행
- Gate 5: 미진행

현재 모델 버전은 `2.1.0-research`, Gate 상태는 `RESEARCH`, 최종 적용분포는 `M0 only`입니다.

## 4. Gate 2-3R 결과

- Null proxy false activation: 4/1,000 = 0.4%, 기준 0.1% 초과
- 지속 과정 M1 엄격 탐지: 100%
- 반전 과정 M2 엄격 탐지: 71%
- 고정 번호 편향 2%·5%·10% 엄격 탐지: 0%
- M3 구조변화·일시 편향 활성화: 0%
- Pair factor 3.0 사전지정 Pair 탐지: 22%
- 80% power 최소 fixed-bias 또는 Pair 효과크기: 없음
- 결과 해시: `ec57a01e7781d5679cc8fc1b1c146055b06b6836740924cfbb0f1bfd6bef15c6`

## 5. M3 구조적 차단

현재 계약은 다음과 같습니다.

```text
Null calibration = 1,000
최소 plus-one empirical p = 1/1,001
Holm tests = 4
최소 adjusted p = 4/1,001 = 0.003996004
alpha = 0.001
```

따라서 현재 계약에서는 M3가 수학적으로 활성화될 수 없습니다. 이 문제를 해결하려면 사용자 승인을 받은 새 검정 계약이 필요합니다.

## 6. 브랜치 및 PR 원칙

- `main`에 직접 개발하지 않습니다.
- 작업별 별도 브랜치와 Draft PR을 사용합니다.
- 사용자 검토 전 병합하지 않습니다.
- 검증된 브랜치·태그·모델 버전을 덮어쓰지 않습니다.
- 현재 브랜치: `feature/gate2-synthetic-validation-r1`
- 현재 Draft PR: #9
- Gate 2-3 및 2-3R 실패 결과를 삭제하지 않습니다.

## 7. 변경 금지

사용자 승인 없이 다음을 변경하지 않습니다.

- M0 제거 또는 비중 하한 완화
- M1·M2·M3 역할 변경
- temperature grid 변경
- alpha 0.001 완화
- positive-control 효과크기·변화시점 삭제 또는 변경
- 실패 seed 제외
- pair interaction 예측 활성화
- 실제 과거번호 Walk-forward 실행
- 1231회 또는 이후 실제 후보 생성
- UI·Supabase 개발 진행
- `통계적 우위 없음` 표시 제거

## 8. 다음 변경에 필요한 승인

1. M3 검정 해상도 해결
   - calibration 최소 3,999개 이상 또는
   - 사전등록 단일 omnibus/maxT 검정
2. Gate proxy 오탐 제어 강화
3. 장기 고정편향 탐지기 분리 여부
4. 반전 과정 71% 처리 기준
5. Pair 진단 유지·폐기·재설계 결정
6. 새 모델 버전

코드를 먼저 변경하지 말고 변경 사유, 기존 수식 차이, 기대효과, 과적합 위험, 검증방법, 버전안을 문서화하여 사용자 승인을 받습니다.

## 9. 데이터 및 공개정책

- 공식 확인 전 데이터로 실제 미래예측을 공개하거나 잠그지 않습니다.
- `auto_checked` 데이터는 승인된 연구 범위에서만 사용합니다.
- 모든 연구 출력에는 `research_only: true`, `public_release_allowed: false`를 포함합니다.
- 실제 당첨번호를 HTML·JavaScript·테스트에 중복 하드코딩하지 않습니다.
- pair positive-control의 사전지정 번호쌍 결과를 실제 데이터 pair 선택 근거로 사용하지 않습니다.

## 10. 실행 투명성

Gate 2-3R 전체 수치 실험은 커밋된 수식을 옮긴 결정론적 standalone mirror에서 실행했습니다. 사용 가능한 GitHub 연결 도구로 Actions workflow를 추가·디스패치할 수 없어 GitHub CI 확인은 미완료입니다. 이를 CI 통과 또는 최종 검증 완료로 표현하지 않습니다.

## 11. 작업 종료 시 필수 업데이트

- `handoff/PROJECT_HANDOFF.md`
- `handoff/DECISION_LOG.md` 또는 승인된 별도 결정 기록
- 현재 Gate 작업 로그
- Draft PR 설명
- 실패 결과와 남은 위험

## 12. 비개발자 사용자 보고

작업 완료 보고에는 다음을 명확히 적습니다.

- 무엇을 변경했는지
- 무엇이 개선됐는지
- 무엇이 실패했는지
- Gate 통과 여부
- 실제 데이터 작업이 차단됐는지
- 사용자가 다음으로 승인해야 할 의사결정
