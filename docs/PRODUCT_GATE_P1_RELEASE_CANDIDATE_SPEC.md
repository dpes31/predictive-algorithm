# Product Gate P1 — Release-Candidate Assembly Specification

상태: 사용자 검토용 상세 구현 명세  
작성일: 2026-07-01  
기준 브랜치: `docs/minimal-product-completion-roadmap`  
대상 구현 브랜치: `feature/product-p1-release-candidate`  
제품 계약 버전: `product-release-candidate-1.0.0`

## 1. 목적

기존 구현을 새로 만들지 않고 다음 자산을 하나의 release-candidate 경로로 조립한다.

- Gate 1의 1~1230회 canonical data
- Gate 2-2 exact 6-of-45 distribution engine
- Gate 2-2 deterministic 6개 번호 × 5세트 생성기
- 기존 future-data cutoff·hash·research-only 안전장치

P1은 알고리즘 개선 단계가 아니다. 검증 실패한 M1~M4를 재활성화하지 않고 최종 사용자 분포를 exact M0로 고정하는 조립 단계다.

이번 Gate에서는 명세만 작성한다. Python 구현, 데이터 대조 실행, product QA, 실제 Walk-forward, HTML 수정, CAL, SEALED, 모바일 UI, main 병합은 수행하지 않는다.

## 2. 조립 원칙

1. 기존 코드 재사용을 우선하고 새 알고리즘을 추가하지 않는다.
2. 최종 사용자 분포는 항상 exact M0다.
3. M1~M4의 계산결과는 제품 확률에 합성하지 않는다.
4. target draw 이전 회차만 입력으로 허용한다.
5. 같은 canonical input과 version·seed는 byte-identical 결과를 생성해야 한다.
6. `auto_checked` 데이터는 연구형 출력에만 허용한다.
7. 제품은 `통계적 우위 없음`을 명시한다.
8. 기존 실패 결과와 hash를 삭제·변경하지 않는다.
9. P1 구현 branch는 `main`을 기준으로 만들지 않는다.
10. P1 통과는 예측력 통과가 아니라 실행계약 조립 완료를 의미한다.

## 3. 기준 자산

### 3.1 Gate 1 canonical data

Source branch:

```text
feature/gate1-governance-foundation
```

Required source files:

```text
data/draws.json
data/source_manifest.json
data/checksums.sha256
reports/data_integrity.json
reports/gate1_summary.md
```

Frozen dataset facts:

```text
data_version = draws-2026.06.27-r1
range = 1..1230
record_count = 1230
dataset_sha256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification_status = auto_checked
locked = false
```

P1은 이 데이터를 공식 검증완료 데이터로 승격하지 않는다.

### 3.2 Gate 2-2 engine

Source PR: `#6`

Required modules:

```text
engine/contracts.py
engine/data_loader.py
engine/distributions.py
engine/elementary_symmetric.py
engine/candidate_optimizer.py
engine/hashing.py
engine/prediction_run.py
engine/config.py
engine/experts/uniform.py
engine/experts/persistence.py
engine/experts/reversal.py
engine/experts/regime_change.py
engine/randomness_gate.py
```

Required tests to preserve:

```text
tests/test_data_cutoff.py
tests/test_elementary_symmetric.py
tests/test_engine_contract.py
tests/test_prediction_run.py
tests/test_weights_and_gate.py
```

### 3.3 Research history references

P1 branch must preserve references to:

- PR #15 `NOT PASSED`
- PR #22 `NO_ELIGIBLE_CONFIG`
- PR #29 `ORACLE_PASS`
- PR #32 `PREDICTABLE_GROUP_FAIL`

These records justify the M0-only product lock.

## 4. Branch and source assembly

### 4.1 Future implementation branch

```text
feature/product-p1-release-candidate
```

Base:

```text
product-p1-release-candidate-spec
```

P1 implementation must import or copy only the required, already-reviewed files from their source branches. It must not merge every historical Draft PR wholesale.

### 4.2 Assembly manifest

Before implementation, create:

```text
release/assembly_manifest.json
```

Required fields:

