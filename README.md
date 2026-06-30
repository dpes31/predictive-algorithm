# Predictive Algorithm

과거 로또 6/45 데이터와 이후 누적 데이터를 기반으로 다음 회차의 **6개 번호 조합 5세트**를 생성하고, 추첨 전에 예측을 잠근 뒤 실제 결과와 비교·검증하는 연구형 확률예측 프로젝트입니다.

## 현재 단계

- Gate 0: 승인 완료
- Gate 1: 데이터·아카이브 구현 완료, 사용자 검토 대기
- Gate 2: 미착수

## Gate 1 현재 상태

- 데이터 범위: 1~1230회
- 구조·체크섬·파생 아카이브 테스트: 통과
- 동일 입력 재생성 SHA 검사: 통과
- 과거번호 검색·연도 필터·정렬·원형 번호 UI: 구현
- 공식 자동 대조: 기존 동행복권 JSON 엔드포인트가 응답하지 않아 미완료
- 현재 검증상태: 1,230개 모두 `auto_checked`, 잠금 해제

공식 대조 전 데이터를 `verified`로 과장하지 않습니다. 자세한 내용은 [`docs/GATE1_REVIEW_GUIDE.md`](docs/GATE1_REVIEW_GUIDE.md)와 [`reports/gate1_summary.md`](reports/gate1_summary.md)를 확인하십시오.

## 핵심 원칙

- 단순 출현빈도 추천기로 축소하지 않음
- M0 균등 무작위, M1 지속, M2 반전, M3 구조변화를 동시에 평가
- 무작위성 검정을 비균등모형 활성화 게이트로 사용
- 신호가 없으면 균등모형으로 복귀
- 사용자에게 95% 불확실성 구간 표시
- 99.9%는 모델 승격 기준이며 적중확률 표현이 아님
- 미래 데이터 누출 금지
- 모든 실패 결과와 이전 모델 버전 보존

## AI 에이전트 필수 읽기 순서

Codex 또는 다른 AI 에이전트는 코드 변경 전에 다음 문서를 순서대로 읽어야 합니다.

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/ALGORITHM_SPEC.md`](docs/ALGORITHM_SPEC.md)
3. [`docs/NON_NEGOTIABLES.md`](docs/NON_NEGOTIABLES.md)
4. [`docs/DATA_POLICY.md`](docs/DATA_POLICY.md)
5. [`docs/VALIDATION_PROTOCOL.md`](docs/VALIDATION_PROTOCOL.md)
6. [`handoff/PROJECT_HANDOFF.md`](handoff/PROJECT_HANDOFF.md)
7. [`handoff/DECISION_LOG.md`](handoff/DECISION_LOG.md)
8. [`handoff/WORK_LOG.md`](handoff/WORK_LOG.md)

## 비개발자 검토 문서

- [`docs/GATE1_REVIEW_GUIDE.md`](docs/GATE1_REVIEW_GUIDE.md): 실행·검색·필터·상태표시 검토법과 Gate 2 데이터 사용정책 선택
- [`reports/gate1_summary.md`](reports/gate1_summary.md): 자동 무결성 검사 결과
- [`reports/secondary_crosscheck.md`](reports/secondary_crosscheck.md): 보조 교차검증과 한계

## 개발 운영

- `main` 직접 개발 금지
- 기능 브랜치와 Draft PR 사용
- 사용자 검토 전 임의 병합 금지
- 모든 작업 종료 시 `handoff/` 문서 갱신
- 핵심 수식 변경은 사용자 승인과 모델 버전 증가 필수

## 개발 Gate

1. **Gate 0** — 계획·수식·운영 정책 승인
2. **Gate 1** — 데이터 무결성·과거 회차 아카이브
3. **Gate 2** — 예측 엔진 v1·walk-forward 검증
4. **Gate 3** — HTML UX·5세트 결과 화면
5. **Gate 4** — 수식과 코드 일치 감사·사용자 검수
6. **Gate 5** — Supabase 이전·자동 수집 및 평가

## 관련 링크

- [MVP 계획 및 알고리즘 고정 명세 — Issue #1](https://github.com/dpes31/predictive-algorithm/issues/1)
- [Gate 1 Draft PR #2](https://github.com/dpes31/predictive-algorithm/pull/2)
