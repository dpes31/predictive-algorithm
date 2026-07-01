# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-R2 구현 완료·CI 통과**  
현재 브랜치: `feature/gate2p-r2-correction-engine`  
기준 브랜치: `feature/gate2p3-correction-spec`  
관련 이슈: #18  
현재 Draft PR: #19

## 1. 목적

로또 6/45 다음 회차에 대해 정확히 6개 번호 조합 5세트를 출력하는 연구형 모바일 예측기를 개발한다. 장기적으로 일반 의사결정 알고리즘으로 확장하지만 현재 검증대상은 로또 예측기다.

## 2. Gate 상태

- Gate 2-3 / 2-3R: NOT PASSED
- Gate 2-3P-1: 승인 완료
- Gate 2-3P-2: 완료
- Gate 2-3P-3: NOT PASSED
- Gate 2-3P-R1: 승인 완료
- Gate 2-3P-R2: **구현 완료·CI 통과**
- Gate 2-3P-R3: DEV 검수 미착수
- Gate 2-3P-R4: sealed validation 차단
- 실제 메타데이터 파일럿: 차단
- 실제 Walk-forward: 차단
- 모바일 MVP: 차단

현재 Gate state는 `RESEARCH`, 최종 적용분포는 `M0 only`, deployable M4 weight는 0이다.

## 3. 동결 버전

```text
model_version = 4.0.0-research
feature_contract_version = 3.0.0
physical_data_schema_version = 1.0.0
```

실패한 `3.0.0-research` 결과와 보고서는 변경하지 않는다.

## 4. R2 구현

### M4

- field별 prequential likelihood-ratio e-process
- stable / transient family 분리
- hierarchical partial pooling
- unseen context parent fallback
- machine × ball-set residual 강한 수축
- evidence 부족 시 exact M0
- activation / deactivation `1000 / 100`
- transient windows `13 / 26 / 52 / 104`
- forced return 52회

### Metadata

- post-draw timestamp veto
- current-result field veto
- schema mismatch veto
- source traceability 검사
- invalid metadata에서 M4 전체 weight 0

### M3

- 기존 maxT 대신 restart-mixture e-process
- 45개 번호와 고정 betting-fraction grid
- 13회 간격 restart
- 최대 process life 208회
- detector와 방향점수 분리

### 제품 계약

- M0~M4 역할 유지
- exact 6-of-45 distribution
- 6개 번호 × 5세트
- RESEARCH M0-only
- M3·M4 cap 각각 10%
- Pair-number interaction 비활성

## 5. CI

- workflow run: `28483762170`
- head SHA: `6f264309a8e5cd5ee076cd235ff76c3684bcb5cc`
- canonical data validation: PASS
- compile: PASS
- full unit tests: PASS
- deterministic smoke twice: PASS
- research-only guard: PASS
- public-release guard: PASS
- smoke artifact: `7996617074`
- smoke digest: `sha256:e82f74246d3983b2653b465b55fcd475c5f0ea382eb46c1eefe95a529aa197af`
- unit-test artifact: `7996615246`

## 6. 검증 기준

- false activation <= 0.1%
- one-sided 95% upper <= 0.2%
- lift 1.25 strict detection >= 80%
- lift 1.50 strict detection >= 95%
- 기존 실패 시나리오와 효과크기 유지
- 한 개 mandatory check 실패 시 NOT PASSED

## 7. 다음 단계

Gate 2-3P-R3:

1. DEV namespace에서 허용 grid 평가
2. null false activation 우선으로 config 선택
3. lift 1.25 방향정확도 제약 확인
4. 선택 config와 commit hash 잠금
5. deterministic development report 생성

R3 통과 뒤에만 별도 승인으로 R4 sealed validation을 실행한다.

## 8. 금지

- main 병합
- CAL·SEALED 조기 실행
- 기준 완화
- 실패 seed 또는 시나리오 삭제
- 실제 Walk-forward
- 공개 후보 생성
- 모바일 UI 개발

## 9. 링크

- Issue #18: `https://github.com/dpes31/predictive-algorithm/issues/18`
- Draft PR #19: `https://github.com/dpes31/predictive-algorithm/pull/19`
- R1 spec PR #17: `https://github.com/dpes31/predictive-algorithm/pull/17`
