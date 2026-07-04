# Gate 2-3R 합성 재검증 결과

## 1. 결론

**Gate 2-3R은 통과하지 못했습니다.**

보정으로 지속·반전 신호의 탐지력은 개선됐지만, 균등 null 오탐률과 M3·고정편향·Pair positive-control 기준을 충족하지 못했습니다. 따라서 Gate 상태는 `RESEARCH`, 최종분포는 `M0 100%`를 유지하며 Gate 2-4 실제 데이터 Walk-forward는 계속 차단합니다.

## 2. 실험 계약

- 모델 버전: `2.1.0-research`
- Feature contract: `1.1.0`
- Temperature grid: `0.05 / 0.10 / 0.20 / 0.50 / 1.00`
- Null calibration: 1,000개 × 1,230회
- 독립 null validation: 1,000개 × 1,230회
- Positive-control: 시나리오당 100개 × 1,230회
- Alpha: 0.001
- 과거 실제 당첨번호 사용: 없음

## 3. 균등 null 오탐 결과

| 검사 | 이벤트 | 관측률 | 95% 단측 상한 | 0.1% 점추정 기준 |
|---|---:|---:|---:|---|
| Gate proxy | 4/1,000 | 0.40% | 0.9130% | 미통과 |
| M3 raw diagnostic | 0/1,000 | 0.00% | 0.2991% | 점추정 통과·상한 미통과 |
| 전체 Pair 탐색 | 0/1,000 | 0.00% | 0.2991% | 점추정 통과·상한 미통과 |
| 사전지정 Pair | 0/1,000 | 0.00% | 0.2991% | 점추정 통과·상한 미통과 |

가장 중요한 실패는 Gate proxy 오탐이 **4/1,000, 0.4%**로 사전기준 0.1%를 초과한 것입니다.

## 4. Positive-control 결과

| 시나리오 | 기대모형 | 엄격 탐지율 | 기대모형 양의 점수율 | Proxy/진단 탐지율 |
|---|---|---:|---:|---:|
| 고정 번호 편향 +2% | M1 | 0% | 0% | 1% |
| 고정 번호 편향 +5% | M1 | 0% | 0% | 0% |
| 고정 번호 편향 +10% | M1 | 0% | 0% | 3% |
| 최근 52회 지속 과정 | M1 | 100% | 100% | 100% |
| 최근 52회 반전 과정 | M2 | 71% | 79% | 68% |
| 400·800회 구조변화 | M3 | 0% | 0% | M3 0% |
| 52회 일시 편향 | M3 | 0% | 0% | M3 0% |
| Pair factor 1.25 | Pair | 0% | — | Target Pair 0% |
| Pair factor 1.50 | Pair | 0% | — | Target Pair 0% |
| Pair factor 2.00 | Pair | 1% | — | Target Pair 1% |
| Pair factor 3.00 | Pair | 22% | — | Target Pair 22% |

### 개선된 부분

- 지속 과정 M1 엄격 탐지율: **0% → 100%**
- 반전 과정 M2 엄격 탐지율: **0% → 71%**
- Temperature sub-expert가 기존 `η=±z`의 과확신을 완화해 동적 과정의 Log Loss와 Brier Score가 개선됐습니다.

### 여전히 실패한 부분

- 고정 번호 편향 2%·5%·10%: 엄격 탐지율 모두 0%
- 반전 과정: 71%로 80% 기준 미달
- M3 구조변화·일시 편향: 활성화 및 엄격 탐지 모두 0%
- Pair factor 3.0: 사전지정 Pair 탐지율 22%
- 사전범위에서 80% power를 달성한 fixed-bias 또는 Pair 효과크기 없음

## 5. M3의 구조적 검증 불가능성

이번 M3 0%는 단순히 신호가 약해서만 발생한 결과가 아닙니다.

```text
Null calibration series = 1,000
최소 plus-one empirical p = 1 / 1,001 = 0.000999001
4개 진단 Holm 최소 adjusted p = 4 / 1,001 = 0.003996004
승인 alpha = 0.001
```

따라서 현재 계약에서는 **어떤 관측값이 나와도 M3 adjusted p가 0.001 이하가 될 수 없습니다.** Raw diagnostic 분리로 3.0 포화 문제는 제거됐지만, `1,000회 Monte Carlo + plus-one p + 4개 Holm` 조합 자체가 M3 활성화를 수학적으로 차단합니다.

Raw null 99.9% 기준은 다음과 같습니다.

- Shift 52: 4.9038
- Shift 104: 4.8954
- CUSUM: 5.9453
- 전체 Pair max: 9.1706
- 사전지정 Pair: 5.9597

## 6. Gate 판정

```text
Gate 2-3R: NOT PASSED
Gate state: RESEARCH
Final distribution: M0 only
Gate 2-4: BLOCKED
Actual candidate release: BLOCKED
```

## 7. 다음 보정에 필요한 별도 승인사항

현재 승인 범위를 넘어서는 변경이므로 자동 적용하지 않았습니다.

1. M3 검정 해상도 해결
   - Null calibration을 최소 3,999개 이상으로 확대하거나
   - Holm 대신 사전등록된 단일 omnibus/maxT 검정을 사용
2. Gate proxy 오탐 제어 강화
   - 0.4% 오탐 원인 진단 및 score threshold 보수화
3. 고정편향 모형 분리 검토
   - 최근 변화형 M1과 장기 고정편향 탐지기를 같은 모델로 묶는 구조 재검토
4. 반전 과정 71%를 80% 이상으로 올릴지, 71%를 탐지 한계로 명시할지 결정
5. Pair interaction은 계속 예측 비활성 유지 권고

## 8. 실행 투명성

GitHub 브랜치와 Draft PR에 2.1.0 보정 코드를 반영했습니다. 다만 사용 가능한 GitHub 연결 도구로는 Actions workflow를 추가·디스패치할 수 없어, 전체 수치 실험은 커밋된 수식을 그대로 옮긴 결정론적 standalone mirror에서 실행했습니다. GitHub CI 확인은 아직 완료되지 않았으며, 이를 검증 완료로 과장하지 않습니다.

Report hash: `ec57a01e7781d5679cc8fc1b1c146055b06b6836740924cfbb0f1bfd6bef15c6`
