# Phase 5 T4y Fig.5/Fig.6 Review-Grid Radial Gate

Date: 2026-07-09

Decision:

```text
GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE READY FOR T7 REVIEW
```

## Scope

T4y investigated the T12b Stage 1 radial blocker in the conservative
Fig.5/Fig.6 review grid without changing Fourier, radial phase, RW/Zerilli,
Route B, Q014/Q015/Q018, or boundary conventions.

No `lmax` values were lowered, no modes or Table-I points were skipped, no
diagnostic thresholds were relaxed, and no Fig.5/Fig.6 NPZ/PDF/PNG or
Kirchhoff artifacts were generated.

## Stage A: T12b Blocker Reproduction

Parameters:

```text
M=1
k=2.5
ell=160
sector=odd/even
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
required_eval_radius in {sqrt(20^2+30^2), sqrt(25^2+30^2)}
```

Observed default-path behavior:

| point | sector | default result |
|---|---|---|
| `far_axis_x20_z30` | odd/even | structured `evanescent_tail_required_radius_solver_failed` after BVP plus bidirectional fallback failed before a certified required-radius solution |
| `far_axis_x25_z30` | odd/even | structured `evanescent_tail_required_radius_uncovered`; local valid-until radius does not certify the requested radius |

Direct Riccati/log-amplitude oracle returned finite local values for all four
records with residuals at machine precision scale.

## Stage B: Review-Grid Classification

Output:

```text
runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json
```

Inputs:

```text
kM = [2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0]
Table-I radii = x=[0,1,2,3,10,15,20,25], z=30
sector = odd/even
r_out=300, r_in_eps=1e-6, rtol=1e-10, atol=1e-12
```

Summary:

| classification | count |
|---|---:|
| default_covered | 6156 |
| default_fail_closed_uncovered | 1582 |
| default_fail_closed_solver_failed | 36 |
| default_error_other | 0 |

The complete measured transition set has 1618 records. No unstructured default
errors remain.

## Stage C: Direct Oracle Validation

Output:

```text
runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json
```

Summary:

| diagnostic | value |
|---|---:|
| oracle_validated | 1618 |
| max_effective_residual | 8.062852725174548e-16 |
| max_outer_boundary_residual | 8.062852725174548e-16 |
| max_normalization_residual | 5.564226404572962e-16 |
| max_log_derivative_match_residual | 4.1656245120705334e-16 |
| max_match_condition_number | 4.02684563758389 |
| max_abs_A_in_minus_one | 0.0 |
| sensitivity records | 21 |
| max loose/tight relative psi | 1.0038374163759307e-07 |
| max loose/tight relative dpsi_dr | 1.003844364249682e-07 |
| max loose/tight relative A_out | 1.9562971613732602e-07 |

## Stage D: Opt-In Adapter

Implemented a new exact adapter:

```text
experimental_required_radius_oracle="q018_tablei_review_grid_transition"
```

This is separate from the existing reviewed adapters:

```text
q018_riccati
q018_tablei_km4_transition
```

The new adapter is only entered after the default production radial path fails
with a recoverable structured required-radius no-go. Default-covered modes
remain on the normal production path and do not call the experimental oracle.

Envelope:

```text
Schwarzschild M=1
k in {2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0}
required_eval_radius exactly one of the eight Table-I radii at z=30
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
ell/point membership exactly the measured T4y transition set
sector=odd/even
```

Warning code:

```text
q018_tablei_review_grid_transition_oracle_used
```

Out-of-envelope requests fail closed with structured
`q018_experimental_oracle_out_of_envelope` metadata.

## Stage E: Resume Preflight

Output:

```text
runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json
```

Summary:

| diagnostic | value |
|---|---:|
| default_covered_from_stage_b | 6156 |
| transition_records_expected | 1618 |
| adapter_validated | 1618 |
| failures | 0 |
| previous_blocker_records_validated | 4 |
| max_effective_residual | 8.062852725174548e-16 |
| max_boundary_residual | 8.062852725174548e-16 |
| max_match_condition_number | 4.02684563758389 |

This is a radial-only preflight. It did not start T8 and did not generate
Fig.5/Fig.6 production artifacts.

## Changed Files

- `src/schwgw/numerics/radial_solver.py`
- `tests/physics/test_radial_solver.py`
- `tests/physics/test_q018_production_integration_design.py`
- `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
- `docs/handoffs/T4_current.md`
- `status.md`

Generated metadata:

- `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
- `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
- `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`

## Verification

RED test before implementation:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_returns_local_production_radial_solution tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_matches_direct_experimental_oracle_on_anchor_modes tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_keeps_default_covered_modes_on_production_path tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_default_path_does_not_call_experimental_oracle tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_rejects_out_of_envelope
```

Result:

```text
19 failed, 1 passed
```

The failures were the expected unsupported
`q018_tablei_review_grid_transition` oracle name.

GREEN tests after implementation:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_returns_local_production_radial_solution tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_matches_direct_experimental_oracle_on_anchor_modes tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_keeps_default_covered_modes_on_production_path tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_default_path_does_not_call_experimental_oracle tests/physics/test_q018_production_integration_design.py::test_q018_review_grid_opt_in_rejects_out_of_envelope
```

```text
20 passed
```

Required radial/Q018/unit verification:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
```

```text
317 passed, 108 warnings, 16 subtests passed
```

Full repository verification:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

```text
549 passed, 117 skipped, 1 xfailed, 108 warnings, 79 subtests passed
```

Warnings are expected SciPy overflow/invalid warnings from deliberately
exercised fail-closed BVP/bidirectional paths before the opt-in adapter is
invoked.

## Remaining Gates

- T7bq must independently review the T4y adapter and radial gate evidence.
- T8 Fig.5/Fig.6 review-grid production remains blocked until T7 accepts this
  gate.
- Do not broaden `q018_tablei_review_grid_transition` beyond the exact
  measured envelope above without a new measured classification and review.
