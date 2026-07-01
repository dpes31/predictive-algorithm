# Project Handoff

최종 갱신일: 2026-07-01  
현재 Gate: **Gate 2-3P-M4F-2 source-access specification 완료·승인 대기**  
현재 브랜치: `feature/gate2p-m4f2-source-access-spec`  
기준 브랜치: `feature/gate2p-m4f1-data-feasibility-spec`  
관련 Issue: #34  
현재 Draft PR: #35

## 프로젝트 상태

- Gate 2-3P-R3M-3-2: `PREDICTABLE_GROUP_FAIL`
- M3 past-number path: `FROZEN`
- Gate 2-3P-M4F-1: 승인 완료
- Gate 2-3P-M4F-2: **명세 완료·승인 대기**
- 실제 source audit: `NOT_EVALUATED`
- 외부기관 자료 접근: 미실행
- 데이터 수집·Python·DEV: 미실행
- Gate 2-3P-M4F-3 이후: `BLOCKED`
- CAL·SEALED·실제 번호·모바일: `BLOCKED`
- 최종 적용분포: `M0 only`

현재 모델은 `5.0.0-research`, M4 data feasibility contract는 `1.0.0`, source-access audit contract는 `1.0.0`이다.

## 이전 실패 잠금

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

M3 past-number learner는 추가 튜닝하지 않는다.

## M4F-2 산출물

- `docs/GATE2_M4_SOURCE_ACCESS_AUDIT_SPEC.md`
- `docs/GATE2_M4_SOURCE_ACCESS_DECISION_RULES.md`
- `docs/GATE2_M4_AUTHORITY_SECURITY_TIMESTAMP_CHECKLIST.md`
- `docs/templates/M4_FIELD_LEVEL_DATA_DICTIONARY_TEMPLATE.md`
- `schemas/m4_metadata_sample.schema.json`
- `schemas/examples/m4_metadata_dummy_record.json`
- `docs/templates/M4_DATA_REQUEST_DONGHAENG_DRAFT.md`
- `docs/templates/M4_DATA_REQUEST_MBC_DRAFT.md`

두 기관 문서는 모두 미발송 초안이며 실제 외부행위가 아니다.

## Source-access hard criteria

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

최종 PASS에는 H1~H8 모두 PASS가 필요하다.

Evidence level:

```text
E0_UNVERIFIED
E1_DOCUMENTED
E2_SAMPLED
E3_SYSTEM_VERIFIED
```

PASS에는 각 hard criterion 최소 E2, 핵심 timestamp·audit trail에는 E3 또는 이에 준하는 공식 증빙이 필요하다.

## Deterministic decision rules

판정 우선순위:

```text
1. path-ending evidence confirmed -> NO_DATA_PATH
2. H1~H8 all PASS             -> SOURCE_ACCESS_PASS
3. all H known and any FAIL   -> SOURCE_ACCESS_FAIL
4. otherwise                  -> AUDIT_INCOMPLETE
```

### SOURCE_ACCESS_PASS

- machine 또는 ball-set stable primary source 존재
- 최소 520회 연결 가능
- timestamp 의미·수정이력·outcome 분리 확인
- 연구권한·보안·field traceability 충족

PASS는 데이터 확보나 예측력 승인이 아니라 M4F-3 ingestion-only shadow 설계 진입자격만 뜻한다.

### SOURCE_ACCESS_FAIL

원천 또는 접근경로는 존재하지만 hard criterion 하나 이상이 미달한 상태다. 기준완화 없이 remediation 가능성만 기록한다.

### NO_DATA_PATH

다음 중 하나가 공식 확인된 상태다.

- primary 원기록 부재
- 520회 역사범위 복구 불가
- timestamp·draw linkage 재구성 불가
- outcome 분리 불가
- 최종적 연구제공 불가
- 책임기관 식별 불가
- 공개 proxy만 존재

무응답만으로 NO_DATA_PATH를 판정하지 않는다.

### AUDIT_INCOMPLETE

회신·증빙·sample·timestamp 정의가 부족한 중간상태다. PASS로 보지 않는다.

## Field dictionary and schema

Field dictionary는 다음을 필수 기록한다.

- 원 field와 canonical field
- business definition과 causal rationale
- source system·record ID
- data type·unit·null meaning
- observed/recorded/available timestamp 의미
- correction·retention 규칙
- 역사적 coverage
- outcome·personal information 여부
- evidence level·reliability score·field status

JSON Schema는 outcome field를 포함하지 않으며 `additionalProperties=false`, provenance, availability class, quality status를 필수화한다. Dummy record는 합성 예시다.

## Authority·security·timestamp checklist

- data owner·승인권한·연구사용
- 520회 원천·ID·coverage
- outcome 분리
- observed/recorded/available 시각 의미
- timezone·clock source·수정 전 timestamp 보존
- 암호화·최소권한·접근로그·파기
- immutable ID·version history·checksum

`UNKNOWN`은 PASS가 아니다.

## 현재 금지

- 외부기관 접촉 또는 문서 전달
- 데이터 수신·열람·다운로드
- scraping·OCR·영상추출
- Python 구현·schema 실행
- ingestion shadow
- synthetic·실제 metadata 검증
- 추가 DEV
- CAL·SEALED
- 실제 번호 Walk-forward
- 사용자용 번호 생성
- 모바일 UI
- main 병합

## 다음 단계

다음 단계는 `Gate 2-3P-M4F-2A request package finalization`이다. 발신주체·연구주체·보존기간·수신부서·권한조건을 확정하고 최종 문안만 잠근다. 외부 전달은 다시 별도 승인한다.
