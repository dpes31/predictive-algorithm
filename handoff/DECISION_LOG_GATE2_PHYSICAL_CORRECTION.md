# Gate 2 Physical Correction Decision Record

## D-022 — Gate 2-3P-R 보정 명세 작성

- 결정일: 2026-07-01
- 사용자 승인:
  - Gate 2-3P-3 `NOT PASSED` 결과 승인
  - Gate 2-3P-R 보정 명세 작성 승인
- 기준 모델: `3.0.0-research`
- 제안 모델: `4.0.0-research`
- 브랜치: `feature/gate2p3-correction-spec`
- Issue: #16

## 실패 근거

- proxy false activation: 0.100000%, 95% 상한 0.205288%
- M3 false activation: 0.160000%
- irrelevant metadata activation: 0.120048%
- lift 1.25 strict detection: 0.0%~24.2%
- post-draw-error activation: 2.6%
- signal-decay M0 return: 65.8%

## 보정 방향

1. field별 prequential likelihood-ratio e-process
2. evidence가 없으면 exact M0를 반환하는 global abstention
3. stable context와 transient context 내부 분리
4. field parent와 context child의 hierarchical partial pooling
5. interaction residual의 별도 강한 수축
6. post-draw timestamp·결과필드 global veto
7. M3 maxT를 anytime-valid restart-mixture e-process로 교체
8. activation 1000 / deactivation 100 hysteresis
9. transient expiry와 208회 M0 return 계약
10. development·calibration·sealed validation seed 분리

## 유지되는 기준

- M0~M4 상위 역할
- 정확히 6개 번호 × 5세트 출력
- lift 1.05 / 1.10 / 1.25 / 1.50
- lift 1.25 strict detection 80%
- overall false activation 0.1%
- one-sided 95% upper 0.2%
- M4 deployable cap 10%
- Pair interaction 예측 비활성
- RESEARCH M0-only

## 제안 검증규모

- calibration sanity: 20,000 series
- sealed null: 10,000
- sealed positive: 24,000
- sealed robustness: 18,000
- PASS/FAIL total: 72,000

## 중단조건

`4.0.0-research`가 sealed validation에 실패하면 동일 synthetic suite에서 추가 구조·파라미터 튜닝을 중단한다. 새로운 외부 물리데이터가 확보되기 전 비균등 로또 예측연구를 재개하지 않는다.

## 현재 결정

- 보정 명세만 완료
- Python 구현 미승인
- calibration·sealed validation 미승인
- 실제 데이터·모바일 개발 계속 차단
- `3.0.0-research` 실패결과와 PR #15 보존