```json
{
  "contract_version": "product-release-candidate-1.0.0",
  "source_assets": [
    {
      "path": "data/draws.json",
      "source_ref": "feature/gate1-governance-foundation",
      "source_blob_sha": "<required>",
      "destination_path": "data/draws.json"
    }
  ],
  "engine_source_pr": 6,
  "frozen_result_prs": [15, 22, 29, 32],
  "final_distribution": "M0_ONLY"
}
```

모든 source asset은 원본 blob SHA와 목적지 경로를 기록한다.

## 5. Target draw 입력계약

### 5.1 CLI 입력

Future runner:

```text
python -m product.run_prediction
```

Required arguments:

```text
--target-draw-no INTEGER
--dataset PATH              default: data/draws.json
--generated-at ISO8601      required for byte-identical replay
--output PATH               optional; stdout if omitted
```

Forbidden arguments:

- model weight override
- M1~M4 activation switch
- threshold override
- custom physical metadata
- unregistered random seed
- public-release bypass

### 5.2 Target validation

For canonical 1~1230 data, default next target is:

```text
target_draw_no = 1231
input_last_draw = 1230
```

General invariant:

```text
input_last_draw = target_draw_no - 1
```

Reject when:

- target_draw_no < 2
- input includes any draw_no >= target_draw_no
- input last draw does not equal target-1
- draw numbers are non-contiguous
- duplicate draw exists
- fewer than configured minimum history draws are present
- dataset hash differs from the manifest without a registered dataset-version change

Historical target replay may be supported later for QA, but P1 product runner defaults to the next unseen draw only.

## 6. Final distribution lock

### 6.1 Product weights

```text
product_weights = {
  "M0": 1.0,
  "M1": 0.0,
  "M2": 0.0,
  "M3": 0.0,
  "M4": 0.0
}
```

No gate evidence can alter these weights in P1.

### 6.2 Exact uniform combination probability

For every valid six-number set S:

```text
P(S) = 1 / C(45,6)
C(45,6) = 8,145,060
```

Each candidate's `joint_probability` must equal the uniform probability within the chosen serialization precision. Each candidate's `lift_vs_uniform` must equal `1.0`.

### 6.3 Shadow-only models

M1~M4 may be instantiated only under a separately named shadow path.

Rules:

- shadow weights may be computed for diagnostics
- shadow values must not enter `product_weights`
- shadow values must not affect candidate selection
- shadow failure must not block M0 generation unless a safety invariant is violated
- shadow fields must be nested under `diagnostics.shadow`
- user-facing advantage status remains false regardless of shadow output

P1 may disable all shadow computation for the minimal runner. Shadow enabled/disabled modes must produce identical candidate sets.

## 7. Candidate generation contract

Reuse the existing uniform branch of `engine/candidate_optimizer.py`.

Fixed values:

```text
number_count = 45
pick_count = 6
candidate_count = 5
uniform_candidate_pool = 3000
```

Required invariants:

- exactly 5 candidate sets
- each set contains exactly 6 integers
- each integer is within 1..45
- numbers inside each set are strictly ascending
- no duplicate number inside a set
- no duplicate set across the 5 candidates
- rank is exactly 1..5
- deterministic diversity selection
- candidate generation uses only the registered deterministic seed

M0에서는 모든 조합의 확률이 동일하므로 rank는 확률 우위 순위가 아니라 deterministic display order다.

## 8. Seed contract

Seed is computed with existing canonical hash utilities.

Canonical seed payload:

```json
[
  "product-release-candidate-1.0.0",
  "<data_hash>",
  "<model_version>",
  "<config_hash>",
  "<target_draw_no>"
]
```

Formula:

```text
seed = SHA256(canonical_json(seed_payload))
```

Do not include machine time, process ID, hostname, unordered map iteration, or operating-system random state.

`generated_at` is recorded in output but must not alter candidate sets or seed.

## 9. Version and hash contract

### 9.1 Required versions

```text
product_contract_version = product-release-candidate-1.0.0
model_version = 5.0.0-research-m0-product
engine_core_version = 2.0.0-research
feature_contract_version = 1.0.0
candidate_contract_version = 1.0.0
```

The model suffix explicitly identifies the M0 product lock and does not imply 5.0 nonuniform activation.

### 9.2 Data hash

```text
data_hash = SHA-256 of exact data/draws.json bytes
```

