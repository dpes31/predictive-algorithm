# Gate 2 Physical Evidence Progress

최종 갱신: 2026-07-01  
현재 브랜치: `feature/gate2p3-correction-spec`  
기준 브랜치: `feature/gate2p3-validation`  
관련 이슈: #16

## 전체 진행률

| 단계 | 내용 | 상태 | 진척도 |
|---|---|---|---:|
| Gate 2-3P-1 | M4·데이터·검증 명세 | 사용자 승인 완료 | 100% |
| Gate 2-3P-2 | Python 구현 | 사용자 승인 완료 | 100% |
| Gate 2-3P-3 | 합성 null/positive 전체 재검증 | NOT PASSED | 100% |
| Gate 2-3P-R1 | 보정 아키텍처·검증 명세 | 완료, 사용자 검토 대기 | 100% |
| Gate 2-3P-R2 | `4.0.0-research` Python 구현 | 미착수 | 0% |
| Gate 2-3P-R3 | unit·smoke·development 검수 | 차단 | 0% |
| Gate 2-3P-R4 | sealed 전체 재검증 | 차단 | 0% |
| Gate P-1 | 실제 메타데이터 100회 파일럿 | 차단 | 0% |
| Gate 2-4P | 실제 데이터 Walk-forward | 차단 | 0% |
| 모바일 MVP | 5세트 결과 UI | 차단 | 0% |

## Gate 2-3P-3 실패 기준

- proxy false activation: 5/5,000 = 0.100000%
- proxy one-sided 95% upper: 0.205288% — 기준 실패
- M3 false activation: 0.160000% — 기준 실패
- irrelevant metadata activation: 0.120048%
- lift 1.25 strict detection: 0.0%~24.2%, 목표 80%
- post-draw-error activation: 2.6%
- signal-decay M0 return: 65.8%, 목표 80%

## Gate 2-3P-R1 완료 항목

### 제안 버전

- model: `4.0.0-research`
- feature contract: `3.0.0`
- physical metadata schema: `1.0.0` 유지

### M4 보정

- field별 prequential likelihood-ratio e-process
- stable / transient family 내부 분리
- evidence threshold 1000 / 100 hysteresis
- evidence 부족 시 exact M0 abstention
- hierarchical partial pooling
- interaction residual 별도 수축
- 단일 field·interaction·transient weight cap

### 데이터 안전

- post-draw timestamp global veto
- 현재회차 결과필드 global veto
- required contradiction global veto
- optional unknown은 해당 field만 제외
- invalid metadata에서 M4 weight 0

### M3 보정

- 기존 maxT 폐기 제안
- 번호·betting fraction·restart mixture e-process
- trigger 1000 / deactivation 100
- detection과 post-change prediction 분리
- trigger 최대수명 208회

### 검증 독립성

- development / calibration / sealed seed namespace 분리
- sealed manifest 실행 전 commit
- 첫 결과 후 코드·config 수정 금지
- 실패 seed 제외 금지

## 유지되는 기준

- 6개 번호 × 5세트 출력
- M0~M4 상위 역할
- RESEARCH 최종분포 M0-only
- M4 cap 10%
- Pair interaction 예측 비활성
- false activation 0.1%
- one-sided 95% upper 0.2%
- lift 1.25 strict detection 80%
- 기존 실패 시나리오와 효과크기 유지

## 제안 R4 검증규모

- calibration sanity: 20,000
- sealed null: 10,000
- sealed positive: 24,000
- sealed robustness: 18,000
- total PASS/FAIL series: 72,000

## 중단 원칙

`4.0.0-research`가 sealed validation에 실패하면 동일 synthetic suite에서 추가 튜닝을 중단한다. 새로운 외부 물리데이터가 확보되기 전 비균등 로또 예측연구를 재개하지 않는다.

## 현재 차단사항

- R2 Python 구현 — 사용자 승인 전 차단
- hyperparameter grid 실행
- calibration·sealed validation
- 실제 metadata predictor pilot
- 실제 1~1230회 Walk-forward
- 실제 미래 번호 5세트 공개
- 모바일 UI·Supabase
- M4 deployable weight 적용

## 다음 사용자 결정

다음 세 가지를 승인해야 R2 구현을 시작한다.

1. 보정 아키텍처
2. 모델 버전 `4.0.0-research`
3. sealed validation과 실패 시 중단 원칙
