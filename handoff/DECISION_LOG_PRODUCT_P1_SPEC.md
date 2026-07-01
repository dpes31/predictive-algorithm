# Product Gate P1 Specification Decision Record

## D-058 — Minimal product path approved

The user approved Product Gates P1 through P4 and requested P1 specification only.

## D-059 — P1 assembly boundary

P1 reuses existing assets:

- Gate 1 canonical draws 1..1230
- Gate 2-2 exact fixed-size distribution
- deterministic five-set candidate optimizer
- existing hashing and future-data cutoff logic

No new prediction algorithm is introduced.

## D-060 — M0 product lock

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

M1 through M4 are shadow-only and cannot affect product candidates or displayed advantage.

## D-061 — Product disclosure

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

## D-062 — Initial target contract

For the existing canonical dataset:

```text
target_draw_no = 1231
input_last_draw = 1230
```

All supplied records must be strictly before the target. The runner must not silently trim target or future records.

## D-063 — Hash contract

Required:

- data hash
- model hash
- config hash
- prediction hash

The seed is derived only from contract version, data hash, model version, config hash, and target draw. Runtime clock and host state are excluded.

## D-064 — Rollback and source integrity

Future implementation must create assembly and rollback manifests. Historical source branches, frozen reports, and main must not be modified.

## D-065 — Current scope

```text
P1 specification = COMPLETE / APPROVAL PENDING
Python assembly = NOT STARTED
P2 QA = BLOCKED
P3 HTML = BLOCKED
P4 release lock = BLOCKED
```

No Python implementation, data reconciliation, product QA, walk-forward, HTML change, CAL, SEALED, mobile work, or main merge was performed.
