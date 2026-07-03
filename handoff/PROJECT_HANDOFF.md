# Project Handoff

최종 갱신일: 2026-07-03  
현재 작업: **Algorithm Integration Gate A1 상세 명세 완료**  
현재 브랜치: `docs/algorithm-integration-a1-spec`  
기준 브랜치: `feature/product-p1-release-candidate`  
기준 병합 커밋: `9d6766d21e51758cca1840c8098645d0e0ee8042`  
계약: `research-ensemble-spec-1.0.0`

## 현재 상태

```text
P1 = P1_ASSEMBLED
P1 implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
PR #45 = CLOSED / NOT MERGED
PR #46 = MERGED
external access = PERMANENTLY RETIRED
A1 specification = A1_SPEC_COMPLETE
A1 user approval = PENDING
A2 implementation = NOT AUTHORIZED
Walk-forward = NOT RUN
HTML / CAL / SEALED / mobile = NOT RUN
main merge = NOT PERFORMED
```

## 필수 읽기

1. `docs/EXTERNAL_ACCESS_RETIREMENT_POLICY.md`
2. `docs/ALGORITHM_IMPROVEMENT_AUDIT.md`
3. `reports/algorithm_improvement_audit_lock.json`
4. `docs/ALGORITHM_INTEGRATION_A1_SPEC.md`
5. `docs/ALGORITHM_INTEGRATION_A1_REGISTRIES.md`
6. `docs/ALGORITHM_INTEGRATION_A1_ACCEPTANCE.md`
7. `reports/algorithm_integration_a1_spec_report.json`
8. `reports/algorithm_integration_a1_spec_lock.json`
9. `reports/product_p1_acceptance.json`
10. `reports/product_p1_acceptance_lock.json`
11. 기존 Gate report·lock

## A1 핵심 계약

```text
CONTROL_M0 = 기존 P1 rollback 경로
RESEARCH_ENSEMBLE = 명시적 연구모드
score contract = score-45-1.0.0
hypothesis registry = hypothesis-registry-1.0.0
user input registry = user-input-registry-1.0.0
physical adapter = user-physical-adapter-1.0.0
output schema = research-ensemble-output-1.0.0
```

고정 기여상한:

```text
historical total <= 0.60
single hypothesis <= 0.10
hypothesis total <= 0.25
single physical field <= 0.05
physical total <= 0.15
final logit absolute cap = 0.35
```

M1 persistence와 M2 reversal은 target 이전 loss만 사용하는 bounded sequential weight로 통합한다. M3는 승인된 pre-target change evidence가 active일 때만 eligible이며 그 외에는 0이다. 과거 `PREDICTABLE_GROUP_FAIL` parameter는 변경하지 않는다.

사용자 관점과 물리변수는 승인 registry만 사용한다. 공통 nominal 값처럼 번호 간 차이를 만들지 못하는 값은 직접 contribution 0이다.

## 영구 금지

- 외부 당첨결과 사이트 접속과 재시도
- 외부기관 문의
- 새로운 공식·비공식 출처 탐색
- 사용자가 제공하지 않은 물리변수 수집 또는 추정
- B2~B5를 알고리즘 개발 차단조건으로 복원
- 과거 failure·hash·report·lock·rollback 수정 또는 삭제

## A1 판정

`docs/ALGORITHM_INTEGRATION_A1_ACCEPTANCE.md`의 D1~D10이 모두 문서화되어 `A1_SPEC_COMPLETE`다. 이 판정은 구현 통과나 예측력 검증을 의미하지 않는다.

## 다음 승인 경계

사용자 승인 후에만 `Algorithm Integration Gate A2`로 이동한다.

```text
next contract = research-ensemble-implementation-1.0.0
scope = Python implementation and unit tests only
```

A2 승인 전 Python 구현, Walk-forward, hyperparameter 탐색, HTML, CAL, SEALED, 모바일 및 `main` 병합을 진행하지 않는다.
