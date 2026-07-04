# AGENTS.md

모든 작업 전 이 문서와 실제 branch·commit·PR·report·lock 상태를 대조한다.

## 공통 원칙

- 미래 데이터 누출 금지
- 동일 data/version/config/seed에서 재현 가능한 결과
- 실패 결과, hash, report, lock, rollback, workflow history 보존
- `main` 직접 작업 금지
- 사용자 승인 없는 `main` 병합 금지
- 외부 결과 사이트 검증·수집, 외부기관 문의, 새 출처 탐색 금지
- 사용자가 제공하지 않은 물리변수 수집·추정 금지
- force push·history rewrite·failure evidence 삭제 금지

## 실제 저장소 상태

```text
historical C4 status = PRODUCT_READY_RESEARCH_M0 / LOCKED
PR #59 = MERGED to main
PR #59 merge commit = a6181fcb41a2de59f63c7c0912af63091f75dc35

current work branch = codex/pr59-production-final-closeout
base branch = main
base commit = a6181fcb41a2de59f63c7c0912af63091f75dc35
Draft PR = #60 / OPEN / NOT MERGED

post-merge closeout result = PR59_PRODUCTION_CLOSEOUT_BLOCKED_DEPLOYMENT
implementation complete = true
Python 3.11 regression = PASS
Python 3.12 regression = PASS
local actual browser click = PASS
Production deployment = NOT COMPLETE
Production actual browser click = NOT COMPLETED
next Gate = NONE
```

PR #60은 알고리즘 개발 Gate가 아니다. PR #59 이후 Production 배포·실제 클릭을 닫기 위한 사후 Closeout 브랜치다.

## 잠긴 제품 기준

```text
data range = 1..1230
record count = 1230
data version = draws-2026.06.27-r1
data SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification status = auto_checked
officially locked = false

final distribution = M0_ONLY
M0=1.0, M1=M2=M3=M4=0.0
statistical_edge=false
reason=no_validated_nonuniform_signal
research_only=true
public_release_allowed=false
locked prediction hash=119f28875355952fa5c80e2095e70c096aee081ee56c750fa4caf2e373c5fe32
```

다음 파일은 PR #60에서 변경하지 않는다.

- `data/draws.json`
- `schemas/product_prediction.schema.json`
- `public/product-prediction.json`
- `product/config.py`
- `product/run_prediction.py`
- `product/dynamic_prediction.py`
- 기존 C1~C4 report·lock·rollback
- Draft PR #51 및 모든 A4 failure evidence

## 현재 검증 결과

```text
Gate 1 frozen offline integrity = PASS / run 28694335706
Product P1 Assembly = PASS / run 28694335708
Product full UI workflow = run 28694335697
Python 3.11 = PASS
Python 3.12 = PASS
local Playwright actual click = PASS

Vercel Preview = authentication protection page
Production root = HTTP 200 but PR #59 application marker missing
Production /api/archive = HTTP 404
new Vercel deployment = blocked by api-deployments-free-per-day
```

현재 차단은 CONTROL_M0 또는 앱 코드 실패로 판정하지 않는다. Vercel 배포 제한, Preview 인증 보호, Production 미갱신으로 인해 원격 실제 클릭을 시작하지 못한 상태다.

## 필수 읽기

1. `handoff/PROJECT_HANDOFF.md`
2. `docs/PRODUCT_READY_RESEARCH_M0.md`
3. `release/research_release_manifest.json`
4. `release/public_wording_lock.json`
5. `release/product_closeout_c4_rollback_manifest.json`
6. `reports/product_closeout_c4_final.json`
7. `reports/product_closeout_c4_release_lock.json`
8. `reports/pr59_production_final_closeout.json`
9. `reports/pr59_production_final_closeout_lock.json`
10. `release/pr59_production_final_closeout_rollback_manifest.json`
11. Draft PR #51과 모든 A4 failure evidence

## 다음 승인 전 금지

- PR #60의 `main` 병합
- Production 성공 판정
- 기존 blocked report·lock·rollback 수정 또는 삭제
- CONTROL_M0, 가중치, data, schema, fixture 변경
- A4 재평가 또는 다음 Gate 진행

다음 승인이 필요한 작업은 PR #60 병합과 Vercel Production 재배포 후 실제 클릭 재검증뿐이다. 성공 시 기존 blocked 기록은 유지하고 별도의 append-only success record를 추가한다.
