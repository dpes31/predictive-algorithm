# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽는다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 정확히 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다.

- M0 균등 기준 유지
- M1 지속, M2 반전, M3 구조변화, M4 물리·운영 증거 역할 유지
- 근거 부족 시 exact M0
- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패 결과와 불확실성 보존
- 사용자 승인 전 다음 Gate 진행 금지
- main 직접 개발·병합 금지

## 2. 필수 읽기

1. `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`
2. `handoff/PROJECT_HANDOFF.md`
3. `reports/data_integrity.json`
4. `reports/gate1_summary.md`
5. `docs/GATE2_ENGINE_SPEC.md`
6. `docs/GATE2_PHYSICAL_EVIDENCE_SPEC.md`
7. `docs/GATE2_PHYSICAL_DATA_SCHEMA.md`
8. `docs/GATE2_PHYSICAL_VALIDATION_PROTOCOL.md`
9. `reports/gate2_3p3_full_summary.md`
10. `docs/GATE2_PHYSICAL_CORRECTION_SPEC.md`
11. `reports/gate2_3p_r3_dev_lock.json`
12. `docs/GATE2_M3_FEASIBILITY_CORRECTION_SPEC.md`
13. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
14. `docs/GATE2_PREDICTABLE_GROUP_FEASIBILITY_SPEC.md`
15. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`

M4F-1·M4F-2 source-access 문서는 선택적 참고자료이며 기본 다음 단계가 아니다.

## 3. 현재 브랜치와 상태

현재 브랜치: `docs/full-history-recovery-audit`  
기준 브랜치: `feature/gate2p-m4f2-source-access-spec`  
현재 Draft PR: `#37`  
현재 모델: `5.0.0-research`  
Gate state: `RESEARCH`  
최종 적용분포: `M0 only`

```text
Gate 1 archive = PRESENT / STRUCTURALLY PASSED / AUTO_CHECKED
M0-M3 core = IMPLEMENTED
M4 3.0 engine = IMPLEMENTED / SYNTHETIC VALIDATION NOT PASSED
4.0 correction engine = IMPLEMENTED / NO_ELIGIBLE_CONFIG
5.0 oracle = PASS
5.0 past-only predictable group = FAIL / FROZEN
external-contact path = OPTIONAL_DEFERRED
CAL = NOT RUN
SEALED = NOT RUN
actual-number M4 walk-forward = NOT RUN
main merge = NOT PERFORMED
```

## 4. Gate 1 데이터·아카이브

기준 브랜치: `feature/gate1-governance-foundation`  
Draft PR: `#2`

존재:

- `data/draws.json`
- `data/source_manifest.json`
- `data/checksums.sha256`
- `reports/data_integrity.json`
- `reports/gate1_summary.md`
- `app/index.html`
- `app/data/archive_index.json`

검증 결과:

```text
data version = draws-2026.06.27-r1
range = 1..1230
record count = 1230
missing draws = 0
duplicate draws = 0
structural errors = 0
date gaps = 0
SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
deterministic rebuild = true
```

주의:

- 1,230개는 모두 `auto_checked`
- official JSON endpoint unavailable로 `official_matches=0`
- source는 `smok95_lotto_mirror`
- 구조·checksum은 통과했지만 officially verified/locked라고 표현하지 않는다.

## 5. 저장소 기준 전체 이력

| Gate | PR | 상태 |
|---|---:|---|
| Gate 1 | #2 | 1~1230 데이터·HTML 아카이브 구축 |
| Gate 2-1 | #4 | exact 6-of-45·M0~M3·검증 명세 고정 |
| Gate 2-2 | #6 | Python core·5세트 생성기 구현 |
| Gate 2-3 | #8 | synthetic validation NOT PASSED |
| Gate 2-3R | #9 | synthetic rerun NOT PASSED |
| Gate 2-3P-1 | #11 | M4 물리변수 명세 완료 |
| Gate 2-3P-2 | #13 | M4 엔진 구현·CI PASS |
| Gate 2-3P-3 | #15 | 37,000 series 검증 NOT PASSED |
| Gate 2-3P-R1 | #17 | 4.0 correction 명세 완료 |
| Gate 2-3P-R2 | #19 | 4.0 correction engine·CI PASS |
| Gate 2-3P-R3 | #22 | NO_ELIGIBLE_CONFIG |
| Gate 2-3P-R3M-1 | #27 | 5.0 수학적 교정 명세 완료 |
| Gate 2-3P-R3M-2 | #29 | ORACLE PASS |
| Gate 2-3P-R3M-3-1 | #31 | predictable-group 계약 고정 |
| Gate 2-3P-R3M-3-2 | #32 | PREDICTABLE_GROUP_FAIL |

모든 PR은 Draft·미병합으로 보존한다.

## 6. M4 3.0 실제 구현 범위

PR #13에서 코드로 구현됨:

- `PhysicalDrawMetadata` / `EvidenceValue`
- source·상태·observed_at·pre-draw availability·confidence 검증
- 당첨번호·보너스·현재 배출순서 field 차단
- completeness·reliability·traceability 계산
- target 이전 결과만 사용하는 contextual M4 expert
- 최소 context support와 강한 0 수축
- 품질·지원 미달 exact M0 fallback
- exact 6-of-45와 M0~M4 통합
- M4 후보비중 상한 10%
- synthetic generator·deterministic smoke·unit tests

3.0 active context fields:

- machine ID·generation
- ball-set ID·generation
- machine/ball/operation regime ID

