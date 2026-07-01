# Project Handoff

최종 갱신일: 2026-07-01  
현재 작업: **Gate 1~Gate 2-3P-R3M-3-2 저장소 이력 재감사·복원 완료**  
현재 브랜치: `docs/full-history-recovery-audit`  
기준 브랜치: `feature/gate2p-m4f2-source-access-spec`  
현재 Draft PR: #37

## 현재 상태

```text
Gate 1 archive = PRESENT / STRUCTURALLY PASSED / AUTO_CHECKED
M0-M3 core = IMPLEMENTED
M4 3.0 engine = IMPLEMENTED / SYNTHETIC VALIDATION NOT PASSED
4.0 correction engine = IMPLEMENTED / NO_ELIGIBLE_CONFIG
5.0 oracle = PASS
5.0 past-only predictable group = FAIL / FROZEN
final distribution = M0_ONLY
external contact path = OPTIONAL_DEFERRED
CAL / SEALED / actual M4 walk-forward = NOT RUN
main merge = NOT PERFORMED
```

상세 감사기록: `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`

## Gate 1 데이터·웹 아카이브

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

검증:

```text
data version = draws-2026.06.27-r1
range = 1..1230
records = 1230
missing = 0
duplicates = 0
structural errors = 0
date gaps = 0
SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
deterministic rebuild = true
```

제한:

- 전체 1,230건은 `auto_checked`
- official endpoint unavailable로 `official_matches=0`
- source는 `smok95_lotto_mirror`
- 구조·checksum은 통과했지만 official verified/locked는 아님

## 전체 Gate 이력

| Gate | PR | 결과 |
|---|---:|---|
| Gate 1 | #2 | 1~1230 데이터·HTML 아카이브 구축 |
| Gate 2-1 | #4 | exact 6-of-45·M0~M3·검증 명세 |
| Gate 2-2 | #6 | Python core·5세트 생성기 구현 |
| Gate 2-3 | #8 | synthetic validation NOT PASSED |
| Gate 2-3R | #9 | synthetic rerun NOT PASSED |
| Gate 2-3P-1 | #11 | M4 물리변수 명세 |
| Gate 2-3P-2 | #13 | M4 엔진 구현·CI PASS |
| Gate 2-3P-3 | #15 | 37,000 series 검증 NOT PASSED |
| Gate 2-3P-R1 | #17 | 4.0 correction 명세 |
| Gate 2-3P-R2 | #19 | 4.0 engine·CI PASS |
| Gate 2-3P-R3 | #22 | NO_ELIGIBLE_CONFIG |
| Gate 2-3P-R3M-1 | #27 | 5.0 수학 교정 명세 |
| Gate 2-3P-R3M-2 | #29 | Oracle DEV PASS |
| Gate 2-3P-R3M-3-1 | #31 | predictable-group 명세 |
| Gate 2-3P-R3M-3-2 | #32 | PREDICTABLE_GROUP_FAIL |

모든 PR은 Draft·미병합으로 보존됐다.

## M4 실제 구현과 물리변수 구분

PR #13 실제 구현:

- physical metadata validator
- source·timestamp·pre-draw availability·confidence 검증
- 현재 결과 field와 post-draw 누출 차단
- completeness·reliability·traceability 계산
- contextual M4 expert와 strong shrinkage
- 지원 부족 시 exact M0 fallback
- M0~M4 통합과 M4 10% cap
- synthetic generator·smoke·unit tests

| 변수 | 저장소 기준 상태 |
|---|---|
| 추첨기 ID·세대·regime | 엔진 구현 + synthetic |
| 볼 세트 ID·세대·교체 regime | 엔진 구현 + synthetic |
| 5개 볼 세트 B1~B5 | synthetic + generic engine context |
| 추첨기×볼 세트 | 엔진 구현 + synthetic |
| 정비·정비 후 회차 | schema / generic 4.0 support, 실제 data 없음 |
| 볼 사용 횟수 | schema only |
| 공 무게 4g·허용오차 | schema only, 번호별 질량 계산 없음 |
| 공 직경·구형도·마모 | schema only |
| 온도·습도·기압 | schema + temporary-environment synthetic |
| 항온항습 유지 | 가설·synthetic 수준 |
| 혼합시간·공기압 | schema only |
| 사전 테스트 condition | schema + shared/independent synthetic |
| 정확히 9회 테스트 | 전용 숫자 입력 구현 없음 |
| 과거 배출순서 | schema only |
| 초단위·고속영상 | 미구현 |
| 결측·ID오류·post-draw 오류 | validation 구현 |

