# Gate 2 Physical Evidence Progress

최종 갱신: 2026-06-30  
현재 브랜치: `feature/gate2-physical-evidence-spec`  
관련 이슈: #10

## 전체 진행률

| 단계 | 내용 | 상태 | 진척도 |
|---|---|---|---:|
| Gate 2-3P-1 | M4·데이터·검증 명세 | 완료, 사용자 검토 대기 | 100% |
| Gate 2-3P-2 | Python 구현 | 미착수 | 0% |
| Gate 2-3P-3 | 합성 null/positive 재검증 | 미착수 | 0% |
| Gate P-1 | 실제 메타데이터 100회 파일럿 | 미착수 | 0% |
| Gate 2-4P | 실제 데이터 Walk-forward | 차단 | 0% |
| 모바일 MVP | 5세트 결과 UI | 차단 | 0% |

## Gate 2-3P-1 완료 항목

- 기존 M0~M3와 5세트 출력 유지
- M4 물리·운영 증거모형 정의
- 추첨기·볼 세트·교체·환경·모의추첨·과거 배출순서 스키마 정의
- 데이터 출처·관측시각·사전가용성·신뢰도 계약 정의
- M3를 단일 maxT omnibus 검정으로 변경하는 안 정의
- null·positive·결측·오분류·regime 합성 시나리오 정의
- 통과·중단 기준 고정
- 제안 모델 버전 `3.0.0-research`

## 현재 차단사항

- 실제 1~1230회 Walk-forward
- 실제 다음 회차 후보 공개
- 모바일 UI 구현
- M4 코드 구현

M4 코드 구현은 Gate 2-3P-1 명세 사용자 승인 후 시작한다.

## 다음 실행 순서

1. 사용자 명세 승인
2. `feature/gate2-physical-evidence-engine` 브랜치 생성
3. metadata validator와 M4 구현
4. maxT calibrator 구현
5. synthetic generator·tests·CI 구현
6. smoke 통과
7. 전체 합성검증
8. 결과에 따라 실제 메타데이터 파일럿 또는 연구 중단
