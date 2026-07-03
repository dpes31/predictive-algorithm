# Project Handoff

최종 갱신일: 2026-07-03  
현재 작업: **Product Closeout Gate C2 내부 Product QA 완료**  
현재 브랜치: `qa/product-closeout-c2-internal`  
기준 브랜치: `feature/product-p1-release-candidate`  
기준 커밋: `2f6d42fad4517b744f33132ad7ad1061678e6340`  
계약: `product-closeout-qa-1.0.0`  
Draft PR: `#53`

## 현재 상태

```text
P1 = P1_ASSEMBLED
A1 = A1_SPEC_COMPLETE / MERGED
A2 = A2_IMPLEMENTATION_PASS / MERGED
A3 = A3_SPEC_COMPLETE / MERGED
A4 = A4_EVALUATION_FAIL / Draft PR #51 preserved
C1 = PRODUCT_CLOSEOUT_SPEC_COMPLETE / MERGED
C2 = PRODUCT_CLOSEOUT_QA_PASS / Draft PR #53

CONTROL_M0 = default and rollback
RESEARCH_ENSEMBLE = research-only / product runtime isolated
actual user hypothesis entries = 0
actual physical entries = 0
next Gate = NOT AUTHORIZED
main merge = NOT PERFORMED
```

## C2 기준점

- evaluated commit: `f14e4fc2fddfc53459a505315db9078cbaf00a28`
- workflow: `28660594719` / run #1
- Python 3.11 two repeats: PASS
- Python 3.12 two repeats: PASS
- cross-runtime reproducibility: PASS
- canonical result hash: `07a3e3986eb888b12963489b6a658f455eb6cd81fd594b5cb7dbb5cf64eb086f`
- decision hash: `308f1650a4f58a7a2fa737a0645bd03d8709fb174cd3566f34ebeb7111e872d8`

## 완료 검증

- data version·range·count·SHA-256
- draw continuity·duplicates·number validity
- target-1 cutoff·future-data block
- JSON Schema positive·11 negative fixtures
- 정확히 5세트 × 6개 번호
- M0-only weights와 고정 disclosure
- RESEARCH_ENSEMBLE runtime isolation
- prediction·schema·config·data·manifest·rollback hash
- P1/A1/A2/A3 및 Draft PR #51 evidence preservation

## 필수 읽기

1. `AGENTS.md`
2. `docs/PRODUCT_CLOSEOUT_M0_SPEC.md`
3. `handoff/PRODUCT_CLOSEOUT_C2_HANDOFF.md`
4. `reports/PRODUCT_CLOSEOUT_C2_STATUS.md`
5. `reports/product_closeout_c2_internal_qa.json`
6. `reports/product_closeout_c2_internal_qa_lock.json`
7. `release/product_closeout_c2_rollback_manifest.json`
8. 기존 P1/A1/A2/A3 및 A4 evidence

## 금지 범위

- Product Closeout Gate C3 또는 HTML 구현
- PR #53 병합
- A4 재평가·parameter 변경
- 실제 hypothesis·physical entry 활성화
- 외부접속·새 데이터 수집
- CAL·SEALED·모바일
- `main` 병합

Draft PR #51은 계속 `OPEN / DRAFT / NOT MERGED` 상태로 보존한다.