일반 규격을 회차별 실측값으로 표현하지 않는다.

## 3.0 전체 합성검증

PR #15:

```text
total series = 37,000
proxy false activation upper = 0.205288% > 0.2%
M3 false activation = 0.160000% > 0.1%
irrelevant metadata activation = 0.120048% > 0.1%
```

Lift 1.25 strict detection:

- ball set 0.8%
- machine 24.2%
- machine×ball 0.8%
- regime reversal 0.0%
- temporary environment 0.0%
- pretest shared 0.4%
- target 80%

판정: `NOT PASSED`. 실행오류가 아니라 통계기준 미달이다.

## 4.0 교정 이력

PR #17 명세:

- field-level e-process
- stable/transient family
- partial pooling
- timestamp/result global veto
- restart-mixture M3
- activation/deactivation 1000/100
- process life 208
- DEV/CAL/SEALED 분리

PR #19 구현:

- model `4.0.0-research`
- verified head `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow `28483871565` success

PR #22 DEV:

```text
81 configs
P4 lift 1.25
200 × 1230 draws
M3 activation 0/200
max e 1.2128703085422197
eligible config none
```

잠금:

- implementation `f07ac19c1871498cdc953ee9bd34c31b52e0947b`
- workflow `28489870505`
- report hash `f9947423f47ced82004577c81fab3f85b6d3f668f130e4651a2a3773003c5bf4`
- lock hash `db8527b145c1368b7500585358e152ea24954ffa80a8bf33949890d53059cfbf`
- decision `NO_ELIGIBLE_CONFIG`

## 5.0 교정 이력

PR #27:

- threshold 1000·208 life·lift 1.25·80% power 비양립 분석
- pre-activation 520과 post-activation 208 분리
- exact group LR·predict-then-bet

PR #29 Oracle PASS:

- implementation `37fd815220ccd363f019f3798366a2060872e073`
- workflow `28493929179`
- tests 96 PASS
- activation 91.85%, median delay 241
- null false activation 0.08%, upper 0.1443001%
- report hash `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

Oracle PASS는 true group과 change point를 아는 수학적 상한이다.

PR #31/#32 past-only learner:

- 520 window, half-life 104, prior 52
- 260 warmup + five 52-folds
- sizes 6/10/15, 52-draw freeze
- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests 105 PASS
- availability 33.66%, activation 1.35%, direction 78.6839%
- Log Loss/Brier delta 음수
- null safety PASS
- decision `PREDICTABLE_GROUP_FAIL`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

Past-only predictable-group 경로는 동결한다.

## 실제 Walk-forward 상태

완료:

- 1~1230 데이터 아카이브
- exact probability engine
- 5세트 생성기
- synthetic M4 validation

미완료:

- 실제 회차별 machine·ball-set·공 측정·환경 metadata를 결합한 1~1230 walk-forward
- 실제 물리변수 기반 예측력 검증

## 외부기관 접촉 경로

```text
M4F-1/M4F-2 docs = optional reference
M4F-2A = OPTIONAL_DEFERRED
external contact = STOPPED
requests sent = false
data received = false
```

요청서 초안은 참고문서로만 보존하고 기본 개발경로에서 제외한다.

## 현재 금지

- 외부기관 접촉·발송
- 신규 Python 구현
- 추가 DEV
- 기준 완화 또는 실패 seed 삭제
- CAL·SEALED
- 실제 번호 Walk-forward
- 모바일 UI·Supabase
- main 병합

## 다음 단계

이번 요청 범위는 저장소 이력 재감사와 문서 복원까지다. 신규 개발·검증은 사용자 별도 지시 전 진행하지 않는다.
