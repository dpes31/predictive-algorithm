# Gate 2-2 Engine Core Status

작성일: 2026-06-30  
브랜치: `feature/gate2-engine-core`  
모델 버전: `2.0.0-research`

## 구현 상태

- Exact fixed-size distribution: 구현
- M0: 구현
- M1 persistence sub-experts: 구현
- M2 reversal sub-experts: 구현
- M3 regime sub-experts: 구조 구현, change gate 0 유지
- Sequential weight update: 구현
- Randomness gate state machine: 구현
- Deterministic five-set optimizer: 구현
- Research-only output contract: 구현
- Full historical Walk-forward: 미구현
- Gate 2-3 null calibration: 미구현

## 개발 중 독립 실행 검증

표준 라이브러리 Python 3 환경에서 초기 엔진 테스트 18개를 실행했고 모두 통과했습니다.

## GitHub Actions 최종 검증

Workflow:

```text
Gate 2 engine core
Run ID: 28424836513
Conclusion: success
```

통과 단계:

1. Checkout
2. Python 3.12 설정
3. Gate 1 canonical data 재검증
4. 전체 unit tests
5. synthetic uniform smoke 2회 실행
6. 두 smoke JSON byte 단위 비교
7. research-only 안전필드 assertion
8. artifact 업로드

저장소 전체 테스트 수:

```text
32 tests passed
```

Artifact:

```text
name: gate2-engine-core-smoke
artifact id: 7972584334
sha256: fdefd93b6a6af229f9398840c4cb334335098d8044010e17f930776edd51a1fb
expires: 2026-07-14
```

## 검증 항목

- 미래 데이터 차단
- 연구용 `auto_checked` 허용
- 공개용 unlocked 데이터 거부
- elementary symmetric polynomial 정확성
- 작은 상태공간 확률합 1
- 주변확률 합이 pick count와 일치
- top combination 확률순 정렬
- M1~M3 주변확률 합 6
- M3 calibration 전 균등 유지
- 피처 해시 재현
- 피처 값 유한성 및 winsor 범위
- 연구단계 최종 M0
- 후보 5세트 고유성
- 후보 포트폴리오 커버리지
- 한 회차 가중치 폭증 제한
- CANDIDATE 비균등 비중 30% 상한
- 모델 버전·번호수·세트수·군중회피 상한 계약

## 합성 smoke 결과

- 합성 데이터: uniform 6/45, 320회
- target: synthetic 321회
- gate: `RESEARCH`
- final weights: M0 1.0
- advantage: `통계적 우위 없음`
- research_only: true
- public_release_allowed: false
- 후보 5세트: 생성 및 재현 확인

## 현재 판정

Gate 2-2의 코드·수학적 정합성·재현성·연구용 안전장치는 자동검증을 통과했습니다.

이는 실제 예측력 검증을 의미하지 않습니다. 비균등 신호의 오탐률과 탐지력은 Gate 2-3, 실제 역사적 성능은 Gate 2-4에서 평가합니다.
