# Project Handoff

최종 갱신일: 2026-07-01  
현재 작업: **6개 번호 × 5세트 제품의 완료·미완료·동결 항목 및 최소 잔여단계 재정리 완료**  
현재 브랜치: `docs/minimal-product-completion-roadmap`  
기준 브랜치: `docs/full-history-recovery-audit`

## 1. 현재 상태

```text
Gate 1 archive = PRESENT / STRUCTURALLY PASSED / AUTO_CHECKED
M0-M3 core = IMPLEMENTED
M4 3.0 engine = IMPLEMENTED / VALIDATION NOT PASSED
4.0 correction engine = IMPLEMENTED / NO_ELIGIBLE_CONFIG
5.0 oracle = PASS
5.0 past-only predictable group = FAIL / FROZEN
final distribution = M0_ONLY
external contact = OPTIONAL_DEFERRED / STOPPED
CAL / SEALED / actual M4 walk-forward = NOT RUN
main merge = NOT PERFORMED
```

상세 이력:

- `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`
- `docs/MINIMAL_PRODUCT_COMPLETION_ROADMAP.md`

## 2. 현재 완성 가능한 제품

외부기관 접촉과 검증되지 않은 비균등 모델을 제외하면 다음 제품을 완성할 수 있다.

```text
M0-safe research product
```

제품계약:

- 다음 회차 6개 번호 × 5세트
- 5세트 중복 없음
- 동일 data/model/config/seed에서 동일 결과
- 미래 데이터 미사용
- final distribution exact M0
- `statistical_edge=false`
- `reason=no_validated_nonuniform_signal`
- 화면에 `통계적 우위 없음`
- data/model/config/prediction hash 기록

M1~M4는 shadow diagnostics로만 유지한다.

## 3. 구현 완료 항목

### Gate 1 data and archive

- 1~1230회 canonical JSON
- 1,230개 회차
- 누락·중복·구조 오류 0
- deterministic rebuild
- SHA-256 `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- HTML archive와 index

제한:

- 전체 데이터 `auto_checked`
- official endpoint exact-match 잠금 미완료

### Exact engine and five-set foundation

- exact 6-of-45 fixed-size distribution
- elementary symmetric polynomial normalization
- number marginals
- finite mixtures
- deterministic k-best combinations
- M0 uniform
- 6개 번호 × 5세트 생성 기반
- duplicate-set prevention
- deterministic seed와 prediction hash

### Safety and research modules

- target 이후 데이터 rejection
- RESEARCH에서 M0-only
- metadata 누출 차단
- unsupported context exact M0 fallback
- M1 persistence shadow
- M2 reversal shadow
- M3 regime-change structure
- M4 contextual engine
- 4.0 correction engine
- 5.0 oracle and predictable-group code
- synthetic validation, CI, unit tests, result/hash locks

## 4. 미완료 항목

### 제품 조립

- Gate 1 data와 최종 safe engine의 단일 release-candidate branch
- target draw 입력부터 결과 반환까지 단일 runner/API
- 최종 output JSON schema
- version·hash·fallback reason 통합

### 데이터 운영

- 공식 공개 당첨결과와의 exact-match 정책
- 신규 회차 append·재검증
- mismatch 발생 시 release 차단

### 제품 QA

- canonical data load부터 5세트까지 end-to-end test
- byte-identical reproducibility
- future-data rejection
- five-set uniqueness·range·count
- M0-only scope lock
- shadow model이 제품 확률에 미반영됨을 검증

### 화면·릴리스

- 기존 HTML과 runner 결과 연결
- release manifest
- acceptance report
- known limitations
- rollback commit
- public wording lock

## 5. 검증 실패로 동결

### M4 3.0

PR #15 `NOT PASSED`:

- ball-set detection 0.8%
- machine 24.2%
- machine×ball 0.8%
- regime reversal 0.0%
- temporary environment 0.0%
- pretest shared 0.4%
- target 80%

제품 가중치 적용 금지.

### 4.0 correction

PR #22 `NO_ELIGIBLE_CONFIG`:

- 81 configs
- M3 activation 0/200
- max e 1.2128703085422197

임의 winner 선택, threshold 1000 완화, 208 life 완화, R4 진입 금지.

### 5.0 past-only predictable group

PR #32 `PREDICTABLE_GROUP_FAIL`:

- availability 33.66%
- activation 1.35%
- direction 78.6839%
- Log Loss/Brier delta 음수
- null safety만 PASS

window·half-life·prior·fold·group sizes 사후수정 금지.

### 물리변수 직접 적용

다음은 실제 회차별 입력이 없으므로 제품 가중치에 직접 사용하지 않는다.

- 공 무게·직경·구형도·마모 일반규격
- 항온항습 설명
- 사전 테스트 정확히 9회
- 비회차별 추첨기·볼 교체 설명

## 6. 외부기관 없는 최소 잔여단계

남은 단계는 **4개**다.

### Product Gate P1 — Release-candidate 조립

- Gate 1 canonical data
- Gate 2-2 exact engine·5세트 생성기
- exact M0-only final distribution
- M1~M4 shadow-only
- 단일 runner와 output schema

PASS:

- target draw → 정확히 5세트
- 미래 데이터 0
- `statistical_edge=false`
- prediction hash 재현

### Product Gate P2 — 데이터·통합 QA

- 공식 공개결과 대조정책
- data integrity
- end-to-end deterministic QA
- five-set contract
- M0-only scope lock

PASS:

- 모든 acceptance test PASS
- 동일 입력 byte-identical
- non-uniform product weight 0

### Product Gate P3 — HTML MVP 연결

기존 HTML에 다음만 연결한다.

- target draw
- 5세트
- `통계적 우위 없음`
- model/data version
- prediction hash
- 생성시각

모바일 앱·Supabase·회원·결제·알림은 제외한다.

### Product Gate P4 — Research release lock

- release manifest
- hashes
- acceptance report
- limitations
- frozen failure references
- rollback commit
- public wording

최종 상태:

```text
PRODUCT_READY_RESEARCH_M0
```

이는 5세트 제품동작이 완료됐지만 비균등 예측우위는 인정되지 않았음을 뜻한다.

## 7. 최소 제품경로에서 제외

- 동행복권·MBC 접촉
- M4F-2A
- 비공개 metadata 수집
- 추가 M3/M4 탐색
- CAL·SEALED
- 실제 물리 metadata walk-forward
- 모바일 앱
- Supabase

## 8. 현재 승인범위와 금지

이번 작업은 문서 재정리만 수행했다.

미실행:

- Python 구현
- release-candidate 조립
- 데이터 대조 실행
- product QA
- 실제 Walk-forward
- HTML 수정
- 추가 DEV
- CAL·SEALED
- 모바일 UI
- main 병합

## 9. 다음 단계

사용자 승인 후에만 `Product Gate P1 — Release-candidate 조립 명세`를 작성한다. P1 명세 승인 전 코드 변경을 시작하지 않는다.
