# Algorithm Integration Gate A3 Acceptance Contract

상태: `SPEC COMPLETE / A4 NOT AUTHORIZED`

계약: `research-ensemble-evaluation-spec-1.0.0`

## A3 판정

`A3_SPEC_COMPLETE`는 다음 D1~D12가 모두 문서화되고 report·lock이 일치할 때만 가능하다.

```text
D1 CONTROL_M0 대비 단일 confirmatory comparison
D2 historical-only와 10개 ablation lane
D3 minimum history·warm-up·target sequence 고정
D4 target-1 cutoff와 leakage 차단
D5 joint log-score primary metric
D6 Brier·calibration·temporal stability
D7 multiple-comparison 및 Holm policy
D8 미승인 user hypothesis·physical lane 차단
D9 A4 PASS·FAIL·BLOCKED 정의
D10 version·hash·report·lock·rollback
D11 P1·A1·A2 및 기존 failure evidence 보존
D12 A4 별도 승인 경계
```

필수 문서 또는 lock을 만들 수 없으면 `A3_SPEC_BLOCKED`다. Conditional PASS는 없다.

## A4 판정 상태

```text
A4_EVALUATION_PASS
A4_EVALUATION_FAIL
A4_EVALUATION_BLOCKED
```

Poor performance는 BLOCKED가 아니라 FAIL이다.

## A4 integrity 기준

다음은 모두 mandatory다.

```text
E1 contract와 base commit 일치
E2 dataset version·range·count·hash 일치
E3 targets가 정확히 352..1230, 879개
E4 모든 target input_last_draw = target-1
E5 미래 데이터 접근 0
E6 CONTROL_M0 regression 0
E7 10개 lane 모두 생성
E8 empty-registry equivalence 전부 PASS
E9 미승인 user·physical lane 실행 0
E10 finite·normalized exact distribution
E11 Python 3.11/3.12 각 2회 동일
E12 target metric row 누락 0
E13 모든 stored hash 독립 재계산 일치
E14 network dependency 0
E15 prior report·lock·rollback mutation 0
E16 parameter·window·threshold·target subset 사후 변경 0
```

## A4 PASS 기준

다음을 모두 만족해야 한다.

```text
E1~E16 all PASS
mean joint log-score difference > 0
one-sided 95% moving-block-bootstrap lower bound > 0
mean marginal Brier gain >= 0
4개 chronological quarter 중 3개 이상 mean delta > 0
final cumulative joint log-score difference > 0
runtime·repeat 간 manifest·metrics·decision hash 동일
research-only disclosure 유지
```

Diagnostic ablation significance와 candidate hit count는 PASS 기준을 대체하지 않는다.

## A4 FAIL 기준

평가가 실행된 뒤 mandatory integrity 또는 PASS 기준 중 하나라도 충족하지 못하면 FAIL이다. Dataset hash mismatch, leakage, nondeterminism, target 누락, primary·Brier·stability 기준 미달도 FAIL이다. 모든 partial·failed result와 hash를 보존한다.

## A4 BLOCKED 기준

유효 target row를 만들기 전에 승인된 source artifact, dataset 파일, Python 3.11/3.12 runtime 또는 offline dependency가 없어 실행 자체가 불가능할 때만 BLOCKED다.

## 즉시 중단규칙

다음이 발견되면 신규 target 실행을 중단한다.

- target 또는 미래 outcome을 prediction 입력에 사용
- CONTROL_M0 변경
- 미승인 registry entry 활성화
- 외부 URL·network client 실행
- prior lock mutation
- NaN·infinity·invalid probability·hash mismatch
- target range 또는 fixed config 변경

중단 전 결과는 partial evidence로 남긴다.

## A4 필수 산출물

- frozen evaluation harness
- target-level metric rows
- lane aggregate metrics
- calibration 및 multiple-comparison report
- equivalence 및 runtime reproducibility report
- implementation report·lock
- result report·lock
- rollback manifest

## Rollback

A4는 별도 branch와 Draft PR에서 수행한다. rollback은 A4 변경만 제거하고 Product P1, A1, A2, 기존 failure evidence와 A3 report·lock을 보존한다. Force push와 history rewrite를 금지한다.

## 다음 승인 경계

A3 승인 전 A4를 구현하거나 실행하지 않는다.

```text
next gate = Algorithm Integration Gate A4
next contract = research-ensemble-evaluation-implementation-1.0.0
scope = frozen evaluation harness and fixed retrospective evaluation only
```
