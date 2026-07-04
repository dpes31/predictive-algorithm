# Gate 2-3P-R Validation and Acceptance Protocol

상태: 사용자 검토용 고정 명세  
대상 제안 모델: `4.0.0-research`  
적용 Gate: `Gate 2-3P-R2` 구현 이후

## 1. 목적

보정된 M3·M4가 다음을 동시에 만족하는지 검증한다.

1. 무작위·무관 메타데이터에서 abstain
2. 실제 합성 관계가 있을 때 방향과 확률을 탐지
3. 사후정보·timestamp 오류에서 전체 M4 차단
4. 일시적 신호 종료 후 M0 복귀
5. regime reversal을 허용된 오탐률 안에서 탐지

Gate 2-3P-3에서 실패한 효과크기와 핵심 시나리오는 삭제하거나 완화하지 않는다.

## 2. 검증 단계 분리

### 2.1 Development

용도:

- 코드 디버깅
- hyperparameter grid 선택
- 실행시간·메모리 확인
- smoke

금지:

- 최종 PASS/FAIL 계산
- sealed seed 사용
- 결과가 좋은 seed 선별

### 2.2 Calibration sanity

용도:

- e-process가 구현상 null에서 폭주하지 않는지 확인
- global veto가 항상 작동하는지 확인
- threshold를 선택하는 용도가 아님

고정 threshold:

```text
activation e-value = 1000
deactivation e-value = 100
```

Calibration 결과를 보고 threshold를 변경하지 않는다.

### 2.3 Sealed validation

- 최종 PASS/NOT PASSED 전용
- seed manifest를 실행 전에 commit
- 첫 결과 생성 후 코드·config 변경 금지
- infrastructure failure 시 동일 seed만 재실행
- 일부 shard·seed 제외 금지

## 3. Seed manifest

각 seed는 다음 문자열의 SHA-256에서 결정한다.

```text
Gate2-3P-R4|4.0.0-research|category|scenario|effect|replicate
```

SHA-256 앞 64 bit를 unsigned integer로 변환한다.

Manifest 필수필드:

- category
- scenario
- effect size
- replicate index
- seed
- expected draw count
- config hash
- code commit hash

Manifest hash를 workflow 시작 전에 보존한다.

## 4. 시나리오 유지

### Null

- N0 완전 균등·metadata 없음
- N1 무관 메타데이터
- N2 조건의존 결측
- N3 측정오차
- N4 잘못된 ID 15%
- N5 교체 이벤트만 존재

### Positive

- P1 볼 세트별 번호효과
- P2 추첨기별 번호효과
- P3 추첨기 × 볼 세트 상호작용
- P4 교체 후 방향 전환
- P5 일시적 환경효과
- P6 사전 모의추첨 shared latent condition

효과크기:

```text
1.05 / 1.10 / 1.25 / 1.50
```

### Robustness

- metadata 결측 10% / 30% / 50%
- ID 오분류 5% / 15%
- confidence 과대평가 10% / 30%
- post-draw timestamp 오류 20%
- 신규 regime 저지원
- 관계 소멸
- 방향 반전
- 독립 pretest

## 5. 추가 correction-specific control

### C1. 단일 무관 field

한 개 field만 무관한 값을 제공한다. 해당 field e-value가 장기적으로 1을 체계적으로 초과하지 않아야 한다.

### C2. 유효 field + 다수 무관 field

1개 유효 field와 6개 무관 field를 함께 제공한다.

요구:

- 유효 field가 최대 weight
- 무관 field 총 weight <= 20%
- 유효 field 단독 모델 대비 Δ Log Loss 저하 <= 10%

### C3. Stable signal only

Transient family가 없어도 stable family가 탐지해야 한다.

### C4. Transient signal only

Stable family가 없어도 restart mixture가 일시적 신호를 탐지하고 종료 후 복귀해야 한다.

### C5. Global veto

하나의 supplied field에 post-draw timestamp가 존재하면 다른 field가 완전해도 M4 전체가 `INVALID_METADATA`가 되어야 한다.

### C6. Regime reset

볼 세대가 변경되면 이전 context residual을 직접 재사용하지 않아야 한다.

## 6. 실험 규모

### Development — PASS/FAIL 제외

- null 2,000
- positive scenario·effect별 200
- robustness scenario별 200

### Calibration sanity — PASS/FAIL 보조

- M3 null 10,000
- M4 field-evidence null 10,000

### Sealed independent null

- 10,000 series
- null scenario별 가능한 균등배분
- series당 1,230 draws

### Sealed positive

- scenario·effect size별 1,000 series
- 6 scenarios × 4 effects × 1,000 = 24,000

### Sealed robustness

- scenario별 1,000 series
- 기존 12 scenarios = 12,000
- correction-specific 6 scenarios × 1,000 = 6,000

### PASS/FAIL 총 규모

```text
Calibration sanity 20,000
Sealed null        10,000
Sealed positive    24,000
Sealed robustness  18,000
Total              72,000 series
```

Development 결과는 총계에 포함하지 않는다.

## 7. 평가 단위

