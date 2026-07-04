# Gate 2-3P-R Implementation Plan

상태: 사용자 검토용  
대상 제안 모델: `4.0.0-research`

## 단계

1. R1 명세: 현재 단계
2. R2 Python 구현
3. R3 unit·smoke·development synthetic 검수
4. R4 sealed 전체 재검증

## 신규 모듈 제안

- `engine/eprocess.py`
- `engine/metadata_veto.py`
- `engine/experts/physical_stable.py`
- `engine/experts/physical_transient.py`
- `engine/experts/physical_hierarchy.py`
- `engine/experts/change_eprocess.py`
- `engine/abstention.py`
- `simulation/correction_scenarios.py`
- `simulation/correction_validation.py`
- `scripts/build_sealed_seed_manifest.py`
- `scripts/run_gate2_correction_shard.py`
- `scripts/aggregate_gate2_correction.py`

## 구현 순서

### 1. Metadata global veto

- post-draw timestamp 존재 시 M4 전체 invalid
- 현재 회차 결과필드 존재 시 invalid
- optional unknown은 해당 field만 제외
- invalid 상태에서는 exact M0

### 2. Hierarchical field distribution

- field parent와 context child 분리
- unseen context는 parent fallback
- interaction residual은 machine·ball 주효과에 추가
- exact 6-of-45 normalization 유지

### 3. Field e-process

- 과거 정보만 사용해 `Q[j,t]` 생성
- exact joint probability likelihood ratio 사용
- log-domain 누적
- 결측 field는 evidence 유지

### 4. Stable·transient 분리

- stable regime reset
- transient restart 13·26·52·104
- transient 104회 expiry
- family별 evidence 기록

### 5. M3 change e-process

- 번호·betting fraction·restart mixture
- trigger 1000
- deactivation 100
- detector와 번호방향 prediction 분리

### 6. Abstention state machine

- `INVALID_METADATA`
- `ABSTAIN`
- `SHADOW_ACTIVE`
- `CANDIDATE_ELIGIBLE`
- `FORCED_RETURN`

RESEARCH 상태 deployable distribution은 항상 M0다.

## Hyperparameter grid

허용:

- `k_global`: 260 / 520 / 1040
- `k_context`: 90 / 260 / 520
- `effect_clip`: 0.10 / 0.20 / 0.35
- `k_m3`: 90 / 260 / 520

고정:

- activation evidence 1000
- deactivation evidence 100
- M3·M4 cap 각각 10%
- transient restart 13/26/52/104
- 최대 change life 208회

Grid는 development seed에서만 선택하고 sealed validation 전 잠근다.

## 필수 테스트

- post-draw·result-field global veto
- unseen context parent fallback
- interaction residual 중심화
- M0일 때 evidence=1
- 결측 field evidence 불변
- activation/deactivation hysteresis
- stable regime reset
- transient expiry
- M3 trigger·expiry
- RESEARCH M0-only
- 6개 번호 × 5세트 재현성

## CI

PR CI:

- syntax
- unit tests
- deterministic smoke
- seed namespace audit
- public-release safety

Full validation:

- sealed manifest 검증
- shard hash 검증
- duplicate row 차단
- aggregate row count 검증
- 자동 PASS/NOT PASSED 판정

## 현재 승인 범위

현재는 R1 명세 작성까지만 승인됐다.

별도 승인 전 금지:

- 4.0 코드 구현
- grid 실행
- calibration·sealed validation
- 실제 데이터 Walk-forward
- 모바일 UI 개발
