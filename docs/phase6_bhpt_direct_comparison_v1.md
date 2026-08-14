# Phase 6 BHPT-direct / conditioned-radial comparison V1

This evidence consumer closes a narrow Priority-2 implementation gap: the
external BHPT direct-integration output is compared, without fitting, to the
SchWO conditioned-radial baseline on the exact frozen 30-key external-direct
calibration inventory.  It does not run either solver and does not rerun paper
figures.

## Scientific scope

- External `phase_factor` is compared directly with the conditioned baseline
  `S`, whose frozen definition is `S=-A_out/((-1)**ell)`.
- External `reflection_ratio=Reflection/Incidence` is compared directly with
  conditioned `A_out` after the internal `A_in=1` normalization is rechecked.
- Transmission moduli are compared.  Complex transmission remains
  `NOT_ASSESSED` until both methods have an identical, auditable horizon/master
  phase-normalization ledger.
- Every successful key reports complex absolute difference, modulus
  difference, wrapped phase difference, both flux residuals, the external
  three-match-radius spread, and the internal ladder and uncertainty records.
- No numerical acceptance threshold is frozen.  The 24 comparable keys are
  therefore `PARTIAL`, never `PASS`.
- The six conditioned-radial failures at `(kM,ell)=(1,20),(2,60),(4,120)` in
  both parity sectors remain `FAIL`; no external value fills an internal
  failure.
- The external even sector is an independently integrated Zerilli radial
  solution.  This is not a claim of an independently implemented even-sector
  MST calculation.

The result is selected-domain evidence only.  It is neither full production
domain acceptance nor a global project state.

## Immutable result contract

A successful publication creates one fresh `0555` root with exactly three
`0444`, `nlink=1` files:

- `comparison.json`: native 30-key detail, complete external/internal artifact
  identities, source implementation hashes, metrics, failures, and separate
  uncertainty ledgers;
- `report.json`: exact
  `schwgw_phase6_v1_typed_physical_result_v1` projection for
  `V1/radial_s_matrix_flux`, with 30 expected item IDs, 24 `PARTIAL`, six
  `FAIL`, role `INDEPENDENT_SCIENCE`, independence class `EXTERNAL_SOURCE`, and
  no global-GREEN or Li-figure gate;
- `manifest.json`: hashes and binds both files, the exact 24/6 state counts,
  source role, and overall `FAIL`.

`report.json` includes the `comparison.json` SHA-256.  Publication then records
both identities in the manifest and performs a full source rebuild.  A path
collision is rejected; no automatic retry or overwrite occurs.

Although `report.json` conforms to the generic typed-result schema, release
preparation must consume this root through the dedicated
`BHPT_DIRECT_COMPARISON_V1` three-file adapter.  Accepting the report in
isolation would discard the external/internal identity ledger and is therefore
prohibited.  The public native validator is
`validate_published_bhpt_conditioned_comparison(root)`.

## Input requirements

The consumer accepts only:

1. a terminal immutable BHPT-direct formal root whose source/method validation
   status is `PASS`, whose external record count is 30, and whose scientific
   acceptance remains `NOT_ASSESSED` before this comparison;
2. the terminal immutable 86-shard conditioning campaign root;
3. exactly eight terminal immutable conditioning shard roots for `kM` in
   `0.5, 1, 2, 4` and both `odd/even` sectors.

An active, partial, blocked, mutable, or aliased BHPT root is rejected and must
not be used as science.

## Command line

Use exact CPython 3.14 with the project `src` directory on `PYTHONPATH`.  First
run a no-write preflight:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3.14 \
  scripts/phase6_compare_bhpt_direct_conditioned.py \
  --comparison-id phase6_bhpt_direct_conditioned_selected_v1 \
  --bhpt-root /absolute/terminal/bhpt_direct_root \
  --conditioning-campaign-root /absolute/v1_conditioning_campaign_root \
  --shard-root /absolute/k0p5_odd_root \
  --shard-root /absolute/k0p5_even_root \
  --shard-root /absolute/k1_odd_root \
  --shard-root /absolute/k1_even_root \
  --shard-root /absolute/k2_odd_root \
  --shard-root /absolute/k2_even_root \
  --shard-root /absolute/k4_odd_root \
  --shard-root /absolute/k4_even_root \
  --check-only
```

After the BHPT root is terminal and the preflight succeeds, replace
`--check-only` with one fresh absent absolute output root:

```bash
--output-root /absolute/fresh/phase6_bhpt_direct_conditioned_selected_v1
```

The formal comparator must not be published from an active BHPT run.  This V1
implementation intentionally publishes no real result root until the terminal
source root is separately authorized.
