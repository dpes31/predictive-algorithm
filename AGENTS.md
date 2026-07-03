# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서와 `handoff/PROJECT_HANDOFF.md`를 읽고 실제 저장소 상태와 대조한다.

## 1. 절대 원칙

- 최종 제품분포는 `M0_ONLY`다.
- M1~M4는 shadow-only이며 후보세트·seed·hash·제품확률에 영향을 주지 않는다.
- 미래 데이터 누출을 허용하지 않는다.
- 동일 data/version/seed는 동일 결과를 생성한다.
- 기존 실패 결과, hash, report, lock과 rollback 기록을 삭제·수정하지 않는다.
- 사용자 승인 전 다음 Gate로 진행하지 않는다.
- `main`에 직접 작업하거나 병합하지 않는다.
- 모든 구현은 별도 브랜치와 Draft PR에서 수행한다.

## 2. 필수 읽기

1. `handoff/FULL_HISTORY_AUDIT_GATE1_TO_R3M3.md`
2. `docs/MINIMAL_PRODUCT_COMPLETION_ROADMAP.md`
3. `docs/PRODUCT_GATE_P1_RELEASE_CANDIDATE_SPEC.md`
4. `docs/PRODUCT_GATE_P2_QA_SPEC.md`
5. `docs/PRODUCT_GATE_P2_QA_IMPLEMENTATION.md`
6. `reports/product_p1_acceptance.json`
7. `reports/product_p1_acceptance_lock.json`
8. `reports/product_p2_official_reconciliation.json`
9. `reports/product_p2_qa.json`
10. `reports/product_p2_qa_lock.json`
11. `release/product_p2_source_manifest.json`
12. `handoff/PROJECT_HANDOFF.md`
13. 기존 Gate report·lock 파일

## 3. 현재 단계

```text
branch = qa/product-p2-data-integration
base = feature/product-p1-release-candidate
Draft PR = #45
P1 contract = product-release-candidate-1.0.0
P2 contract = product-qa-1.0.0
P1 assembly = P1_ASSEMBLED
P2 specification = APPROVED / MERGED
P2 QA implementation = IMPLEMENTED
P2 workflow = 28639851500 / SUCCESS
P2 final decision = P2_QA_BLOCKED
P3 = BLOCKED
main merge = NOT PERFORMED
```

## 4. 잠금값

```text
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
P1 acceptance SHA-256 = a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139
P1 workflow = 28525611462 / SUCCESS
data version = draws-2026.06.27-r1
data range = 1..1230
data records = 1230
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
final distribution = M0_ONLY
weights = M0=1, M1=M2=M3=M4=0
```

P2는 위 baseline을 수정하지 않고 read-only로 검증했다.

## 5. P2 실행 결과

```text
QA execution commit = 33390760cb6857fb25944dc6879c184561eeecb5
workflow run = 28639851500
workflow conclusion = SUCCESS
Python 3.11.15 = PASS
Python 3.12.13 = PASS
B1 = PASS
B2~B5 = BLOCKED
B6~B18 = PASS
P2 = P2_QA_BLOCKED
```

동행복권 공식 JSON endpoint와 공식 결과 페이지가 모두 timeout되어 authoritative source를 평가할 수 없었다. 비공식 출처로 대체하지 않았다.

Canonical state:

```text
AUTO_CHECKED
-> RECONCILIATION_PENDING
-> OFFICIAL_RECONCILIATION_BLOCKED
```

`OFFICIALLY_VERIFIED`와 `LOCKED`에는 도달하지 않았다. 평가된 항목의 FAIL은 없다.

## 6. P2 evidence lock

```text
reconciliation report = reports/product_p2_official_reconciliation.json
reconciliation SHA-256 = cc57190b898b8593d306c84ded1b3d4a2ab67202230598b7de5b4288cec916c1
QA report = reports/product_p2_qa.json
QA report SHA-256 = 518883ba634cfa86a0a38935f2bf84f447c5d1bec3cf2ed783e9fb9e5ac5c133
QA lock = reports/product_p2_qa_lock.json
source manifest = release/product_p2_source_manifest.json
source manifest SHA-256 = 4a5cfe663086995639d2a7046a4e487b5e388302c25b33c269e066cf1c0c5a63
workflow artifact id = 8058273810
workflow artifact digest = sha256:e1343d717ca3ba5ac6e35320b87e4eb5e09c38d93a48a3824c6baef1547c9983
```

## 7. 판정 규칙

```text
P2_QA_PASS = B1~B18 all PASS
P2_QA_BLOCKED = authoritative official source unavailable
P2_QA_FAIL = any evaluated criterion failure
```

Conditional PASS와 waiver는 없다.

## 8. 현재 금지사항

사용자 별도 승인 전 다음을 수행하지 않는다.

- P3 HTML MVP
- historical/prospective Walk-forward
- M1~M4 활성화 또는 튜닝
- canonical data 수정
- 비공식 출처를 이용한 승인상태 승격
- HTML 수정·배포
- CAL·SEALED
- 모바일 UI·Supabase
- `main` 병합

## 9. 다음 승인 대기

현재 다음 Gate는 없다. authoritative official source 접근이 가능한 조건에서 P2 공식 대조만 재시도할 수 있다. B1~B18 전 항목 PASS와 사용자 별도 승인 전에는 P3로 진행하지 않는다.
