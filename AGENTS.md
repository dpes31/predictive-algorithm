# AGENTS.md

모든 개발 에이전트는 작업 전에 이 문서를 읽는다.

## 프로젝트 목적

로또 6/45의 6개 번호 조합 5세트를 출력하는 연구형 예측기를 개발한다. 현재 검증대상은 로또 예측기이며, 근거 부족 시 exact M0을 유지한다.

핵심 원칙:

- 미래 데이터 누출 금지
- 동일 입력·버전·seed 재현
- 실패 결과와 불확실성 보존
- 제품 출력은 6개 번호 × 5세트
- 사용자 승인 전 다음 Gate 진행 금지

## 필수 읽기

1. `docs/GATE2_M4_DATA_FEASIBILITY_SPEC.md`
2. `docs/GATE2_M4_SOURCE_ACCESS_AUDIT_SPEC.md`
3. `docs/GATE2_M4_SOURCE_ACCESS_DECISION_RULES.md`
4. `docs/GATE2_M4_AUTHORITY_SECURITY_TIMESTAMP_CHECKLIST.md`
5. `docs/templates/M4_FIELD_LEVEL_DATA_DICTIONARY_TEMPLATE.md`
6. `schemas/m4_metadata_sample.schema.json`
7. `schemas/examples/m4_metadata_dummy_record.json`
8. `docs/templates/M4_DATA_REQUEST_DONGHAENG_DRAFT.md`
9. `docs/templates/M4_DATA_REQUEST_MBC_DRAFT.md`
10. `handoff/PROJECT_HANDOFF.md`
11. `handoff/GATE2_PHYSICAL_PROGRESS.md`
12. `handoff/DECISION_LOG_GATE2_M4F2_SPEC.md`

## 현재 상태

- Gate 2-3P-R3M-3-2: `PREDICTABLE_GROUP_FAIL`
- M3 past-number path: `FROZEN`
- Gate 2-3P-M4F-1: 승인 완료
- Gate 2-3P-M4F-2: **명세 완료·승인 대기**
- 실제 source audit: `NOT_EVALUATED`
- 외부기관 자료 접근: 미실행
- 데이터 수집·코드 구현·DEV: 미실행
- Gate 2-3P-M4F-3 이후: `BLOCKED`
- CAL·SEALED·실제 번호 검증·모바일: `BLOCKED`
- 최종 적용분포: `M0 only`

현재 브랜치: `feature/gate2p-m4f2-source-access-spec`  
기준 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`  
관련 Issue: `#34`  
현재 Draft PR: `#35`  
현재 모델: `5.0.0-research`  
M4 data feasibility contract: `1.0.0`  
Source-access audit contract: `1.0.0`

## 이전 결과 잠금

- predictable-group implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

이 결과를 변경하거나 M3 learner를 추가 튜닝하지 않는다.

## M4F-2 hard criteria

```text
H1 primary source existence
H2 historical coverage
H3 timestamp integrity
H4 immutable identity and correction history
H5 outcome separation
H6 research authorization
H7 security feasibility
H8 field-level traceability
```

Evidence level:

```text
E0_UNVERIFIED
E1_DOCUMENTED
E2_SAMPLED
E3_SYSTEM_VERIFIED
```

최종 PASS에는 H1~H8 모두 PASS가 필요하다. 핵심 timestamp와 audit trail은 E3 또는 이에 준하는 공식 증빙을 요구한다.

## 판정 우선순위

```text
1. path-ending evidence confirmed -> NO_DATA_PATH
2. H1~H8 all PASS             -> SOURCE_ACCESS_PASS
3. all H known and any FAIL   -> SOURCE_ACCESS_FAIL
4. otherwise                  -> AUDIT_INCOMPLETE
```

`SOURCE_ACCESS_PASS`는 데이터 확보나 예측력 통과가 아니라, 다음 ingestion-only 설계의 진입 자격만 의미한다.

## M4F-2 산출물

- source-access audit specification
- deterministic decision rules
- authority·security·timestamp checklist
- field-level dictionary template
- outcome-free JSON Schema
- synthetic dummy record
- 기관별 미발송 자료구조 문의서 초안 2종

초안에는 개인정보, 테스트 번호열, 보안상세, outcome field를 포함하지 않는다.

## 금지사항

별도 승인 전 다음을 수행하지 않는다.

- 외부기관 접촉 또는 문서 전달
- 데이터 수신·열람·다운로드
- scraping·OCR·영상추출
- Python 구현·schema 실행
- ingestion shadow
- synthetic 또는 실제 metadata 검증
- 추가 DEV
- CAL·SEALED
- 실제 번호 Walk-forward
- 사용자용 번호 생성
- 모바일 UI·Supabase 개발
- main 병합

## 다음 Gate

다음 단계는 `Gate 2-3P-M4F-2A request package finalization`이다. 발신주체, 연구주체, 보존기간, 수신부서, 권한조건을 확정하고 최종 문안만 잠근다. 외부 전달은 다시 별도 승인한다.
