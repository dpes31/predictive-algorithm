# Product Gate P2 — Data and Integration QA Specification

Status: `SPEC COMPLETE / APPROVAL PENDING`  
Contract version: `product-qa-1.0.0`  
Base implementation: `feature/product-p1-release-candidate`  
P1 implementation lock: `099d917abd1b635c830fee343a47d3bd23e0c052`

## 1. Purpose

Product Gate P2 verifies that the P1 M0-only release candidate is built on an approved canonical dataset and that its product contract remains intact under schema, cutoff, shadow-isolation, reproducibility, hash, manifest and rollback checks.

P2 does not test predictive superiority. P2 must not activate M1~M4, tune any model, run historical/prospective Walk-forward, modify HTML, run CAL/SEALED, modify mobile/Supabase, or merge to `main`.

## 2. Locked inputs

P2 QA must start from the exact P1 implementation lock and the following immutable references.

```text
P1 contract              = product-release-candidate-1.0.0
P1 implementation lock   = 099d917abd1b635c830fee343a47d3bd23e0c052
P1 workflow              = 28525611462 / SUCCESS
P1 acceptance report     = reports/product_p1_acceptance.json
P1 acceptance report sha = a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139
Gate 1 data version      = draws-2026.06.27-r1
Gate 1 range             = 1..1230
Gate 1 record count      = 1230
Gate 1 data sha256       = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
Final distribution       = M0_ONLY
Product weights          = M0=1, M1=M2=M3=M4=0
```

If any locked input differs before QA begins, P2 must stop as `P2_PREFLIGHT_FAIL`.

## 3. P2 execution branch and future artifacts

The future QA implementation, after separate approval, must use:

```text
branch = qa/product-p2-data-integration
base   = feature/product-p1-release-candidate
```

Required future artifacts:

```text
reports/product_p2_official_reconciliation.json
reports/product_p2_qa.json
reports/product_p2_qa_lock.json
release/product_p2_source_manifest.json
```

This specification does not create or populate those execution artifacts.

## 4. Official-result reconciliation policy

### 4.1 Authoritative source hierarchy

Only official draw-result records may approve the canonical dataset.

Priority:

1. official downloadable draw archive or official structured endpoint;
2. official per-draw result pages;
3. an official published file supplied by the lottery operator.

News, blogs, community archives, screenshots, OCR-only extraction and third-party APIs cannot approve the canonical dataset.

### 4.2 Comparison fields

Each draw `1..1230` must be compared field-by-field:

```text
draw_no
published draw date
six winning numbers
bonus number
```

Winning numbers are compared as a sorted six-integer set. The source's displayed extraction order must not be silently substituted for the canonical sorted representation.

### 4.3 Coverage requirement

Approval requires:

```text
expected draws = 1230
matched draws  = 1230
missing draws  = 0
extra draws    = 0
field mismatches = 0
unresolved records = 0
```

Partial sampling cannot produce `OFFICIALLY_VERIFIED` or `LOCKED`.

### 4.4 Unavailable source

If the official source is temporarily inaccessible, rate-limited or structurally unavailable:

```text
status = OFFICIAL_RECONCILIATION_BLOCKED
```

This is not a data PASS and not a mismatch FAIL. No fallback to a third-party source is permitted.

### 4.5 Mismatch handling

Any mismatch produces:

```text
status = OFFICIAL_RECONCILIATION_FAIL
P2 = STOP
P3 = BLOCKED
```

The QA process must not edit `data/draws.json` in place. A correction requires a separate data-correction branch, a complete old/new diff, a regenerated checksum set, a new data version, new manifests, and a fresh P1 assembly.

## 5. Canonical data approval-state machine

Allowed states:

```text
AUTO_CHECKED
RECONCILIATION_PENDING
OFFICIAL_RECONCILIATION_BLOCKED
OFFICIAL_RECONCILIATION_FAIL
OFFICIALLY_VERIFIED
LOCKED
```

Allowed transitions:

```text
AUTO_CHECKED -> RECONCILIATION_PENDING
RECONCILIATION_PENDING -> OFFICIAL_RECONCILIATION_BLOCKED
OFFICIAL_RECONCILIATION_BLOCKED -> RECONCILIATION_PENDING
RECONCILIATION_PENDING -> OFFICIAL_RECONCILIATION_FAIL
RECONCILIATION_PENDING -> OFFICIALLY_VERIFIED
OFFICIALLY_VERIFIED -> LOCKED
```

