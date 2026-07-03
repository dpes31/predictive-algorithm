# Algorithm Audit Handoff

Date: 2026-07-03

Branch: `docs/algorithm-audit`

Base: `feature/product-p1-release-candidate`

## State

```text
P1 = P1_ASSEMBLED
PR #45 = CLOSED / NOT MERGED
external access = PERMANENTLY RETIRED
algorithm audit = COMPLETE
next Gate = Algorithm Integration Gate A1 / APPROVAL PENDING
main merge = NOT PERFORMED
```

## Retired work

No external result-site access, retry workflow, institutional inquiry, B2-B5 contact loop, new source discovery or collection of unprovided physical variables is allowed.

Historical PR #45 runs, reports, hashes and locks remain preserved and are not part of the active development path.

## Audit result

The current product is M0-only. It produces deterministic diversified sets from a uniform distribution. Historical draws affect the data hash, cutoff and seed, but not non-uniform number scores.

Required next improvements are:

- connect approved past-only features to number logits;
- assemble research modules through one integration layer;
- define a registry for user-supplied values and hypotheses;
- add a physical-value adapter that never invents inputs;
- separate `CONTROL_M0` and `RESEARCH_ENSEMBLE`;
- record component contribution and ablation diagnostics.

The prior M4, correction-grid and predictable-group failures remain frozen.

## Next approval boundary

Only the specification for `Algorithm Integration Gate A1`, contract `research-ensemble-spec-1.0.0`, may proceed after user approval. Implementation, Walk-forward, HTML, CAL, SEALED, mobile work and `main` merge remain prohibited.
