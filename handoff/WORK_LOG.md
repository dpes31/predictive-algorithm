# Work Log

이 파일은 append-only 작업 기록입니다. 기존 항목을 삭제하거나 재작성하지 않습니다.

---

## 2026-06-30 — Gate 0 승인 및 거버넌스 기반 구축

### 작업자

- ChatGPT / GitHub connector

### 사용자 결정

- Gate 0 승인
- 핵심 알고리즘과 변경 금지사항을 Markdown으로 고정
- 향후 Codex 및 타 AI 에이전트가 이어서 개발할 수 있도록 최상위 운영문서 필요
- 모든 작업마다 인수인계와 히스토리 누적 필요

### 수행 내용

- 빈 저장소를 `README.md`로 초기화
- 작업 브랜치 `feature/gate1-governance-foundation` 생성
- `AGENTS.md` 작성
- `docs/ALGORITHM_SPEC.md` v1.0.0 작성 및 FROZEN 표시
- `docs/NON_NEGOTIABLES.md` 작성
- `docs/DATA_POLICY.md` 작성
- `docs/VALIDATION_PROTOCOL.md` 작성
- `handoff/PROJECT_HANDOFF.md` 작성
- `handoff/WORK_LOG.md` 생성
- `handoff/DECISION_LOG.md` 생성 예정

### 핵심 보호조치

- M0~M3 동적 혼합모형 박제
- 균등모형 자동복귀 원칙 박제
- 단일 빈도식 축소 금지
- 95% 불확실성 표시와 99.9% 승격 기준 박제
- 미래 데이터 누출 금지
- 예측 잠금과 동일 입력 재현성 원칙 박제
- 작업 종료 시 handoff 문서 갱신 의무화

### 검증

- GitHub 저장소 접근 및 쓰기 권한 확인
- main 초기화 완료
- 별도 feature 브랜치에서 문서 생성 확인

### 남은 작업

- `handoff/DECISION_LOG.md` 생성
- README를 전체 문서 안내 구조로 확장
- Draft PR 생성
- Gate 1 데이터·아카이브 개발 시작

### 알려진 위험

- 1230회 사용자 제공값은 공식 독립 대조 전이므로 `pending_manual`
- 실제 데이터 파일과 테스트는 아직 저장소에 추가되지 않음

---

## 2026-06-30 — 거버넌스 작업 완료 추가 기록

### 완료 항목

- `handoff/DECISION_LOG.md` 생성 완료
- README 문서 진입점 및 Gate 안내 확장 완료
- Draft PR #2 생성 완료
- `handoff/PROJECT_HANDOFF.md`에 PR·다음 작업·위험 갱신 완료

### 산출물

- 브랜치: `feature/gate1-governance-foundation`
- Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/2`
- 계획 이슈: `https://github.com/dpes31/predictive-algorithm/issues/1`

### 다음 작업

- 사용자에게 거버넌스 문서와 Draft PR 보고
- Gate 1 데이터·아카이브 기반 구현
- 실제 데이터 적재 전 공식 출처와 1230회 상태 재확인

### 검증 상태

- 문서 9개가 별도 feature 브랜치에 존재
- main에는 초기 README만 존재하며 개발내용은 병합되지 않음
- PR은 Draft 상태이며 사용자 승인 전 병합하지 않음

---

## 2026-06-30 — Gate 1 데이터·아카이브 구현

### 작업자

- ChatGPT / GitHub connector
- GitHub Actions

### 구현 범위

- 예측 엔진은 변경하지 않음
- 1~1230회 단일 원본 데이터 구축
- 데이터 스키마·체크섬·검증상태 구현
- 검색 가능한 과거번호 아카이브 HTML 구현
- 자동 CI 검증과 재현성 검사 구현

### 추가 파일

- `.gitignore`
- `requirements.txt`
- `data/draws.schema.json`
- `data/draws.json`
- `data/source_manifest.json`
- `data/checksums.sha256`
- `scripts/build_dataset.py`
- `scripts/validate_draws.py`
- `scripts/build_archive.py`
- `app/index.html`
- `app/archive.html`
- `app/assets/css/app.css`
- `app/assets/js/archive.js`
- `app/data/archive_index.json`
- `tests/test_data_integrity.py`
- `tests/test_static_contract.py`
- `.github/workflows/gate1-build.yml`
- `reports/data_integrity.json`
- `reports/gate1_summary.md`
- `reports/secondary_crosscheck.md`
- `docs/GATE1_REVIEW_GUIDE.md`

### 데이터 결과

- 데이터 버전: `draws-2026.06.27-r1`
- 범위: 1~1230회
- 레코드 수: 1,230개
- 결측 회차: 0
- 중복 회차: 0
- 구조검사: 통과
- 레코드 체크섬: 통과
- 데이터셋 SHA-256: `57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1`
- 동일 입력 재생성 SHA 유지: 통과

### 공식 검증 상태

- 기존 동행복권 JSON 엔드포인트가 자동 요청에 응답하지 않음
- 공식 exact match: 0
- `verified`: 0
- `auto_checked`: 1,230
- `locked`: 0
- 공식 대조 전 데이터를 공식 검증 완료로 과장하지 않음

