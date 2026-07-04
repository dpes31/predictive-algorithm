# Gate 2-3P-R3M-3-2 Result Record

## Contract

The approved predictable-group contract `1.0.0` was implemented unchanged.

- outer window 520
- half-life 104
- prior strength 52
- internal validation 260 + five 52-draw folds
- group sizes 6, 10, 15
- 52-draw freeze
- DEV-PG and DEV-PG-CI only
- threshold 1000
- active life 208

## Decision

```text
status = PREDICTABLE_GROUP_FAIL
```

Positive:

- availability `0.3366` — FAIL
- activation `0.0135` — FAIL
- median delay `421` — PASS
- direction accuracy `0.7868389780154486` — FAIL
- direction trials `6732` — FAIL
- mean delta Log Loss `-0.0029845604295056435` — FAIL
- lower delta Log Loss `-0.003194311935549518` — FAIL
- mean delta Brier `-1.6941950397462026e-05` — FAIL
- lower delta Brier `-1.8087599218264927e-05` — FAIL

Null:

- activations `1 / 10000`
- rate `0.0001` — PASS
- one-sided 95% upper `0.00047429765916447847` — PASS

## Lock

- implementation `156f286db9242f0e8f45c0bda9246e57d22d57da`
- workflow `28499321746`
- tests `105 PASS`
- artifact `8002526507`
- artifact digest `sha256:8ba3958b1dcd45dac6ee436b9911f39281138287cd212fc1591283f985d1c6b1`
- seed hash `5fa4ab0038468a38f7a06a41928752c1a444ba9a17eef64e10a2d3d64cc69038`
- report hash `9c604e27684737017120a95f11849c2648394c99525cf53ca262828fd514ec37`
- lock hash `e150983980c91ca1c29d7fa82523b0195e1502d02191bddea823f74bed611d04`

## Gate state

```text
Full M3 DEV = BLOCKED
Gate 2-3P-R4 = BLOCKED
Final distribution = M0 only
```

Null safety passed, but the past-only number learner failed availability, detection, direction, Log Loss, and Brier. No post-result tuning is authorized.

The next action must be specification-only: decide whether to stop the M3 past-number path or design a separate M4-first gate using genuinely pre-draw physical and operational variables.
