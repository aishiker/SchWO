# T4 Current Handoff

Last updated: 2026-07-17
Thread: T4ab, further-local radial/Q018 gate.

## Exact decision

```text
GREEN / FURTHER LOCAL RADIAL GATE READY
```

## Frozen evidence

- Exact 24-frequency radial-only contract, both sectors, eight Table-I points,
  `M=1`, `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`.
- Classification: 81,792 records; 3,218 literal sector-aware transitions;
  78,574 default-covered; 3,178 structured uncovered; 40 structured
  solver-failed; zero default-other.
- Direct oracle: 3,218/3,218 validated; max effective residual
  `7.116571212464012e-16`; max relative sensitivity
  `1.7593903638313873e-07`.
- All 24 checkpoints are `complete=true`, `decision=PASS`.
- Adapter preflight: 3,218/3,218 passed, zero failures; solver
  `q018_tablei_further_local_transition_oracle`; warning
  `q018_tablei_further_local_transition_oracle_used`.

## Provenance and verification

- Exact five-path implementation commit: `c3a6479`.
- Classification/oracle/preflight SHA-256: `3bfe7d84a463e332d77724f58189fe3f565d9a385a4431f5a92ea58f15d11696`,
  `82ebed2447f7566a391ea1915c88ee3bf55f0c86b8c0207e2bd1eb2ca075d0c0`,
  `8fdabdbd1bc4765d1ee5155824df1ba88b154c58e14058d68129d58ec36a1021`.
- Classification snapshot: `52889944b58ec8aae442afb7c743679fcbbd9d3dd21819cc61cf1364b683eb43`;
  final-adapter snapshot is separately hash-linked in the preflight artifact.
- Fresh audit: `PASS records=81792 transitions=3218 checkpoints=24`.
- Focused pytest: 352 passed; Ruff: passed; full pytest: 643 passed, 117
  skipped, 1 xfailed.

## Scope and next handoff

No lmax extension, recursive midpoint, uniform/full grid, T8aq, observable,
plot, fixture, Kirchhoff, paper, or GitHub action occurred.  The existing T7
task may now receive only the frozen T7ca independent review; T8aq remains
forbidden pending T7ca and T0.
