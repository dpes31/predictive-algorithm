# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽고 실제 브랜치·commit·report·lock 상태와 대조한다.

## 1. 프로젝트 목적

대한민국 로또 6/45 다음 회차에 대해 정확히 6개 번호 조합 5세트를 반환하는 재현 가능한 연구형 제품을 개발한다.

두 실행경로를 엄격히 분리한다.

```text
CONTROL_M0        = Product P1 exact M0 기본·rollback 경로
RESEARCH_ENSEMBLE = Algorithm Integration A2 연구 전용 점수경로
```

공통 원칙:

- 미래 데이터 누출 금지
- 동일 data/version/config/seed/registry에서 동일 결과
- 실패 결과, hash, report, lock, rollback 보존
- 사용자 승인 전 다음 Gate 진행 금지
- `main` 직접 작업·병합 금지
- 외부 결과 사이트 접속, 외부기관 문의, 새 출처 탐색 금지
- 사용자가 제공하지 않은 물리변수 수집·추정 금지

## 2. 현재 기준점

```text
current branch = docs/algorithm-integration-a3-evaluation-spec
base branch = feature/product-p1-release-candidate
base commit = 901ececb1add7f55879b6efb744d435fdbc31ced

P1 contract = product-release-candidate-1.0.0
P1 status = P1_ASSEMBLED
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052

A1 contract = research-ensemble-spec-1.0.0
A1 status = A1_SPEC_COMPLETE / MERGED

A2 contract = research-ensemble-implementation-1.0.0
A2 status = A2_IMPLEMENTATION_PASS / MERGED
A2 PR = #48
A2 merge commit = 901ececb1add7f55879b6efb744d435fdbc31ced
A2 rollback mode = CONTROL_M0

A3 contract = research-ensemble-evaluation-spec-1.0.0
A3 status = SPECIFICATION IN PROGRESS
A4 evaluation implementation/execution = NOT AUTHORIZED

actual user hypothesis entries active = 0
actual physical entries active = 0
Walk-forward = NOT RUN
hyperparameter exploration = NOT RUN
HTML / CAL / SEALED / mobile = NOT RUN
main merge = NOT PERFORMED
```

## 3. 작업 전 필수 읽기

1. `AGENTS.md`
2. `handoff/PROJECT_HANDOFF.md`
3. `handoff/ALGORITHM_INTEGRATION_A2_HANDOFF.md`
4. `reports/algorithm_integration_a2_post_merge_state.json`
5. 해당 Gate의 `docs/` 명세
6. 해당 Gate의 report와 lock
7. `reports/product_p1_acceptance.json`
8. `reports/product_p1_acceptance_lock.json`
9. `docs/EXTERNAL_ACCESS_RETIREMENT_POLICY.md`
10. 기존 실패 report·lock과 rollback manifest

A3에서는 추가로 다음을 읽는다.

- `docs/ALGORITHM_INTEGRATION_A1_SPEC.md`
- `docs/ALGORITHM_INTEGRATION_A1_REGISTRIES.md`
- `docs/ALGORITHM_INTEGRATION_A1_ACCEPTANCE.md`
- `reports/algorithm_integration_a1_spec_report.json`
- `reports/algorithm_integration_a1_spec_lock.json`
- `reports/ALGORITHM_INTEGRATION_A2_STATUS.md`
- `reports/algorithm_integration_a2_implementation.json`
- `reports/algorithm_integration_a2_implementation_lock.json`
- `release/algorithm_integration_a2_rollback_manifest.json`

## 4. 잠긴 제품 기준

Product P1:

```text
data range = 1..1230
record count = 1230
data version = draws-2026.06.27-r1
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification status = auto_checked
officially locked = false

default runner = python -m product.run_prediction
final distribution = M0_ONLY
M0=1.0, M1=M2=M3=M4=0.0
statistical_edge=false
reason=no_validated_nonuniform_signal
research_only=true
public_release_allowed=false
```

A2는 Product P1 파일과 잠금을 변경하지 않고 `research_ensemble/`에 격리돼 있다. `CONTROL_M0`는 계속 기본·rollback 경로다.

## 5. A2 구현 기준

```text
implementation contract = research-ensemble-implementation-1.0.0
model version = 6.0.0-research
score contract = score-45-1.0.0
output schema = research-ensemble-output-1.0.0
hypothesis registry = hypothesis-registry-1.0.0
user input registry = user-input-registry-1.0.0
physical adapter = user-physical-adapter-1.0.0
```

고정 상한:

```text
historical total <= 0.60
single hypothesis <= 0.10
hypothesis total <= 0.25
single physical field <= 0.05
physical total <= 0.15
final logit absolute cap = 0.35
```

A2 검증:

- Python 3.11 / 3.12 PASS
- canonical P1 regression PASS
- I1~I24 PASS
- 실제 사용자 entry 0
- synthetic fixture만 사용
- prior failure·lock 변경 0

## 6. A3 허용 범위

A3는 평가를 실행하지 않고 평가계약만 고정한다.

허용:

- CONTROL_M0 대비 RESEARCH_ENSEMBLE 평가 정의
- historical-only와 10개 ablation lane 정의
- target-1 cutoff와 고정 target sequence 정의
- joint log-score 중심 metric hierarchy 정의
- marginal Brier, calibration, stability 보조지표 정의
- 통계판정, 다중비교, 중단규칙 정의
- A4 PASS/FAIL/BLOCKED 기준 정의
- version/hash/report/lock/rollback 요구사항 정의
- 실제 사용자 hypothesis·physical lane 차단정책 정의
- 문서 정합화와 Draft PR 생성

## 7. 현재 금지사항

사용자 별도 승인 전 다음을 수행하지 않는다.

- 평가 Python harness 구현
- 실제 historical Walk-forward 또는 prospective 평가
- hyperparameter·window·threshold·weight 탐색
- 실제 user hypothesis 또는 physical entry 활성화
- 외부 사이트 접속·재시도
- 외부기관 문의·새 출처 탐색
- canonical data 수정
- Product P1 또는 A1·A2 report/lock/hash/rollback 수정·삭제
- HTML 수정·배포
- CAL·SEALED
- 모바일 UI·Supabase
- `main` 병합

## 8. 외부접근 및 과거 P2 처리

PR #45의 `P2_QA_BLOCKED` 결과는 역사적 evidence로 보존한다. 외부접근·공식대조 B2~B5는 알고리즘 개발의 차단조건으로 복원하지 않는다. 기존 데이터가 공식 잠금된 것처럼 표현하지 않는다.

## 9. 현재 Gate 판정 경계

A3 문서·report·lock이 모두 일치하면:

```text
A3_SPEC_COMPLETE
```

이는 평가 통과나 예측력 입증을 의미하지 않는다.

다음 단계는 별도 사용자 승인 후에만 가능한 `Algorithm Integration Gate A4`다.

```text
next contract = research-ensemble-evaluation-implementation-1.0.0
scope = frozen evaluation harness implementation and fixed historical evaluation only
```

A3 승인 전 A4를 구현하거나 실행하지 않는다.
