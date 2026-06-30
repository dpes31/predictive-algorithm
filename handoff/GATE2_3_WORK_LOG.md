# Gate 2-3 Work Log

- 작업일: 2026-06-30
- 작업 브랜치: `feature/gate2-synthetic-validation`
- 기준 브랜치: `feature/gate2-engine-core`
- 사용자 승인: Gate 2-2 승인, Gate 2-3 합성 null/positive-control 검증 진행

## 현재 구현

- exact weighted synthetic sampler
- fixed bias, persistence, reversal, regime shift, temporary anomaly, pair-factor scenarios
- block-aligned incremental diagnostics
- familywise null calibration over forecast origins
- Holm correction and M3 change-gate calculation
- exact blockwise M0/M1/M2/M3 probability probe
- independent null score calibration
- synthetic proxy decision
- binomial one-sided upper confidence bound
- JSON and Markdown report generation
- smoke tests and CI workflow

## 금지 범위 유지

- 실제 1~1230회 Walk-forward 미실행
- 1231회 후보 미생성
- pair interaction 예측모형 비활성
- 실제 공개예측 미허용
- Supabase 및 UI 미연결
