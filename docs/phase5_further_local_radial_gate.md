# T4ab Further-Local Radial/Q018 Gate

## Decision

```text
GREEN / FURTHER LOCAL RADIAL GATE READY
```

This is a radial-only gate for the 24 frozen further-local frequencies.  It
does not establish any amplification, observable, Kirchhoff, plotting, paper,
or production-grid result.

## Evidence

- Classification: 81,792 unique records at the exact frozen frequencies,
  sectors, eight Table-I radii, and boundary contract; 78,574 default-covered,
  3,178 structured uncovered, 40 structured solver-failed, and zero
  `default_error_other`.
- Literal sector-aware envelope: 3,218 transitions, all direct-oracle
  validated.  Max effective residual is `7.116571212464012e-16`; max relative
  sensitivity is `1.7593903638313873e-07`.
- All 24 atomic checkpoints are `complete=true` and `decision=PASS`.
- Integrated adapter `q018_tablei_further_local_transition`: 3,218/3,218
  preflight records passed with zero failures and exact saved-oracle values.

## Provenance

- Implementation commit: `c3a6479703f6c2d64aa2903edc7cf2db3d1ed112`.
- Classification artifact: `3bfe7d84a463e332d77724f58189fe3f565d9a385a4431f5a92ea58f15d11696`.
- Oracle-validation artifact: `82ebed2447f7566a391ea1915c88ee3bf55f0c86b8c0207e2bd1eb2ca075d0c0`.
- Resume-preflight artifact: `8fdabdbd1bc4765d1ee5155824df1ba88b154c58e14058d68129d58ec36a1021`.
- Classification snapshot: `52889944b58ec8aae442afb7c743679fcbbd9d3dd21819cc61cf1364b683eb43`.

The pre-adapter classification snapshot is separate from the final-adapter
snapshot and is hash-linked in `resume_preflight.json`.  Classification and
oracle records were not recomputed after adapter integration.

## Fresh verification

- Gate audit: `PASS records=81792 transitions=3218 checkpoints=24`.
- Focused pytest: `352 passed`.
- Ruff: passed on the five frozen paths.
- Full pytest: `643 passed, 117 skipped, 1 xfailed`.
- Scope: the implementation commit changes exactly the authorized five paths;
  the run directory has exactly 24 checkpoints plus classification, oracle,
  preflight, and manifest artifacts, with no temporary or quarantined output.
