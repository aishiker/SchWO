# Phase 6 V1 high-ell adaptive-Jost repair

Date: 2026-08-10

## Scope and verdict

This repair addresses the final 230 algorithmic failures left by the overnight
pole-safe radial campaign.  The exact domain is `kM=8`, both parity sectors,
and `ell=605..720` excluding `ell=606` (115 keys per sector).  It is an
extended radial-validation slice, not the 40-frequency production
finite-radius domain and not Phase-6 V2.

All 230 keys now pass the frozen numerical radius/Jost/flux gates.  Their
per-key and aggregate state remains **PARTIAL**, because the exact keys do not
have an independent arbitrary-precision or external solve and their convention
uncertainty is not assessed.  No global GREEN is permitted.

## Numerical diagnosis and repair

The full-state tortoise-coordinate ODE propagation was finite.  The failure was
the finite-radius outer basis: at `r_out=300M`, the 160-term Jost expansion for
these very high multipoles was not sufficiently asymptotic.  The two Jost
columns acquired a large common normalization and the V1 absolute incoming-
coefficient floor rejected them.  Removing that floor alone would have created
a false pass because the local basis ODE residual and tail were still large.

The evidence-bound V1 backend was therefore left byte-for-byte unchanged.  A
new wrapper, `src/schwgw/numerics/adaptive_jost_radial.py`, evaluates a generic
radius ladder `(1,2,4,8) * requested_r_out` and selects the first candidate that
simultaneously satisfies:

- maximum local Jost ODE residual `<= 1e-10`;
- maximum Jost tail ratio `<= 1e-8`;
- basis condition number `<= 1e8`;
- relative 2x2 determinant `>= 1e-8`.

This policy depends only on numerical basis quality.  It has no `Q018`, paper
figure, frequency, or multipole envelope.  It then delegates propagation to
the unchanged scaled full-state backend and records both requested and selected
outer radii.

## Immutable evidence

The formal root is:

```text
runs/phase6/radial_validation/
  v1_high_ell_adaptive_jost_repair_v1_20260810_py314/
```

It is mode `0555`; its two files are regular `0444`, `nlink=1`.  The strict
validator rebuilds all 230 records from the immutable boundary-ladder JSONL and
current bound implementation sources, then requires exact report equality.

```text
repair_report.json  4354a581704947160c11e646a3a97a345417943b7ad405f5043429cc22a9dc78
manifest.json       0fb711f03b1fac5c030f4ede47a0b06a3652e04ae729095a8d6087461f209ca2
```

Selection and convergence summary:

```text
selected 600M       218 keys
selected 1200M       12 keys
algorithmic repair  230/230
numerical failures    0
overall states       230 PARTIAL
```

Across all 230 keys, the `600M <-> 1200M` ladder has maximum complex-S and
wrapped-phase differences `9.978992937331159e-8` and
`9.978992937531572e-8 rad`.  The selected-radius `Jost order 160 <-> 224`
rematch has maximum complex-S and wrapped-phase differences
`9.841647671969678e-11` and `9.841638615171178e-11 rad`.  The maximum radius-
ladder `log|T|` difference is `5.997662810841575e-9`; all selected-node flux
residuals are below `1e-8`.

The independent 60/80-dps mpmath campaign remains selected-domain evidence,
not exact coverage of these 230 keys.  As an implementation-family cross-check,
the new wrapper agrees with the frozen `kM=8, ell=315` odd/even 80-dps anchors
at complex-S differences `1.4577725555197251e-8` and
`1.4577633288180863e-8`.  This does not promote the 230-key certificate beyond
PARTIAL.

## Other overnight results and qualifications

- The production finite-radius repair completed all `3,382/3,382` former
  failures and emitted `27,056 = 3,382 * 8` states with zero solver failure.
- The predecessor-success continuity run completed `12,020/12,020` keys with
  zero failure; its maximum wrapped phase difference is
  `0.002710129551448004 rad`.
- The independent selected AP campaign closed all `24/24` ladders; its maximum
  step-size relative complex-S difference is `6.717661091204782e-7` against a
  `2e-6` gate.  Its convention budget remains frozen but not externally
  cross-checked.
- The original 5,798-key tolerance/Jost diagnostic produced `5,568 PARTIAL`
  and `230 FAIL`.  Its scientific bytes and hashes are intact, but its manifest
  recorded the five payload modes before sealing (`0644` recorded versus
  `0444` actual).  That immutable root is therefore qualified as a diagnostic
  with stale mode metadata and is not rewritten.  The clean high-ell repair
  certificate is derived from the separately validated boundary-ladder root.

## Verification

Under CPython 3.14.6, the adaptive backend, high-ell certifier, frozen scaled
backend, and boundary-ladder tests pass `14/14`; focused Ruff check and format
pass.  The complete Phase-6 plus legacy-isolation unit selection passes
`344 passed, 2 skipped` under the exact absolute overlay-first runtime
contract.  Formal publication check-only, one fresh publish, strict immutable
reload, and a second independent full rebuild all pass.  No paper figure was
rerun.
