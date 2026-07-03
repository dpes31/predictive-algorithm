# AGENTS.md

모든 작업 전 이 문서와 실제 branch·commit·report·lock 상태를 대조한다.

## 공통 원칙

- 미래 데이터 누출 금지
- 동일 data/version/config/seed에서 재현 가능한 결과
- 실패 결과, hash, report, lock, rollback, workflow history 보존
- 사용자 승인 전 다음 Gate 진행 금지
- `main` 직접 작업·병합 금지
- 외부 결과 사이트 접속, 외부기관 문의, 새 출처 탐색 금지
- 사용자가 제공하지 않은 물리변수 수집·추정 금지

## 현재 기준점

```text
current branch = qa/product-closeout-c2-internal
base branch = feature/product-p1-release-candidate
base commit = 2f6d42fad4517b744f33132ad7ad1061678e6340
Draft PR = #53

P1 = P1_ASSEMBLED
A1 = A1_SPEC_COMPLETE / MERGED
A2 = A2_IMPLEMENTATION_PASS / MERGED
A3 = A3_SPEC_COMPLETE / MERGED
A4 = A4_EVALUATION_FAIL / Draft PR #51 preserved
C1 = PRODUCT_CLOSEOUT_SPEC_COMPLETE / MERGED
C2 = PRODUCT_CLOSEOUT_QA_PASS / Draft PR #53

C2 contract = product-closeout-qa-1.0.0
C2 evaluated implementation = f14e4fc2fddfc53459a505315db9078cbaf00a28
C2 revalidated head = 0886101fe3e6d3ac78dd4c69f5450e2b77097107
C2 workflow = 28660867695 / run #13
P1 regression workflow = 28660867693 / run #55
C2 canonical result hash = 4e5ba17f8316bcb30a827a9a35d744633121cc2afdebab48535af2cb09265854
rollback mode = CONTROL_M0
next Gate authorized = false
```

## 필수 읽기

1. `AGENTS.md`
2. `handoff/PROJECT_HANDOFF.md`
3. `docs/PRODUCT_CLOSEOUT_M0_SPEC.md`
4. `reports/product_closeout_spec_report.json`
5. `reports/product_closeout_spec_lock.json`
6. `handoff/PRODUCT_CLOSEOUT_C2_HANDOFF.md`
7. `reports/PRODUCT_CLOSEOUT_C2_STATUS.md`
8. `reports/product_closeout_c2_internal_qa.json`
9. `reports/product_closeout_c2_internal_qa_lock.json`
10. `release/product_closeout_c2_rollback_manifest.json`
11. Product P1·A1·A2·A3 report, lock, rollback
12. Draft PR #51과 A4 failure evidence

## 잠긴 제품 기준

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

## C2 검증 결과

```text
data identity and validity = PASS
target-1 cutoff and future-data block = PASS
JSON Schema positive and 11 negative fixtures = PASS
five distinct sets x six numbers = PASS
M0-only scope and fixed disclosure = PASS
RESEARCH_ENSEMBLE runtime isolation = PASS
Python 3.11 two repeats = PASS
Python 3.12 two repeats = PASS
cross-runtime reproducibility = PASS
Product P1 regression = PASS
hash, manifest, rollback = PASS
40 immutable paths = PASS
Draft PR #51 preservation = PASS
```

## 보존 대상

- Product P1, A1, A2, A3 report·lock·rollback
- C1 spec·report·lock
- Draft PR #51 and all A4 report·lock·rollback·hash·workflow history
- 기존 M3/M4 및 predictable-group failure evidence
- C2 report·lock·rollback·workflow artifacts

삭제, 재분류, force push, history rewrite를 금지한다.

## 현재 금지사항

사용자 별도 승인 전 다음을 수행하지 않는다.

- Product Closeout Gate C3 HTML MVP
- PR #53 병합
- A4 재평가 또는 parameter 변경
- 실제 hypothesis·physical entry 활성화
- 외부접속 또는 신규 데이터 수집
- canonical data 또는 product runtime 변경
- CAL·SEALED·모바일
- `main` 병합
