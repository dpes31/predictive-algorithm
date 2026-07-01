# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽는다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 정확히 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다.

- 신호가 없으면 exact M0
- 미래 데이터 누출 금지
- 동일 data/version/seed에서 동일 결과
- 실패 결과와 hash 보존
- 사용자 승인 전 다음 Gate 진행 금지
- main 직접 개발·병합 금지

## 2. 필수 읽기

1. `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`
2. `docs/MINIMAL_PRODUCT_COMPLETION_ROADMAP.md`
3. `handoff/PROJECT_HANDOFF.md`
4. `reports/data_integrity.json`
5. `reports/gate1_summary.md`
6. `docs/GATE2_ENGINE_SPEC.md`
7. `reports/gate2_3p3_full_summary.md`
8. `reports/gate2_3p_r3_dev_lock.json`
9. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
10. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`

M4F source-access 문서는 선택적 참고자료이며 기본 개발경로가 아니다.

## 3. 현재 상태

현재 브랜치: `docs/minimal-product-completion-roadmap`  
기준 브랜치: `docs/full-history-recovery-audit`  
현재 모델: `5.0.0-research`  
최종 제품분포: `M0 only`

```text
Gate 1 archive = PRESENT / STRUCTURALLY PASSED / AUTO_CHECKED
M0-M3 core = IMPLEMENTED
M4 3.0 engine = IMPLEMENTED / VALIDATION NOT PASSED
4.0 correction engine = IMPLEMENTED / NO_ELIGIBLE_CONFIG
5.0 oracle = PASS
5.0 past-only predictable group = FAIL / FROZEN
external contact = OPTIONAL_DEFERRED / STOPPED
CAL = NOT RUN
SEALED = NOT RUN
actual M4 metadata walk-forward = NOT RUN
main merge = NOT PERFORMED
```

## 4. 제품 정의

외부기관 접촉 없이 현재 완성 가능한 제품은 다음이다.

```text
M0-safe research product
```

필수 출력:

- 정확히 6개 번호 × 5세트
- 세트 중복 없음
- `statistical_edge=false`
- `reason=no_validated_nonuniform_signal`
- data/model/config/prediction hash
- 사용자 표시: `통계적 우위 없음`

M1~M4는 shadow diagnostics로만 보존하며 제품 확률에 반영하지 않는다.

## 5. 구현 완료

### 데이터·아카이브

- 1~1230회 `data/draws.json`
- 누락·중복·구조 오류 0
- SHA-256 `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- deterministic rebuild
- HTML archive

제한: 전체 데이터는 `auto_checked`이며 공식 exact-match 잠금은 미완료다.

### 엔진·출력

- exact 6-of-45 distribution
- exact number marginals
- M0 uniform
- M1/M2/M3 shadow experts
- M4 contextual engine
- deterministic 6개 번호 × 5세트 생성 기반
- prediction hash
- 미래 데이터 hard rejection
- metadata 부족 시 exact M0 fallback

### 연구·검증 인프라

- synthetic null/positive/robustness generators
- CI smoke·unit tests
- DEV/CAL/SEALED namespace 분리
- report·hash lock

## 6. 미완료

- Gate 1 data와 최종 safe engine을 한 release-candidate branch에서 조립
- 단일 command/API로 target draw → 5세트 반환
- 최종 JSON output schema 잠금
- official public result 대조·신규 회차 append 정책
- end-to-end product acceptance tests
- 기존 HTML과 runner 결과 연결
- release manifest·rollback·public wording lock

## 7. 검증 실패로 동결

### M4 3.0

PR #15 `NOT PASSED`:

- ball set 0.8%
- machine 24.2%
- machine×ball 0.8%
- regime reversal 0.0%
- temporary environment 0.0%
- pretest shared 0.4%
- target 80%

제품 적용 금지.

### 4.0

PR #22 `NO_ELIGIBLE_CONFIG`:

- 81 configs
- M3 activation 0/200
- max e 1.2128703085422197

임의 config 선택·threshold 완화·R4 진입 금지.

### 5.0 past-only learner

PR #32 `PREDICTABLE_GROUP_FAIL`:

- availability 33.66%
- activation 1.35%
- direction 78.6839%
- Log Loss/Brier delta 음수

window·prior·fold·group size 사후수정 금지.

### 실제값 없는 물리변수

공 무게·직경·구형도·마모, 항온항습, 사전 테스트 9회, 비회차별 장비·볼 교체 설명은 제품 가중치에 직접 사용하지 않는다.

## 8. 최소 잔여 개발단계

외부기관 접촉 없이 제품 완성까지 남은 단계는 4개다.

### P1 — Release-candidate 조립

- canonical data 연결
- exact engine·5세트 생성기 연결
- M0-only 강제
- 단일 runner·output schema 확정

### P2 — 데이터·통합 QA

- 공식 공개결과 대조정책
- end-to-end deterministic test
- five-set contract test
- M0-only scope lock

### P3 — HTML MVP 연결

- target draw
- 5세트
- `통계적 우위 없음`
- version·hash·생성시각

### P4 — Research release lock

- release manifest
- hashes
- acceptance report
- known limitations
- rollback commit
- public wording lock

최종 상태:

```text
PRODUCT_READY_RESEARCH_M0
```

## 9. 제품 완성의 필수조건이 아닌 경로

- 동행복권·MBC 접촉
- 비공개 물리 metadata 수집
- M4F-2A
- 추가 M3/M4 탐색
- CAL·SEALED
- 실제 물리 metadata walk-forward
- 모바일 앱·Supabase

## 10. 현재 금지사항

이번 승인범위에서는 다음을 수행하지 않는다.

- Python 구현
- release-candidate 조립
- 데이터 대조 실행
- product QA 실행
- 실제 Walk-forward
- HTML 수정
- 추가 DEV
- CAL·SEALED
- 모바일 UI
- main 병합

## 11. 다음 Gate

사용자 승인 후에만 `Product Gate P1 — Release-candidate 조립 명세`로 이동한다. P1 승인 전 코드 변경을 시작하지 않는다.
