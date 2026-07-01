# Product Gate P1 Result Decision Record

## D-066 — P1 assembly approved and executed

The approved contract `product-release-candidate-1.0.0` was implemented on `feature/product-p1-release-candidate`.

## D-067 — Existing assets only

Reused:

- Gate 1 canonical draws 1..1230
- Gate 2-2 exact fixed-size distribution
- elementary symmetric normalization
- deterministic five-set candidate optimizer
- canonical hashing and future-data cutoff

No new prediction model or tuning parameter was introduced.

## D-068 — Product distribution lock

```text
M0 = 1.0
M1 = 0.0
M2 = 0.0
M3 = 0.0
M4 = 0.0
```

Shadow diagnostics do not enter candidate generation, seed, prediction hash, or product weights.

## D-069 — P1 implementation lock

```text
spec commit = 84e051ecf81f93309d179a610b6ea543e28c8298
assembly commit = 365bd35bd31929c75ca6f65cf62d1b816ab2235b
rollback manifest commit = 396c4fa2a370083365750be5d563b7ffd8e7146e
implementation lock = 099d917abd1b635c830fee343a47d3bd23e0c052
```

## D-070 — CI history

Initial run `28525288118` failed and remains preserved.

The candidate number representation was normalized from tuple-like Python output to JSON arrays. The corrected implementation was locked at `099d917abd1b635c830fee343a47d3bd23e0c052`.

Final run:

```text
workflow = 28525611462
Python 3.11 = PASS
Python 3.12 = PASS
unit tests = 14 PASS
canonical output generation = PASS
```

## D-071 — Acceptance decision

All P1 criteria A1 through A13 passed.

Decision:

```text
P1_ASSEMBLED
```

This is an assembly and safety-contract result, not a finding of predictive advantage.

## D-072 — Disclosure lock

```text
research_only = true
public_release_allowed = false
statistical_edge = false
reason = no_validated_nonuniform_signal
advantage_status = 통계적 우위 없음
```

## D-073 — Data status

The assembled dataset remains:

```text
data_version = draws-2026.06.27-r1
range = 1..1230
records = 1230
SHA-256 = 57bb04ef188b5b06298b8a97fc73174d746de0568e33423f50029de31efa5cf1
verification = auto_checked
officially_locked = false
```

No official-result reconciliation was executed.

## D-074 — Out-of-scope checks

The Vercel status failed because of a build-rate limit. It is non-blocking for P1 because HTML and deployment validation were expressly excluded.

## D-075 — Next boundary

The next allowed step is specification-only work for Product Gate P2.

Blocked until separate approval:

- official-result reconciliation
- P2 QA execution
- actual Walk-forward
- HTML work
- CAL or SEALED
- mobile work
- main merge