Forbidden transitions:

- `AUTO_CHECKED -> LOCKED`
- `OFFICIAL_RECONCILIATION_BLOCKED -> OFFICIALLY_VERIFIED`
- `OFFICIAL_RECONCILIATION_FAIL -> LOCKED`
- any state transition based on sampled or third-party results

`OFFICIALLY_VERIFIED` requires the complete reconciliation report. `LOCKED` additionally requires regenerated checksums, source manifest, approval identity, approval timestamp, report hash and immutable commit reference.

## 6. JSON Schema QA

Schema under test:

```text
schemas/product_prediction.schema.json
```

### 6.1 Required positive validation

The canonical P1 result for target draw 1231 must validate without coercion or field deletion.

Required invariants include:

- exactly five candidate sets;
- exactly six integers per set;
- values `1..45`;
- ascending, unique numbers in each set;
- no duplicate candidate set;
- ranks `1..5`;
- `final_distribution = M0_ONLY`;
- `M0=1`, `M1~M4=0`;
- `statistical_edge = false`;
- `reason = no_validated_nonuniform_signal`;
- `research_only = true`;
- `public_release_allowed = false`;
- all required version, hash, seed and cutoff fields present.

### 6.2 Required negative validation

Each mutation below must fail independently:

- missing required property;
- unknown top-level property when prohibited by schema;
- six-number set reduced to five or expanded to seven;
- duplicate number within a set;
- number outside `1..45`;
- duplicate candidate set;
- invalid rank sequence;
- nonuniform probability or `lift_vs_uniform != 1.0`;
- `statistical_edge = true`;
- any nonzero M1~M4 product weight;
- malformed or missing SHA-256 value;
- invalid target or cutoff relationship.

Schema validation must not auto-correct the payload.

## 7. Future-data cutoff QA

### 7.1 Canonical positive case

```text
target_draw_no = 1231
input_first_draw = 1
input_last_draw = 1230
input_record_count = 1230
all draw_no < 1231
```

### 7.2 Mandatory negative cases

The runner must hard-fail when:

1. a record with `draw_no >= target_draw_no` exists;
2. `target_draw_no - 1` is absent;
3. duplicate draw numbers exist;
4. an internal operation silently truncates future records instead of rejecting input;
5. reported `input_last_draw`, count or cutoff hash differs from the actual input;
6. target draw is non-integer, nonpositive or otherwise invalid.

The failure must occur before candidate generation.

## 8. Shadow-isolation QA

M1~M4 remain diagnostics-only. The following runs must produce identical candidate sets, seed, product weights, probability values, config hash, model hash and prediction hash:

```text
shadow = omitted
shadow = {}
shadow = arbitrary valid diagnostics payload A
shadow = materially different diagnostics payload B
shadow key order changed
```

Only the diagnostics section and `shadow_enabled` indicator may differ.

Any influence from shadow data on product candidates or product hashes produces `P2_SHADOW_ISOLATION_FAIL` and blocks P3.

## 9. Five-set reproducibility QA

### 9.1 Repeatability

For identical locked inputs, repeat the canonical target run at least three times per supported Python version.

Required equality:

- candidate sets and rank order;
- deterministic seed;
- data/model/config/prediction hashes;
- cutoff hash;
- product flags and weights.

### 9.2 Cross-runtime equality

Python 3.11 and 3.12 must produce the same product-core result. `generated_at` may differ, but it must not alter candidates, seed or prediction hash.

### 9.3 Controlled-change tests

- changing only `generated_at` must not change product-core output;
- changing shadow diagnostics must not change product-core output;
- changing target draw must change the deterministic seed and normally the candidate output;
- changing a locked model/config/data input must change its corresponding hash and invalidate prior prediction equivalence.

## 10. Hash QA

### 10.1 Data hash

Recompute SHA-256 directly from `data/draws.json`. It must match:

- `product/config.py` expected hash;
- `release/assembly_manifest.json`;
- `release/rollback_manifest.json`;
- `reports/product_p1_acceptance.json`.

