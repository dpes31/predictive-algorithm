# Project Handoff

최종 갱신일: 2026-07-03  
현재 작업: **Product Gate P2 데이터·통합 QA 상세 명세 완료**  
현재 브랜치: `docs/product-p2-qa-spec`  
기준 브랜치: `feature/product-p1-release-candidate`  
관련 Issue: #43  
P1 계약: `product-release-candidate-1.0.0`  
P2 계약: `product-qa-1.0.0`

## 1. 현재 상태

```text
P1 specification = APPROVED
P1 assembly = P1_ASSEMBLED
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
P1 workflow = 28525611462 / SUCCESS
P2 specification = SPEC COMPLETE / APPROVAL PENDING
P2 official reconciliation = NOT RUN
P2 product QA = NOT RUN
P3 HTML MVP = BLOCKED
P4 research release lock = BLOCKED
final product distribution = M0_ONLY
M1~M4 = SHADOW_ONLY
external contact = OPTIONAL_DEFERRED / STOPPED
CAL / SEALED / actual walk-forward = NOT RUN
main merge = NOT PERFORMED
```

필수 문서:

- `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`
- `docs/MINIMAL_PRODUCT_COMPLETION_ROADMAP.md`
- `docs/PRODUCT_GATE_P1_RELEASE_CANDIDATE_SPEC.md`
- `docs/PRODUCT_GATE_P2_QA_SPEC.md`
- `reports/product_p1_acceptance.json`
- `reports/product_p1_acceptance_lock.json`

## 2. P1 locked baseline

### Data

```text
source branch = feature/gate1-governance-foundation
data version = draws-2026.06.27-r1
range = 1..1230
records = 1230
SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification = auto_checked
officially locked = false
```

### Product implementation

```text
P1 spec commit = 84e051ecf81f93309d179a610b6ea543e28c8298
assembly commit = 365bd35bd31929c75ca6f65cf62d1b816ab2235b
rollback manifest commit = 396c4fa2a370083365750be5d563b7ffd8e7146e
implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
acceptance report sha256 = a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139
workflow = 28525611462 / SUCCESS
Python 3.11 = PASS
Python 3.12 = PASS
unit tests = 14 PASS
A1~A13 = PASS
```

P2는 이 baseline을 수정하지 않고 read-only로 검증한다.

## 3. Product contract retained

```text
runner = python -m product.run_prediction
target_draw_no = required
input_last_draw = target_draw_no - 1
initial target = 1231
initial input last draw = 1230
```

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

Shadow diagnostics cannot alter candidate sets, seed, product weights, probabilities, config/model hash or prediction hash.

## 4. P2 official reconciliation policy

Only official draw-result records can approve the canonical dataset.

Source priority:

1. official downloadable archive or official structured endpoint;
2. official per-draw pages;
3. official published file supplied by the operator.

Third-party APIs, blogs, community archives, news, screenshots and OCR-only extraction cannot approve the data.

Each draw `1..1230` must match on:

```text
draw_no
draw date
six winning numbers
bonus number
```

Required totals:

```text
matched = 1230
missing = 0
extra = 0
mismatches = 0
unresolved = 0
```

If the official source is inaccessible, status is `OFFICIAL_RECONCILIATION_BLOCKED`. Any mismatch is `OFFICIAL_RECONCILIATION_FAIL`; data must not be edited inside QA.

## 5. Canonical approval states

```text
AUTO_CHECKED
RECONCILIATION_PENDING
OFFICIAL_RECONCILIATION_BLOCKED
OFFICIAL_RECONCILIATION_FAIL
OFFICIALLY_VERIFIED
LOCKED
```

Complete zero-mismatch reconciliation is required for `OFFICIALLY_VERIFIED`. `LOCKED` additionally requires regenerated checksums, source manifest, approval identity/timestamp, report hash and immutable commit.

No direct `AUTO_CHECKED -> LOCKED` transition is permitted.

## 6. P2 QA domains

### JSON Schema

- canonical output must validate without coercion;
- exactly five distinct six-number sets;
- numbers 1..45, sorted, unique;
- M0-only product weights;
- fixed research/public/statistical-edge disclosures;
- required versions, seed, hashes and cutoff fields;
- negative mutations must fail independently.

### Future-data cutoff

Positive canonical case:

```text
target_draw_no = 1231
input_last_draw = 1230
all draw_no < 1231
```

Hard-fail cases include target-or-later records, missing target-1, duplicate draws, silent future truncation, false cutoff metadata and invalid target.

### Shadow isolation

Omitted, empty and materially different shadow payloads must yield identical:

- candidate sets and ranks;
- seed;
- product weights and probabilities;
- model/config/prediction hashes.

Only diagnostic fields may differ.

### Reproducibility

- minimum three repeats per supported Python version;
- Python 3.11 and 3.12 product-core equality;
- generated_at changes must not change candidates, seed or prediction hash;
- target/data/model/config changes must invalidate the corresponding deterministic identity.

### Hash, manifest and rollback

Recompute and cross-check:

- data hash;
- model hash;
- config hash;
- prediction hash;
- cutoff hash;
- source refs, commits, paths and blob SHAs in assembly manifest;
- rollback base/pre-assembly/assembled/lock commits and policies.

## 7. P2 acceptance criteria

B1~B18 are mandatory:

```text
B1  P1 lock/report hashes match
B2  official source is authoritative and archived
B3  1..1230 zero-mismatch reconciliation
B4  state reaches OFFICIALLY_VERIFIED
B5  complete lock package reaches LOCKED
B6  canonical JSON validates
B7  all negative schema cases fail
B8  canonical cutoff passes
B9  all future-data mutations hard-fail
B10 shadow isolation passes
B11 repeated-run reproducibility passes
B12 Python 3.11/3.12 product-core equality
B13 all required hashes recompute exactly
B14 assembly manifest resolves completely
B15 rollback manifest is internally consistent
B16 final distribution remains M0_ONLY
B17 disclosure remains fixed
B18 frozen research sources/results remain unchanged
```

Final decisions:

```text
P2_QA_PASS    = B1~B18 all PASS
P2_QA_BLOCKED = official source cannot be evaluated
P2_QA_FAIL    = any evaluated criterion failure
```

No conditional PASS and no waiver.

## 8. Future P2 implementation artifacts

After separate approval, use:

```text
branch = qa/product-p2-data-integration
base = feature/product-p1-release-candidate
```

Required artifacts:

```text
reports/product_p2_official_reconciliation.json
reports/product_p2_qa.json
reports/product_p2_qa_lock.json
release/product_p2_source_manifest.json
```

The report must record source inventory, reconciliation counts/mismatches, state transitions, schema/cutoff/shadow/reproducibility/hash/manifest results and B1~B18 decisions.

## 9. Stop and rollback

On `P2_QA_FAIL`:

- preserve evidence and stop;
- do not start P3;
- do not rewrite P1 history;
- revert only P2 QA changes if the QA code is defective;
- open a separate data-correction gate if canonical data is wrong;
- rebuild P1 with a new data version/hash after any correction.

P1 implementation lock remains the rollback anchor.

## 10. Current exclusions

Not performed or authorized:

- actual official-result reconciliation;
- P2 QA implementation or workflow execution;
- canonical data correction;
- historical/prospective Walk-forward;
- M1~M4 activation or tuning;
- physical metadata ingestion;
- HTML modification or deployment;
- CAL·SEALED;
- mobile UI·Supabase;
- main merge.

## 11. Next step

The next allowed step, after user approval, is `Product Gate P2 QA implementation and execution` on a separate QA branch. P3 remains blocked until the P2 result and lock are separately approved.
