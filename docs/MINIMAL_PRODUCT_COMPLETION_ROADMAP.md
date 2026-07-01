# Minimal Product Completion Roadmap

작성일: 2026-07-01  
상태: 사용자 검토용 재정리 명세  
작업 브랜치: `docs/minimal-product-completion-roadmap`  
기준 브랜치: `docs/full-history-recovery-audit`

## 1. 목적

복원된 Gate 1~Gate 2-3P-R3M-3-2 이력을 기준으로 다음을 분리한다.

1. 6개 번호 × 5세트 제품에 이미 구현된 항목
2. 제품 연결·운영 관점에서 미완료인 항목
3. 검증 실패로 동결해야 하는 항목
4. 외부기관 접촉 없이 제품을 완성하기 위한 최소 잔여 단계

이번 문서는 분류와 로드맵만 고정한다. Python 구현, 추가 DEV, CAL, SEALED, 실제 Walk-forward, 모바일 UI, main 병합을 수행하지 않는다.

## 2. 제품의 현실적 정의

외부 실측 metadata가 없고 비균등 모델이 검증을 통과하지 못한 현재 상태에서 완성 가능한 제품은 다음이다.

```text
M0-safe research product
```

필수 동작:

- 다음 회차에 대해 정확히 6개 번호 × 5세트 출력
- 5세트는 서로 중복되지 않음
- 동일 data/version/seed에서 동일 결과
- 미래 회차 데이터 사용 금지
- 검증된 비균등 신호가 없으면 exact M0 사용
- 사용자 화면에 `통계적 우위 없음` 표시
- M1~M4는 shadow diagnostics로만 보존
- prediction hash와 data version 기록
- public release와 research output을 구분

현재 상태에서 M1~M4를 제품 확률에 적용하거나 “당첨확률을 높인다”고 표현하면 안 된다.

## 3. 구현 완료 항목

### 3.1 데이터·아카이브

- 1~1230회 `data/draws.json`
- 1,230개 회차 연속성·중복·구조 검증
- dataset SHA-256
- deterministic rebuild
- HTML 아카이브와 archive index
- data version 및 source manifest

제한: 전체 데이터가 `auto_checked`이며 official endpoint exact-match 잠금은 완료되지 않았다.

### 3.2 Exact probability core

- exact 6-of-45 fixed-size distribution
- elementary symmetric polynomial normalization
- 번호별 marginal 계산
- finite mixture
- deterministic k-best combination
- M0 uniform model

### 3.3 5세트 생성 기반

- 정확히 6개 번호 × 5세트
- 동일 세트 중복 금지
- deterministic seed
- 균등상태 diversified portfolio
- prediction hash

### 3.4 안전장치

- target draw 이후 데이터 hard rejection
- research-only 상태
- public release 차단
- RESEARCH final distribution M0=1
- 현재 결과·보너스·배출순서 metadata 차단
- post-draw timestamp 차단
- metadata 부족 시 exact M0 fallback

### 3.5 연구모듈 구현

- M1 persistence shadow experts
- M2 reversal shadow experts
- M3 regime-change 구조
- M4 contextual physical/operational engine
- 4.0 field-level e-process correction engine
- 5.0 exact group LR oracle engine
- past-only predictable-group learner

이 항목들은 코드가 존재한다는 뜻이며 제품 적용 승인을 의미하지 않는다.

### 3.6 검증·재현 인프라

- deterministic synthetic generators
- null, positive, robustness scenarios
- CI smoke와 unit tests
- DEV/CAL/SEALED namespace 분리
- result report와 hash lock
- 실패 결과 보존

## 4. 미완료 항목

### 4.1 단일 제품 실행경로

현재 여러 Draft PR과 계층형 브랜치에 데이터·엔진·교정모듈이 분산돼 있다.

미완료:

- Gate 1 canonical data와 최종 안전 엔진을 한 release-candidate branch에서 조립
- 단일 command/API로 target draw를 입력하고 5세트를 반환
- config/version/data hash를 한 결과 payload에 통합
- shadow diagnostics와 사용자 표시값을 분리

### 4.2 제품 출력계약 최종화

미완료:

- JSON 결과 schema 최종 잠금
- 정확히 5세트·각 6개·범위 1~45·세트 내 중복 0 계약
- `statistical_edge=false`와 `reason=no_validated_nonuniform_signal` 고정
- model/data/config/prediction hash 필수화
- 사용자 표시 문구 고정

### 4.3 Canonical data release 상태

현재 1~1230회 데이터는 구조 검증은 통과했지만 공식 exact-match 잠금이 아니다.

미완료:

- 공식 공개결과와 전체 또는 증분 대조
- verified/locked 상태 분리
- 신규 회차 append·재검증 절차
- 데이터 불일치 시 release 거부

기관 비공개자료 요청은 필요하지 않다. 공식 공개 당첨결과 대조만 대상이다.

### 4.4 End-to-end product QA

미완료:

- canonical data 로드부터 5세트 출력까지 통합 테스트
- 같은 입력 두 번의 byte-identical 결과
- 미래 데이터 차단 테스트
- M0 exact fallback 테스트
- 다섯 세트 uniqueness·범위·정렬 검증
- 결과 payload hash 재현
- 연구용 비균등 모델이 제품분포에 섞이지 않는 scope lock

### 4.5 웹 결과표 연결

Gate 1 HTML 아카이브는 존재하지만 최종 예측 runner 결과와 연결된 제품화 화면은 잠금되지 않았다.

