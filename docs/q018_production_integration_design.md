# Q018 Production-Integration Design

Date: 2026-07-07

Thread: T4u radial ODE and matching

Status: T4r design accepted by T7am; T4s implemented the reviewed explicit
opt-in adapter; T7an accepted the discrete-anchor adapter.  T4u extends the
reviewed opt-in production envelope to the continuous R60_K2 suppressed band
`ell=153..180`, pending T7ap review.  This document still does not authorize
R60_K2 artifacts.

## 1. Problem Statement

T4q/T7al accepted the broader experimental Q018 oracle anchor matrix for

```text
M=1, k=2, required_radius=60, r_out=300,
ell=[153,156,168,180], sector=[odd,even].
```

T4u then checked the continuous suppressed band required by
`compute_polarization(..., lmax=180)`: `ell=153..180`, odd/even, at the same
R60_K2 settings.  The accepted method lives behind
`schwgw.numerics.experimental`, is not exported by `schwgw.numerics`, and is
called by `solve_radial_mode(...)` only through the reviewed explicit opt-in
adapter.  The default production path still correctly fails closed for that
suppressed band through `BoundaryConfig.required_eval_radius=60`.

The missing production decision is not whether the experimental matrix is
finite.  The missing decision is how a production run would opt in, how the
result would be labelled and serialized, what parameter envelope is certified,
and what partial-wave convergence evidence must exist before a saved R60
artifact is allowed.

## 2. Current Evidence

- T7al accepted all 8 experimental anchor modes as finite
  unit-incoming-at-infinity radial fields with credible residual proxies.
- T4u directly validated the continuous `ell=153..180`, odd/even oracle
  matrix at `M=1`, `k=2`, `r=60`, `r_out=300`, `r_in_eps=1e-6`,
  `rtol=1e-10`, and `atol=1e-12`.
- Production `solve_radial_mode(..., required_eval_radius=60)` still raises
  `evanescent_tail_required_radius_uncovered` by default for the same
  suppressed band.
- Default-covered modes, including low ell and the R60_K2 `ell<=152` boundary
  checked by T4u, remain on the ordinary production path even when the run-level
  opt-in string is present.
- The evidence does not cover `kM=4`, R60_K4, arbitrary incident direction,
  larger observer domains, or a spin-2 observable-level tail bound.

## 3. Proposed Production Policy

Production remains fail-closed by default.  T4u keeps the explicit opt-in through

```python
BoundaryConfig(
    required_eval_radius=60.0,
    experimental_required_radius_oracle="q018_riccati",
)
```

The value `None` is the default and preserves current fail-closed behavior.
The value `"q018_riccati"` is a run-level permission, not a command to bypass
ordinary radial solving.  `solve_radial_mode(...)` first tries the normal
production branch; the oracle is attempted only if that branch fails with
`evanescent_tail_required_radius_uncovered`.  Unknown values and
out-of-envelope oracle requests fail closed.

### 3.1 Allowed Envelope

The T4u production-integration slice accepts only the already reviewed
continuous experimental envelope when the oracle is actually needed:

| field | allowed value |
|---|---|
| background | Schwarzschild `M=1` |
| `k` | `2.0` |
| `required_eval_radius` | `60.0` |
| `r_out` | `300.0` |
| `r_in_eps` | `1e-6` |
| `rtol` / `atol` | `1e-10` / `1e-12` |
| `ell` | `153..180` |
| sector | odd/even |
| method | `riccati_log_derivative_match` |

Everything outside this envelope should raise a structured production no-go
rather than falling back to zero-tail suppression, changing `ell_max`, or
relaxing tolerances.

## 4. Metadata Requirements

Any production radial result using this opt-in must carry enough metadata to
distinguish it from the default BVP and from the old
`evanescent_tail_suppressed` policy.

Required radial diagnostic or warning fields:

- `code="q018_required_radius_oracle_used"` or a similarly explicit value;
- `experimental_required_radius_oracle="q018_riccati"`;
- `method="riccati_log_derivative_match"`;
- `production_integration_review_id="T4u/T7ap-pending"` before review;
- `experimental_evidence="T4u continuous ell=153..180 matrix"`;
- `sector`, `ell`, `k`, `required_eval_radius`, `r_out`;
- `r_in_eps`, `rtol`, `atol`, precision note;
- finite flags for `psi`, `dpsi_dr`, `A_in`, `A_out`;
- `outer_boundary_residual`, `normalization_residual`,
  `log_derivative_match_residual`, condition number, step counts, runtime;