- series length: 1,230 draws
- minimum history: 299 draws
- forecast block: 52 draws
- macro blocks:
  - A: 300–609
  - B: 610–919
  - C: 920–1230
- 미래 데이터 사용: 0건

## 8. 평가 지표

### Safety

- M4 false activation rate
- M3 false activation rate
- one-sided 95% exact binomial upper bound
- irrelevant-field activation
- global-veto success rate
- metadata-invalid residual weight

### Predictive power

- joint Δ Log Loss vs M0
- number-level Δ Brier vs M0
- calibration error
- strict detection rate
- direction accuracy
- expected field top-weight rate
- minimum detectable effect

### Adaptation

- first activation delay
- regime reversal adaptation delay
- signal-end M0 return delay
- stale transient weight
- old-regime residual reuse rate

## 9. Strict detection — M4

M4 positive-control series는 다음을 모두 만족할 때만 strict success다.

1. `E_M4 >= 1000`이 최소 1회 발생
2. M4 mean Δ Log Loss > 0
3. M4 mean Δ Brier >= 0
4. 최소 2개 macro block에서 Δ Log Loss > 0
5. 기대 방향 정확도 >= 80%
6. expected family 또는 field가 최대 evidence weight
7. M4가 M1·M2·M3보다 mean Δ Log Loss에서 엄격히 우수
8. metadata global veto가 발생하지 않음

P4 regime reversal은 M3 strict condition도 함께 만족해야 한다.

## 10. Strict detection — M3

M3 success:

1. `E_M3 >= 1000`
2. false activation이 아닌 사전지정 change 이후 trigger
3. post-change mean Δ Log Loss > 0
4. post-change mean Δ Brier >= 0
5. 방향 정확도 >= 80%
6. change 이후 208 draws 이내 trigger
7. trigger 후 208 draws 이내 deactivation 또는 새 regime 안정화

## 11. Null 통과기준

### Overall M4

```text
observed false activation <= 0.1%
one-sided 95% exact upper <= 0.2%
```

### Overall M3

```text
observed false activation <= 0.1%
one-sided 95% exact upper <= 0.2%
```

### N1 irrelevant metadata

- activation <= 0.1%
- mean Δ Log Loss <= 0
- mean Δ Brier <= 0
- median active field count = 0

### N2–N5

- 각 scenario observed activation <= 0.2%
- 결측·오분류 증가에 따라 evidence 또는 nonuniform strength가 증가하지 않음

## 12. Positive 통과기준

Lift 1.25에서 각 P1–P6은 다음을 모두 만족해야 한다.

```text
strict detection >= 80%
mean Δ Log Loss > 0
mean Δ Brier >= 0
mean direction accuracy >= 80%
```

추가:

- P4 M3 activation >= 80%
- P5 signal 종료 후 208회 이내 M0 return >= 80%
- P6 independent-pretest control과 구분 가능

Lift 1.50에서는 각 scenario strict detection >= 95%를 요구한다.

Lift 1.05·1.10은 실패로 Gate를 막지 않지만 최소탐지효과 보고에 포함한다.

## 13. Robustness 통과기준

- missingness 10→30→50%에서 mean nonuniform strength 비증가
- ID 오분류 5→15%에서 confidence 비증가
- confidence 과대평가가 false activation을 0.1% 초과시키지 않음
- post-draw timestamp error global veto = 100%
- invalid metadata에서 M4 nonuniform probability = 0건
- independent pretest activation <= 0.1%
- direction reversal 208회 이내 적응 >= 80%
- signal decay 208회 이내 M0 return >= 80%
- old-regime residual direct reuse = 0건

## 14. Correction-specific 통과기준

- C1 무관 field activation <= 0.1%
- C2 유효 field top-weight >= 80%
- C2 무관 field 총 weight <= 20%
- C3 stable strict detection >= 80% at lift 1.25
- C4 transient strict detection >= 80% at lift 1.25
- C4 M0 return >= 80% within 208 draws
- C5 global veto = 100%
- C6 old residual reuse = 0건

## 15. 전체 Gate 판정

모든 mandatory check가 통과해야 `PASS`다.

부분통과·조건부통과를 사용하지 않는다.

```text
한 개 mandatory check라도 실패
→ Gate 2-3P-R4 = NOT PASSED
```

## 16. 통과 후 허용범위

PASS 시 허용:

- Gate P-1 실제 메타데이터 100회 feasibility pilot
- source coverage와 pre-draw availability 조사
- 실제 Walk-forward 명세 작성

PASS 후에도 금지:

- 실제 미래번호 공개
- 예측력 주장
- M4 deployable weight 적용
- 모바일 prediction product activation

실제 데이터 Walk-forward와 prospective validation이 별도로 필요하다.

## 17. 실패 후 중단

NOT PASSED 시:

- 동일 synthetic suite를 대상으로 추가 구조·파라미터 튜닝 금지
- threshold 완화 금지
- 실패 seed 제외 금지
- 새로운 외부 물리데이터가 확보되기 전 비균등 로또 예측연구 중단
- `3.0.0-research`와 `4.0.0-research` 실패결과 모두 보존
