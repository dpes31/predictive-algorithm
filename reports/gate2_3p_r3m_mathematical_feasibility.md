# Gate 2-3P-R3M Mathematical Feasibility Report

상태: 명세 전 수학적 적합성 분석 완료  
작성일: 2026-07-01  
기준 결과: Gate 2-3P-R3 `NO_ELIGIBLE_CONFIG`  
기준 모델: `4.0.0-research`  
제안 후속 모델: `5.0.0-research`  

## 1. 결론

현재 계약의 다음 네 조건은 동시에 만족할 수 없다.

1. activation threshold = `1000`
2. M3 evidence life = `208 draws`
3. mandatory effect = `lift 1.25`
4. strict detection power = `80%`

Gate 2-3P-R3의 0/200 활성화는 단순 하이퍼파라미터 실패가 아니라 정보량 부족과 mixture dilution이 결합된 구조적 결과다.

Threshold `1000`과 실패 결과는 유지한다. 해결책은 threshold를 낮추는 것이 아니라 detector evidence horizon과 post-activation active life를 분리하는 것이다.

```text
pre-activation evidence horizon = 520 draws
post-activation deployable life = 208 draws
activation threshold = 1000 unchanged
```

## 2. 기준 시나리오

P4 regime reversal은 다음 분포를 사용한다.

- 전체 번호: 45
- 선택 번호: 6
- favored set 크기: 10
- favored weight: 1.25
- change point: 615
- 전반 favored: 1~10
- 후반 favored: 36~45

균등 null에서 favored 선택 개수를 `K`라 하면 대안분포는 다음과 같다.

```text
P_r(S) ∝ r ^ |S ∩ F|
r = 1.25
|F| = 10
|S| = 6
```

정규화 상수 비율:

```text
Z(r) / C(45, 6) = 1.3786734752438325
```

대안분포에서 기대 favored 개수:

```text
E_r[K] = 1.5479558826836606
```

번호별 포함확률:

```text
favored number = 0.15479558826836606
other number   = 0.12720126049475255
uniform p0     = 0.13333333333333333
```

## 3. Oracle information bound

Favored set과 change point를 사전에 정확히 아는 최적 oracle likelihood-ratio조차 회차당 기대 log evidence가 다음에 불과하다.

```text
KL(P_1.25 || P_0)
= E_r[K] * log(1.25) - log(Z(r) / C(45,6))
= 0.024294585890841103 nats / draw
```

Threshold 1000의 log scale은 다음이다.

```text
log(1000) = 6.907755278982137
```

208회 동안 oracle이 얻는 기대 log evidence:

```text
208 * KL = 5.053273865294949
exp(5.053273865294949) = 156.53409807084515
```

즉, mixture dilution이 전혀 없는 oracle조차 208회 기대 evidence가 1000에 도달하지 못한다.

정규근사 기준 최종시점 threshold 초과확률은 약 28.3%다. 이는 요구된 80%와 양립하지 않는다. 이 값은 설계 판단용 근사치이며 후속 구현 시 exact deterministic simulation으로 재확인해야 한다.

## 4. 80% power에 필요한 최소 정보기간

Oracle 단일가설 기준으로 다음 근사를 사용한다.

```text
n * KL - z_0.80 * sqrt(n * Var(log LR)) >= log(1000)
```

계산 결과:

```text
single oracle hypothesis ≈ 448 draws
```

Mixture는 true component에 부여된 초기 wealth `w`만큼 추가 penalty를 발생시킨다.

```text
required component evidence ≈ 1000 / w
additional log penalty = log(1 / w)
```

정규근사상 80% power 필요기간:

| 동등가설 수 | true weight | 약식 필요 draw |
|---:|---:|---:|
| 1 | 1 | 448 |
| 2 | 1/2 | 483 |
| 4 | 1/4 | 518 |
| 8 | 1/8 | 552 |
| 16 | 1/16 | 586 |
| 45 | 1/45 | 636 |

따라서 `520 draws`는 최대 4개의 핵심 구조가설에 제한된 detector에서만 lift 1.25 / threshold 1000 / power 80%를 근사적으로 만족할 수 있는 최소 실용 구간이다.

520회에서 정규근사 최종시점 power:

```text
single oracle hypothesis ≈ 86.9%
4-way equal mixture      ≈ 80.3%
8-way equal mixture      ≈ 76.3%
```

## 5. 기존 M3가 1.21에 머문 이유

기존 M3는 다음 축을 동시에 평균 mixture했다.

- 45 numbers
- 8 betting fractions
- 13-draw restart origins
- 최대 208회 life 안의 다수 active restarts

한 시점에 최대 약 16개 restart가 존재하므로 명목 component 수는 최대 다음 규모다.

```text
45 * 8 * 16 = 5,760
```

모든 component를 균등 평균하면 true component의 초기 wealth는 약 `1 / 5760`이다. Threshold 1000을 넘으려면 true component 자체는 대략 `5,760,000` 수준까지 성장해야 한다.

하지만 lift 1.25의 208회 oracle 기대 evidence는 약 156.5에 불과하다. 따라서 R3에서 관측된 최대 e-value `1.2128703085422197`은 detector 구현오류만으로 설명되는 값이 아니라 mixture 구조상 예상 가능한 결과다.

## 6. 양립 가능성 판정

| 계약 조합 | 판정 |
|---|---|
| threshold 1000 + 208 evidence life + lift 1.25 + 80% power | 불가능 |
| threshold 1000 + 520 evidence horizon + 208 active life + 4-way 핵심 mixture | 조건부 가능 |
| threshold 완화 | 금지 |
| 실패 seed·scenario 제거 | 금지 |
| 45×8×restart 균등 mixture 유지 | 부적합 |

## 7. 신규 설계 원칙

1. Threshold `1000` 유지
2. Post-activation active life `208` 유지
3. Pre-activation evidence horizon을 `520`으로 분리
4. 45개 번호별 detector 대신 exact 6-of-45 group likelihood-ratio 사용
5. 핵심 구조가설 mixture를 최대 4개 primary hypotheses로 제한
6. 나머지 exploratory hypotheses는 activation 권한 없이 diagnostic-only로 분리
7. Candidate group은 결과를 본 뒤 선택하지 않고 past-only predict-then-bet 방식으로 고정
8. Oracle feasibility → predictable group learning → full detector 순서로 검증
9. Oracle gate가 실패하면 후속 detector 구현 중단
10. R4 CAL·SEALED는 새 구조의 DEV 적격 config가 잠기기 전까지 계속 차단

## 8. 최종 판단

`4.0.0-research` M3를 파라미터만 조정해서는 해결할 수 없다. 새로운 구조는 breaking architecture change이므로 제안 버전은 `5.0.0-research`다.

이 보고서는 명세 판단 자료이며 Python 구현, 추가 DEV, CAL, SEALED를 포함하지 않는다.
