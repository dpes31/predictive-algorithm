# Project Handoff

최종 갱신일: 2026-07-01  
현재 작업: **Product Gate P1 release-candidate 조립 및 A1~A13 검증 완료**  
현재 브랜치: `feature/product-p1-release-candidate`  
기준 브랜치: `product-p1-release-candidate-spec`  
Draft PR: #42  
P1 계약: `product-release-candidate-1.0.0`

## 1. 현재 상태

```text
P1 specification = APPROVED
P1 assembly = P1_ASSEMBLED
implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
workflow = 28525611462 / SUCCESS
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
- `reports/product_p1_acceptance.json`
- `reports/product_p1_acceptance_lock.json`

## 2. 조립된 자산

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

P1은 official verified 또는 locked 상태로 승격하지 않았다.

### Gate 2-2 reuse

실제 재사용 파일:

- `engine/contracts.py`
- `engine/data_loader.py`
- `engine/config.py`
- `engine/elementary_symmetric.py`
- `engine/distributions.py`
- `engine/candidate_optimizer.py`
- `engine/hashing.py`

새 예측 알고리즘이나 하이퍼파라미터는 추가하지 않았다.

## 3. Product runner

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

Initial canonical contract:

```text
target_draw_no = 1231
input_last_draw = 1230
```

Hard barrier:

```text
all input draws < target_draw_no
input_last_draw = target_draw_no - 1
```

Target 또는 이후 회차가 포함되거나 target-1이 없으면 실패한다. Full dataset을 입력한 뒤 내부에서 target 이후를 조용히 제거하지 않는다.

## 4. Final distribution lock

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

Shadow diagnostics는 임의 값이 들어와도 다음을 바꿀 수 없다.

- candidate sets
- seed
- prediction hash
- product weights
- statistical-edge disclosure

Required flags:

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

## 5. Five-set output contract

- exactly 5 sets
- exactly 6 integers per set
- numbers 1..45
- ascending numbers
- no number duplicate within a set
- no duplicate set
- ranks 1..5
- each probability `1 / C(45,6)`
- each `lift_vs_uniform = 1.0`

M0 rank는 확률 우위가 아니라 deterministic display order다.

## 6. Versions and hashes

```text
product contract = product-release-candidate-1.0.0
model = 5.0.0-research-m0-product
engine core = 2.0.0-research
feature contract = 1.0.0
candidate contract = 1.0.0
```

Output includes:

- data hash
- model hash
- config hash
- prediction hash
- deterministic seed
- cutoff hash

Seed source:

```text
contract version + data hash + model version + config hash + target draw
```

`generated_at`, machine time, hostname, process ID와 OS random state는 후보세트에 영향을 주지 않는다.

## 7. 구현 파일

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
.github/workflows/product-p1.yml
```

## 8. Assembly and rollback

```text
spec commit = 84e051ecf81f93309d179a610b6ea543e28c8298
assembly commit = 365bd35bd31929c75ca6f65cf62d1b816ab2235b
rollback manifest commit = 396c4fa2a370083365750be5d563b7ffd8e7146e
implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
```

- `release/assembly_manifest.json` records source ref, blob SHA and destination.
- `release/rollback_manifest.json` records the pre-assembly and assembled commits.
- source branches, frozen reports and main were not modified.
- artifact 이후 force rewrite는 금지하고 revert commit을 사용한다.

## 9. P1 test result

Initial run:

```text
run 28525288118 = FAILURE / preserved
```

Candidate number tuples를 JSON arrays로 정규화한 correction 후:

```text
run 28525611462 = SUCCESS
Python 3.11 = PASS
Python 3.12 = PASS
unit tests = 14 PASS
canonical output generation = PASS
```

A1~A13:

```text
A1 data hash matches manifest = PASS
A2 target contract = PASS
A3 input last draw = target-1 = PASS
A4 M0=1 and M1~M4=0 = PASS
A5 five distinct six-number sets = PASS
A6 uniform probability = PASS
A7 lift_vs_uniform=1.0 = PASS
A8 statistical_edge=false = PASS
A9 reason fixed = PASS
A10 prediction hash reproducible = PASS
A11 frozen sources/results unchanged = PASS
A12 rollback manifest complete = PASS
A13 research/public flags fixed = PASS
```

Report:

- `reports/product_p1_acceptance.json`
- report SHA-256 `a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139`

Vercel check failure is a build-rate-limit status and is outside P1. HTML modification and deployment validation were not performed.

## 10. Current exclusions

- official-result reconciliation execution
- P2 product QA
- historical/prospective Walk-forward
- M1~M4 activation or tuning
- physical metadata ingestion
- HTML modification or deployment
- CAL·SEALED
- mobile UI·Supabase
- main merge

## 11. Next step

The next allowed step is `Product Gate P2 — data/integration QA specification`. P2 QA execution, official data reconciliation and actual Walk-forward require a separate approval.
