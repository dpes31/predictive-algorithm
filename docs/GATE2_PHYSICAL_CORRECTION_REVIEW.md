# Gate 2-3P-R1 Review Guide

## 현재 단계

보정 명세 작성 완료. 구현과 재검증은 아직 시작하지 않았다.

## 핵심 변경

### 기존 3.0

```text
모든 물리 field를 평균 결합
→ 약한 잡음도 비균등 확률 생성
```

### 제안 4.0

```text
각 field가 M0보다 실제로 나은지 evidence 누적
→ evidence 1000 이상인 field만 사용
→ evidence 부족 시 M4 전체 M0
```

## 실패별 보정

| 실패 | 보정 |
|---|---|
| 무관 metadata 활성 | field e-process와 abstention |
| 볼 세트 신호 희석 | hierarchical partial pooling |
| 안정·일시 신호 혼합 | stable / transient 분리 |
| 신호 종료 후 잔존 | expiry와 강제 M0 return |
| post-draw 오류 활성 | global veto |
| M3 오탐·저탐지 | restart-mixture change e-process |

## 유지되는 것

- 로또번호 예측기 목적
- 1~45 번호별 확률
- 6개 번호 × 5세트 결과
- M0~M4 상위 구조
- 검증 전 M0-only
- 실제 미래번호 공개 차단

## 제안 버전

`4.0.0-research`

단순 파라미터 조정이 아니라 M3·M4 내부 판단구조를 교체하므로 major version으로 제안한다.

## 구현 후 검증

- 총 72,000개 PASS/FAIL 시계열
- lift 1.25 strict detection 80% 유지
- 오탐률 0.1% 유지
- 신뢰상한 0.2% 유지
- 한 항목이라도 실패하면 NOT PASSED

## 최종 중단조건

4.0도 실패하면 동일 합성환경에서 추가 튜닝을 중단한다. 새로운 외부 물리데이터가 확보돼야 연구를 재개한다.

## 승인 대상

1. 보정 구조
2. `4.0.0-research`
3. sealed validation 계약
4. 실패 시 중단 원칙
