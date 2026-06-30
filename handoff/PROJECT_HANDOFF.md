# Project Handoff

최종 갱신일: 2026-06-30  
현재 Gate: **Gate 2-3P-1 물리·운영 증거모형 확장 명세 완료 · 사용자 검토 대기**  
현재 작업 브랜치: `feature/gate2-physical-evidence-spec`  
기준 브랜치: `feature/gate2-synthetic-validation-r1`  
관련 이슈: `#10 Gate 2-3P-1 물리·운영 증거모형 확장 명세`

## 1. 프로젝트 목적

로또 6/45 다음 회차에 대해 6개 번호 조합 5세트를 출력하는 모바일 예측기를 개발한다.

장기적으로 동일한 구조를 일반 의사결정 알고리즘으로 확장하지만, 현재 제품과 검증대상은 계속 로또번호 예측기다.

## 2. 기존 Gate 상태

- Gate 1: 승인 완료
- Gate 2-1: 승인 완료
- Gate 2-2: 승인 완료
- Gate 2-3: NOT PASSED
- Gate 2-3R: NOT PASSED
- 현재 Gate state: `RESEARCH`
- 현재 최종 적용분포: `M0 only`
- 실제 데이터 Walk-forward: 차단
- 실제 미래 후보 공개: 차단

Gate 2-3R 핵심 결과:

- Null proxy false activation 0.4%
- 지속 M1 엄격 탐지 100%
- 반전 M2 엄격 탐지 71%
- 고정편향 M1 탐지 0%
- M3 활성화 0%
- Pair factor 3.0 탐지 22%

## 3. 새로운 개발방향

기존 M0~M3와 5세트 출력을 유지하고, 추첨 전에 관측 가능한 물리·운영 데이터를 별도 증거모형 M4로 추가한다.

```text
과거 당첨번호
+ 추첨기·볼 세트·교체 구간
+ 사전 공개 운영조건
+ 과거 배출순서 요약
+ 데이터 신뢰도·결측
→ 번호 1~45 상대 포함확률
→ 6개 번호 조합 5세트
```

예측력이 보장된 것이 아니라, 기존보다 원인에 가까운 사전변수를 사용해 검증 가능한 가설을 추가한 것이다.

## 4. Gate 2-3P-1 완료 항목

- `docs/GATE2_PHYSICAL_EVIDENCE_SPEC.md`
  - M4 수식과 안전장치
  - M0~M3 유지
  - M3 maxT omnibus 변경안
  - 제안 버전 `3.0.0-research`
- `docs/GATE2_PHYSICAL_DATA_SCHEMA.md`
  - 회차별 물리 메타데이터 계약
  - 출처·관측시각·사전가용성·신뢰도
  - 결과 데이터와 메타데이터 분리
- `docs/GATE2_PHYSICAL_VALIDATION_PROTOCOL.md`
  - null·positive·robustness 시나리오
  - maxT 10,000 calibration
  - independent null validation 5,000
  - strict 통과·중단 기준
- `handoff/GATE2_PHYSICAL_PROGRESS.md`
  - 단계별 진행률과 차단상태

## 5. 고정 유지사항

- M0 균등 기준모형
- M1 지속
- M2 반전·평균회귀
- M3 구조변화
- 정확히 6개를 선택하는 조합분포
- 후보 5세트 출력
- 동일 입력·버전 재현성
- 신호 미확인 시 M0 복귀
- 군중 회피 최대 5%
- Pair interaction 예측 비활성
- `통계적 우위 없음` 표시
- 미래 데이터 누출 금지

## 6. 신규 M4 핵심

```text
eta_4[i,t] = sum(j) reliability[j,t] * beta[j,i,t] * x[j,t]
```

- 사전 관측 가능한 변수만 사용
- 결측이면 기여 0
- 강한 0 수축
- 번호별 효과 중심화
- 장비·볼 교체 후 기존 효과 감쇠
- 데이터 완전성·신뢰도 미달 시 M4 비중 0
- CANDIDATE에서도 M4 비중 초기 상한 10%

## 7. 다음 단계

### Gate 2-3P-2 — 개발

명세 사용자 승인 후 별도 브랜치에서 구현한다.

1. metadata contracts·validator
2. M4 hierarchical shrinkage expert
3. M3 maxT calibrator
4. physical synthetic generator
5. future-leakage·missingness·determinism tests
6. CI smoke

### Gate 2-3P-3 — 재검증

개발 완료 후에만 실행한다.

- maxT null calibration 10,000
- model null calibration 4,000
- independent null validation 5,000
- positive scenario별 500
- 무관변수·결측·오분류·교체·관계소멸 검증

### Gate P-1 — 실제 데이터 파일럿

합성검증 통과 후 최근 100회 기준 실제 메타데이터 확보 가능성을 조사한다.

## 8. 현재 차단사항

- M4 코드 구현 — 명세 승인 전 차단
- 전체 합성검증 — 구현 전 차단
- 실제 1~1230회 Walk-forward
- 실제 미래 번호 공개
- 모바일 UI 개발
- Supabase 연결

## 9. 다음 사용자 결정

다음 세 가지를 한 번에 승인해야 Gate 2-3P-2 구현을 시작할 수 있다.

1. M4 물리·운영 증거모형 추가
2. M3를 단일 maxT omnibus로 변경
3. 모델 버전 `3.0.0-research`

## 10. 링크

- Issue #10: `https://github.com/dpes31/predictive-algorithm/issues/10`
- Branch: `feature/gate2-physical-evidence-spec`
- 이전 Gate 2-3R Draft PR: `https://github.com/dpes31/predictive-algorithm/pull/9`