최소 제품에서는 모바일 앱이 아니라 기존 HTML에 다음만 연결하면 된다.

- target draw
- 5세트
- data/model version
- prediction hash
- `통계적 우위 없음`
- M0 fallback 사유

이번 단계에서는 UI를 구현하지 않는다.

### 4.6 운영 절차

미완료:

- 신규 공식 회차 확인
- 데이터 append
- integrity check
- 다음 target draw 결정
- deterministic prediction 생성
- 결과 snapshot 보존
- 실제 당첨결과 공개 후 평가기록 append

## 5. 검증 실패로 동결된 항목

### 5.1 M4 3.0 제품 적용

PR #15 결과 `NOT PASSED`.

동결:

- ball-set effect를 제품 가중치로 사용
- machine effect를 제품 가중치로 사용
- machine×ball interaction을 제품 가중치로 사용
- temporary environment effect를 제품 가중치로 사용
- pretest effect를 제품 가중치로 사용

실패기준과 seed를 변경하지 않는다.

### 5.2 M3/M4 4.0 config 선택

PR #22 결과 `NO_ELIGIBLE_CONFIG`.

동결:

- 81개 config 중 임의 winner 선택
- threshold 1000 완화
- 208회 life 완화
- R4 진입

### 5.3 Past-only predictable group

PR #32 결과 `PREDICTABLE_GROUP_FAIL`.

동결:

- 520 window learner의 제품 적용
- half-life·prior·fold·group size 사후수정
- 과거번호만으로 favored group을 만들었다는 주장

### 5.4 실제값 없는 물리변수

다음은 제품 가중치에 직접 사용하지 않는다.

- 공 무게·직경·구형도·마모 일반규격
- 항온항습 설명
- 사전 테스트 9회라는 운영설명
- 추첨기·볼 교체에 대한 비회차별 설명

회차별 사전관측값이 없으므로 shadow hypothesis 또는 문서정보로만 보존한다.

### 5.5 CAL·SEALED

- CAL 미실행
- SEALED 미실행
- 현재 실행 금지
- 통과하지 않은 모델을 PROMOTED로 표시 금지

## 6. 최소 잔여 개발단계

외부기관 접촉 없이 제품 완성까지 필요한 최소 단계는 **4개**다.

### Product Gate P1 — Release-candidate 조립

목적:

- 기존 구현을 새로 발명하지 않고 한 branch에서 조립

작업:

- Gate 1 canonical data 연결
- Gate 2-2 exact engine·5세트 생성기 연결
- 최종 distribution을 exact M0로 강제
- M1~M4는 shadow-only로 연결하거나 완전히 비활성화
- 단일 runner와 결과 schema 확정

통과조건:

- target draw 입력 → 정확히 5세트 출력
- 미래 데이터 미사용
- `statistical_edge=false`
- prediction hash 재현

### Product Gate P2 — 데이터·통합 QA

목적:

- 예측력 튜닝이 아니라 제품 실행의 정확성과 재현성 검증

작업:

- 데이터 범위·중복·번호 유효성 재검증
- 공식 공개결과 대조정책 적용
- end-to-end deterministic test
- five-set contract test
- M0-only scope lock test
- 실패 시 공개 차단

통과조건:

- 모든 product acceptance test PASS
- 동일 입력 byte-identical
- 비균등 model weight 0

### Product Gate P3 — HTML MVP 연결

목적:

- 기존 Gate 1 HTML을 계산결과 표시화면으로 사용

최소 화면:

- 다음 target draw
- 5개 후보세트
- `통계적 우위 없음`
- model/data version
- prediction hash
- 생성시각

제외:

- 모바일 네이티브 앱
- Supabase
- 회원·결제·알림
- 비균등 우위 표현

### Product Gate P4 — Research release lock

목적:

- 제품을 `검증된 예측기`가 아니라 `재현 가능한 연구형 5세트 생성기`로 잠금

필수 산출물:

- release manifest
- data/config/model hashes
- product acceptance report
- known limitations
- M3/M4 frozen-result references
- rollback commit
- public wording lock

최종 상태:

```text
PRODUCT_READY_RESEARCH_M0
```

이는 다음을 뜻한다.

- 5세트 제품동작 완료
- 비균등 예측우위 미인정
- 신호 없음 명시
- 이후 실제 prospective evidence가 생길 때만 별도 모델 승격

## 7. 최소경로에서 제외되는 단계

다음은 제품 완성의 필수조건이 아니다.

- 동행복권·MBC 접촉
- 비공개 물리 metadata 수집
- M4F-2A
- 추가 M3/M4 hyperparameter 탐색
- CAL·SEALED
- 실제 물리 metadata walk-forward
- 모바일 앱
- Supabase

이 항목들은 향후 별도 연구 또는 제품확장 경로다.

## 8. 단계 수와 현재 위치

```text
현재: 역사 복원·상태 분류 완료
남음: P1 조립 → P2 제품 QA → P3 HTML 연결 → P4 release lock
```

즉, 외부기관 접촉과 비균등 모델 재검증을 제외하면 **최소 4단계**다.

## 9. 현재 승인범위

이번 사용자 승인범위는 문서 재정리까지다.

미실행:

- Python 구현
- 기존 코드 조립
- 데이터 대조 실행
- product QA 실행
- 실제 Walk-forward
- HTML 수정
- CAL·SEALED
- main 병합