### 보조 교차검증

- 1~1229회 추첨일·본번호 6개를 이전 별도 데이터셋과 비교
- 불일치: 0건
- 1230회 본번호·보너스번호를 동행복권 발표 인용 보도와 비교
- 보너스번호 1~1229회는 별도 공식 전수 대조가 완료되지 않았음을 명시

### UI 기능

- 회차 검색
- 연도 필터
- 최신순·오래된순 정렬
- 30개 단위 더 보기
- 구간별 원형 번호 색상
- 보너스번호 표시
- 검증상태 배지
- 출처·잠금·체크섬 상세 펼침
- 전체·최근 52·30·10회 번호 빈도 참고 통계
- 통계가 미래 예측력이 아니라는 경고 표시
- Gate 1에서는 예측 버튼 비활성 유지

### 자동 검증

GitHub Actions `Gate 1 data and archive build`에서 다음 단계가 모두 통과함.

- 데이터 생성
- 오프라인 무결성 검사
- 아카이브 파생 데이터 생성
- 동일 입력 재생성 SHA 비교
- Python 단위 테스트
- HTML 정적 계약 테스트
- 리뷰 ZIP 아티팩트 생성

### 수동 UI 확인

- 데스크톱 렌더링 확인
- 모바일 렌더링 확인
- 1230 검색 시 1건 표시 확인
- 오름차순 정렬 시 1회가 첫 카드로 표시됨을 확인
- 2026년 필터 결과 확인
- 번호별 통계 45개 행 확인

### 남은 위험 및 다음 판단

- 공식 자동 대조 경로가 현재 차단되어 1,230개 모두 잠금 해제 상태
- Gate 2 예측 입력으로 사용하기 전에 공식 검증 전략을 확정해야 함
- 사용자 UI 검토 및 Gate 1 승인 전 Draft PR 병합 금지

---

## 2026-06-30 — Vercel Preview 배포 경로 설정

### 사용자 상황

- Vercel 프로젝트 연결 및 Production 배포 완료
- 현재 배포 소스가 `main`의 초기 커밋이라 루트 화면에서 `404: NOT_FOUND` 확인

### 수행 내용

- feature 브랜치에 `vercel.json` 추가
- `/` 요청을 `/app/index.html`로 임시 리다이렉트
- `/archive` 요청을 `/app/archive.html`로 임시 리다이렉트
- `main` 병합 없이 feature 브랜치 Preview에서 Gate 1 화면을 확인할 수 있도록 구성

### 다음 확인

- Vercel Deployments에서 `feature/gate1-governance-foundation` 소스의 Preview 배포가 생성되는지 확인
- Preview URL에서 홈과 `/archive` 접속 확인
- Production은 사용자 승인 전까지 `main` 초기 상태로 유지

---

## 2026-06-30 — Gate 1 승인 및 Gate 2-1 예측 엔진 명세

### 사용자 승인

- Gate 1 UI와 1230회 표시 확인 완료
- 현재 `auto_checked` 데이터의 연구용 백테스트 사용 승인
- 실제 미래예측 공개와 데이터 잠금은 공식 검증 완료 후 진행
- Gate 2 계획 승인
- 인수인계 자료 계속 누적 요청

### 작업 브랜치

- `feature/gate2-engine-spec`
- 기준: `feature/gate1-governance-foundation`

### 생성 항목

- Issue #3 `Gate 2-1 예측 엔진 명세 및 백테스트 계약 고정`
- `docs/GATE2_ENGINE_SPEC.md`
- `docs/GATE2_FEATURE_CONTRACT.md`
- `docs/GATE2_BACKTEST_PROTOCOL.md`
- `docs/GATE2_IMPLEMENTATION_PLAN.md`

### 고정한 핵심 설계

- 조합확률을 6차 elementary symmetric polynomial로 정확 정규화
- M0~M3와 sub-expert 구조
- 지속·반전 가설 분리
- pair interaction 초기값 0 및 별도 승격조건
- CLOSED / RESEARCH / CANDIDATE / PROMOTED gate 상태
- 역사적 백테스트만으로 PROMOTED 금지
- 외부 Walk-forward 300~1230회
- Block A 300~609, B 610~919, C 920~1230
- Joint Log Loss 1차 지표
- Number-level Brier와 Calibration 보조지표
- 1,000개 균등 null 시계열
- 2%·5%·10% planted bias 및 지속·반전·구조변화 positive-control
- 52회 moving-block bootstrap, 20,000회 반복
- 4개 사전비교 Holm-Bonferroni
- 실제 승격은 최소 52회 prospective와 e-value 1000 필요
- 동일 입력·버전·설정 결정론적 재현

### 현재 상태

- Gate 2-1 문서는 `REVIEW CANDIDATE`
- Python 예측 엔진은 아직 작성하지 않음
- 연구용 1231회 후보도 아직 생성하지 않음
- 사용자 승인 후 Gate 2-2 엔진 골격으로 이동

### 다음 작업

- Gate 2-1 Draft PR 생성
- 사용자에게 핵심 의사결정과 변경사항 보고
- 승인 시 별도 구현 브랜치에서 Gate 2-2 시작
