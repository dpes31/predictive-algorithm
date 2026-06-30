# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-3R 합성 재검증 완료 · NOT PASSED**  
현재 작업 브랜치: `feature/gate2-synthetic-validation-r1`  
기준 브랜치: `feature/gate2-synthetic-validation`  
현재 Draft PR: `#9 Gate 2-3R synthetic validation rerun`

## 1. 현재 판정

- Gate 1: 승인 완료
- Gate 2-1: 승인 완료
- Gate 2-2: 승인 완료
- Gate 2-3: NOT PASSED
- Gate 2-3R: **NOT PASSED**
- Gate state: `RESEARCH`
- 최종 적용분포: `M0 only`
- Gate 2-4 실제 데이터 Walk-forward: **차단**
- 실제 후보 공개: **차단**

## 2. Gate 2-3R 승인 변경

- 모델 버전: `2.1.0-research`
- Feature contract: `1.1.0`
- M1/M2 temperature grid: `0.05, 0.10, 0.20, 0.50, 1.00`
- M3 raw diagnostic과 clipped prediction feature 분리
- 전체 Pair 탐색과 사전지정 Pair power 검정 분리
- 엄격 positive-control 성공 판정 적용
- 기존 실패 시나리오와 효과크기 유지

## 3. 재실험 계약

- Null calibration: 1,000개 시계열
- 독립 null validation: 1,000개 시계열
- Positive-control: 시나리오당 100회
- 시계열당 1,230회
- Alpha: 0.001
- Seed base: 20260630
- 과거 실제 당첨번호 사용: 없음
- Report hash: `ec57a01e7781d5679cc8fc1b1c146055b06b6836740924cfbb0f1bfd6bef15c6`

## 4. 핵심 결과

### Null

| 검사 | 이벤트 | 관측률 | 95% 단측 상한 |
|---|---:|---:|---:|
| Gate proxy | 4/1,000 | 0.40% | 0.9130% |
| M3 raw diagnostic | 0/1,000 | 0.00% | 0.2991% |
| 전체 Pair 탐색 | 0/1,000 | 0.00% | 0.2991% |
| 사전지정 Pair | 0/1,000 | 0.00% | 0.2991% |

Gate proxy 오탐률이 사전기준 0.1%를 초과했습니다.

### Positive controls

- 고정 번호 편향 2%·5%·10%: 엄격 탐지 0%
- 지속 과정 M1: 엄격 탐지 100%
- 반전 과정 M2: 엄격 탐지 71%
- 구조변화 M3: 활성화·엄격 탐지 0%
- 52회 일시 편향 M3: 활성화·엄격 탐지 0%
- Pair factor 3.0: 사전지정 Pair 탐지 22%
- 80% power 최소 fixed-bias 효과: 없음
- 80% power 최소 Pair 효과: 없음

## 5. 개선과 실패

### 개선

- 지속 과정 M1: 0% → 100%
- 반전 과정 M2: 0% → 71%
- Temperature sub-expert로 동적 신호에서 기존 과확신이 완화됨

### 미해결

- Null proxy false activation 0.4%
- 장기 고정편향 M1 탐지 실패
- 반전 71%로 80% 미달
- M3 검정 구조상 활성화 불가능
- Pair 검정력 부족

## 6. M3 구조적 모순

현재 승인 계약:

```text
Null calibration = 1,000
plus-one 최소 empirical p = 1/1,001 = 0.000999001
4개 진단 Holm 최소 adjusted p = 4/1,001 = 0.003996004
alpha = 0.001
```

따라서 어떤 M3 관측값도 adjusted p ≤ 0.001을 만들 수 없습니다. Raw diagnostic 분리로 winsorization 포화는 제거됐지만, calibration 수와 다중검정 계약 때문에 M3 활성화가 수학적으로 불가능합니다.

## 7. 다음 변경은 별도 승인 필요

1. M3 calibration을 최소 3,999개 이상으로 확대하거나 단일 omnibus/maxT 검정으로 변경
2. Gate proxy 오탐 0.4% 원인 분석 및 threshold 보수화
3. 장기 고정편향 탐지기를 최근 지속형 M1과 분리할지 결정
4. 반전 71%를 개선할지 검출 한계로 인정할지 결정
5. Pair interaction은 예측 비활성 유지 권고

## 8. 실행 투명성

GitHub 브랜치와 Draft PR에 보정 코드를 반영했습니다. 사용 가능한 GitHub 연결 도구로 Actions workflow를 추가·디스패치할 수 없어, 전체 수치 실험은 커밋된 수식을 그대로 옮긴 결정론적 standalone mirror에서 실행했습니다. GitHub CI 확인은 아직 완료되지 않았습니다.

## 9. 필수 문서

1. `AGENTS.md`
2. `docs/GATE2_3R_APPROVAL.md`
3. `docs/GATE2_3R_MODEL_AMENDMENT.md`
4. `reports/gate2_3r_full_summary.md`
5. `reports/gate2_3r_full_summary.json`
6. `handoff/GATE2_3R_WORK_LOG.md`
7. `handoff/DECISION_LOG.md`
8. 본 파일

## 10. 링크

- Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/9`
- Branch: `feature/gate2-synthetic-validation-r1`
