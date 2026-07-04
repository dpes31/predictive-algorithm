# Gate 2-2 엔진 골격 검토 안내

상태: 구현 완료 후 자동검증 대기  
범위: 수학적 정합성·데이터 차단·재현성·합성 균등 smoke test  
미포함: 전체 931회 백테스트, 비균등모형 승격, 실제 1231회 공개예측, UI 연결

## 이번 단계에서 구현한 것

- 1~45 번호 중 정확히 6개를 선택하는 확률분포
- elementary symmetric polynomial 기반 정규화
- 번호별 정확한 주변 포함확률
- M0 균등모형
- M1 지속 sub-expert 7종
- M2 반전·평균회귀 sub-expert 7종
- M3 구조변화 sub-expert 4종
- 한 회차 결과가 가중치를 폭증시키지 않는 순차 갱신식
- CLOSED / RESEARCH / CANDIDATE / PROMOTED 상태기계
- 연구단계에서 최종 공개분포를 M0로 고정하는 안전장치
- 결정론적 5세트 후보 생성
- 미래 회차 데이터 입력 차단
- 연구용과 공개용 데이터 상태 분리
- 동일 입력·동일 버전의 결과 해시 재현

## 현재 M3 처리

M3의 피처와 분포 구조는 구현했지만, 실제 활성화 계수인 `change_gate`는 0으로 고정했습니다.

이유:

- 명세상 M3 활성화에는 균등 Monte Carlo null calibration이 필요
- 해당 calibration은 Gate 2-3 범위
- 검증 전 임의 임계값으로 구조변화를 활성화하지 않기 위함

따라서 Gate 2-2의 M3는 구조가 존재하지만 M0와 같은 분포를 냅니다.

## 현재 출력의 의미

합성 균등 데이터 smoke test에서는 다음 상태가 정상입니다.

```text
gate_state: RESEARCH
advantage_status: 통계적 우위 없음
model_weights: M0 1.0 / M1 0 / M2 0 / M3 0
shadow_weights: M0~M3 각 0.25
research_only: true
public_release_allowed: false
```

후보 5세트가 출력되더라도 예측력 검증 결과가 아니라, 균등분포에서 결정론적으로 만든 테스트 포트폴리오입니다.

## 자동검증 항목

- Gate 1 원본 데이터 무결성
- 전체 Python 단위테스트
- 작은 상태공간에서 확률합 1
- 번호별 주변확률 합 6
- 피처 값 유한성·범위·해시 재현
- 미래 데이터 차단
- `auto_checked` 공개예측 차단
- 단일 회차 가중치 폭증 방지
- CANDIDATE 비균등 비중 최대 30%
- 연구단계 최종 M0 복귀
- 후보 5세트 중복 없음
- 동일 smoke 실행 파일 byte 단위 일치

## 다음 단계

Gate 2-2 검수 통과 후 Gate 2-3에서 다음을 구현합니다.

1. 균등 null 시계열 반복실험
2. 고정 편향 positive control
3. 지속·반전·구조변화 synthetic signal
4. M3 change gate null calibration
5. 오탐률·탐지력·복귀시간 측정
6. pair interaction은 진단만 수행하고 여전히 비활성화

전체 실제 데이터 Walk-forward는 Gate 2-4에서 진행합니다.
