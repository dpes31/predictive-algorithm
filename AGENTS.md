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
4. `docs/PRODUCT_GATE_P2_QA_SPEC.md`
5. `reports/product_p1_acceptance.json`
6. `reports/product_p1_acceptance_lock.json`
7. `handoff/PROJECT_HANDOFF.md`
8. `reports/data_integrity.json`
9. `reports/gate2_3p3_full_summary.md`
10. `reports/gate2_3p_r3_dev_lock.json`
11. `reports/gate2_3p_r3m2_oracle_dev_lock.json`
12. `reports/gate2_3p_r3m3_predictable_group_dev_lock.json`

M4F source-access 문서는 선택적 참고자료이며 기본 개발경로가 아니다.

## 3. 현재 상태

현재 브랜치: `docs/product-p2-qa-spec`  
기준 브랜치: `feature/product-p1-release-candidate`  
관련 Issue: `#43`  
P1 계약: `product-release-candidate-1.0.0`  
P2 계약: `product-qa-1.0.0`  
최종 제품분포: `M0_ONLY`

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
external contact = OPTIONAL_DEFERRED / STOPPED
CAL = NOT RUN
SEALED = NOT RUN
main merge = NOT PERFORMED
```

## 4. P1 locked baseline

Gate 1 data:

- `data/draws.json`
- 1~1230회, 1,230 records
- data version `draws-2026.06.27-r1`
- SHA-256 `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- verification status `auto_checked`
- officially locked `false`

P1 implementation:

- implementation lock `099d917abd1b635c830fee343a47d3bd23e0c052`
- acceptance report SHA-256 `a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139`
- A1~A13 PASS
- Python 3.11 / 3.12 PASS
- 14 unit tests PASS

P2는 이 baseline을 수정하지 않고 검증해야 한다.

## 5. Product contract

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

Final weights:

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

Required flags:

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

M1~M4 shadow diagnostics는 후보세트, seed, prediction hash와 제품확률에 영향을 줄 수 없다.

## 6. P2 QA scope

P2 상세 명세는 `docs/PRODUCT_GATE_P2_QA_SPEC.md`를 따른다.

검증대상:

- 공식 결과 1~1230회 전수 대조 정책
- canonical data 상태 전환
- JSON Schema positive/negative validation
- 미래 데이터 hard-fail
- shadow isolation
- 5세트 반복·cross-runtime 재현성
- data/model/config/prediction/cutoff hash 재계산
- assembly manifest와 rollback manifest 정합성
- B1~B18 PASS/BLOCKED/FAIL 판정

## 7. Canonical data state contract

Allowed states:

```text
AUTO_CHECKED
RECONCILIATION_PENDING
OFFICIAL_RECONCILIATION_BLOCKED
OFFICIAL_RECONCILIATION_FAIL
OFFICIALLY_VERIFIED
LOCKED
```

전체 1~1230회가 공식 출처와 zero mismatch로 일치해야만 `OFFICIALLY_VERIFIED`가 가능하다. sampled verification, third-party source 또는 unavailable official source는 승격 근거가 아니다.

## 8. P2 acceptance

모든 B1~B18은 mandatory다.

```text
P2_QA_PASS    = B1~B18 all PASS
P2_QA_BLOCKED = authoritative official source unavailable
P2_QA_FAIL    = any evaluated criterion failure
```

Conditional PASS와 waiver는 없다. P2 결과가 사용자에게 별도 승인되기 전 P3를 시작하지 않는다.

## 9. Rollback

- P1 implementation lock은 변경하지 않는다.
- P2 QA 결함은 P2 branch만 revert한다.
- canonical mismatch는 별도 data-correction gate로 이동한다.
- 데이터 수정 후에는 새 data version/hash로 P1을 다시 조립한다.
- artifact 이후 force history rewrite는 금지한다.

## 10. 현재 금지사항

사용자 별도 승인 전 다음을 수행하지 않는다.

- 실제 공식 데이터 대조
- P2 QA 코드·workflow 작성 또는 실행
- canonical data 수정
- 실제 historical/prospective Walk-forward
- M1~M4 활성화·튜닝
- 물리 metadata 입력
- HTML 수정·배포
- CAL·SEALED
- 모바일 UI·Supabase
- main 병합

## 11. 다음 Gate

다음 허용단계는 사용자 승인 후 `Product Gate P2 QA 구현·실행`이다. 구현 전 별도 branch, report/lock artifact, B1~B18 테스트와 중단정책을 그대로 적용한다.
