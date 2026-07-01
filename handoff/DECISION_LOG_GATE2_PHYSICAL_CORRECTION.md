# Gate 2 Physical Correction Decision Record

## D-022 — Gate 2-3P-R 보정 명세

- 결정일: 2026-07-01
- Gate 2-3P-3 `NOT PASSED` 결과 승인
- 보정 명세와 모델 `4.0.0-research` 승인
- 기준 모델: `3.0.0-research`
- 명세 브랜치: `feature/gate2p3-correction-spec`
- Issue: #16
- Draft PR: #17

실패 근거:

- proxy false activation 0.100000%, 95% 상한 0.205288%
- M3 false activation 0.160000%
- irrelevant metadata activation 0.120048%
- lift 1.25 strict detection 0.0%~24.2%
- post-draw-error activation 2.6%
- signal-decay M0 return 65.8%

보정 방향:

1. field별 prequential e-process
2. exact-M0 abstention
3. stable / transient 분리
4. hierarchical partial pooling
5. interaction residual 강한 수축
6. metadata global veto
7. M3 restart-mixture e-process
8. activation / deactivation 1000 / 100
9. transient expiry와 208회 return
10. DEV / CAL / SEALED 분리

## D-023 — Gate 2-3P-R2 Python 구현

- 사용자 승인일: 2026-07-01
- 구현 브랜치: `feature/gate2p-r2-correction-engine`
- Issue: #18
- Draft PR: #19
- 상태: 구현 완료·CI 통과
- model: `4.0.0-research`
- feature contract: `3.0.0`

최신 검증 기준점:

- verified head: `d0c2ba9d7d65d5a437236a3d19ea1891877540fd`
- workflow run: `28483871565`
- smoke artifact: `7996655664`
- unit-test artifact: `7996653569`

구현 CI는 코드 무결성과 재현성만 확인하며 예측력을 입증하지 않는다.

## D-024 — Gate 2-3P-R3 DEV 평가

- 사용자 승인일: 2026-07-01
- 브랜치: `feature/gate2p-r3-dev-grid`
- Issue: #21
- 허용 namespace: DEV만
- CAL·SEALED: 실행 금지
- main 병합: 금지

등록 grid:

- M4 `k_global`: 260 / 520 / 1040
- M4 `k_context`: 90 / 260 / 520
- M4 `effect_clip`: 0.10 / 0.20 / 0.35
- M3 `k_m3`: 90 / 260 / 520
- 결합 config: 81개

선택규칙:

1. lift 1.25 mandatory 방향 제약 확인
2. null false activation 최소화
3. 동률이면 큰 prior와 작은 clip
4. 적격 후보가 없으면 임의 선택 금지
5. 결과는 config 상태와 implementation commit hash로 잠금

## D-025 — R3 사전 구현감사

R1 명세와 R2 실행경로 사이에서 다음 누락을 발견했다.

- M3 trigger draw 기록
- trigger 후 208회 종료 처리
- post-change `k_m3` predictor
- prediction runner corrected M3 연결

R3 실행 전 승인된 명세대로 보완했다. threshold·효과크기·검증기준은 변경하지 않았다.

## 유지 기준

- M0~M4 역할
- 6개 번호 × 5세트
- lift 1.05 / 1.10 / 1.25 / 1.50
- lift 1.25 strict detection 80%
- overall false activation 0.1%
- one-sided 95% upper 0.2%
- M3·M4 cap 각각 10%
- Pair-number interaction 비활성
- RESEARCH M0-only

## 중단조건

`4.0.0-research`가 sealed validation에 실패하면 동일 synthetic suite의 추가 튜닝을 중단한다. 적격 DEV config가 없으면 R4를 실행하지 않는다.

## 현재 결정

- R2 구현 승인·완료
- R3 DEV 평가 승인·진행 중
- CAL·SEALED 미승인
- 실제 데이터·모바일 개발 차단
- `3.0.0-research` 실패결과와 PR #15 보존
