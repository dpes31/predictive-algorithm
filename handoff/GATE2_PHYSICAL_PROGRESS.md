# Gate 2 Physical Evidence Progress

최종 갱신: 2026-06-30  
현재 브랜치: `feature/gate2p2-engine`  
기준 브랜치: `feature/gate2-physical-evidence-spec`  
관련 이슈: #12  
Draft PR: #13

## 전체 진행률

| 단계 | 내용 | 상태 | 진척도 |
|---|---|---|---:|
| Gate 2-3P-1 | M4·데이터·검증 명세 | 사용자 승인 완료 | 100% |
| Gate 2-3P-2 | Python 구현 | 완료, 사용자 검토 대기 | 100% |
| Gate 2-3P-3 | 합성 null/positive 전체 재검증 | 미착수 | 0% |
| Gate P-1 | 실제 메타데이터 100회 파일럿 | 미착수 | 0% |
| Gate 2-4P | 실제 데이터 Walk-forward | 차단 | 0% |
| 모바일 MVP | 5세트 결과 UI | 차단 | 0% |

## Gate 2-3P-2 완료 항목

### 모델·계약

- 모델 버전 `3.0.0-research`
- Feature contract `2.0.0`
- Physical metadata schema `1.0.0`
- 기존 M0~M3 유지
- 신규 M4 물리·운영 증거모형 구현
- M4 초기 배포 비중 상한 10%
- RESEARCH 상태 최종분포 M0=100% 유지

### 데이터 안전

- 출처·관측시각·사전가용성·신뢰도 검증
- 현재 회차 결과 필드 입력 차단
- 추첨 후 관측값의 pre-draw 위장 차단
- inferred·unknown 데이터의 예측 입력 차단
- 메타데이터 스키마 버전 검증
- 결측·신뢰도 미달 시 M4 균등 fallback

### M4

- 추첨기·볼 세트·regime context별 번호 포함률 학습
- Beta-style 강한 0 수축
- 번호별 logits 중심화
- context support 최소 20회
- 다수 필드 추가만으로 확신이 커지지 않도록 평균 결합
- 동일 입력·seed 재현성

### M3 maxT

- 단일 familywise maxT calibration 구현
- plus-one empirical p-value
- 별도 Holm 중복 적용 없음
- full contract 최소 null 10,000개
- calibration 부족 시 M3 비활성

### Synthetic·CI

- ball-set·machine·regime reversal·missingness scenario generator
- deterministic physical smoke runner
- 전체 unit test 통과
- smoke 2회 byte-for-byte 동일 결과 확인
- research-only·public-release 차단 계약 확인

## 검증 결과

- GitHub Actions run: `28444499045`
- Conclusion: `success`
- canonical data validation: success
- unit tests: success
- deterministic physical smoke: success
- research-only contract: success
- smoke artifact ID: `7980514978`
- smoke artifact SHA-256: `8134f362de8e9c06f90fcd04586b27871ec4f5cfa84eba952e6036799e836253`
- unit-test artifact ID: `7980514368`
- unit-test artifact SHA-256: `a107163d564a4d80d32112332959e2148deef267b7396d11fd409755178c4896`
- smoke report hash: `d6f504ccbc964a72fd2e870e0ae1c933a07241b4cb16a868436e1455d218a7f7`

## Smoke 해석 제한

Smoke 결과는 코드 실행·계약·재현성 확인이다. 단일 holdout의 Log Loss 값은 예측력 증거가 아니다.

- unrelated scenario에서도 M4 계산은 가능하지만 RESEARCH 최종 가중치는 0이다.
- ball-set 단일 holdout이 M0보다 나빴던 결과도 그대로 보존한다.
- Gate 2-3P-3에서 수천 개 null·positive series로 오탐률과 탐지력을 다시 평가해야 한다.

## 현재 차단사항

- Gate 2-3P-3 전체 통계검증 — 사용자 승인 전 차단
- 실제 1~1230회 Walk-forward
- 실제 다음 회차 후보 공개
- 모바일 UI 구현
- Supabase 연결
- Pair interaction 예측 활성화

## 다음 실행 순서

1. 사용자 Gate 2-3P-2 구현 승인
2. `feature/gate2-physical-validation` 브랜치 생성
3. maxT null 10,000 calibration 구현·실행
4. model null 4,000 / independent null 5,000 실행
5. positive scenario·effect size별 500 실행
6. 결측·오분류·관계소멸 robustness 실행
7. Gate 2-3P-3 통과·실패 판정
8. 통과 시 실제 메타데이터 100회 파일럿