For the initial assembly it must equal the Gate 1 checksum recorded in the assembly manifest. If serialization differs despite equivalent records, P1 must stop and require an explicit data release decision rather than silently changing the hash.

### 9.3 Config hash

`config_hash` is SHA-256 of canonical JSON containing only product-effective constants:

```json
{
  "candidate_count": 5,
  "final_distribution": "M0_ONLY",
  "number_count": 45,
  "pick_count": 6,
  "uniform_candidate_pool": 3000
}
```

Research-only M1~M4 tuning constants are excluded from the product-effective config hash and may be placed in a separate `shadow_config_hash`.

### 9.4 Model hash

`model_hash` is SHA-256 of:

- exact source blobs used by the product path
- product contract version
- engine core version
- final product weights

At minimum include:

```text
engine/distributions.py
engine/elementary_symmetric.py
engine/candidate_optimizer.py
engine/hashing.py
product runner module
product output-contract module
```

### 9.5 Prediction hash

The hash payload excludes `prediction_hash` itself and excludes non-deterministic environment metadata.

Required payload:

```json
{
  "contract_version": "product-release-candidate-1.0.0",
  "target_draw_no": 1231,
  "input_last_draw": 1230,
  "data_version": "draws-2026.06.27-r1",
  "data_hash": "<sha256>",
  "model_version": "5.0.0-research-m0-product",
  "model_hash": "<sha256>",
  "config_hash": "<sha256>",
  "seed": "<sha256>",
  "product_weights": {"M0": 1.0, "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0},
  "candidate_sets": ["<canonical candidate objects>"],
  "statistical_edge": false,
  "reason": "no_validated_nonuniform_signal"
}
```

```text
prediction_hash = SHA256(canonical_json(payload))
```

## 10. Output JSON schema contract

Future file:

```text
schemas/product_prediction.schema.json
```

Canonical shape:

```json
{
  "schema_version": "1.0.0",
  "contract_version": "product-release-candidate-1.0.0",
  "target_draw_no": 1231,
  "input_last_draw": 1230,
  "generated_at": "2026-07-01T00:00:00Z",
  "research_only": true,
  "public_release_allowed": false,
  "statistical_edge": false,
  "reason": "no_validated_nonuniform_signal",
  "advantage_status": "통계적 우위 없음",
  "final_distribution": "M0_ONLY",
  "product_weights": {
    "M0": 1.0,
    "M1": 0.0,
    "M2": 0.0,
    "M3": 0.0,
    "M4": 0.0
  },
  "candidate_sets": [
    {
      "rank": 1,
      "numbers": [1, 2, 3, 4, 5, 6],
      "joint_probability": 0.0000001227738048,
      "lift_vs_uniform": 1.0
    }
  ],
  "versions": {
    "data_version": "draws-2026.06.27-r1",
    "model_version": "5.0.0-research-m0-product",
    "engine_core_version": "2.0.0-research",
    "feature_contract_version": "1.0.0",
    "candidate_contract_version": "1.0.0"
  },
  "hashes": {
    "data_hash": "<sha256>",
    "model_hash": "<sha256>",
    "config_hash": "<sha256>",
    "prediction_hash": "<sha256>"
  },
  "seed": "<sha256>",
  "diagnostics": {
    "shadow_enabled": false,
    "shadow": null
  },
  "limitations": [
    "canonical_data_auto_checked_not_officially_locked",
    "no_validated_nonuniform_signal",
    "not_a_claim_of_improved_lottery_odds"
  ]
}
```

Schema requirements:

- `additionalProperties=false` at every product-contract object level
- exactly 5 candidate items
- exactly 6 unique integers per candidate
- candidate numbers 1..45
- ranks 1..5 unique
- `statistical_edge` const false
- `reason` const `no_validated_nonuniform_signal`
- `final_distribution` const `M0_ONLY`
- M0 weight const 1.0
- M1~M4 weights const 0.0
- `research_only` const true
- `public_release_allowed` const false
- all hashes match `^[a-f0-9]{64}$`

The example numbers are schema illustration only and must never be used as a prediction fixture.

## 11. Future-data barrier

Reuse and strengthen the existing `records_for_target` behavior.

Hard conditions:

