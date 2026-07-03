# Project Handoff

최종 갱신일: 2026-07-03  
현재 브랜치: `qa/product-p2-data-integration`  
기준 브랜치: `feature/product-p1-release-candidate`  
Draft PR: #45  
계약: `product-qa-1.0.0`

## 현재 판정

```text
P1 = P1_ASSEMBLED
P1 lock = 099d917abd1b635c830fee343a47d3bd23e0c052
P2 specification = APPROVED / MERGED
P2 implementation = IMPLEMENTED
P2 workflow = 28639851500 / SUCCESS
P2 official reconciliation = OFFICIAL_RECONCILIATION_BLOCKED
P2 final = P2_QA_BLOCKED
B1, B6~B18 = PASS
B2~B5 = BLOCKED
P3 = BLOCKED
main merge = NOT PERFORMED
```

Workflow는 성공했지만 동행복권 공식 JSON endpoint와 공식 결과 페이지가 모두 timeout되어 authoritative source를 평가하지 못했다. 비공식 출처로 대체하지 않았으며 평가된 항목의 FAIL은 없다.

## Locked baseline

```text
P1 acceptance SHA-256 = a86049cdd041a92ab9c4f644d607c7212313c464d2fbb333ce1fda24dadaa139
data version = draws-2026.06.27-r1
range / records = 1..1230 / 1230
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
final distribution = M0_ONLY
weights = M0=1, M1=M2=M3=M4=0
```

P2는 위 baseline과 canonical data를 수정하지 않고 검증했다.

## 실행 결과

```text
QA execution commit = 33390760cb6857fb25944dc6879c184561eeecb5
Python 3.11.15 / 3.12.13 = PASS
artifact id = 8058273810
artifact digest = sha256:e1343d717ca3ba5ac6e35320b87e4eb5e09c38d93a48a3824c6baef1547c9983
```

검증 완료 항목: JSON Schema, 미래 데이터 차단, shadow 격리, 3회 반복, Python 교차 재현성, hash 재계산, assembly/rollback manifest, M0-only disclosure, frozen history.

공식 대조 상태:

```text
expected = 1230
matched = 0
missing / unresolved = 1230 / 1230
mismatch = 0
AUTO_CHECKED -> RECONCILIATION_PENDING -> OFFICIAL_RECONCILIATION_BLOCKED
```

`OFFICIALLY_VERIFIED`와 `LOCKED`에는 도달하지 않았다.

## Evidence

```text
reports/product_p2_official_reconciliation.json
reports/product_p2_qa.json
reports/product_p2_qa_lock.json
release/product_p2_source_manifest.json
```

```text
reconciliation SHA-256 = cc57190b898b8593d306c84ded1b3d4a2ab67202230598b7de5b4288cec916c1
QA report SHA-256 = 518883ba634cfa86a0a38935f2bf84f447c5d1bec3cf2ed783e9fb9e5ac5c133
source manifest SHA-256 = 4a5cfe663086995639d2a7046a4e487b5e388302c25b33c269e066cf1c0c5a63
```

## 금지 범위

P3, Walk-forward, M1~M4 활성화, canonical data 수정, HTML, CAL, SEALED, 모바일/Supabase, `main` 병합은 진행하지 않는다. 기존 failure·hash·report·lock·rollback은 보존한다.

## 다음 승인 경계

현재 다음 Gate는 없다. authoritative official source 접근이 가능한 조건에서 P2 공식 대조만 재시도한다. B1~B18 전 항목 PASS와 사용자 별도 승인 전에는 P3로 진행하지 않는다.
