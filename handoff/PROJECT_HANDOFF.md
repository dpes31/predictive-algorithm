# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-3P-3 전체 합성검증 완료 · NOT PASSED**  
현재 작업 브랜치: `feature/gate2p3-validation`  
기준 브랜치: `feature/gate2p2-engine`  
관련 이슈: `#14 Gate 2-3P-3 validation`  
현재 Draft PR: `#15 Gate 2-3P-3: full synthetic validation`

## 1. 프로젝트 목적

로또 6/45 다음 회차에 대해 정확히 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다.

장기적으로 동일 구조를 일반 의사결정 알고리즘으로 확장하지만 현재 제품과 검증대상은 계속 로또번호 예측기다.

## 2. Gate 상태

- Gate 1: 승인 완료
- Gate 2-1: 승인 완료
- Gate 2-2: 승인 완료
- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- Gate 2-3P-1: 승인 완료
- Gate 2-3P-2: 승인 완료
- Gate 2-3P-3: **NOT PASSED**
- Gate 2-3P-R: 사용자 결정 대기
- Gate P-1 실제 메타데이터 파일럿: 차단
- Gate 2-4P 실제 Walk-forward: 차단
- 모바일 MVP: 차단

현재 Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`, M4 deployable weight는 0이다.

## 3. 현재 모델 계약

- model version: `3.0.0-research`
- feature contract: `2.0.0`
- physical metadata schema: `1.0.0`
- 출력: 6개 번호 × 5세트
- M0: 균등 기준
- M1: 지속
- M2: 반전·평균회귀
- M3: 구조변화
- M4: 물리·운영 context
- Pair interaction: 예측 비활성
- research only: true
- public release allowed: false

## 4. Gate 2-3P-3 실행

구현:

- `simulation/physical_validation.py`
- `scripts/run_gate2_physical_validation_shard.py`
- `scripts/aggregate_gate2_physical_validation.py`
- `tests/test_physical_validation.py`
- `.github/workflows/gate2p3-full.yml`

실험 규모:

- maxT null calibration: 10,000
- model null calibration: 4,000
- independent null validation: 5,000
- positive control: 12,000
- robustness: 6,000
- total: 37,000 synthetic series
- 20 deterministic shards

## 5. 실행 무결성

- workflow run: `28451343507`
- workflow conclusion: success
- head SHA: `56f5ace469ee42a1b5743029092585724819796b`
- all 20 shards: success
- aggregate job: success
- summary artifact ID: `7983755657`
- summary artifact digest: `sha256:58526bd3b6f9a178575092f0affdb29d115139bd9dd1210dac04ef768dbe7ca7`
- report hash: `b59cc753eda4058f0b55a685a136da01a327dd6b6b7fc33b10fd4758dfc36948`

Workflow success and model validation success are different. The experiment executed successfully but the model failed the frozen criteria.

## 6. 핵심 결과

### Null

- proxy false activation: 5/5,000 = 0.100000%
- proxy one-sided 95% upper: 0.205288% — FAIL, criterion 0.2%
- M3 false activation: 8/5,000 = 0.160000% — FAIL, criterion 0.1%
- irrelevant metadata activation: 0.120048% — FAIL, criterion 0.1%
- irrelevant metadata mean M4 Δ Log Loss: -0.009065

### Lift 1.25 strict detection

- ball set: 0.8%
- machine: 24.2%
- machine × ball: 0.8%
- regime reversal: 0.0%
- temporary environment: 0.0%
- pretest shared: 0.4%

Frozen target was 80%. No scenario passed.

### Robustness

Passed:

- missingness did not increase model strength
- independent pretest did not activate
- direction reversal adaptation within 208 draws: 100%

Failed:

- post-draw-error activation: 2.6%
- signal-decay M0 return within 208 draws: 65.8%, criterion 80%
- M3 regime-reversal activation at lift 1.25: 0.2%, criterion 80%

## 7. 판정

```text
Gate 2-3P-3 = NOT PASSED
Model 3.0.0-research = not eligible for Gate P-1
Gate state = RESEARCH
Final distribution = M0 only
```

이 판정은 모든 알고리즘 개발이 불가능하다는 뜻이 아니다. 고정된 `3.0.0-research` 구조가 사전등록된 오탐·탐지력 기준을 충족하지 못했다는 뜻이다.

## 8. 진단

아래는 결과 기반 진단이며 승인된 수정안은 아니다.

1. M4의 동일 평균결합 구조가 무관한 context 잡음을 충분히 억제하지 못함
2. 볼 세트·상호작용처럼 표본이 분산되는 context의 신호가 shrinkage와 평균결합으로 희석됨
3. 일시적 신호 학습과 신호 종료 후 M0 복귀가 느림
4. M3 maxT가 오탐 제어와 구조변화 탐지력을 동시에 확보하지 못함
5. 일부 post-draw 오류가 있을 때 전체 M4를 비활성화하는 global veto가 없음

## 9. 다음 권고 단계

`Gate 2-3P-R` 보정 명세를 먼저 작성해야 한다.

검토 대상:

- field별 sequential evidence weights
- null-calibrated sparsity·abstention
- hierarchical partial pooling
- stable context와 transient context 분리
- invalid timestamp global veto
- M3 change detector 재설계
- 명시적 signal decay·M0 return 계약
- 신규 모델 버전과 동일 규모 재검증 기준

사용자 승인 전 수정 구현이나 재검증을 진행하지 않는다.

## 10. 현재 차단사항

- 실제 메타데이터 기반 예측 파일럿
- 실제 1~1230회 Walk-forward
- 실제 미래 번호 5세트 공개
- 모바일 UI·Supabase
- M4 가중치 적용
- Pair interaction 활성화

## 11. 결과 파일

- `reports/gate2_3p3_full_summary.md`
- `reports/gate2_3p3_result_manifest.json`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 본 파일

## 12. 링크

- Issue #14: `https://github.com/dpes31/predictive-algorithm/issues/14`
- Draft PR #15: `https://github.com/dpes31/predictive-algorithm/pull/15`
- Gate 2-3P-2 PR #13: `https://github.com/dpes31/predictive-algorithm/pull/13`
- Branch: `feature/gate2p3-validation`
