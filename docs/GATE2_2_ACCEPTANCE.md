# Gate 2-2 Acceptance Checklist

## Scope

Gate 2-2 accepts the engine skeleton only. It does not claim predictive advantage.

## Required pass conditions

- [ ] Gate 1 canonical data validator passes
- [ ] All Python unit tests pass
- [ ] Small-state exact probability sum equals 1
- [ ] Number marginals sum to 6
- [ ] Future target and later records are rejected
- [ ] `auto_checked` data cannot be used for public prediction
- [ ] Gate RESEARCH final weights equal M0=1
- [ ] Candidate sets are exactly five and unique
- [ ] Same input produces identical smoke JSON bytes
- [ ] M3 remains inactive before Gate 2-3 null calibration
- [ ] Research output has `public_release_allowed: false`
- [ ] Handoff files are updated
- [ ] Draft PR remains unmerged until user review

## Not evaluated in Gate 2-2

- Historical 300~1230 Walk-forward advantage
- 99.9% candidate promotion threshold
- 95% uncertainty intervals
- Null false activation rate across 1,000 series
- Planted-signal detection power
- Pair interaction
- Actual future draw candidate publication
