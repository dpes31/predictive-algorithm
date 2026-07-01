# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽는다.

## 1. 프로젝트 목적

로또 6/45 다음 회차의 정확히 6개 번호 조합 5세트를 출력하는 연구형 제품을 개발한다.

- 최종 제품분포는 exact M0
- M1~M4는 shadow-only
- 미래 데이터 누출 금지
- 동일 data/version/seed에서 동일 결과
- 실패 결과와 hash 보존
- 사용자 승인 전 다음 Gate 진행 금지
- main 직접 개발·병합 금지

## 2. 필수 읽기

1. `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`
2. `docs/MINIMAL_PRODUCT_COMPLETION_ROADMAP.md`
3. `docs/PRODUCT_GATE_P1_RELEASE_CANDIDATE_SPEC.md`
4. `handoff/PROJECT_HANDOFF.md`
5. `reports/data_integrity.json`
6. `reports/gate1_summary.md`
7. `docs/GATE2_ENGINE_SPEC.md`
8. `reports/gate2_3p3_full_summary.md`
9. `reports/gate2_3p_r3_dev_lock.json`
10. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
11. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`

M4F source-access 문서는 선택적 참고자료이며 기본 개발경로가 아니다.

## 3. 현재 상태

현재 브랜치: `product-p1-release-candidate-spec`  
기준 브랜치: `docs/minimal-product-completion-roadmap`  
P1 계약: `product-release-candidate-1.0.0`  
현재 모델: `5.0.0-research`  
최종 제품분포: `M0_ONLY`

```text
P1 specification = COMPLETE / APPROVAL PENDING
P1 Python assembly = NOT STARTED
P2 product QA = BLOCKED
P3 HTML MVP = BLOCKED
P4 release lock = BLOCKED
external contact = OPTIONAL_DEFERRED / STOPPED
CAL = NOT RUN
SEALED = NOT RUN
main merge = NOT PERFORMED
```

## 4. P1 제품계약

### Target input

```text
runner = python -m product.run_prediction
target_draw_no = required
input_last_draw = target_draw_no - 1
```

Canonical initial target:

```text
target_draw_no = 1231
input_last_draw = 1230
```

Target 또는 이후 회차가 입력에 포함되면 즉시 실패한다.

### Final weights

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

M1~M4 shadow 값은 후보세트·제품확률에 영향을 줄 수 없다.

### Product flags

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

## 5. P1 source assets

Gate 1:

- `data/draws.json`
- data version `draws-2026.06.27-r1`
- 1~1230회
- SHA-256 `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- status `auto_checked`, not officially locked

Gate 2-2 reuse:

- exact fixed-size distribution
- elementary symmetric normalization
- uniform expert
- deterministic candidate optimizer
- hashing
- data cutoff
- prediction contracts

새 알고리즘을 추가하지 않는다.

## 6. Candidate contract

- exactly 5 sets
- exactly 6 numbers per set
- numbers 1..45
- ascending within each set
- no duplicate number within a set
- no duplicate set
- ranks 1..5
- each probability `1 / C(45,6)`
- each `lift_vs_uniform = 1.0`

M0 rank는 확률우위가 아니라 deterministic display order다.

## 7. Hash contract

Required hashes:

- `data_hash`
- `model_hash`
- `config_hash`
- `prediction_hash`

Seed payload:

```text
contract version + data hash + model version + config hash + target draw
```

Machine time, hostname, process ID, OS random state를 seed에 포함하지 않는다. `generated_at`은 결과에 기록하되 후보세트에 영향을 주지 않는다.

## 8. Output contract

Future schema:

```text
schemas/product_prediction.schema.json
```

필수:

- additional properties 차단
- exactly 5 candidates
- statistical_edge const false
- reason const `no_validated_nonuniform_signal`
- final_distribution const `M0_ONLY`
- M0 weight 1.0, M1~M4 weight 0.0
- research_only true
- public_release_allowed false
- versions, hashes, seed, limitations

## 9. Rollback

Future implementation branch:

```text
feature/product-p1-release-candidate
```

필수 manifest:

- `release/assembly_manifest.json`
- `release/rollback_manifest.json`

Source branch·frozen result·main은 수정하지 않는다. Published artifact 이후 rollback은 force-reset이 아니라 revert commit을 사용한다.

Automatic rejection:

- data hash mismatch
- source blob mismatch
- nonzero M1~M4 product weight
- invalid candidate contract
- prediction hash non-reproducible
- future-data violation
- frozen result modification

## 10. Planned minimum files

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

## 11. 현재 금지사항

이번 Gate에서는 다음을 수행하지 않는다.

- Python 구현
- data asset 조립
- 공식 데이터 대조 실행
- product QA
- 실제 Walk-forward
- HTML 수정
- M1~M4 활성화·튜닝
- CAL·SEALED
- 모바일 UI·Supabase
- main 병합

## 12. 다음 Gate

사용자 승인 후에만 `feature/product-p1-release-candidate`에서 Python assembly를 수행한다. P2 QA, 실제 Walk-forward와 HTML 수정은 P1 구현에 포함하지 않는다.
