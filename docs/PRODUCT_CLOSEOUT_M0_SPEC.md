# Product Closeout M0 Specification

상태: `SPECIFICATION ONLY / IMPLEMENTATION NOT AUTHORIZED`  
계약: `product-closeout-spec-1.0.0`  
작성일: 2026-07-03  
작업 브랜치: `docs/product-closeout-m0-spec`  
기준 브랜치: `feature/product-p1-release-candidate`  
기준 커밋: `09e6b19f0e351e59982e6167335cbe23fada83b0`

## 1. 목적

A4의 고정 retrospective 평가 실패를 변경하지 않고 알고리즘 연구를 종료한다. 이후 제품 범위를 `CONTROL_M0` 기반의 재현 가능한 로또 6/45 연구형 5세트 생성기로 고정하고, 내부 Product QA·HTML MVP·Research Release Lock을 거쳐 `PRODUCT_READY_RESEARCH_M0` 상태에 도달하기 위한 상세 계약을 사전 등록한다.

이 문서는 명세 전용이다. Python 구현, A4 재평가, parameter 탐색, 실제 hypothesis·물리변수 활성화, 외부접속, HTML 구현, CAL, SEALED, 모바일 및 `main` 병합을 승인하지 않는다.

## 2. 권위 있는 기준점

### 2.1 Product P1

```text
contract = product-release-candidate-1.0.0
status = P1_ASSEMBLED
implementation lock commit = 099d917abd1b635c830fee343a47d3bd23e0c052
default runner = python -m product.run_prediction
final distribution = M0_ONLY
M0=1.0, M1=M2=M3=M4=0.0
statistical_edge=false
reason=no_validated_nonuniform_signal
research_only=true
public_release_allowed=false
```

### 2.2 A4 실패 evidence

A4 evidence는 Draft PR #51과 `feature/algorithm-integration-a4-evaluation` 브랜치에 읽기 전용으로 보존한다. Product Closeout 브랜치로 병합하거나 수정하지 않는다.

```text
A4 result = A4_EVALUATION_FAIL
A4 evaluated commit = ee10a16b8c6259948bc8b2ed77d555452b9ff3a9
A4 workflow = 28653030201 / run #37
A4 canonical result hash = c886f07c2fa7fd01cfa49d2d0e4174d6c9802ac0856aff2fd13d54da44fde3b7
A4 rollback mode = CONTROL_M0
```

A4는 E1~E16 integrity, 미래 데이터 차단, CONTROL_M0 회귀, 10개 lane, equivalence, Python 3.11/3.12 재현성을 통과했지만 joint log-score, marginal Brier, temporal stability 필수 성능기준을 모두 통과하지 못했다.

## 3. 알고리즘 연구 종료 계약

현재 연구 세대의 상태를 다음으로 고정한다.

```text
algorithm_generation = RESEARCH_ENSEMBLE_6.0.0
research_status = FROZEN_FAILED_RESEARCH
promotion_status = NOT_PROMOTED
product_weight = 0
re_evaluation_authorized = false
```

금지사항:

- A4 결과를 보고 window, threshold, weight, half-life, prior, target subset 변경
- 동일 A4 결과를 다른 threshold로 재분류
- A4 실패를 `BLOCKED`, `INCONCLUSIVE`, `CONDITIONAL_PASS`로 변경
- 기존 target 352~1230을 재사용한 사후 모델선택
- A4 report, lock, rollback, hash, workflow history 수정·삭제

향후 새로운 연구는 독립 정보와 별도 contract·branch·사전등록 평가를 가진 새 세대로만 가능하며 Product Closeout의 필수조건이 아니다.

## 4. 제품 정체성

제품의 공식 정의:

```text
product_type = M0-safe research product
product_name_class = reproducible Lotto 6/45 five-set generator
prediction_advantage_claim = prohibited
final_distribution = exact uniform 6-of-45
```

제품이 제공하는 것은 검증된 당첨 예측우위가 아니라 다음이다.

- 정확히 6개 번호로 구성된 5개 후보세트
- 동일 입력에서 재현되는 deterministic output
- data/model/config/prediction identity
- 미래 데이터 차단
- 검증된 비균등 신호가 없다는 명시적 disclosure

## 5. CONTROL_M0 단일 제품분포

모든 제품 output은 다음 가중치만 허용한다.

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

필수 규칙:

1. exact uniform 6-of-45 distribution만 제품 후보생성에 사용한다.
2. 각 6개 조합의 확률은 `1 / C(45,6)`이다.
3. 각 candidate의 `lift_vs_uniform`은 정확히 `1.0`이다.
4. 비균등 score, rank, weight 또는 shadow result가 candidate 선택에 영향을 주면 hard fail이다.
5. M0 생성이 불가능하면 다른 모델로 fallback하지 않고 제품실행을 실패시킨다.

## 6. 6개 번호 × 5세트 출력계약

### 6.1 입력

최소 입력:

```text
target_draw_no
dataset_path or locked dataset identity
fixed product config
fixed seed derivation inputs
generated_at for snapshot metadata
```

각 target `t`에서 마지막 입력 회차는 정확히 `t-1`이어야 한다.

