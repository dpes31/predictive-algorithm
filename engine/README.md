# Gate 2 Engine Core

이 디렉터리는 `docs/GATE2_ENGINE_SPEC.md`와 관련 계약을 코드로 옮긴 연구용 Python 엔진입니다.

## 현재 구현 범위

- 고정 크기 6개 조합 확률분포
- M0~M3 expert 구조
- leakage-safe feature snapshot
- 순차 가중치 갱신식
- conservative randomness gate
- 결정론적 5세트 후보 선택
- 연구용 출력 해시

## 아직 구현하지 않은 범위

- 전체 Walk-forward state persistence
- 1,000개 null simulation
- planted positive-control
- M3 Monte Carlo calibration
- 95% uncertainty interval
- pair interaction 활성화
- 실제 미래예측 공개·잠금
- HTML 연결

## 실행

```bash
PYTHONPATH=. python scripts/run_gate2_smoke.py
```

출력은 합성 균등 데이터 기반 연구용 smoke 결과이며 실제 로또 추천이 아닙니다.
