# Gate 2-3R Decision Record

## D-018 — Gate 2-3R 재검증 실패 및 Gate 2-4 차단 유지

- 결정일: 2026-06-30
- 사용자 승인 범위:
  - 모델 버전 `2.1.0-research`
  - M1/M2 temperature grid 0.05, 0.10, 0.20, 0.50, 1.00
  - M3 raw diagnostic 분리
  - 전체 Pair와 사전지정 Pair 검정 분리
  - 엄격 positive-control 성공 판정
  - 기존 실패 시나리오 유지

### 재실험

- Null calibration: 1,000개 시계열
- 독립 null validation: 1,000개 시계열
- Positive-control: 시나리오당 100회
- 시계열당 1,230회
- Alpha: 0.001
- 실제 과거번호 사용: 없음
- 결과 해시: `ec57a01e7781d5679cc8fc1b1c146055b06b6836740924cfbb0f1bfd6bef15c6`

### 결과

- Gate proxy false activation: 4/1,000 = 0.4%
- 지속 M1 엄격 탐지: 100%
- 반전 M2 엄격 탐지: 71%
- 고정편향 M1 엄격 탐지: 전 구간 0%
- M3 활성화: 0%
- Pair factor 3.0 사전지정 Pair 탐지: 22%
- 80% power 최소 fixed-bias·Pair 효과크기: 없음

### 구조적 발견

1,000개 calibration과 plus-one empirical p-value를 사용하면 최소 raw p는 `1/1001`입니다. M3의 4개 진단에 Holm 보정을 적용하면 최소 adjusted p는 `4/1001 = 0.003996004`입니다. Alpha 0.001보다 크므로 현재 계약에서 M3 활성화는 수학적으로 불가능합니다.

### 결정

- Gate 2-3R을 `NOT PASSED`로 판정
- Gate state `RESEARCH` 유지
- 최종 사용자 분포 `M0 only` 유지
- Gate 2-4 실제 데이터 Walk-forward 차단 유지
- 실제 후보 생성·공개 차단 유지
- Pair interaction 예측 비활성 유지
- 현 결과를 삭제하거나 seed·효과크기를 소급 변경하지 않음

### 후속 변경

다음 변경은 별도 사용자 승인이 필요합니다.

1. M3 calibration 최소 3,999개 이상 또는 omnibus/maxT 검정
2. Gate proxy false activation 제어 강화
3. 장기 고정편향 탐지기 분리 여부
4. 반전 71%의 허용 여부
5. Pair 진단 유지·폐기·재설계
6. 새 모델 버전

### 실행 제한

GitHub 브랜치에는 보정 코드가 반영됐으나 사용 가능한 연결 도구로 Actions workflow를 디스패치할 수 없었습니다. 전체 수치 결과는 커밋된 수식을 옮긴 결정론적 standalone mirror에서 산출됐으며 GitHub CI 확인은 미완료입니다.
