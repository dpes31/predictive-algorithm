# Full Repository Audit: Gate 1 through Gate 2-3P-R3M-3-2

작성일: 2026-07-01  
상태: 저장소 기준 이력 복원 완료  
작업 브랜치: `docs/full-history-recovery-audit`

## 1. 감사 목적

최신 M4F 문서가 기존 데이터·엔진·검증 이력을 충분히 계승하지 못한 문제를 수정한다. 이 문서는 Gate 1 데이터 아카이브부터 3.0·4.0·5.0 연구모델과 R3M-3-2 실패 잠금까지의 실제 저장소 이력을 복원한다.

외부기관 접촉 경로는 핵심 개발경로에서 제거하고 `OPTIONAL_DEFERRED`로 둔다. 기존 요청서 초안은 미발송 참고문서로만 보존한다.

## 2. Gate 1 데이터와 웹 아카이브

기준 브랜치: `feature/gate1-governance-foundation`  
Draft PR: #2  
Preview: `https://predictive-algorithm-git-feature-gate1-d2743e-dpes31s-projects.vercel.app/app/index.html`

존재 파일:

- `data/draws.json`
- `data/source_manifest.json`
- `data/checksums.sha256`
- `reports/data_integrity.json`
- `reports/gate1_summary.md`
- `app/index.html`
- `app/data/archive_index.json`
- `scripts/build_dataset.py`
- `scripts/validate_draws.py`
- `scripts/build_archive.py`

잠금된 검증 사실:

```text
data version: draws-2026.06.27-r1
range: 1..1230
records: 1230
first draw: 1
last draw: 1230
last date: 2026-06-27
missing draws: 0
duplicate draws: 0
structural errors: 0
structural warnings: 0
date gaps: 0
dataset SHA-256: 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
deterministic rebuild: true
```

중요한 제한:

- 1,230개 레코드는 모두 `auto_checked`다.
- 당시 공식 JSON endpoint가 이용 불가하여 `official_matches=0`이다.
- 원 source는 `smok95_lotto_mirror`로 기록돼 있다.
- 따라서 구조·범위·checksum은 검증됐지만 `officially verified` 또는 `locked`로 표현하지 않는다.

## 3. 전체 개발 이력

| 단계 | PR | 결과 | 실제 수행내용 |
|---|---:|---|---|
| Gate 1 | #2 | 데이터·아카이브 구축 | 1~1230회 canonical JSON, 무결성 보고서, HTML archive, deterministic rebuild |
| Gate 2-1 | #4 | 명세 완료 | M0~M3, exact 6-of-45, 5세트, walk-forward·검증 계약 고정 |
| Gate 2-2 | #6 | 엔진 구현 완료 | exact fixed-size distribution, M0~M3 shadow engine, 미래누출 차단, 5세트 생성기 |
| Gate 2-3 | #8 | NOT PASSED | 최초 synthetic validation 실패 |
| Gate 2-3R | #9 | NOT PASSED | 수정 synthetic rerun 실패, 기존 실패 보존 |
| Gate 2-3P-1 | #11 | 물리변수 명세 완료 | M4 schema, 물리·운영 변수, M3 maxT, null/positive protocol |
| Gate 2-3P-2 | #13 | 구현·CI PASS | M4 metadata validator, contextual expert, leakage barrier, shrinkage, M0 fallback, synthetic generator |
| Gate 2-3P-3 | #15 | NOT PASSED | 37,000 synthetic series 전체 검증, 통계기준 미달 |
| Gate 2-3P-R1 | #17 | 4.0 명세 완료 | e-process, stable/transient family, global veto, restart-mixture M3, 1000/100 hysteresis |
| Gate 2-3P-R2 | #19 | 4.0 구현·CI PASS | field-level e-process, partial pooling, M3/M4 correction engine, 5세트·M0 유지 |
| Gate 2-3P-R3 | #22 | NO_ELIGIBLE_CONFIG | 81 config DEV 평가, M3 0/200 활성, 전 config prune, R4 차단 |
| Gate 2-3P-R3M-1 | #27 | 5.0 수학 명세 완료 | threshold 1000·208 life·lift 1.25 비양립 분석, 520 evidence horizon 분리 |
| Gate 2-3P-R3M-2 | #29 | ORACLE PASS | exact group LR, oracle 520회 DEV, 수학적 상한 가능성 확인 |
| Gate 2-3P-R3M-3-1 | #31 | predictable-group 명세 완료 | 520 window, 260+5x52 CV, sizes 6/10/15, 52 freeze |
| Gate 2-3P-R3M-3-2 | #32 | PREDICTABLE_GROUP_FAIL | past-only learner 구현·DEV-PG, null 안전성 통과·예측효용 실패 |

