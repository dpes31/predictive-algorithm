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

표준 라이브러리 Python 3 환경에서 다음 명령을 실행했습니다.

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

결과:

```text
18 tests passed
```

검증 항목:

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

## 합성 smoke 결과

- 합성 데이터: uniform 6/45, 320회
- target: synthetic 321회
- gate: `RESEARCH`
- final weights: M0 1.0
- advantage: `통계적 우위 없음`
- research_only: true
- public_release_allowed: false
- 후보 5세트: 생성 및 재현 확인

CI가 별도로 동일 테스트와 smoke 결과 byte 비교를 실행합니다.
