# T8 Current Handoff

Last updated: 2026-07-14

## Thread Role And Current Status

T8al completed the bounded units/dtype metadata-contract hardening for the
accepted 18×8 Kirchhoff Eq. (47) scalar comparison baseline.

Decision:

```text
GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT HARDENED
```

The correction is metadata-only. Every non-metadata array is byte-identical
to T8ak and retains its frozen NumPy-array SHA256 fingerprint. The formula,
branches, backend, dps, grid, numerical values, masks, phases, and non-claims
are unchanged. T7bt was dispatched successfully to existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `gpt-5.6-sol`, thinking `high`;
T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636` was notified.

## Completed Work

- Executed `docs/superpowers/plans/2026-07-14-t8al-kirchhoff-metadata-contract.md`
  using `executing-plans`, TDD, and fresh completion verification.
- Added exact `units` and `dtype` mappings for all 16 non-metadata arrays to
  embedded NPZ metadata, JSON sidecar, and manifest.
- Bumped schema to
  `phase5_t8al_kirchhoff_review_grid_v2_units_dtype`.
- Added fail-closed runtime validation that actual array dtypes exactly match
  the frozen mapping.
- Preserved the T8ak artifacts under
  `/tmp/schwo_t8al_pre_metadata_contract/` and regenerated only the same three
  project artifact paths.
- Commit `7966be1 fix: record Kirchhoff units and dtypes` contains exactly
  `src/schwgw/io/kirchhoff.py` and
  `tests/unit/test_kirchhoff_artifact.py`.

## Artifacts And Hashes

Accepted T8aj source hashes remain unchanged:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

T8al output hashes:

```text
66c59851e6eaf6bf5691c8026e0d528edbf304ae4bbcfc47a0290c14f87fdb55  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz
0b20d62be1fe39b48ce90ca2a8d0f7798fff489a777f18b2bf2d7c268376fdf3  runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json
fb138038b783d2a511df94f6552a5d77a06ae7f1a32dc4c80ea54ee7f3c5e632  runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md
```

## Tests And Verification

- Required TDD RED: old schema assertion failed; implementation then passed.
- Focused pytest: `9 passed in 0.36s`.
- Ruff: `All checks passed!`.
- Numerical identity: `T8AL_NUMERICAL_ARRAY_IDENTITY=PASS` for all 16
  non-metadata arrays, including exact equality and frozen `.npy` SHA256.
- Metadata surfaces: `T8AL_METADATA_SURFACES=PASS`.
- Full pytest: `558 passed, 117 skipped, 1 xfailed, 85 warnings, 79 subtests
  passed in 311.85s`.
- Forbidden production-source diff and forbidden downstream-output searches
  were empty; baseline directory contains exactly three files.
- Existing warnings are the prior Weyl/Wigner/radial numerical warnings; no
  Kirchhoff warning or non-finite value was introduced.

## Incomplete Work

- T7bt must independently review this metadata-only correction.
- T0 must close the gate after T7bt reports its exact decision.
- No plotting, dense production, fixture, or paper-style stage is authorized.

## Blocking Issues And Non-Blocking Warnings

- No T8al blocker remains.
- The shared working tree contains accumulated coordination-document changes;
  they were preserved and excluded from the scoped code commit.
- T7bt independent acceptance is still required before T0 milestone handling.

## Files The Next Thread Must Read

1. `status.md`
2. `docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md`
3. `docs/superpowers/plans/2026-07-14-t8al-kirchhoff-metadata-contract.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `src/schwgw/io/kirchhoff.py`
7. `tests/unit/test_kirchhoff_artifact.py`
8. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz`
9. `runs/phase5/fig5_fig6_kirchhoff_baseline/tablei_kirchhoff_baseline_values.npz.json`
10. `runs/phase5/fig5_fig6_kirchhoff_baseline/manifest.md`
11. `/tmp/schwo_t8al_pre_metadata_contract/`

## Frozen Decisions

- Eq. (47), its branches, positive-frequency no-conjugation policy,
  coordinate-derived eta, backend `mpmath 1.4.1`, and `dps=60` are unchanged.
- All non-metadata arrays and their frozen fingerprints are immutable.
- Kirchhoff remains scalar, polarization-independent, and comparison-only.
- It must not enter solver, denominator, masks, normalization, calibration,
  Q018, boundary policy, or polarization channels.

## Forbidden Actions

- Do not modify or regenerate T8al implementation/artifacts during T7bt.
- Do not create plots, 40-frequency/dense production, fixtures, interpolation,
  smoothing, Appendix D/E, or paper-style candidates.
- Do not modify formula, precision, source grid, solver, configs, or regression
  fixtures, and do not push GitHub from T7/T8.
- Scientific/test failures must not be bypassed by changing model.

## Superseded Prompts

- T8ak and T8al implementation prompts are complete and must not be reused by
  T7bt to repair source or artifacts.
- T12/T12b and all later-stage plotting/production prompts remain superseded.

## Exact Next Task

T7bt is now running in existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` with `gpt-5.6-sol`, thinking `high`.
It must independently execute
`docs/prompts/phase5_t7bt_fig5_fig6_kirchhoff_metadata_contract_review.md`
and send its exact decision to T0 task
`019f5ec5-84ba-79e2-8c77-1160b150a636`.

## Allowed Files, Verification Commands, And Definition Of Done

- T7bt may modify only `status.md`, `docs/handoffs/T7_current.md`, and its
  required archive. It is review-only.
- T7bt must independently verify all nine checks in its frozen prompt,
  including every per-array fingerprint, all metadata surfaces, focused pytest,
  Ruff, full pytest, source hashes, directory cardinality, and forbidden scope.
- T8al exact GREEN requires all recorded checks, fresh status/T8 handoff
  verification, successful T7bt dispatch, and T0 notification.