### 6.2 후보세트

출력은 정확히 5개 candidate를 포함한다.

각 candidate:

- 정확히 6개 정수
- 각 번호 범위 1~45
- 세트 내부 중복 0
- 오름차순 정렬
- 5개 세트 상호 중복 0
- rank 1~5 중복 없이 부여
- uniform probability와 lift 1.0 기록

후보 5개 미만 또는 초과, 번호 중복, 범위위반, 동일세트 중복은 release-blocking failure다.

### 6.3 재현성

동일한 다음 입력에서 canonical payload는 byte-identical이어야 한다.

```text
data version and data hash
product contract and config
seed derivation inputs
target_draw_no
generated_at
```

실시간 clock을 자동 삽입해 canonical hash를 바꾸지 않는다. 생성시각은 caller가 명시하거나 canonical QA fixture로 고정한다.

## 7. 필수 상태·문구 계약

제품 JSON과 HTML은 다음 값을 변경 없이 사용한다.

```text
statistical_edge = false
reason = no_validated_nonuniform_signal
research_only = true
public_release_allowed = false
```

한국어 사용자 표시문구:

```text
통계적 우위 없음
검증된 비균등 신호가 없어 균등확률 모델을 사용합니다.
이 결과는 당첨을 예측하거나 당첨확률 향상을 보장하지 않습니다.
```

금지 문구:

- 당첨확률 상승
- 예측 성공률
- AI 추천번호가 일반 선택보다 우월
- 물리·양자·통계 신호로 당첨 가능성 향상
- 검증된 예측기

`public_release_allowed=false`는 Research Release Lock 완료 후에도 별도 공개승인 전 유지한다. `PRODUCT_READY_RESEARCH_M0`는 내부·연구용 제품 완성을 뜻하며 자동 public deployment 승인이 아니다.

## 8. RESEARCH_ENSEMBLE 완전 격리

제품 경로는 `research_ensemble`을 실행하거나 import해 제품값을 만들지 않는다.

필수 격리:

1. 제품 entrypoint는 `python -m product.run_prediction`만 사용한다.
2. product package에서 `research_ensemble` runtime import 금지.
3. M1~M4 score 또는 A4 metric을 후보생성 입력으로 사용 금지.
4. research registry, hypothesis, physical adapter를 제품 payload 입력으로 사용 금지.
5. HTML에서 RESEARCH_ENSEMBLE 후보세트·점수·우위를 표시 금지.
6. A4 evidence는 known limitation과 audit reference로만 연결한다.
7. 연구코드 오류가 CONTROL_M0 제품 실행을 실패시키거나 변경시키면 격리 실패다.

허용되는 연결은 파일경로·commit·hash를 known limitation에 기록하는 정적 reference뿐이다.

## 9. 데이터 상태와 disclosure

현재 고정 데이터:

```text
draw range = 1..1230
record count = 1230
data version = draws-2026.06.27-r1
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification_status = auto_checked
officially_locked = false
```

필수 disclosure:

- 저장소 내 구조·연속성·중복·번호 유효성 검사를 통과했다.
- 공식 공개결과와의 전수 exact-match 잠금은 완료되지 않았다.
- 공식 검증·공식 인증·공식 데이터 잠금으로 표현하지 않는다.
- 외부접근과 B2~B5는 Product Closeout 차단조건으로 복원하지 않는다.
- 신규 외부 출처 탐색 또는 결과 사이트 접근을 수행하지 않는다.

HTML 최소 표시:

```text
데이터 상태: 내부 자동검사 완료(auto_checked)
공식 전수 대조 잠금: 미완료
데이터 범위: 1~1230회
데이터 버전 및 SHA-256
```

## 10. 내부 Product QA 범위

다음 단계의 QA는 외부접속 없이 저장소 내부 artifact만 검증한다.

### 10.1 데이터·입력

- dataset path 존재
- data version, range, count, SHA-256 일치
- draw_no 1~1230 연속성
- duplicate draw 0
- 각 draw 번호 6개·범위 1~45·중복 0
- target-1 cutoff
- target 이상 미래 데이터 접근 0
- malformed·missing·hash mismatch negative test

### 10.2 출력계약

- JSON Schema positive validation
- required field 누락, extra invalid type, 잘못된 번호 negative validation
- candidate 정확히 5개
- 각 candidate 6개
- 번호범위·정렬·중복 검증
- 세트 상호중복 0
- uniform probability와 lift 1.0
- fixed flags·reason 검증

### 10.3 M0-only scope lock

- product weights exact M0-only
- product runtime import graph에 `research_ensemble` 없음
- research registry·physical adapter 접근 0
- shadow score가 candidate 또는 hash에 영향 0
- CONTROL_M0 canonical regression PASS

### 10.4 재현성·hash

- Python 3.11·3.12
- runtime별 최소 2회
- 동일 fixture canonical payload byte-identical
- prediction hash independent recomputation
- schema, config, data, model, manifest hash 정합성
- clock·workflow ID가 prediction identity에 혼입되지 않음

### 10.5 rollback·보존