모든 PR은 Draft·미병합 상태이며 `main`은 변경하지 않았다.

## 4. Gate 2-3P-2 M4 실제 구현 범위

PR #13에서 실제 코드로 구현된 항목:

- `PhysicalDrawMetadata`와 `EvidenceValue`
- source type, status, source URL, observed_at, pre-draw availability, confidence 검증
- 현재회차 당첨번호·보너스·배출순서 field 차단
- metadata completeness, reliability, pre-draw rate, traceability 계산
- target 이전 결과만 사용하는 contextual M4 expert
- 최소 context support와 강한 0 수축
- 품질·지원 미달 시 exact uniform fallback
- exact 6-of-45 distribution과 M0~M4 prediction integration
- M4 candidate weight cap 10%
- deterministic synthetic smoke와 unit tests

3.0 엔진의 실제 active context fields:

- `machine.machine_id`
- `machine.machine_generation`
- `ball_set.ball_set_id`
- `ball_set.ball_generation`
- `regime.machine_regime_id`
- `regime.ball_regime_id`
- `regime.operating_procedure_regime_id`

즉, 엔진은 해당 metadata가 주어질 경우 과거 동일 context의 번호별 포함률을 수축 추정하도록 구현됐다. 실제 회차별 물리 metadata가 적재됐다는 뜻은 아니다.

## 5. 물리변수별 구현 상태

상태 코드:

```text
IMPLEMENTED_ENGINE       실제 엔진 입력·검증·확률경로 존재
SCHEMA_ONLY              문서·필드 계약만 존재
SYNTHETIC_ONLY           가상 효과 시나리오로만 검증
SCHEMA_AND_SYNTHETIC     schema와 가상 시나리오 존재, 실제값 경로 없음
NOT_IMPLEMENTED          전용 계산·실제 데이터 경로 없음
```

