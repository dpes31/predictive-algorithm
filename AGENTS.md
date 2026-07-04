# AGENTS.md

모든 작업 전 이 문서와 실제 branch·commit·report·lock 상태를 대조한다.

## 공통 원칙

- 미래 데이터 누출 금지
- 동일 data/version/config/seed에서 재현 가능한 결과
- 실패 결과, hash, report, lock, rollback, workflow history 보존
- `main` 직접 작업·병합 금지
- 외부 결과 사이트 접속, 외부기관 문의, 새 출처 탐색 금지
- 사용자가 제공하지 않은 물리변수 수집·추정 금지
- force push·history rewrite·failure evidence 삭제 금지

## 최종 제품 상태

```text
current branch = release/product-closeout-c4-research-lock
base branch = feature/product-p1-release-candidate
base commit = f60b7278a88635596c502e34c4b56b535db8c1d7

P1 = P1_ASSEMBLED
A1 = A1_SPEC_COMPLETE / MERGED
A2 = A2_IMPLEMENTATION_PASS / MERGED
A3 = A3_SPEC_COMPLETE / MERGED
A4 = A4_EVALUATION_FAIL / Draft PR #51 preserved
C1 = PRODUCT_CLOSEOUT_SPEC_COMPLETE / MERGED
C2 = PRODUCT_CLOSEOUT_QA_PASS / MERGED
C3 = PRODUCT_CLOSEOUT_HTML_PASS / MERGED
C4 = PRODUCT_READY_RESEARCH_M0 / LOCKED

release contract = product-closeout-release-lock-1.0.0
rollback mode = CONTROL_M0
development complete = true
next Gate = NONE
```

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
prediction hash=119f28875355952fa5c80e2095e70c096aee081ee56c750fa4caf2e373c5fe32
```

## 필수 읽기

1. `handoff/PROJECT_HANDOFF.md`
2. `docs/PRODUCT_READY_RESEARCH_M0.md`
3. `release/research_release_manifest.json`
4. `release/public_wording_lock.json`
5. `release/product_closeout_c4_rollback_manifest.json`
6. `reports/product_closeout_c4_final.json`
7. `reports/product_closeout_c4_release_lock.json`
8. C1·C2·C3 report·lock·rollback
9. Draft PR #51과 모든 A4 failure evidence

## 최종 제한

이 저장소의 현재 제품은 연구용 deterministic M0 번호 생성기다. 당첨번호 예측 또는 당첨확률 향상을 주장하지 않는다. 공개배포, `main` 병합, A4 재평가, parameter 변경, 실제 hypothesis·physical entry 활성화, 외부접속, CAL, SEALED, 모바일 작업은 별도 승인 전 수행하지 않는다.