```text
max(input.draw_no) = target_draw_no - 1
all(input.draw_no) < target_draw_no
input draw numbers are contiguous
```

The product runner must not accept a complete dataset containing target or later draws and then silently slice it. The caller or explicit loader must materialize the cutoff-safe view, and the cutoff manifest must be hashed.

Required cutoff manifest:

```json
{
  "target_draw_no": 1231,
  "input_first_draw": 1,
  "input_last_draw": 1230,
  "input_record_count": 1230,
  "excluded_draws_at_or_after_target": 0,
  "cutoff_hash": "<sha256>"
}
```

Reject when `excluded_draws_at_or_after_target` is not zero for the supplied product input.

## 12. Public-release and wording lock

P1 remains research-only.

Required flags:

```text
research_only = true
public_release_allowed = false
statistical_edge = false
advantage_status = 통계적 우위 없음
```

Forbidden wording:

- 예측력이 검증됨
- 당첨확률 향상
- 추천번호
- 고확률 번호
- 물리변수 반영으로 우위 확보

Allowed wording:

- 연구형 5세트 생성
- 균등분포 기반
- 통계적 우위 없음
- 결과는 오락·연구 목적

## 13. Rollback structure

### 13.1 No mutation of source branches

P1 implementation must not modify:

- `feature/gate1-governance-foundation`
- historical Gate 2 branches
- frozen result files
- `main`

### 13.2 Rollback manifest

Before implementation output is accepted, create:

```text
release/rollback_manifest.json
```

Required fields:

```json
{
  "base_ref": "product-p1-release-candidate-spec",
  "base_commit": "<sha>",
  "implementation_branch": "feature/product-p1-release-candidate",
  "pre_assembly_commit": "<sha>",
  "assembled_commit": "<sha>",
  "source_asset_hashes": {},
  "rollback_action": "reset implementation branch to pre_assembly_commit",
  "main_affected": false
}
```

Rollback is branch-local. No history rewriting or force update is permitted after a validation artifact has been published. After publication, rollback must use a revert commit.

### 13.3 Automatic rollback conditions

P1 must be rejected and reverted if:

- data hash mismatch
- source blob differs from assembly manifest
- M1~M4 product weight nonzero
- candidate count not 5
- candidate length not 6
- duplicate candidate
- prediction hash non-reproducible
- future-data cutoff violation
- research/public flags differ from constants
- frozen result file modified

## 14. Planned file layout

P1 implementation may create only the minimum product wrapper files.

```text
product/__init__.py
product/config.py
product/contracts.py
product/run_prediction.py
schemas/product_prediction.schema.json
release/assembly_manifest.json
release/rollback_manifest.json
tests/test_product_contract.py
tests/test_product_cutoff.py
tests/test_product_reproducibility.py
```

It may reuse existing `engine/` modules without redesigning them.

No HTML, database, API server, mobile, or external-data module is included in P1.

## 15. P1 acceptance criteria

Implementation may be considered `P1_ASSEMBLED` only when all are true.

```text
A1 canonical Gate 1 data hash matches assembly manifest
A2 target draw contract validates
A3 input last draw equals target-1
A4 final product weights exactly M0=1, M1~M4=0
A5 exactly five distinct six-number sets
A6 all candidate probabilities equal exact uniform probability
A7 lift_vs_uniform equals 1.0
A8 statistical_edge=false
A9 reason=no_validated_nonuniform_signal
A10 same input produces byte-identical hash payload and prediction hash
A11 no frozen result or source branch modified
A12 rollback manifest complete
A13 research_only=true and public_release_allowed=false
```

P1 acceptance tests are defined here but are not executed in this Gate.

## 16. Out of scope

- official-result reconciliation execution
- product QA execution
- historical or prospective Walk-forward
- M1~M4 tuning or activation
- physical metadata ingestion
- CAL·SEALED
- HTML modification
- API server
- mobile UI
- Supabase
- main merge

## 17. Next gate boundary

After P1 specification approval, the next allowed action is Python assembly on `feature/product-p1-release-candidate` only.

P2 data/integration QA must not be executed during P1 implementation. P1 may run unit tests necessary to prove assembly correctness, but must not perform actual historical Walk-forward or model-power evaluation.
