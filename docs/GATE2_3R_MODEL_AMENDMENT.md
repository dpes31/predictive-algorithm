# Gate 2-3R Model Amendment v1.0.0

Status: USER APPROVED
Approved model version: `2.1.0-research`

## 1. M1/M2 temperature grid

The following temperature coefficients are fixed before rerun:

```text
T = {0.05, 0.10, 0.20, 0.50, 1.00}
```

For every existing M1 or M2 feature score `z`, create one subexpert per temperature:

```text
M1 eta(feature,T) = +T * z(feature)
M2 eta(feature,T) = sign(feature) * T * z(feature)
```

No temperature is selected after viewing results. All temperature-feature combinations remain concurrent subexperts and receive the same bounded sequential loss update.

## 2. M3 raw diagnostics

Prediction features remain winsorized to `[-3,+3]`.

Gate-only diagnostics are calculated before winsorization:

- raw max absolute shift 52
- raw max absolute shift 104
- raw CUSUM aggregate
- entropy 52

The familywise null distribution over all forecast origins is recalibrated from these raw diagnostics. M3 prediction logits remain:

```text
eta_M3 = change_gate * winsorized_feature
```

## 3. Pair diagnostic

Pair interaction remains disabled in prediction.

Two diagnostics are reported separately:

- exploratory all-pair maximum over 990 pairs and all origins
- preregistered planted-pair statistic for positive-control power measurement

The planted-pair test is used only to quantify diagnostic sensitivity when the pair is known by construction. It does not authorize scanning historical data and selecting a favorable pair.

## 4. Strict positive-control success

A planted scenario is counted as correctly detected only when all relevant conditions hold:

1. expected model mean delta log loss is strictly positive
2. expected model is strictly greater than every competing non-uniform model
3. expected model Brier score is not worse than M0
4. at least two macro blocks have positive delta log loss for persistent scenarios
5. M3 scenarios additionally require at least one calibrated M3 gate activation
6. pair scenarios require preregistered-pair adjusted tail probability at or below alpha

Ties at zero are not wins.

## 5. Rerun contract

The failed Gate 2-3 scenarios and effect sizes are preserved:

- fixed lift 1.02 / 1.05 / 1.10
- persistence coefficient 0.20
- reversal coefficient 0.20
- regime shift lift 1.10 at draws 400 and 800
- temporary lift 1.10 for 52 draws
- pair factor 1.25 / 1.50 / 2.00 / 3.00

Full rerun:

- 1,000 null calibration series
- independent 1,000 null validation series
- 100 repetitions per positive-control scenario
- 1,230 draws per series
- alpha 0.001

## 6. Prohibited

- changing the temperature grid after results
- removing failed weak effects
- using historical real draws during Gate 2-3R
- activating pair interactions in prediction
- proceeding to Gate 2-4 unless Gate 2-3R passes
