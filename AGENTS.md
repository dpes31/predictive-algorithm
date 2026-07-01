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
4. `reports/product_p1_acceptance.json`
5. `reports/product_p1_acceptance_lock.json`
6. `handoff/PROJECT_HANDOFF.md`
7. `reports/data_integrity.json`
8. `reports/gate2_3p3_full_summary.md`
9. `reports/gate2_3p_r3_dev_lock.json`
10. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
11. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`

M4F source-access 문서는 선택적 참고자료이며 기본 개발경로가 아니다.

## 3. 현재 상태

현재 브랜치: `feature/product-p1-release-candidate`  
기준 브랜치: `product-p1-release-candidate-spec`  
Draft PR: `#42`  
P1 계약: `product-release-candidate-1.0.0`  
최종 제품분포: `M0_ONLY`

```text
P1 specification = APPROVED
P1 assembly = P1_ASSEMBLED
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
P1 workflow = 28525611462 / SUCCESS
P2 product QA = BLOCKED
P3 HTML MVP = BLOCKED
P4 research release lock = BLOCKED
external contact = OPTIONAL_DEFERRED / STOPPED
CAL = NOT RUN
SEALED = NOT RUN
main merge = NOT PERFORMED
```

## 4. P1 조립 결과

Gate 1 자산:

- `data/draws.json`
- 1~1230회, 1,230 records
- data version `draws-2026.06.27-r1`
- SHA-256 `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- verification status `auto_checked`
- officially locked `false`

Gate 2-2 재사용:

- exact fixed-size distribution
- elementary symmetric normalization
- deterministic uniform candidate optimizer
- canonical hashing
- canonical draw loader와 future-data cutoff

새 예측 알고리즘과 새 하이퍼파라미터는 추가하지 않았다.

## 5. Product contract

### Target

```text
runner = python -m product.run_prediction
target_draw_no = required
input_last_draw = target_draw_no - 1
```

Initial canonical target:

```text
target_draw_no = 1231
input_last_draw = 1230
```

Target 또는 이후 회차가 입력되거나 target-1이 없으면 실패한다.

### Final weights

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

M1~M4 shadow diagnostics는 후보세트, seed, prediction hash와 제품확률에 영향을 줄 수 없다.

### Flags

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

## 6. Candidate and hash contract

Candidate:

- exactly 5 sets
- exactly 6 numbers per set
- numbers 1..45
- ascending and unique within each set
- no duplicate set
- ranks 1..5
- probability `1 / C(45,6)`
- `lift_vs_uniform = 1.0`

Required hashes:

- data hash
- model hash
- config hash
- prediction hash

Seed uses only:

```text
contract version + data hash + model version + config hash + target draw
```

`generated_at`, hostname, process ID와 OS random state는 후보세트에 영향을 주지 않는다.

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

## 8. P1 검증 결과

Final workflow:

```text
run = 28525611462
Python = 3.11, 3.12
unit tests = 14
unit-test step = PASS
canonical output step = PASS
```

A1~A13 모두 PASS:

- data hash·target cutoff
- M0-only weight
- five-set contract
- uniform probability와 lift
- fixed disclosure
- reproducible prediction hash
- frozen result 미변경
- rollback manifest
- research/public flags

초기 workflow `28525288118` 실패는 보존한다. Candidate JSON의 번호 tuple을 JSON array로 정규화한 뒤 correction commit `099d917abd1b635c830fee343a47d3bd23e0c052`에서 재검증을 통과했다.

Vercel status failure는 build-rate-limit이며 P1 범위가 아니다. HTML 수정·배포검증은 수행하지 않았다.

## 9. Rollback

- assembly commit: `365bd35bd31929c75ca6f65cf62d1b816ab2235b`
- rollback manifest commit: `396c4fa2a370083365750be5d563b7ffd8e7146e`
- implementation lock: `099d917abd1b635c830fee343a47d3bd23e0c052`
- main affected: false

Artifact 공개 이후 force history rewrite는 금지하고 revert commit만 사용한다.

## 10. 현재 금지사항

사용자 별도 승인 전 다음을 수행하지 않는다.

- 공식 데이터 대조 실행
- P2 product QA
- 실제 historical/prospective Walk-forward
- M1~M4 활성화·튜닝
- 물리 metadata 입력
- HTML 수정·배포
- CAL·SEALED
- 모바일 UI·Supabase
- main 병합

## 11. 다음 Gate

다음 허용단계는 `Product Gate P2 — 데이터·통합 QA 명세`다. P2 명세 승인 전 QA 실행, 공식 데이터 대조와 Walk-forward를 시작하지 않는다.
