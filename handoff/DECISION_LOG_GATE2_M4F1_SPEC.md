# Gate 2-3P-M4F-1 Decision Record

## D-042 — M3 past-number path frozen

The user approved the `PREDICTABLE_GROUP_FAIL` decision and lock. No post-result tuning is permitted.

## D-043 — M4 data-feasibility contract

Contract version: `m4-data-feasibility-1.0.0`

Required separation:

- observed_at
- recorded_at
- available_at
- source_published_at
- ingested_at
- prediction_lock_at
- draw_actual_at

Only A0 records available before prediction lock are deployable candidates. A1 is research-only. A2 and A3 are prohibited.

## D-044 — Minimum data

- ingestion-only shadow: 26 consecutive draws
- retrospective evidence pilot: 520 consecutive linked draws
- stable context support: 104 per level
- interaction support: 52 per cell
- transient support: 260 total and 52 per retained bin

## D-045 — Source hierarchy

- Grade A: signed operator/broadcaster logs, certified measurements, local sensors
- Grade B: official MBC, lottery operator, KMA and government public data
- Grade C: double-reviewed official-source transcription, diagnostic-only
- Grade D: rejected

Public official sources do not currently establish a structured 520-draw archive for machine, ball set, ball measurement, pre-draw operations, or indoor sensors. Without first-party record access, the primary M4 path is `NO_DATA_PATH`.

## D-046 — Pilot entry

All hard criteria must pass:

- lawful source access
- 520 linked draws
- core coverage and reliability
- context variation
- leakage controls
- mandatory synthetic null controls
- machine or ball-set lift 1.25 positive control

Decision states:

```text
REAL_METADATA_PILOT_ENTRY_PASS
REAL_METADATA_PILOT_ENTRY_FAIL
NO_DATA_PATH
```

Conditional PASS is prohibited.

## D-047 — Current scope lock

```text
Gate 2-3P-M4F-1 = SPEC COMPLETE / APPROVAL PENDING
Gate 2-3P-M4F-2 and later = BLOCKED
Full M3 DEV = BLOCKED
Gate 2-3P-R4 = BLOCKED
Final distribution = M0 only
```

No Python implementation, additional DEV, data collection, CAL, SEALED, actual-number walk-forward, mobile work, or main merge was performed.
