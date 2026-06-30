# Gate 2-3P-3 Full Synthetic Validation

- Decision: **NOT PASSED**
- Model: `3.0.0-research`
- Report hash: `b59cc753eda4058f0b55a685a136da01a327dd6b6b7fc33b10fd4758dfc36948`
- Research only: `true`
- Public release allowed: `false`
- Workflow run: `28451343507`
- Summary artifact: `7983755657`
- Artifact digest: `sha256:58526bd3b6f9a178575092f0affdb29d115139bd9dd1210dac04ef768dbe7ca7`

## Experiment size

- maxT calibration: 10,000
- model null calibration: 4,000
- independent null validation: 5,000
- positive controls: 12,000
- robustness: 6,000
- total synthetic series: 37,000

## Independent null validation

- Proxy false activation: 5/5,000 = **0.100000%**
- Proxy one-sided 95% upper: **0.205288%**
- M3 false activation: 8/5,000 = **0.160000%**
- M3 one-sided 95% upper: **0.283731%**

Frozen criteria:

- observed proxy rate <= 0.1%: PASS at the boundary
- proxy one-sided 95% upper <= 0.2%: FAIL
- M3 false activation <= 0.1%: FAIL

## Null scenario detail

| Scenario | Trials | Proxy false activation | M3 false activation | Mean M4 Δ Log Loss | Mean M4 strength |
|---|---:|---:|---:|---:|---:|
| n0_uniform | 835 | 0.000000% | 0.239521% | 0.000000 | 0.000000 |
| n1_irrelevant_metadata | 833 | 0.120048% | 0.120048% | -0.009065 | 0.257413 |
| n2_missing_dependency | 833 | 0.240096% | 0.360144% | -0.002868 | 0.087953 |
| n3_measurement_noise | 833 | 0.120048% | 0.000000% | -0.007788 | 0.240512 |
| n4_wrong_ids | 833 | 0.000000% | 0.240096% | -0.008992 | 0.257277 |
| n5_regime_only | 833 | 0.120048% | 0.000000% | -0.008881 | 0.257194 |

Irrelevant metadata produced a non-zero M4 distribution and exceeded the scenario-level 0.1% activation criterion. Mean predictive performance remained worse than M0.

## Positive controls at lift 1.25

| Scenario | Strict detection | Mean Δ Log Loss | Mean Δ Brier | Direction | M3 activation |
|---|---:|---:|---:|---:|---:|
| p1_ball_set | 0.8% | -0.005348 | -0.00002796 | 79.5% | 0.0% |
| p2_machine | 24.2% | 0.000921 | 0.00000528 | 98.8% | 0.0% |
| p3_machine_ball_interaction | 0.8% | -0.006698 | -0.00003508 | 75.5% | 0.0% |
| p4_regime_reversal | 0.0% | 0.000507 | 0.00000322 | 89.5% | 0.2% |
| p5_temporary_environment | 0.0% | -0.008517 | -0.00004475 | 56.1% | 0.0% |
| p6_pretest_shared | 0.4% | -0.004959 | -0.00002601 | 79.1% | 0.0% |

Frozen lift-1.25 strict-detection target was 80%. No positive scenario met it. The machine scenario was strongest but reached only 24.2%.

## Robustness findings

- Missingness did not increase model strength: PASS.
- Missingness sharply reduced direction accuracy and detection power.
- Independent pretest metadata did not activate the model: PASS.
- Post-draw-error scenario proxy activation was 2.6%: FAIL.
- Direction reversal adaptation within 208 draws was 100%, mean delay 48 draws: PASS.
- Temporary/signal-decay return within 208 draws was below the required 80%: FAIL.
- M3 regime-reversal activation at lift 1.25 was only 0.2%: FAIL.

## Preregistered checks

### Passed

- `null_proxy_rate_le_0_001`
- `missingness_does_not_increase_confidence`
- `independent_pretest_not_activated`
- `direction_reversal_adapts_within_208`
- `p2_machine_lift_1_25_log_loss_positive`
- `p2_machine_lift_1_25_brier_nonnegative`
- `p2_machine_lift_1_25_direction_ge_0_80`
- `p4_regime_reversal_lift_1_25_log_loss_positive`
- `p4_regime_reversal_lift_1_25_brier_nonnegative`
- `p4_regime_reversal_lift_1_25_direction_ge_0_80`

### Failed

- `null_proxy_upper_le_0_002`
- `null_m3_rate_le_0_001`
- `irrelevant_metadata_not_activated`
- `post_draw_error_not_activated`
- `temporary_signal_returns_within_208`
- all six lift-1.25 strict-detection >=80% checks
- ball-set Log Loss, Brier, and direction checks
- machine strict-detection check
- machine-ball interaction Log Loss, Brier, and direction checks
- regime-reversal strict-detection and M3 activation checks
- temporary-environment Log Loss, Brier, and direction checks
- pretest-shared Log Loss, Brier, and direction checks

## Decision

`Gate 2-3P-3 = NOT PASSED`

This is a statistical validation failure, not a workflow or code-execution failure. All 20 shards and the aggregate job completed successfully. The model remains in `RESEARCH`, the final deployable distribution remains `M0 only`, and the following remain blocked:

- real metadata collection as a production predictor
- historical real-data walk-forward
- public future-number candidates
- mobile prediction-product activation
- M4 deployment weight above zero

The result does not prove that all future algorithm development is impossible. It proves that the frozen `3.0.0-research` architecture does not satisfy its preregistered false-activation and detection-power requirements.
