# Phase 5 T4x kM=4 Table-I Transition Error Structuring And Adapter Gate

Date: 2026-07-09

Decision:

```text
GREEN / KM4 TABLE-I TRANSITION ERROR STRUCTURED AND ADAPTER IMPLEMENTED
```

## Scope

T4x addressed the T12 Stage 1 blocker at `kM=4`,
`required_eval_radius=39.051248M`, `r_out=300`, `r_in_eps=1e-6`,
`rtol=1e-10`, `atol=1e-12`.  The original failure was a raw
`numpy.linalg.LinAlgError: SVD did not converge` in the bidirectional radial
fallback condition-number diagnostic for `ell=177`, odd/even.

No Fourier convention, radial phase convention, partial-wave cutoff policy,
boundary policy, Weyl scalar, plotting, fixture, Kirchhoff, or dense benchmark
artifact was changed.

## Stage A: Raw Blocker Reproduction

The default no-oracle path was reproduced for `ell=177`, odd/even.  The
bidirectional fallback reached non-finite horizon-basis match data before
condition-number SVD:

| sector | ell | barrier_action | match_radius | structured tail valid_until_r |
|---|---:|---:|---:|---:|
| odd | 177 | 702.7989610207247 | 45.50567537916857 | 25.855211103192737 |
| even | 177 | 702.7989610121734 | 45.50567536703387 | 25.855211092490098 |

The certified evanescent-tail domain is below the requested
`39.051248M`, so the physically meaningful default result is a structured
`evanescent_tail_required_radius_uncovered` no-go, not raw linear algebra.

## Stage B: Error Structuring

Added finite checks for bidirectional match inputs and converted
`numpy.linalg.LinAlgError` from bidirectional solve/condition-number operations
into structured `RuntimeError`s.  The BVP fallback then maps such failures to
`evanescent_tail_required_radius_uncovered` when the WKB tail-domain diagnostic
shows that the requested radius is not certified.

Regression test:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py::RadialSolverPhysicsTests::test_km4_tablei_transition_linear_algebra_failure_fails_closed
```

Result:

```text
1 passed, 3 warnings, 2 subtests passed
```

## Stage C: Default No-Oracle Classification

Output:

```text
runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json
```

Inputs:

```text
M=1
k=4
ell=2..360
sector=odd/even
required_eval_radius=39.051248
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
no experimental oracle
```

Summary:

| item | value |
|---|---:|
| total records | 718 |
| default covered | 590 |
| structured uncovered | 128 |
| default_error_other | 0 |
| outward_shooting | 42 |
| bidirectional_match | 308 |
| evanescent_tail_suppressed | 368 |
| runtime seconds | 708.6354009159986 |

Measured transition set requiring adapter support:

```text
ell=177..240, sector=odd/even
```

This is a complete measured set from Stage C, not an assumed interval.

## Stage D: Direct Oracle Validation

Output:

```text
runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json
```

The direct experimental Riccati/log-derivative oracle was evaluated on all 128
measured transition modes.

| diagnostic | value |
|---|---:|
| oracle_validated | 128 |
| max_effective_residual | 6.632265483636072e-16 |
| max_outer_boundary_residual | 6.632265483636072e-16 |
| max_normalization_residual | 3.537220957463096e-16 |
| max_log_derivative_match_residual | 3.4230340091223435e-16 |
| max_match_condition_number | 4.02684563758389 |
| runtime seconds | 82.5075008749991 |

All oracle results were finite at the required radius and retained unit
incoming-at-infinity normalization.

## Stage E: Opt-In Adapter

Implemented a new explicit opt-in adapter name:

```text
q018_tablei_km4_transition
```

The adapter is accepted only for this envelope:

```text
background=Schwarzschild, M=1
k=4
required_eval_radius=39.051248
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
ell=177..240
sector=odd/even
```

The returned `RadialSolution` uses unit incoming-at-infinity normalization, so
`A_in` is the outer `exp(-i k r_star)` incoming coefficient and is close to
one.  Metadata warnings use code:

```text
q018_tablei_km4_transition_oracle_used
```

Run-level preflight rejects out-of-envelope global parameters for the new
adapter.  Mode-level validation is applied only when the default path actually
needs the adapter, so ordinary default-covered modes such as `ell=176` and
`ell=241` remain on the production radial path.

The old reviewed R60_K2 adapter name and envelope remain unchanged:

```text
q018_riccati
```

## Changed Files

- `src/schwgw/numerics/radial_solver.py`
- `tests/physics/test_radial_solver.py`
- `tests/physics/test_q018_production_integration_design.py`
- `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
- `docs/handoffs/T4_current.md`
- `status.md`
- `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
- `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`

## Verification

Commands run:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py::RadialSolverPhysicsTests::test_km4_tablei_transition_linear_algebra_failure_fails_closed
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py::test_q018_tablei_km4_opt_in_rejects_out_of_envelope tests/physics/test_q018_production_integration_design.py::test_q018_tablei_km4_opt_in_keeps_default_covered_modes_on_production_path
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Results:

```text
focused gate/default-covered checks:
11 passed

required three-file command:
296 passed, 18 warnings, 14 subtests passed

-m physics:
284 passed, 1 skipped, 360 deselected, 1 xfailed, 9 warnings, 17 subtests passed

full suite:
528 passed, 117 skipped, 1 xfailed, 18 warnings, 77 subtests passed
```

Warnings are the expected SciPy overflow/invalid warnings from the deliberately
failed bidirectional basis path before structured fail-closed handling.

## Remaining Open Issues

- T8 conservative review-grid and Fig.5/Fig.6 production remain blocked until
  independent T7bp review accepts this T4x implementation.
- The new adapter is not a general high-ell radial method.  It is a narrow
  reviewed opt-in bridge for the measured kM=4 Table-I transition envelope.
- No new dense benchmark artifacts, fixtures, plots, Weyl scalars, or
  Kirchhoff outputs were generated.
