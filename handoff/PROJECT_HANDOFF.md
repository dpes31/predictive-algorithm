# Project Handoff

최종 갱신일: 2026-07-01  
현재 작업: **Product Gate P1 release-candidate 상세 구현 명세 완료·승인 대기**  
현재 브랜치: `product-p1-release-candidate-spec`  
기준 브랜치: `docs/minimal-product-completion-roadmap`  
P1 계약: `product-release-candidate-1.0.0`

## 1. 현재 상태

```text
P1 specification = COMPLETE / APPROVAL PENDING
P1 implementation = NOT STARTED
P2 product QA = BLOCKED
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

## 2. P1 목적

기존 자산을 새로 개발하지 않고 한 release-candidate 경로로 조립한다.

- Gate 1 1~1230회 canonical data
- Gate 2-2 exact 6-of-45 engine
- deterministic 6개 번호 × 5세트 생성기
- cutoff·hash·research-only 안전장치

P1은 예측력 개선이나 추가 검증 단계가 아니다.

## 3. Source assets

### Gate 1 data

```text
source branch = feature/gate1-governance-foundation
data version = draws-2026.06.27-r1
range = 1..1230
records = 1230
SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification = auto_checked
locked = false
```

P1은 데이터 상태를 official verified로 승격하지 않는다.

### Gate 2-2 engine

Reuse:

- `engine/contracts.py`
- `engine/data_loader.py`
- `engine/distributions.py`
- `engine/elementary_symmetric.py`
- `engine/candidate_optimizer.py`
- `engine/hashing.py`
- `engine/prediction_run.py`
- `engine/config.py`
- M0~M3 expert modules
- randomness gate

Historical Draft PR 전체를 merge하지 않고 필요한 reviewed file만 assembly manifest에 기록해 조립한다.

## 4. Target draw contract

Future runner:

```text
python -m product.run_prediction
```

Required:

```text
--target-draw-no
--dataset
--generated-at
--output optional
```

Initial canonical run:

```text
target_draw_no = 1231
input_last_draw = 1230
```

Invariant:

```text
input_last_draw = target_draw_no - 1
all input draws < target_draw_no
```

Target 또는 이후 회차가 포함되면 실패한다. Product runner는 전체 dataset을 받은 뒤 몰래 slice하지 않는다.

## 5. Final distribution lock

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

M1~M4 shadow 값은 diagnostics에만 기록할 수 있다. 후보세트·제품확률·사용자 표시에는 영향을 줄 수 없다.

Required flags:

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

## 6. Five-set contract

- exactly 5 sets
- exactly 6 integers per set
- numbers 1..45
- ascending numbers
- no number duplicate within a set
- no set duplicate
- rank exactly 1..5
- deterministic seed
- each probability `1 / 8,145,060`
- each `lift_vs_uniform = 1.0`

M0 rank는 확률 우위가 아니라 deterministic display order다.

## 7. Version and hash contract

Versions:

```text
product contract = product-release-candidate-1.0.0
model = 5.0.0-research-m0-product
engine core = 2.0.0-research
feature contract = 1.0.0
candidate contract = 1.0.0
```

Required hashes:

- data hash
- model hash
- config hash
- prediction hash

Seed:

```text
SHA256(contract version + data hash + model version + config hash + target draw)
```

`generated_at`, hostname, process ID, OS random state는 seed에 포함하지 않는다.

## 8. Output schema

Future file:

```text
schemas/product_prediction.schema.json
```

Required constants:

- `statistical_edge=false`
- `reason=no_validated_nonuniform_signal`
- `final_distribution=M0_ONLY`
- M0=1, M1~M4=0
- `research_only=true`
- `public_release_allowed=false`
- exactly 5 candidate objects
- versions·hashes·seed·limitations
- `additionalProperties=false`

예시 번호는 schema 설명용이며 prediction fixture로 사용하지 않는다.

## 9. Assembly and rollback

Future implementation branch:

```text
feature/product-p1-release-candidate
```

Required files:

```text
release/assembly_manifest.json
release/rollback_manifest.json
```

Assembly manifest는 source ref·blob SHA·destination을 기록한다.

Rollback rules:

- source branches와 frozen reports 수정 금지
- main 영향 없음
- artifact 공개 전 branch-local rollback 가능
- artifact 공개 후 revert commit 사용
- force history rewrite 금지

Automatic reject:

- data/source hash mismatch
- M1~M4 product weight nonzero
- five-set contract violation
- prediction hash non-reproducible
- future-data cutoff violation
- frozen result modification

## 10. Planned implementation files

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

Existing `engine/` modules are reused without redesign.

## 11. P1 acceptance criteria

```text
A1 data hash matches manifest
A2 target contract valid
A3 input last draw = target-1
A4 M0=1 and M1~M4=0
A5 exactly five distinct six-number sets
A6 exact uniform candidate probability
A7 lift_vs_uniform=1.0
A8 statistical_edge=false
A9 reason=no_validated_nonuniform_signal
A10 prediction hash reproducible
A11 frozen source/result unmodified
A12 rollback manifest complete
A13 research_only=true and public_release_allowed=false
```

Acceptance criteria are fixed but not executed in this specification Gate.

## 12. Current exclusions

- Python implementation
- source asset assembly
- official-result reconciliation execution
- product QA execution
- historical/prospective Walk-forward
- HTML modification
- M1~M4 activation or tuning
- physical metadata ingestion
- CAL·SEALED
- mobile UI·Supabase
- main merge

## 13. Next step

User approval is required before Python assembly begins on `feature/product-p1-release-candidate`. P2 QA, actual Walk-forward, and HTML work remain separate later gates.
