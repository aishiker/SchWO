# Phase 5 T7bt Prompt: Review Kirchhoff Units/Dtype Metadata Contract

You are T7bt: independent review of the bounded T8al metadata-contract
hardening. Do not repair source/tests/artifacts or generate later outputs.

## Read First

Read `project.md`, `status.md`, T0/T7/T8 handoffs, the T7bs YELLOW record,
the T8al plan and prompt, `src/schwgw/io/kirchhoff.py`,
`tests/unit/test_kirchhoff_artifact.py`, and both the pre-hardening hashes in
T7bs plus the three current baseline files.

Use `verification-before-completion` and `systematic-debugging` for failures.

## Required Independent Checks

1. Confirm the implementation commit changes only serializer and artifact
   contract test.
2. Confirm schema is
   `phase5_t8al_kirchhoff_review_grid_v2_units_dtype`.
3. Confirm embedded metadata and sidecar contain equal top-level `units` and
   `dtype` mappings covering every non-metadata NPZ array.
4. Confirm actual array dtypes exactly equal the declared mapping.
5. Confirm manifest contains the same unit/dtype pair for every array.
6. Recompute the NumPy `.npy` SHA-256 fingerprint of every non-metadata array
   and compare it with the frozen mapping in the T8al plan. All must match.
7. Confirm T8aj hashes remain unchanged and exactly three current baseline
   files exist.
8. Run focused pytest, Ruff, and full pytest freshly.
9. Confirm no forbidden production diff or downstream output exists.

Do not require the full NPZ/JSON/manifest hashes to remain equal to T8ak; they
must change because metadata/schema changes. Require all non-metadata array
fingerprints to remain equal.

## Allowed Review Writes

- `status.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/archive/T7_2026-07-14_pre_t7bt_metadata_contract.md`

## Decision Labels

```text
ACCEPT GREEN / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT ACCEPTED
ACCEPT YELLOW / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT PARTIAL
REJECT RED / FIG5-FIG6 KIRCHHOFF METADATA CONTRACT FAILED
```

GREEN requires all nine checks. Send the exact decision, new three hashes,
array-fingerprint result, focused/Ruff/full-pytest result, and review-only
changed files to T0 task `019f5ec5-84ba-79e2-8c77-1160b150a636`.

Do not start plotting, 40-frequency production, fixtures, or any later task.
Only T0 may close the gate, synchronize GitHub, and design the next stage.