실제 회차별 metadata가 적재됐다는 뜻은 아니다.

## 7. 물리변수 구현 분류

```text
IMPLEMENTED_ENGINE   실제 입력·검증·확률경로 존재
SCHEMA_ONLY          문서·필드 계약만 존재
SYNTHETIC_ONLY       가상 시나리오로만 검증
SCHEMA_AND_SYNTHETIC schema와 가상 시나리오 존재
NOT_IMPLEMENTED      전용 계산·실제 데이터 경로 없음
```

| 변수 | 상태 |
|---|---|
| 추첨기 ID·세대·regime | IMPLEMENTED_ENGINE + SYNTHETIC |
| 볼 세트 ID·세대·교체 regime | IMPLEMENTED_ENGINE + SYNTHETIC |
| 5개 볼 세트 B1~B5 | SYNTHETIC + generic engine context |
| 추첨기 × 볼 세트 | IMPLEMENTED_ENGINE + SYNTHETIC |
| 정비 이벤트·정비 후 회차 | SCHEMA_ONLY / generic 4.0 support |
| 볼 세트 사용 횟수 | SCHEMA_ONLY |
| 공 무게 4g·허용오차 | SCHEMA_ONLY |
| 공 직경·구형도·마모 | SCHEMA_ONLY |
| 온도·습도·기압 | SCHEMA_AND_SYNTHETIC |
| 항온항습 유지 가정 | SYNTHETIC/ASSUMPTION ONLY |
| 혼합시간·공기압 설정 | SCHEMA_ONLY |
| 사전 테스트 condition | SCHEMA_AND_SYNTHETIC |
| 사전 테스트 정확히 9회 | NOT_IMPLEMENTED AS EXACT VALUE |
| 과거 배출순서 | SCHEMA_ONLY |
| 배출 초단위·고속영상 | NOT_IMPLEMENTED |
| 결측·ID 오분류·post-draw 오류 | IMPLEMENTED_VALIDATION |

일반 규격이나 가설값을 회차별 실측값으로 표현하지 않는다.

## 8. 3.0 전체 검증 잠금

PR #15, model `3.0.0-research`:

```text
total synthetic series = 37,000
proxy false activation = 0.100000%
one-sided upper = 0.205288% > 0.2%
M3 false activation = 0.160000% > 0.1%
irrelevant metadata activation = 0.120048% > 0.1%
```

Lift 1.25 strict detection:

- ball set 0.8%
- machine 24.2%
- machine × ball 0.8%
- regime reversal 0.0%
- temporary environment 0.0%
- pretest shared 0.4%
- target 80%

판정: `NOT PASSED`. 실패는 코드 실행오류가 아니라 통계기준 미달이다.

## 9. 4.0 교정 잠금

### PR #17 — 명세

- field-level e-process
- stable/transient M4
- partial pooling
- global timestamp/result veto
- restart-mixture M3
- activation/deactivation 1000/100
- process life 208
- DEV/CAL/SEALED 분리

### PR #19 — 구현

- model `4.0.0-research`
- verified head `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow `28483871565` PASS

### PR #22 — DEV

```text
81 configs
P4 lift 1.25
200 × 1230 draws
M3 activation = 0/200
max e = 1.2128703085422197
eligible config = none
decision = NO_ELIGIBLE_CONFIG
```

- implementation `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow `28489870505`
- report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

R4는 차단한다.

## 10. 5.0 교정 잠금

### PR #27

- threshold 1000·208 life·lift 1.25·80% power 비양립 분석
- pre-activation 520 / post-activation 208 분리
- exact group LR·predict-then-bet 명세

### PR #29 — Oracle PASS

- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- tests 96 PASS
- positive activation 91.85%
- median delay 241
- null false activation 0.08%
- upper 0.1443001%
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

Oracle PASS는 true group과 change point를 아는 수학적 상한이다.

### PR #31/#32 — Past-only learner

- contract `predictable-group-1.0.0`
- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests 105 PASS
- availability 33.66%
- activation 1.35%
- direction 78.6839%
- Log Loss/Brier delta 음수
- null safety PASS
- decision `PREDICTABLE_GROUP_FAIL`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

Past-only predictable-group 경로는 동결한다.

## 11. 실제 Walk-forward 상태

- 1~1230 데이터 아카이브: 존재
- walk-forward 명세: 존재
- exact 엔진·5세트 생성기: 구현
- M4 synthetic validation: 실행
- 실제 1~1230 번호와 회차별 실측 M4 metadata 결합 walk-forward: 미실행

이를 혼동하지 않는다.

## 12. 외부기관 경로

```text
M4F-1/M4F-2 documents = optional reference
M4F-2A = OPTIONAL_DEFERRED
external contact = STOPPED
requests sent = false
data received = false
```

요청서 초안은 보존하되 기본 다음 단계에서 제외한다.

## 13. 금지사항

별도 사용자 승인 없이 다음을 수행하지 않는다.

- 외부기관 접촉·문서 발송
- 신규 Python 구현
- 추가 DEV
- threshold·기준 완화
- 실패 seed·scenario 삭제
- CAL·SEALED
- 실제 번호 Walk-forward
- 사용자용 미래 후보 공개
- 모바일 UI·Supabase
- main 병합

## 14. 다음 단계

현재 허용된 작업은 이력 감사와 문서 복원뿐이다. 신규 개발·검증 단계는 사용자 별도 지시가 있을 때 다시 정의한다.
