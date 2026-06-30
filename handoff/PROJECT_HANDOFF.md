# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R1 보정 명세 완료 · 사용자 검토 대기**  
현재 작업 브랜치: `feature/gate2p3-correction-spec`  
기준 브랜치: `feature/gate2p3-validation`  
관련 이슈: `#16 Gate 2-3P-R 보정 명세 및 4.0.0-research 제안`  
현재 Draft PR: `#17 Gate 2-3P-R1: correction specification`

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
- Gate 2-3P-3: NOT PASSED, 사용자 결과 승인 완료
- Gate 2-3P-R1: **명세 완료, 사용자 검토 대기**
- Gate 2-3P-R2 Python 구현: 차단
- Gate 2-3P-R3 개발 검수: 차단
- Gate 2-3P-R4 sealed validation: 차단
- Gate P-1 실제 메타데이터 파일럿: 차단
- Gate 2-4P 실제 Walk-forward: 차단
- 모바일 MVP: 차단

현재 Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`, deployable M4 weight는 0이다.

## 3. 실패 기준

Gate 2-3P-3:

- proxy false activation 0.100000%, 95% 상한 0.205288%
- M3 false activation 0.160000%
- irrelevant metadata activation 0.120048%
- lift 1.25 strict detection 0.0%~24.2%
- post-draw-error activation 2.6%
- signal-decay M0 return 65.8%

실행은 성공했지만 `3.0.0-research`가 사전등록 기준을 통과하지 못했다.

## 4. 제안 버전

```text
model_version = 4.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

Major version 제안 이유:

- M4 단일 평균결합 제거
- stable / transient 내부 분리
- field별 evidence gate 추가
- M3 maxT 교체
- metadata global veto 추가
- sealed validation 계약 추가

## 5. 보정 M4

### Field별 evidence

각 field가 독립 fixed-size distribution `Q[j,t]`를 만들고 M0 대비 prequential likelihood ratio를 누적한다.

```text
LR[j,t] = Q[j,t](S_t) / P0(S_t)
```

- stable field: full-regime e-process
- transient field: restart-mixture e-process
- global M4 evidence 1000 미만이면 exact M0
- deactivation evidence 100
- field evidence가 1 이하이면 weight 0

### Stable / transient

Stable:

- machine
- ball set
- generations
- regime
- machine × ball interaction

Transient:

- environment
- pre-draw tests
- mixing condition
- 단기 운영조건

Transient restart windows는 13·26·52·104회로 고정한다.

### Hierarchical pooling

- global M0 → field parent → context child
- unseen context는 parent fallback
- interaction은 machine·ball 주효과와 residual로 분해
- residual support 52 미만이면 0

## 6. Metadata global veto

다음 입력 하나라도 있으면 M4 전체를 invalid 처리한다.

- post-draw timestamp
- pre-draw 표시인데 timestamp 없음
- 현재회차 winning·ordered·bonus 결과필드
- schema mismatch
- verified source traceability 없음
- required field 모순
- future metadata

결과:

```text
P4 = P0
M4 status = INVALID_METADATA
all M4 weights = 0
```

## 7. M3 보정

기존 maxT를 anytime-valid restart-mixture e-process로 교체한다.

- 45개 번호
- betting fraction ±0.02 / ±0.05 / ±0.10 / ±0.20
- 13회 간격 restart
- 최근 104 restart 유지
- activation 1000
- deactivation 100
- trigger 최대수명 208회
- detector와 번호방향 prediction 분리
- 별도 Holm 없음

## 8. 유지되는 제품·안전 계약

- M0~M4 상위 역할 유지
- exact 6-of-45 distribution
- 6개 번호 × 5세트 출력
- RESEARCH M0-only
- CANDIDATE M0 최소 70%
- M3 최대 10%
- M4 최대 10%
- Pair interaction 예측 비활성
- 실제 후보 공개 금지
- `통계적 우위 없음`

## 9. Hyperparameter 선택

허용 grid만 development seed에서 평가한다.

```text
k_global: 260 / 520 / 1040
k_context: 90 / 260 / 520
effect_clip: 0.10 / 0.20 / 0.35
k_m3: 90 / 260 / 520
```

선택 후 config hash를 잠그고 calibration·sealed 결과를 본 뒤 변경하지 않는다.

## 10. R4 sealed validation

- calibration sanity: 20,000 series
- sealed null: 10,000
- sealed positive: 24,000
- sealed robustness: 18,000
- PASS/FAIL total: 72,000

고정 기준:

- M3·M4 false activation <= 0.1%
- one-sided 95% exact upper <= 0.2%
- lift 1.25 P1~P6 strict detection >= 80%
- lift 1.50 strict detection >= 95%
- post-draw-error global veto 100%
- signal 종료 후 208회 이내 M0 return >= 80%
- regime reversal 208회 이내 adaptation >= 80%

한 개 mandatory check라도 실패하면 NOT PASSED다.

## 11. Seed 분리

- DEV: 개발·grid 선택
- CAL: implementation sanity
- SEALED: 최종 판정

SEALED manifest를 첫 실행 전 commit한다. 첫 결과 이후 코드·config·seed 변경과 실패 seed 제외를 금지한다.

## 12. 중단 원칙

`4.0.0-research`가 sealed validation에 실패하면 동일 synthetic suite에서 추가 구조·파라미터 튜닝을 중단한다.

새로운 외부 물리데이터가 확보되기 전:

- 비균등 로또 예측연구 중단
- M0 기반 5세트 생성기는 연구·기록용으로만 유지
- 실제 미래 예측력 주장 금지

## 13. 현재 완료 문서

- `docs/GATE2_PHYSICAL_CORRECTION_SPEC.md`
- `docs/GATE2_PHYSICAL_CORRECTION_VALIDATION.md`
- `docs/GATE2_PHYSICAL_CORRECTION_IMPLEMENTATION_PLAN.md`
- `handoff/DECISION_LOG_GATE2_PHYSICAL_CORRECTION.md`
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
- 본 파일

## 14. 현재 차단사항

- `4.0.0-research` Python 구현
- hyperparameter grid 실행
- calibration·sealed validation
- 실제 메타데이터 예측 파일럿
- 실제 1~1230회 Walk-forward
- 실제 미래 번호 5세트 공개
- 모바일 UI·Supabase

## 15. 다음 사용자 결정

다음 세 가지를 승인해야 Gate 2-3P-R2 구현을 시작한다.

1. 보정 아키텍처
2. 모델 버전 `4.0.0-research`
3. sealed validation 및 실패 시 중단 원칙

## 16. 링크

- Issue #16: `https://github.com/dpes31/predictive-algorithm/issues/16`
- Draft PR #17: `https://github.com/dpes31/predictive-algorithm/pull/17`
- 이전 validation PR #15: `https://github.com/dpes31/predictive-algorithm/pull/15`
- Branch: `feature/gate2p3-correction-spec`