### 10.2 Model hash

Recompute from the exact source paths declared by the product wrapper. Missing, added or modified source files must alter the model hash or fail QA.

### 10.3 Config hash

Recompute from canonical product configuration. Dictionary ordering or serialization environment must not affect the result.

### 10.4 Prediction hash

Recompute from the locked prediction-hash payload. It must exclude wall-clock metadata and shadow diagnostics and include target, cutoff, versions, data/model/config hashes, seed, product weights, candidates and disclosure flags.

## 11. Manifest and rollback QA

### 11.1 Assembly manifest

Every declared source asset must satisfy:

- source ref exists;
- source commit exists;
- source path exists at that ref;
- source blob SHA matches;
- destination path exists;
- content hash matches where specified;
- no undeclared product-critical asset is used.

### 11.2 Rollback manifest

The following references must resolve and be internally consistent:

```text
base_commit
pre_assembly_commit
assembled_commit
implementation_lock_commit
source asset hashes
main_affected = false
force_history_rewrite_after_artifact = false
```

Rollback simulation is not performed in specification work. During future P2 execution, validation is read-only: confirm that pre-artifact rollback points to the pre-assembly commit and post-artifact policy requires a revert commit.

## 12. P2 acceptance criteria

All criteria are mandatory.

```text
B1  P1 lock and acceptance report hashes match
B2  official source is authoritative and archived in a source manifest
B3  all 1..1230 records reconcile with zero mismatch
B4  canonical state reaches OFFICIALLY_VERIFIED
B5  canonical lock package is complete and reaches LOCKED
B6  canonical output passes JSON Schema
B7  all negative schema mutations fail
B8  canonical target cutoff passes
B9  every future-data mutation hard-fails before candidate generation
B10 shadow diagnostics cannot alter product-core output
B11 repeated runs are reproducible
B12 Python 3.11 and 3.12 product-core outputs match
B13 data, model, config, prediction and cutoff hashes recompute exactly
B14 assembly manifest resolves all declared assets
B15 rollback manifest is complete and internally consistent
B16 final distribution remains M0_ONLY
B17 statistical_edge=false and fixed reason remain unchanged
B18 frozen research reports and source branches remain unmodified
```

## 13. Final decisions

### 13.1 PASS

```text
status = P2_QA_PASS
```

Permitted only when B1~B18 all pass. P3 remains blocked until the user separately approves P2 results.

### 13.2 BLOCKED

```text
status = P2_QA_BLOCKED
```

Use when an authoritative official source cannot be accessed or archived, so B2~B5 cannot be evaluated. Do not substitute unofficial sources.

### 13.3 FAIL

```text
status = P2_QA_FAIL
```

Use for any evaluated criterion failure, including data mismatch, schema failure, future leakage, shadow influence, non-reproducibility, hash mismatch, manifest inconsistency or changed product disclosure.

### 13.4 STOP and rollback

On `P2_QA_FAIL`:

- stop immediately after preserving evidence;
- do not start P3;
- do not rewrite P1 history;
- retain the P1 implementation lock;
- if the defect was introduced by P2 QA code, revert the P2 branch only;
- if canonical data is wrong, open a separate data-correction gate and rebuild P1 from the corrected data version.

There is no conditional PASS and no waiver for B1~B18.

## 14. Required P2 report structure

The future `reports/product_p2_qa.json` must contain:

```text
contract_version
status
p1_lock_commit
qa_commit
workflow and Python versions
official source inventory
reconciliation counts and mismatch list
canonical state transition evidence
schema positive and negative results
cutoff positive and negative results
shadow-isolation results
reproducibility matrix
hash recomputation results
manifest and rollback results
B1..B18 decisions
excluded work
```

The lock file must contain the report SHA-256, QA commit, workflow run, final status, canonical data version/hash/state and explicit P3 authorization state.

## 15. Exclusions retained

This specification does not authorize:

- actual official-result reconciliation;
- P2 QA code or workflow execution;
- data correction;
- historical or prospective Walk-forward;
- M1~M4 activation or tuning;
- HTML modification or deployment;
- CAL or SEALED;
- mobile UI or Supabase;
- `main` merge.