- `valid_at_required_radius=True`;
- `unit_incoming_at_infinity=True`;
- a statement that `A_in` remains the outer `exp(-i k r_star)` incoming
  coefficient.

Saved T8 artifacts must serialize this provenance per affected radial mode,
not only as a scalar maximum.  A reader should be able to tell which modes
used the oracle, what evidence reviewed them, and which modes remained in the
ordinary production branches.

## 5. API Boundary

Production should not have `partial_wave.py` call
`schwgw.numerics.experimental` directly.  The safer boundary is:

1. keep `solve_radial_mode(...)` as the only radial API used by
   `compute_polarization(...)`;
2. keep the T4u private adapter inside `src/schwgw/numerics/radial_solver.py`
   unless a future review moves the method from `experimental` into a
   non-experimental internal module;
3. keep the experimental module unexported from `schwgw.numerics`;
4. require the explicit `BoundaryConfig.experimental_required_radius_oracle`
   opt-in before the adapter can run;
5. return a normal `RadialSolution` whose `psi`, `dpsi_dr`, `A_in`, `A_out`,
   `phase_factor`, interpolation helpers, and diagnostics are mutually
   consistent.

This preserves the existing partial-wave contract:

```text
scale = coefficient / A_in
```

No caller should need to know how the high-ell R60 solution was obtained.

## 6. Test Plan

Default tests:

- `solve_radial_mode(... required_eval_radius=60)` for the continuous
  `ell=153..180`, odd/even suppressed matrix keeps raising
  `evanescent_tail_required_radius_uncovered`;
- `schwgw.numerics` does not export `solve_q018_rescaled_oracle`;
- no default test depends on optional oracle dependencies;
- no default path silently calls the experimental oracle.

Opt-in production tests:

- `BoundaryConfig(experimental_required_radius_oracle="q018_riccati")`
  returns a production `RadialSolution` for each continuous suppressed matrix
  member;
- the same run-level opt-in keeps default-covered modes on the ordinary
  production branch;
- require `A_in≈1`, finite fields at `r=60`, residual proxies below the T4q
  thresholds, and explicit oracle provenance metadata;
- require unknown opt-in names to fail closed;
- require out-of-envelope parameters to fail closed with structured metadata.

Regression fixture policy:

- Do not commit an R60_K2 fixture until the production opt-in implementation
  and T7 review pass.
- The first fixture should be selected-probe only, not a full plot artifact.
- The fixture must record radial warning/provenance records and final
  partial-wave convergence data.

Partial-wave convergence gates:

- R60_K2 must use adaptive `lmax` convergence, not fixed early pairs.
- The final adjacent pair must satisfy global `<1e-4` and near-axis `<1e-3`
  thresholds from `docs/numerics.md` / `docs/validation_plan.md`.
- The run must record the final `lmax_values`, final adjacent pair,
  selected-probe and near-axis changes, radial residual maxima, and all oracle
  provenance records.

## 7. Stop / Go Gates

Future T4 implementation must prove:

- the opt-in adapter produces a consistent `RadialSolution` for the reviewed
  continuous `ell=153..180`, odd/even matrix;
- default `None` behavior is unchanged and fail-closed;
- out-of-envelope values are rejected;
- metadata is JSON-safe and self-describing;
- the method does not change Fourier/radial phase conventions, thresholds,
  or `lmax` policy.

Future T7 review must independently rerun:

- default fail-closed matrix;
- opt-in production matrix;
- direct experimental-vs-production consistency for the 8 modes;
- full pytest;
- a selected-probe partial-wave convergence run before any fixture/artifact
  approval.

T8 remains forbidden to:

- generate R60_K2/R60_K4 wave-field artifacts, benchmark fixtures, or plots
  before T4/T7 production integration is accepted;
- run `kM=4`;
- use scalar cutoff alone as a spin-2 production proof;
- change `ell_max`, residual thresholds, or convergence policy to make a run
  pass.

## 8. Explicit Non-Validation

This design does not validate:

- `kM=4`;
- R60_K4;
- arbitrary incident direction;
- larger-domain artifacts;
- scalar-cutoff-only or WKB-only spin-2 production readiness;
- transmission-factor or amplification outputs.

It is a policy and contract-test slice only.
