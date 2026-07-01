# Gate 2-3P-R3M-2 Result Record

## D-027 — Implementation approval applied

- model: `5.0.0-research`
- implementation scope: exact fixed-size evidence and Oracle DEV only
- detection horizon: `520`
- activation threshold: `1000`
- post-activation active life: `208`

## D-028 — Oracle DEV decision

```text
status = ORACLE_PASS
```

Positive result:

- series: `2000`
- activated: `1837`
- rate: `0.9185`
- target: `0.80`
- median delay: `241`

Null result:

- series: `10000`
- activations: `8`
- rate: `0.0008`
- target: `0.001`
- one-sided 95% upper: `0.001443000578280491`
- upper target: `0.002`

## D-029 — Execution lock

- implementation: `37fd815220ccd363f019f3798366a2060872e073`
- workflow: `28493929179`
- tests: `96 PASS`
- artifact: `8000257623`
- artifact digest: `sha256:6c52c97fbd167a2f2ae22e4d225510cc419985c19e08f283dcdfbd6eaec2dafe`
- report hash: `e347d352b9f80e683c1e86c746c69636d25e4e9e635eaf1f1909122f4a525abb`
- lock hash: `97713f07da87488ed63d22325e350c833d73e551c3669a217135fecee524d47d`

## D-030 — Remaining blocks

Oracle PASS does not authorize later stages.

- Gate 2-3P-R3M-3: approval required
- full M3 DEV: blocked
- Gate 2-3P-R4: blocked
- CAL: not executed
- SEALED: not executed
- real data: not executed
- mobile work: not executed
- main merge: not executed
- final distribution: `M0_ONLY`
