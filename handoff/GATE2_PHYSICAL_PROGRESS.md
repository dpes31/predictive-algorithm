# Gate 2 Physical Evidence Progress

최종 갱신: 2026-06-30  
현재 브랜치: `feature/gate2p3-validation`  
기준 브랜치: `feature/gate2p2-engine`  
관련 이슈: #14  
Draft PR: #15

## 전체 진행률

| 단계 | 내용 | 상태 | 진척도 |
|---|---|---|---:|
| Gate 2-3P-1 | M4·데이터·검증 명세 | 사용자 승인 완료 | 100% |
| Gate 2-3P-2 | Python 구현 | 사용자 승인 완료 | 100% |
| Gate 2-3P-3 | 합성 null/positive 전체 재검증 | **NOT PASSED** | 100% |
| Gate 2-3P-R | 보정 명세·재설계 | 사용자 결정 대기 | 0% |
| Gate P-1 | 실제 메타데이터 100회 파일럿 | 차단 | 0% |
| Gate 2-4P | 실제 데이터 Walk-forward | 차단 | 0% |
| 모바일 MVP | 5세트 결과 UI | 차단 | 0% |

## Gate 2-3P-3 실행 규모

- M3 maxT null calibration: 10,000 series
- M4 model null calibration: 4,000 series
- independent null validation: 5,000 series
- positive controls: 12,000 series
- robustness: 6,000 series
- total: 37,000 series
- effect sizes: 1.05 / 1.10 / 1.25 / 1.50
- 20 deterministic shards

## 실행 무결성

- GitHub Actions run: `28451343507`
- workflow conclusion: `success`
- head SHA: `56f5ace469ee42a1b5743029092585724819796b`
- 20 shards: all success
- aggregate: success
- summary artifact: `7983755657`
- artifact digest: `sha256:58526bd3b6f9a178575092f0affdb29d115139bd9dd1210dac04ef768dbe7ca7`
- report hash: `b59cc753eda4058f0b55a685a136da01a327dd6b6b7fc33b10fd4758dfc36948`

CI 성공은 실험 실행 성공을 의미하며 모델 통과를 의미하지 않는다.

## 판정

```text
Gate 2-3P-3 = NOT PASSED
Model state = RESEARCH
Final deployable distribution = M0 only
M4 deployable weight = 0
```

## Null 결과

- proxy false activation: 5/5,000 = 0.100000%
- proxy one-sided 95% upper: 0.205288% — 기준 0.2% 초과
- M3 false activation: 8/5,000 = 0.160000% — 기준 0.1% 초과
- irrelevant metadata scenario activation: 0.120048% — 기준 0.1% 초과
- irrelevant metadata mean M4 Δ Log Loss: -0.009065

관측 proxy rate는 경계값 0.1%를 만족했지만 신뢰상한과 M3 오탐 기준을 통과하지 못했다.

## Lift 1.25 Positive-control 결과

| Scenario | Strict detection | Mean Δ Log Loss | Mean Δ Brier | Direction | M3 activation |
|---|---:|---:|---:|---:|---:|
| ball set | 0.8% | -0.005348 | -0.00002796 | 79.5% | 0.0% |
| machine | 24.2% | 0.000921 | 0.00000528 | 98.8% | 0.0% |
| machine × ball | 0.8% | -0.006698 | -0.00003508 | 75.5% | 0.0% |
| regime reversal | 0.0% | 0.000507 | 0.00000322 | 89.5% | 0.2% |
| temporary environment | 0.0% | -0.008517 | -0.00004475 | 56.1% | 0.0% |
| pretest shared | 0.4% | -0.004959 | -0.00002601 | 79.1% | 0.0% |

Frozen strict-detection target was 80%. 모든 시나리오가 미달했다.

## Robustness 결과

통과:

- missingness 증가에 따라 M4 strength가 증가하지 않음
- independent pretest activation 0%
- direction reversal 208 draws 이내 적응 100%
- mean reversal adaptation delay 48 draws

실패:

- post-draw-error scenario activation 2.6%
- signal-decay return within 208 draws 65.8% — 기준 80% 미달
- missingness 증가 시 direction accuracy 급락
- M3 regime reversal activation 0.2% — 기준 80% 미달

## 실패 원인 가설

다음은 결과로부터의 진단이며 아직 승인된 보정안이 아니다.

1. M4가 유효·무관 context를 같은 평균 결합 구조로 처리해 무관변수 잡음이 남는다.
2. 볼 세트·상호작용 context는 조건별 표본이 분산되어 shrinkage와 다중 context 평균에 의해 신호가 희석된다.
3. 일시적 신호에 대한 학습은 느리고 신호 종료 후 감쇠는 충분히 빠르지 않다.
4. M3 maxT는 오탐률을 충분히 낮추지 못하면서 regime-change 탐지력도 거의 없다.
5. post-draw 오류가 일부 필드에 존재해도 전체 M4를 veto하지 않아 잔여 context가 활성화된다.

## 현재 차단사항

- 실제 메타데이터 예측 파일럿
- 실제 1~1230회 Walk-forward
- 실제 다음 회차 후보 공개
- 모바일 UI 구현
- Supabase 연결
- M4 비중 0 초과 적용
- Pair interaction 예측 활성화

## 다음 의사결정

권고 단계는 `Gate 2-3P-R`이다.

보정 명세에서 다룰 항목:

1. field별 sequential evidence weight와 null-calibrated abstention
2. hierarchical partial pooling
3. stable-context expert와 transient-context expert 분리
4. invalid timestamp 발생 시 M4 global veto
5. M3 change detector 재설계
6. 신호 종료 후 강제 decay·M0 복귀 계약
7. 모델 버전과 재검증 기준 고정

사용자 승인 전 알고리즘을 수정하거나 동일 검증을 반복하지 않는다.
