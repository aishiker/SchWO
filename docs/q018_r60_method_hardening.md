# Q018 R60 Method Hardening

Date: 2026-07-06

Thread: T4m radial ODE and matching

## Scope

This slice hardens the Q018 high-`ell` radial policy for `kM=2` after the
T7ag ACCEPT YELLOW review.  It does not generate R60 wave-field artifacts,
plots, `kM=4` runs, or larger-domain production outputs.  It does not change
Fourier, radial phase, harmonic, tetrad, RW/Zerilli, Route B, Q005, Q014,
residual threshold, or `ell_max` conventions.

## Chosen Route

Route A was implemented: evaluation-radius-aware suppression policy.

`BoundaryConfig` now accepts

```text
required_eval_radius: float | None = None
```

The default `None` preserves the existing behavior.  When the value is set to
`R`, an `evanescent_tail_suppressed` solution may be returned only if its
recorded `valid_until_r >= R`.  If the existing zero-tail suppression policy
does not certify the requested radius, `solve_radial_mode` raises a structured
`RuntimeError` instead of returning a solution that downstream code could
misuse at `r=R`.

## Why Route B Was Not Used

Route B would require a conservative target-radius WKB tail bound with a
spin-2 reconstruction-aware polynomial prefactor allowance.  This slice did
not establish such a bound.  In particular, the scalar-field `ell ~ k r`
intuition is not sufficient evidence for spin-2 RW/Zerilli reconstruction
factors and tensor-harmonic prefactors.  The safe result is therefore
fail-closed R60 handling, not GREEN R60 production readiness.

## Structured No-Go Metadata

For uncovered requested radii the failure message contains JSON metadata with
code `evanescent_tail_required_radius_uncovered`.  The metadata records:

- `sector`, `ell`, `k`
- `solver`
- `barrier_action`
- `suppression_bound`
- `valid_until_r`
- `local_tail_action`
- `tail_action_threshold`
- `required_eval_radius`
- `required_eval_radius_covered`
- `no_go_reason`
- BVP and fallback failure messages

This is intentionally separate from successful warning metadata.  Successful
suppressed solutions still carry warning code `evanescent_tail_suppressed`;
if `required_eval_radius` is set and covered, the warning metadata records the
requested radius and coverage boolean.

## R60_K2 Classification

After this slice, R60_K2 remains **YELLOW / fail-closed**:

- accepted `[-30,30]^2` remains supported by the existing Q018 policy;
- R60 is not silently accepted by the radial solver;
- no reviewed target-radius spin-2 bound or rescaled radial architecture was
  added in this slice.

T8 must not run R60_K2 production from this result alone.  A future GREEN
result needs either a reviewed spin-2 tail bound evaluated at the requested
radius or a radial architecture that propagates reliable fields/diagnostics
through the requested observer radius.

## Future RED Tests

Future method work should preserve these checks:

- default `BoundaryConfig(r_out=300)` still returns
  `evanescent_tail_suppressed` for `k=2`, `ell=153`, and covers the accepted
  `[-30,30]^2` radius;
- `BoundaryConfig(r_out=300, required_eval_radius=60)` cannot return a
  suppressed solution whose `valid_until_r < 60`;
- failure and warning metadata remain JSON-safe and audit-ready.

