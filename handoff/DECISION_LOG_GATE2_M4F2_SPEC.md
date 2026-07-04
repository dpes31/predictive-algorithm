# Gate 2-3P-M4F-2 Decision Record

## D-048 — M4F-1 approval applied

The user approved the physical and operational data-feasibility specification and contract version `1.0.0`.

## D-049 — Source-access audit contract

Contract version: `m4-source-access-1.0.0`

Hard criteria:

- H1 primary source existence
- H2 historical coverage
- H3 timestamp integrity
- H4 immutable identity and correction history
- H5 outcome separation
- H6 research authorization
- H7 security feasibility
- H8 field-level traceability

## D-050 — Evidence levels

```text
E0_UNVERIFIED
E1_DOCUMENTED
E2_SAMPLED
E3_SYSTEM_VERIFIED
```

Final PASS requires at least E2 for all hard criteria. Critical timestamp and audit-trail evidence requires E3 or equivalent official proof.

## D-051 — Deterministic decision precedence

```text
1. path-ending evidence confirmed -> NO_DATA_PATH
2. H1~H8 all PASS             -> SOURCE_ACCESS_PASS
3. all H known and any FAIL   -> SOURCE_ACCESS_FAIL
4. otherwise                  -> AUDIT_INCOMPLETE
```

No-response alone is not `NO_DATA_PATH`.

## D-052 — PASS meaning

`SOURCE_ACCESS_PASS` authorizes only consideration of a future ingestion-only shadow design. It does not authorize:

- data transfer
- prediction evaluation
- Python implementation
- DEV, CAL, or SEALED
- actual-number walk-forward

## D-053 — Path-ending evidence

`NO_DATA_PATH` requires official evidence of at least one of the following:

- primary records do not exist
- 520-draw historical range is irrecoverable
- timestamp or draw linkage cannot be reconstructed
- outcome and metadata cannot be separated
- lawful research access is finally unavailable
- responsible source institution cannot be identified
- only diagnostic public proxies exist

## D-054 — Request drafts

Two request documents were created as unsent drafts:

- `docs/templates/M4_DATA_REQUEST_DONGHAENG_DRAFT.md`
- `docs/templates/M4_DATA_REQUEST_MBC_DRAFT.md`

They request data-existence, structure, timestamp, coverage, permission, and security information only. They exclude personal data, test number sequences, security-sensitive detail, and outcome fields.

No request was sent.

## D-055 — Data dictionary and sample schema

Created:

- field-level dictionary template
- outcome-free JSON Schema
- synthetic dummy record
- authority/security/timestamp checklist

The sample schema rejects unspecified outcome fields and requires provenance, availability classification, correction status, record hash, and quality information.

## D-056 — Current state

```text
Gate 2-3P-M4F-2 = SPEC COMPLETE / APPROVAL PENDING
Actual source audit = NOT_EVALUATED
External contact = NOT_PERFORMED
Data received = false
Python implementation = false
M4F-3 and later = BLOCKED
Final distribution = M0 only
```

## D-057 — Next decision

The next allowed specification step is `Gate 2-3P-M4F-2A request package finalization`.

It must determine:

- sender identity and authority
- research entity and purpose statement
- requested retention period
- receiving departments
- lawful-use and security terms
- final text lock

External delivery remains separately gated.
