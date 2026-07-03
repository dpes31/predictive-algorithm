# Algorithm Improvement Audit

Status: `AUDIT COMPLETE / IMPLEMENTATION NOT AUTHORIZED`

Date: 2026-07-03

Branch: `docs/algorithm-audit`

## 1. Core finding

The current product is a deterministic five-set generator, not the intended integrated research algorithm.

`product/run_prediction.py` creates a fixed-size distribution with all 45 logits equal to zero. Historical draws are used for the data hash, cutoff and deterministic seed, but not for non-uniform number scoring. Product weights remain `M0=1` and `M1=M2=M3=M4=0`.

The next development problem is therefore algorithm integration, not external source access.

## 2. Gaps requiring improvement

1. **Historical features are disconnected.** Persistence, reversal, gap and regime research code exists in repository history but is not used by the active product runner.
2. **Research modules are not assembled.** The Product P1 model hash and config cover the reduced M0 path, not the full M1 through M4 research stack.
3. **Physical integration is incomplete.** The restored M4 engine expects physical and correction fields that are absent from the current Product P1 `engine/config.py`.
4. **Ball weight is not an active number signal.** Repository history classifies nominal ball weight and tolerance as schema-only. A common nominal weight cannot rank numbers unless the user supplied a per-number or otherwise discriminative difference.
5. **The user's hypotheses are not executable.** There is no versioned registry defining each hypothesis, formula, direction, required input, missing-input behavior, contribution cap and rollback rule.
6. **The failed predictable-group model remains frozen.** Its prior failure must not be erased through post-hoc threshold, window, half-life, prior, fold or group-size changes.

## 3. Required improvements

### A. Integrated number-score contract

Create one versioned interface that returns 45 number logits and diagnostics from:

```text
historical structure
+ approved user hypotheses
+ user-supplied physical values
+ approved interactions
- uncertainty penalty
```

The existing exact 6-of-45 distribution and five-set optimizer should consume these logits.

### B. User-input and hypothesis registry

Only values explicitly supplied or approved by the user may enter the registry. Each value must be classified as:

```text
NUMBER_LEVEL
BALL_SET_LEVEL
DRAW_LEVEL
STATIC_ASSUMPTION
NON_DISCRIMINATIVE_REFERENCE
```

A non-discriminative reference may support assumptions or simulations but must not rank numbers directly.

### C. Historical feature layer

Reconnect a small interpretable set of past-only features:

- short and long occurrence deviation;
- inter-arrival gap and gap change;
- persistence and reversal agreement;
- regime-change probability or abstention;
- supported pair or group interactions.

Every feature must end at `target_draw_no - 1`.

### D. Physical-variable adapter

Do not directly connect the old M4 engine to Product P1. Add a versioned adapter that accepts only user-supplied fields, rejects unknown fields, returns zero for non-discriminative inputs, caps physical contribution and remains operable when inputs are missing.

### E. Dual output mode

Keep exact M0 as the control and rollback path. Add a separate research mode:

```text
CONTROL_M0
RESEARCH_ENSEMBLE
```

The research mode may rank five sets but must remain research-only and must not claim proven improvement in winning odds.

### F. Contribution and ablation diagnostics

Record historical, hypothesis, physical, interaction, uncertainty and diversification contributions. The system must support removing each component to test whether it adds information.

## 4. Permanent exclusions

- external lottery-site access or retries;
- external institutional inquiries;
- B2 through B5 as an algorithm-development blocker;
- new official or unofficial source discovery;
- acquisition of physical variables not supplied by the user;
- rewriting prior failure reports, hashes or locks.

## 5. Recommended next Gate

```text
Algorithm Integration Gate A1
contract = research-ensemble-spec-1.0.0
```

A1 is specification-only. It must define the 45-number score interface, user-input registry, historical features, physical adapter, contribution caps, uncertainty handling, dual output modes, diagnostics, ablation, versioning, rollback and implementation acceptance criteria.

A1 must not implement code, run Walk-forward evaluation, modify HTML, run CAL or SEALED, build mobile UI or merge to `main`.
