# Algorithm Integration Gate A4 Status

- Contract: `research-ensemble-evaluation-implementation-1.0.0`
- Spec contract: `research-ensemble-evaluation-spec-1.0.0`
- Evaluated commit: `ee10a16b8c6259948bc8b2ed77d555452b9ff3a9`
- Workflow run: `28653030201` (#37)
- Python 3.11, two repeats: PASS
- Python 3.12, two repeats: PASS
- Cross-runtime reproducibility: PASS
- CONTROL_M0 regression: PASS
- Future-data cutoff: PASS
- Ten lanes and equivalence: PASS
- E1~E16 integrity: PASS
- Primary joint log-score criterion: FAIL
- Marginal Brier guardrail: FAIL
- Temporal stability guardrail: FAIL
- Result: `A4_EVALUATION_FAIL`

Primary result:

```text
mean joint log-score delta = -0.0541462386
one-sided 95% lower bound = -0.0739087181
one-sided p-value = 1.0
cumulative joint log-score delta = -47.5945437
mean marginal Brier gain = -0.000294872446
positive chronological quarters = 0 / 4
```

Canonical result hash:

```text
c886f07c2fa7fd01cfa49d2d0e4174d6c9802ac0856aff2fd13d54da44fde3b7
```

The implementation is structurally valid and reproducible, but the fixed research ensemble underperformed CONTROL_M0 on all mandatory performance guardrails. No parameter was changed after observing the result. `CONTROL_M0` remains the rollback mode.

Actual user hypothesis and physical entries remain zero. No external access, HTML, CAL, SEALED, mobile work, or main merge was performed. No next Gate is authorized.
