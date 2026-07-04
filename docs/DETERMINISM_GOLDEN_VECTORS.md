# CONTROL_M0 결정론 골든 벡터 정책

## 1. 목적

CONTROL_M0 제품(`product/run_prediction.py`, `product/dynamic_prediction.py`)이 제공하는
"동일 입력 → 동일 결과" 계약은 내부적으로 `engine/candidate_optimizer.py`의
`random.Random(int(seed[:16], 16))` 및 `rng.sample(...)` 호출에 의존한다.

CPython은 `random.Random.random()`이 만들어내는 기본 PRNG 스트림에 대해서는
버전 간 안정성을 유지해 왔지만, `random.sample()`이 그 스트림으로부터 만들어내는
정확한 표본 시퀀스에 대해서는 **버전 간 동일성을 공식적으로 보장하지 않는다.**
즉, 현재 관측되는 "동일 입력 → 동일 결과" 동작은 특정 CPython 구현들에서
경험적으로 확인된 사실이지, Python 언어 차원의 공식 보증이 아니다.

이 문서와 `tests/test_product_golden_vectors.py`는 이 위험을 명시적으로 인지하고,
현재 동작을 회귀 테스트로 동결(freeze)하여 향후 Python 버전 변경이나 의도치 않은
코드 변경으로 인한 출력 변화를 조기에 탐지하기 위한 것이다.

## 2. 동결 내용

`tests/test_product_golden_vectors.py`에 세 종류의 골든 벡터를 고정한다.

1. **Golden A (정본 데이터만)**: `run_dynamic_prediction(overlay=[], ...)` 호출 시
   나오는 `seed`, `hashes.effective_data_hash`, `hashes.prediction_hash`,
   `target_draw_no`, 5개 후보 조합, `product_weights`, `statistical_edge` 값을 그대로 고정.
2. **Golden B (고정 오버레이 1건)**: draw_no 1231, draw_date 2026-07-04(정본 마지막
   draw_date 2026-06-27 + 7일), numbers `[3, 11, 19, 27, 35, 43]`, bonus_number 7을
   오버레이로 넣었을 때 나오는 `seed`/해시/후보 조합을 고정.
3. **Golden C (엔진 단위 격리)**: 제품 래퍼를 거치지 않고 `engine/candidate_optimizer.optimize_candidates`를
   직접 호출 — 고정된 합성 시드(`sha256(b"golden-vector-fixed-seed")`), 균일 분포
   (`FixedSizeDistribution`), 제품과 동일한 `EngineConfig` 값(number_count=45,
   pick_count=6, candidate_count=5, uniform_candidate_pool=3000)으로 나온 5개 조합을 고정.
   이는 회귀가 발생했을 때 원인을 제품 래퍼(`product/dynamic_prediction.py`) 쪽인지
   엔진 코어(`engine/candidate_optimizer.py`) 쪽인지 구분하기 위함이다.

## 3. 검증된 버전

위 세 골든 벡터는 아래 네 개의 CPython 인터프리터에서 동일한 코드 경로를 실행하여,
바이트 단위로 동일한 출력이 나오는 것을 확인한 뒤 상수로 고정했다.

- CPython 3.10
- CPython 3.11
- CPython 3.12
- CPython 3.13

검증일: 2026-07-04. 이 문서의 "검증된 버전"은 위 4개 버전에 한정되며, 그 밖의
Python 버전(예: 3.14 이상, 또는 3.9 이하)에 대해서는 어떠한 보증도 하지 않는다.

## 4. 드리프트(불일치) 대응 정책

`tests/test_product_golden_vectors.py`가 실패하는 경우:

- **상수를 조용히 갱신하여 테스트를 통과시키는 것은 금지한다.** 이는 "동일 입력 →
  동일 결과" 계약이 실제로 깨졌다는 신호이며, 사고(incident)로 취급해야 한다.
- 대응은 다음 두 가지 선택지 중 사람이 명시적으로 승인한 것만 적용한다.
  - (a) **문제가 되는 Python 버전 회피/고정**: 배포 및 CI에서 검증된 버전
    집합(3.10~3.13) 안의 버전만 사용하도록 고정하고, 새 버전 채택을 보류한다.
  - (b) **자체 결정론 생성기로 교체**: `random.sample()`에 의존하지 않는
    SHA-256 기반 자체 결정론적 조합 생성기로 교체하고, `DYNAMIC_CONTRACT_VERSION`
    (및 필요 시 `PRODUCT_CONTRACT_VERSION`)을 상향하며, append-only 방식으로
    변경 근거와 영향 범위를 기록(evidence)한다. 이 경로는 반드시 사용자 승인을
    받은 뒤에만 적용한다.
- 두 선택지 모두 기존에 발급된 예측 결과나 잠긴(locked) 기록을 소급 변경하지 않는다.

## 5. Production 런타임 확인 절차

배포 전(예: Vercel) 다음을 확인한다.

1. Vercel 배포 빌드 로그에서 실제 사용되는 Python 버전을 확인한다.
2. 확인된 버전이 3.항의 검증된 버전 집합(3.10, 3.11, 3.12, 3.13) 밖이라면,
   해당 배포는 보류하고 4.항의 대응 정책에 따라 사람의 명시적 결정을 먼저 받는다.
3. 이 절차는 CONTROL_M0의 `statistical_edge: false` 메시징이나 통계적 우위에 대한
   기존 판단을 변경하지 않는다. 이 문서는 오직 "동일 입력 → 동일 결과" 재현성의
   런타임 전제 조건을 확인하기 위한 것이며, 공식적인 외부 검증이나 추가 보증을
   주장하지 않는다.