| 물리·운영 변수 | 상태 | 저장소 기준 정확한 의미 |
|---|---|---|
| 추첨기 ID | IMPLEMENTED_ENGINE + SYNTHETIC | context field와 확률모형 존재. M1/M2 장비 가상효과 검증. 실제 1~1230회 ID 미적재 |
| 추첨기 세대·regime | IMPLEMENTED_ENGINE + SYNTHETIC | 교체 전후 regime context와 reversal 시나리오 존재 |
| 볼 세트 ID | IMPLEMENTED_ENGINE + SYNTHETIC | generic ID context가 구현됐고 synthetic에서는 5개 세트 B1~B5 사용. 실제 세트 이력 미적재 |
| 볼 세대·교체 regime | IMPLEMENTED_ENGINE + SYNTHETIC | regime field와 방향반전·신호소멸 시나리오 존재 |
| 추첨기 × 볼 세트 | IMPLEMENTED_ENGINE + SYNTHETIC | 3.0 validation의 interaction context 및 4.0의 강하게 수축된 residual 구현. 번호쌍 interaction과는 별개 |
| 정비 이벤트·정비 후 회차 | SCHEMA_ONLY / GENERIC 4.0 SUPPORT | 명세 field 존재. 실제 정비원장과 전용 역사자료 없음 |
| 볼 세트 사용 횟수 | SCHEMA_ONLY | 계약에는 존재하지만 실제 회차별 값과 검증된 입력 없음 |
| 공 무게 4g·허용오차 | SCHEMA_ONLY | 실제 번호별 질량을 읽어 물리확률로 변환하는 코드 없음. 일반 규격을 회차별 실측값으로 대체하지 않도록 명세됨 |
| 공 직경·구형도·마모 | SCHEMA_ONLY | 번호별 실측자료가 있을 때만 후보라는 계약. 전용 계산·실제 데이터 없음 |
| 온도·습도·기압 | SCHEMA_AND_SYNTHETIC | schema field 존재. PR #15에서는 `environment.temperature_band` 가상 context로 temporary effect 검증. 실제 실내 수치 미적재 |
| 항온항습 유지 가정 | SYNTHETIC/ASSUMPTION ONLY | 실제 변동자료가 아니라 효과 상한·무관 시나리오로만 취급 |
| 혼합시간·공기압 설정 | SCHEMA_ONLY | 문서상 field만 존재. 실제 장비 control data 없음 |
| 사전 테스트 횟수·조건 | SCHEMA_AND_SYNTHETIC | `pre_draw_tests.condition_id`와 shared/independent latent 시나리오 존재 |
| 사전 테스트 9회 | NOT IMPLEMENTED AS EXACT VALUE | 9회라는 운영정보를 고정 숫자 입력으로 계산한 엔진 없음. 가상 pretest condition만 검증 |
| 과거 배출순서 | SCHEMA_ONLY | target 이전 순서요약만 허용하는 계약. canonical `draws.json`에는 본번호·보너스 중심이며 순서 전용 history 미잠금 |
| 배출 초단위·고속영상 | NOT_IMPLEMENTED | 자료·parser·feature 없음 |
| 결측·오분류·post-draw 오류 | IMPLEMENTED_VALIDATION | 10/30/50% 결측, 5/15% ID 오분류, post-draw error synthetic robustness 존재 |

## 6. Gate 2-3P-3 전체 합성검증

모델: `3.0.0-research`  
PR: #15  
상태: `NOT PASSED`

실험:

```text
M3 maxT null calibration: 10,000
M4 model null calibration: 4,000
independent null validation: 5,000
positive controls: 12,000
robustness: 6,000
total: 37,000
```

주요 실패:

- proxy false activation: 0.100000%, one-sided upper 0.205288% > 0.2%
- M3 false activation: 0.160000% > 0.1%
- irrelevant metadata activation: 0.120048% > 0.1%
- lift 1.25 strict detection:
  - ball set 0.8%
  - machine 24.2%
  - machine × ball 0.8%
  - regime reversal 0.0%
  - temporary environment 0.0%
  - pretest shared 0.4%
- required detection target: 80%
- post-draw-error activation: 2.6%
- signal-decay M0 return within 208 draws: 65.8% < 80%

실패는 코드 실행 실패가 아니라 사전등록 통계기준 미달이다.

## 7. 4.0 교정 이력

### R1 — PR #17

모델 `4.0.0-research`, feature contract `3.0.0` 명세:

- field-specific prequential likelihood-ratio e-process
- exact-M0 abstention
- stable/transient M4 family 분리
- sparse context partial pooling
- machine × ball-set residual 강한 수축
- post-draw·결과누출 global veto
- restart-mixture M3 change process
- activation/deactivation 1000/100
- transient expiry와 208회 active life
- DEV/CAL/SEALED seed 분리

### R2 — PR #19

Python 구현과 CI 통과:

