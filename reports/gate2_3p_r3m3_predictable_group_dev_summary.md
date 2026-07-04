# Gate 2-3P-R3M-3-2 DEV-PG Summary

Status: `PREDICTABLE_GROUP_FAIL`

## Positive

- series: 2,000
- availability: 33.66% / required 80% — FAIL
- activation: 1.35% / required 80% — FAIL
- median delay: 421 / maximum 520 — PASS
- direction: 78.6839% / required 80% — FAIL
- direction trials: 6,732 / required 16,000 — FAIL
- mean delta Log Loss: -0.00298456 — FAIL
- lower delta Log Loss: -0.00319431 — FAIL
- mean delta Brier: -0.00001694195 — FAIL
- lower delta Brier: -0.00001808760 — FAIL

Selected blocks:

- size 6: 3,304
- size 10: 1,969
- size 15: 1,459
- abstain: 13,268

## Null

- series: 10,000
- false activation: 1
- rate: 0.01% / maximum 0.10% — PASS
- one-sided 95% upper: 0.04743% / maximum 0.20% — PASS

## Lock

- implementation: `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow: `28499321746`
- tests: `105 PASS`
- artifact: `8002526507`
- artifact digest: `sha256:8ba3958b1dcd45dac6ee436b9911f39281138287cd212fc1591283f985d1c6b1`
- seed hash: `5fa4ab0038468a38f7a06a41928752c1a444ba9a17eef64e10a2d3d64cc69038`
- report hash: `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash: `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

Null safety passed, but the past-only learner failed availability, activation, direction, Log Loss, and Brier requirements. Full M3 and R4 remain blocked. No criterion or hyperparameter was changed after observing the result.
