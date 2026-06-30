# Gate 2-3R Work Log

- Date: 2026-06-30
- Branch: `feature/gate2-synthetic-validation-r1`
- Base: `feature/gate2-synthetic-validation`
- Model: `2.1.0-research`
- Draft PR: #9

## Implemented

- M1 and M2 temperature subexperts at 0.05, 0.10, 0.20, 0.50 and 1.00
- Raw M3 diagnostics separated from clipped prediction features
- Exploratory all-pair and preregistered target-pair diagnostics separated
- Strict positive-control success definition
- Failed Gate 2-3 scenarios preserved unchanged

## Full rerun

- Null calibration: 1,000 series
- Independent null validation: 1,000 series
- Positive controls: 100 repetitions per scenario
- Draws per series: 1,230
- Alpha: 0.001
- Historical real draws used: no
- Report hash: `ec57a01e7781d5679cc8fc1b1c146055b06b6836740924cfbb0f1bfd6bef15c6`

## Result

- Gate proxy false activation: 4/1,000 = 0.4%
- Persistence strict detection: 100%
- Reversal strict detection: 71%
- Fixed bias strict detection: 0% for all preregistered lifts
- M3 activation: 0%
- Pair factor 3 target-pair detection: 22%
- Gate 2-3R: NOT PASSED

## Structural finding

With 1,000 calibration series, plus-one empirical p-values and Holm adjustment over four M3 diagnostics, the smallest possible adjusted p-value is `4/1001 = 0.003996`, above alpha 0.001. M3 activation is mathematically impossible under the approved contract.

## Execution limitation

The repository implementation was committed, but the connected GitHub tool could not dispatch or add the required Actions workflow. The full numerical run was completed with a deterministic standalone mirror of the committed formulas. GitHub CI confirmation remains pending.

## Gate status

- State: RESEARCH
- Final distribution: M0 only
- Gate 2-4: blocked
- Actual candidate release: blocked
