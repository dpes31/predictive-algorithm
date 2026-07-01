# Gate 2-3P-R3M-3-2 Implementation Start

작성일: 2026-07-01

사용자가 predictable-group contract `1.0.0`과 Gate 2-3P-R3M-3-2 구현·DEV 실행을 승인했다.

허용 범위:
- 고정된 520회 학습창
- 고정 번호 점수식
- 260회 warmup + 52회 5-fold chronological validation
- group size 6, 10, 15 선택
- 52회 group freeze
- DEV-PG, DEV-PG-CI namespace
- 사전등록 positive/null 기준 평가
- 코드·테스트·workflow·result lock·handoff 갱신

금지 범위:
- 결과를 본 뒤 기준 또는 하이퍼파라미터 변경
- full M3
- CAL
- SEALED
- 실제 데이터
- 모바일 UI
- main 병합