- P1/A1/A2/A3 report·lock·rollback 불변
- Draft PR #51과 A4 evidence 불변
- 과거 failure workflow history 보존
- rollback anchor·command·scope 검증
- force push·history rewrite 없음

### 10.6 QA 제외항목

- 공식 결과 사이트 대조
- 외부기관 문의
- 예측력 Walk-forward
- A4 재실행
- hyperparameter 탐색
- 실제 hypothesis·physical entry
- HTML 시각검수
- CAL·SEALED

내부 QA 판정:

```text
PRODUCT_CLOSEOUT_QA_PASS
PRODUCT_CLOSEOUT_QA_FAIL
PRODUCT_CLOSEOUT_QA_BLOCKED
```

성능우위는 QA 대상이 아니다. 내부 fixture 실패는 FAIL이며 외부접근 부재는 BLOCKED 사유가 아니다.

## 11. HTML MVP 최소 표시항목

HTML MVP는 계산모델을 새로 구현하지 않고 잠긴 product JSON을 표시한다.

필수 표시:

1. target draw number
2. 정확히 5개 후보세트
3. 각 세트 6개 번호
4. `통계적 우위 없음`
5. M0 fallback 사유 문구
6. model/contract version
7. data version·range·verification status
8. 공식 잠금 미완료 문구
9. prediction hash
10. 생성시각
11. research-only 및 비보장 disclaimer

필수 동작:

- JSON load 실패 시 이전 결과나 임의번호를 표시하지 않음
- 5세트 계약 위반 시 화면을 release-blocking error로 전환
- 모바일 네이티브 앱, 회원, 결제, 알림, Supabase 제외
- RESEARCH_ENSEMBLE score, hot/cold chart, lift 우위 시각화 제외
- 외부 API 호출 제외

## 12. Research Release Lock 요구사항

최종 lock은 최소 다음을 포함한다.

```text
release manifest
product contract version
product runner source hash
schema hash
config hash
data version and hash
canonical output fixture and hash
internal QA report and lock
HTML asset hash and display-contract check
known limitations
A4 failure evidence references
rollback manifest and rollback anchor
public wording lock
```

Known limitations 필수항목:

- 검증된 비균등 예측우위 없음
- A4_EVALUATION_FAIL
- auto_checked 데이터이며 officially_locked=false
- prospective validation 없음
- CAL·SEALED 미실행
- public_release_allowed=false

Release Lock은 기존 failure 결과를 제거하거나 성공으로 재분류할 수 없다.

## 13. 최종 판정기준

다음 C1~C12를 모두 만족하면 최종 상태를 부여한다.

```text
C1  CONTROL_M0 single distribution locked
C2  exactly five distinct six-number sets
C3  target-1 cutoff and future-data block PASS
C4  fixed flags and reason PASS
C5  RESEARCH_ENSEMBLE runtime isolation PASS
C6  dataset auto_checked disclosure visible
C7  officially_locked=false disclosure visible
C8  internal Product QA PASS
C9  HTML MVP display contract PASS
C10 release manifest, hashes and rollback locked
C11 A4 failure evidence preserved and referenced
C12 public wording and research-only limitations locked
```

최종 상태:

```text
PRODUCT_READY_RESEARCH_M0
```

이 판정의 의미:

- 6개 번호 × 5세트 제품동작 완료
- deterministic M0 제품계약 완료
- 비균등 예측우위 미인정
- 당첨확률 향상 주장 금지
- 내부·연구용 release artifact 완성
- 별도 승인 없는 public deployment와 `main` 병합 불가

다음 중 하나면 최종 판정을 부여하지 않는다.

- 내부 QA FAIL/BLOCKED
- 연구모델이 제품후보에 영향
- 데이터 상태 과대표현
- 필수 disclaimer 누락
- hash 또는 rollback 불일치
- A4 evidence 수정·삭제

## 14. 잔여 Gate와 승인 경계

### Closeout Gate C1 — 현재 명세

```text
contract = product-closeout-spec-1.0.0
result = PRODUCT_CLOSEOUT_SPEC_COMPLETE
```

### Closeout Gate C2 — 내부 Product QA

- 구현 변경 없이 기존 P1 제품경로와 contract 검증
- 필요한 경우 QA harness·fixture·report·lock만 별도 승인 후 구현
- HTML 수정 금지

### Closeout Gate C3 — HTML MVP

- C2 PASS 이후 별도 승인
- 잠긴 product JSON 표시만 구현

### Closeout Gate C4 — Research Release Lock

- C2와 C3 PASS 이후 별도 승인
- 최종 manifest·known limitations·rollback·wording lock
- 결과 `PRODUCT_READY_RESEARCH_M0`

각 Gate는 사용자 별도 승인 전 진행하지 않는다.

## 15. 현재 명세 단계 금지사항

- Product Python 코드 수정
- A4 branch·PR·report·lock·rollback 수정 또는 병합
- A4 재평가
- parameter·window·threshold·weight 변경
- 실제 hypothesis·physical entry 활성화
- 외부사이트 접속
- HTML 구현
- CAL·SEALED
- 모바일
- `main` 병합