- verified head `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow `28483871565`
- deterministic smoke·unit tests 통과
- 최종 적용분포 M0-only 유지

### R3 — PR #22

DEV grid 결과:

- combined configs: 81
- P4 regime reversal, lift 1.25
- 200 series × 1230 draws
- M3 activation 0/200
- max e-value 1.2128703085422197
- eligible config 없음
- decision `NO_ELIGIBLE_CONFIG`
- implementation `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow `28489870505`
- report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`

R4는 차단됐다.

## 8. 5.0 교정 이력

### R3M-1 — PR #27

`5.0.0-research` 수학 명세:

- mixture dilution, threshold 1000, 208회 process life, lift 1.25, 80% power의 기존 동시계약이 비양립함을 분석
- pre-activation evidence horizon 520과 post-activation active life 208 분리
- exact 6-of-45 group LR
- predict-then-bet와 primary-hypothesis cap

### R3M-2 — PR #29

Oracle DEV PASS:

- true favored group과 change point를 아는 oracle 상한
- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- tests 96 PASS
- positive activation 91.85%
- median delay 241
- null false activation 0.08%
- one-sided 95% upper 0.1443001%
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

Oracle PASS는 실제 group을 과거번호로 예측할 수 있다는 뜻이 아니다.

### R3M-3-1 — PR #31

Predictable-group contract `1.0.0`:

- trailing 520 draws
- half-life 104
- prior strength 52
- 260 warmup + five 52-draw folds
- group sizes 6/10/15
- 52-draw freeze
- DEV-PG / DEV-PG-CI

### R3M-3-2 — PR #32

Python 구현 및 DEV 결과:

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests 105 PASS
- status `PREDICTABLE_GROUP_FAIL`
- availability 33.66%
- activation 1.35%
- direction accuracy 78.6839%
- mean/lower Log Loss delta 음수
- mean/lower Brier delta 음수
- null false activation 0.01%, upper 0.04743% PASS
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

과거 번호만 사용하는 predictable-group 경로는 동결한다.

## 9. 실제 Walk-forward 상태

구분해야 한다.

- Gate 1의 1~1230회 데이터 아카이브: 존재
- Gate 2-1의 역사적 walk-forward 계약: 존재
- Gate 2-2 exact 엔진과 5세트 생성기: 구현
- M4 synthetic series 기반 validation: 실행
- 1~1230회 실제 번호와 실제 회차별 M4 metadata를 결합한 production-grade walk-forward: 미실행·차단

따라서 “물리변수 엔진과 합성검증까지 개발됐다”는 것은 맞지만, “공 무게·환경 실측값을 1~1230회에 넣은 실제 물리 walk-forward가 완료됐다”는 기록은 없다.

## 10. 외부기관 접촉 경로

```text
M4F-1/M4F-2 documents = preserved as optional reference
M4F-2A request package = OPTIONAL_DEFERRED
external contact = STOPPED
requests sent = false
data received = false
```

동행복권·MBC 요청서는 삭제하지 않지만 기본 다음 단계에서 제거한다. 사용자 별도 명시적 승인 없이는 기관 접촉·발송·수집을 재개하지 않는다.

## 11. 현재 프로젝트 상태

```text
Gate 1 archive = PRESENT / STRUCTURALLY PASSED / AUTO_CHECKED
M0-M3 core = IMPLEMENTED
M4 3.0 engine = IMPLEMENTED / SYNTHETIC VALIDATION NOT PASSED
4.0 correction engine = IMPLEMENTED / NO_ELIGIBLE_CONFIG
5.0 oracle = PASS
5.0 past-only predictable group = FAIL / FROZEN
final distribution = M0_ONLY
external-contact path = OPTIONAL_DEFERRED
CAL = NOT RUN
SEALED = NOT RUN
main merge = NOT PERFORMED
```

## 12. 금지사항

이번 감사 결과로 다음을 실행하지 않는다.

- 외부기관 접촉·요청 발송
- 신규 Python 구현
- 추가 DEV
- 기준·threshold 완화
- 실패 seed·scenario 삭제
- CAL·SEALED
- 실제 번호 Walk-forward
- 모바일 UI
- main 병합
