# Phase 5 kM=4 Table-I Transition Oracle Probe

Date: 2026-07-09

Thread: T4w radial/Q018 experimental method followup.

## Decision Label

```text
GREEN / KM4 TABLE-I TRANSITION ORACLE PROBE PASSED
```

The existing experimental Riccati/log-derivative oracle stably covers the
T4v/T7bn `kM=4` Table-I transition-band modes at the required radius
`39.051248M`, when called directly as an experimental oracle.

This is not a production adapter expansion.  The reviewed production
`q018_riccati` envelope remains limited to `k=2`, `required_eval_radius=60`,
`r_out=300`, and `ell=153..180`.

## Matrix And Parameters

Direct oracle request:

```text
M = 1
kM = 4.0
required_radius = 39.051248
r_out = 300.0
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
precision_dps = 80 requested
method_hint = rescaled_log_amplitude
```

Implementation note: the oracle records `precision_dps=53` with
`precision_note=double_precision_scipy`; `precision_dps=80` is a requested
contract value, not an arbitrary-precision backend.

Core transition-band modes:

```text
ell=178, ell=180, ell=204, ell=228, ell=240
sector=odd/even
```

Context modes:

```text
ell=169, ell=241, ell=252, ell=300, ell=360
sector=odd/even
```

Metadata-only JSON:

```text
runs/phase5/km4_tablei_transition_oracle_probe/transition_oracle_probe_metadata.json
```

The JSON contains scalar diagnostics and provenance only.  It contains no
field arrays, dense scan arrays, plots, NPZ/HDF5 production data, or Kirchhoff
values.

## Per-Mode Diagnostics

All 10 core modes returned finite `psi`, `dpsi_dr`, `A_in`, and `A_out`.
All core modes had `abs(A_in-1)=0` in the returned unit incoming-at-infinity
normalization.

| sector | ell | `|psi|` | `|dpsi_dr|` | `|A_out|` | `outer_boundary_residual` | `normalization_residual` | `log_derivative_match_residual` | condition | steps `R/O` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| odd | 178 | `3.440327e-03` | `7.300377e-03` | `1.000000000000` | `6.021e-17` | `8.404e-17` | `7.704e-19` | `4.026846` | `1827/2868` |
| even | 178 | `3.440327e-03` | `7.300377e-03` | `1.000000000000` | `6.553e-17` | `5.769e-17` | `2.206e-16` | `4.026846` | `1828/2868` |
| odd | 180 | `1.215430e-03` | `2.715688e-03` | `1.000000000000` | `7.211e-17` | `5.769e-17` | `3.375e-17` | `4.026846` | `1841/2862` |
| even | 180 | `1.215430e-03` | `2.715689e-03` | `1.000000000000` | `7.999e-17` | `5.769e-17` | `8.820e-18` | `4.026846` | `1842/2862` |
| odd | 204 | `1.695440e-10` | `5.710212e-10` | `1.000000000000` | `1.813e-16` | `2.499e-16` | `1.451e-16` | `4.026846` | `2011/2799` |
| even | 204 | `1.695440e-10` | `5.710212e-10` | `1.000000000000` | `1.677e-16` | `5.769e-17` | `4.013e-18` | `4.026846` | `2011/2799` |
| odd | 228 | `2.148660e-19` | `9.246967e-19` | `1.000000000000` | `1.568e-16` | `2.614e-16` | `2.175e-16` | `4.026846` | `2165/2752` |
| even | 228 | `2.148660e-19` | `9.246967e-19` | `1.000000000000` | `1.221e-16` | `5.769e-17` | `1.152e-17` | `4.026846` | `2166/2752` |
| odd | 240 | `1.857947e-24` | `8.795795e-24` | `1.000000000000` | `2.748e-16` | `1.419e-16` | `1.988e-16` | `4.026846` | `2237/2735` |
| even | 240 | `1.857947e-24` | `8.795795e-24` | `1.000000000000` | `1.711e-16` | `5.769e-17` | `2.020e-16` | `4.026846` | `2239/2735` |

Aggregate core maxima:

| diagnostic | maximum |
|---|---:|
| `outer_boundary_residual` | `2.748435773035172e-16` |
| `normalization_residual` | `2.614383712850005e-16` |
| `log_derivative_match_residual` | `2.2058470598903817e-16` |
| single-call runtime | `0.9291951669947593 s` |

## Repeat And Sensitivity Summary

Repeat calls were run for every core and context record.  For the 10 core
modes:

| repeat diagnostic | maximum relative difference |
|---|---:|
| `psi` | `0.0` |
| `dpsi_dr` | `0.0` |
| `A_out` | `0.0` |

Full core tolerance sensitivity was also run:

```text
baseline: rtol=1e-10, atol=1e-12
loose:    rtol=1e-9,  atol=1e-11
tight:    rtol=1e-11, atol=1e-13
```

Maximum relative differences against baseline:

| quantity | maximum |
|---|---:|
| `psi` | `8.951759867083892e-08` |
| `dpsi_dr` | `8.951696206177754e-08` |
| `A_out` | `1.7657732841370013e-07` |

The largest sensitivity is far below the existing Q018 full-regression
stability scale `5e-6` used for the earlier R60_K2 oracle tests.

## Comparison With T4v Fail-Closed Records

T4v failed closed for all 10 core modes through the production radial path:

| sector | ell | T4v code | T4v `valid_until_r` | T4w oracle status |
|---|---:|---|---:|---|
| odd | 178 | `evanescent_tail_required_radius_uncovered` | `26.055783749096506` | finite / GREEN thresholds |
| even | 178 | `evanescent_tail_required_radius_uncovered` | `26.055783738640127` | finite / GREEN thresholds |
| odd | 180 | `evanescent_tail_required_radius_uncovered` | `26.465206738394947` | finite / GREEN thresholds |
| even | 180 | `evanescent_tail_required_radius_uncovered` | `26.465206728375100` | finite / GREEN thresholds |
| odd | 204 | `evanescent_tail_required_radius_uncovered` | `31.396533404752535` | finite / GREEN thresholds |
| even | 204 | `evanescent_tail_required_radius_uncovered` | `31.396533398589646` | finite / GREEN thresholds |
| odd | 228 | `evanescent_tail_required_radius_uncovered` | `36.417786629629866` | finite / GREEN thresholds |
| even | 228 | `evanescent_tail_required_radius_uncovered` | `36.417786625625080` | finite / GREEN thresholds |
| odd | 240 | `evanescent_tail_required_radius_uncovered` | `38.960770674893250` | finite / GREEN thresholds |
| even | 240 | `evanescent_tail_required_radius_uncovered` | `38.960770671616960` | finite / GREEN thresholds |

Context probes also succeeded.  `ell=169` was an ordinary T4v
`bidirectional_match` mode; `ell=241,252,300,360` were T4v
`evanescent_tail_suppressed` modes whose `valid_until_r` already covered
`39.051248M`.  The direct oracle returned finite scalar diagnostics for all
of them.

## Recommendation

T4x production-adapter design is worth scheduling, but only as a reviewed
design/implementation slice.

The evidence supports the statement that the existing experimental oracle can
cover the `kM=4`, Table-I-radius transition-band modes that blocked T4v.
However, the current task did not broaden the production adapter and did not
review run-level partial-wave consequences.  A future T4x slice should define
the exact `kM=4` production envelope, metadata, failure behavior, and tests,
then send that to T7 before any T8 scan is allowed.

## Non-Claims And Forbidden Next Steps

This probe does not claim or authorize:

- production `q018_riccati` support for `kM=4`;
- dense Fig.5/Fig.6 production;
- the T10g conservative review-grid scan;
- 40-frequency scans;
- field maps, plots, fixtures, NPZ/HDF5 production artifacts, or Kirchhoff
  values;
- `R60_K4`;
- threshold, `lmax`, boundary, Q018 policy, production adapter envelope, or
  physics convention changes.

T8 must remain blocked until a follow-up T4 production-adapter design or new
radial-method slice is independently reviewed by T7.

## Verification

Focused existing tests and required static/file checks are recorded in
`status.md` and `docs/handoffs/T4_current.md`.
