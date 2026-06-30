# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-3P-2 Python 구현 완료 · 사용자 검토 대기**  
현재 작업 브랜치: `feature/gate2p2-engine`  
기준 브랜치: `feature/gate2-physical-evidence-spec`  
관련 이슈: `#12 Gate 2-3P-2 physical evidence engine implementation`  
현재 Draft PR: `#13 Gate 2-3P-2: implement M4 physical evidence engine`

## 1. 프로젝트 목적

로또 6/45 다음 회차에 대해 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다.

장기적으로 동일 구조를 일반 의사결정 알고리즘으로 확장하지만 현재 제품과 검증대상은 계속 로또번호 예측기다.

## 2. Gate 상태

- Gate 1: 승인 완료
- Gate 2-1: 승인 완료
- Gate 2-2: 승인 완료
- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- Gate 2-3P-1: 사용자 승인 완료
- Gate 2-3P-2: **구현 완료, 사용자 검토 대기**
- Gate 2-3P-3: 차단
- Gate P-1 실제 메타데이터 파일럿: 차단
- Gate 2-4P 실제 Walk-forward: 차단
- 모바일 MVP: 차단

현재 Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`다.

## 3. 현재 모델 계약

- model version: `3.0.0-research`
- feature contract: `2.0.0`
- physical metadata schema: `1.0.0`
- 출력: 정확히 6개 번호 × 5세트
- M0: 균등 기준
- M1: 지속
- M2: 반전·평균회귀
- M3: 구조변화
- M4: 물리·운영 context
- Pair interaction: 예측 비활성

## 4. Gate 2-3P-2 구현

### 물리 메타데이터

`engine/physical_metadata.py`

- nested metadata flattening
- evidence status·source type 검증
- ISO-8601 timezone 검증
- 추첨 후 관측값의 pre-draw 위장 차단
- winning numbers·ordered numbers·bonus 등 결과필드 차단
- inferred·unknown 데이터 입력 차단
- completeness·reliability·pre-draw·traceability 계산
- duplicate draw·future metadata 차단

### M4 물리·운영 증거모형

`engine/experts/physical_evidence.py`

- 추첨기·볼 세트·regime context별 번호 포함률 집계
- 균등확률 중심의 강한 shrinkage
- context support 최소 20
- target·history confidence 결합
- 번호별 logits 중심화와 효과 clip
- 품질·지원 표본 미달 시 uniform fallback

### M3 maxT

`engine/maxt_gate.py`

- 단일 familywise maxT omnibus
- 모든 origin·진단의 series maximum 사용
- plus-one empirical p-value
- 추가 Holm 중복적용 없음
- 최소 10,000 null calibration 전 activation 금지

### 예측 파이프라인

`engine/prediction_run.py`

- M0~M4 혼합
- target metadata optional 입력
- maxT result optional 입력
- RESEARCH 최종가중치 M0=1.0
- M4 CANDIDATE·PROMOTED 비중 상한 10%
- physical metadata hash를 deterministic seed와 prediction hash에 포함
- 기존 5세트 출력 유지

### 합성·Smoke

- `simulation/physical_scenarios.py`
- `scripts/run_gate2_physical_smoke.py`

시나리오:

- unrelated physical metadata
- ball-set lift
- machine lift
- regime reversal
- 30% missing metadata

## 5. 테스트·CI

최신 성공 실행:

- GitHub Actions run: `28444499045`
- head SHA: `e9f0dc303f596b8db52f2f6193581978944db401`
- conclusion: `success`
- canonical data validation: pass
- unit tests: pass
- deterministic smoke twice: pass
- research-only contract: pass
- public-release prohibition: pass

Artifacts:

- physical smoke: `7980514978`
- physical smoke digest: `sha256:8134f362de8e9c06f90fcd04586b27871ec4f5cfa84eba952e6036799e836253`
- unit-test log: `7980514368`
- unit-test digest: `sha256:a107163d564a4d80d32112332959e2148deef267b7396d11fd409755178c4896`
- smoke report hash: `d6f504ccbc964a72fd2e870e0ae1c933a07241b4cb16a868436e1455d218a7f7`

## 6. Smoke 해석

Smoke는 구현 검증이지 예측력 검증이 아니다.

- M4가 metadata를 읽고 유한한 조합분포를 생성함
- 품질 미달에서는 uniform fallback함
- 동일 seed에서 동일 결과를 생성함
- unrelated metadata에서도 finite-sample 비균등분포는 계산될 수 있으나 RESEARCH 최종가중치는 0임
- ball-set 단일 holdout이 M0보다 나빴던 결과를 삭제하지 않음

대규모 오탐·탐지력 평가는 Gate 2-3P-3에서 수행한다.

## 7. 고정 안전장치

- M0 제거 금지
- M1·M2·M3 유지
- M4 최대비중 10%
- alpha 0.001 유지
- maxT null 최소 10,000
- 현재 회차 결과를 metadata로 사용 금지
- inferred·unknown prediction 기여 0
- pair interaction 예측 비활성
- 실제 후보 공개 금지
- 실패 seed·시나리오 삭제 금지

## 8. 다음 단계

### Gate 2-3P-3 — 전체 합성 재검증

사용자 승인 후 별도 브랜치에서 실행한다.

1. M3 maxT null calibration 10,000
2. 전체 model null calibration 4,000
3. independent null validation 5,000
4. positive scenario·effect size별 500
5. missingness·misclassification·regime robustness
6. Log Loss·Brier·calibration·strict detection 평가
7. 사전기준에 따른 PASS / NOT PASSED 판정

### 통과 후

- Gate P-1 최근 100회 실제 메타데이터 확보 파일럿
- 이후 Gate 2-4P 실제 Walk-forward
- 이후 모바일 5세트 MVP

## 9. 현재 차단사항

- Gate 2-3P-3 전체 실행 — 사용자 승인 전 차단
- 실제 1~1230회 Walk-forward
- 실제 다음 회차 후보 공개
- 모바일 UI
- Supabase

## 10. 필수 읽기

1. `AGENTS.md`
2. `docs/GATE2_PHYSICAL_EVIDENCE_SPEC.md`
3. `docs/GATE2_PHYSICAL_DATA_SCHEMA.md`
4. `docs/GATE2_PHYSICAL_VALIDATION_PROTOCOL.md`
5. `docs/GATE2_PHYSICAL_ENGINE_REVIEW.md`
6. `handoff/GATE2_PHYSICAL_PROGRESS.md`
7. 본 파일
8. `handoff/DECISION_LOG_GATE2_PHYSICAL.md`

## 11. 링크

- Issue #12: `https://github.com/dpes31/predictive-algorithm/issues/12`
- Draft PR #13: `https://github.com/dpes31/predictive-algorithm/pull/13`
- Branch: `feature/gate2p2-engine`
- Spec PR #11: `https://github.com/dpes31/predictive-algorithm/pull/11`
