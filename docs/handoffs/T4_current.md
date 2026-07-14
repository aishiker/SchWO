# T4 Current Handoff

Last updated: 2026-07-09

Thread: T4y, Fig.5/Fig.6 review-grid radial gate.

## Current Status

Decision:

```text
GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE READY FOR T7 REVIEW
```

T4y resolved the T12b Stage 1 radial gate by:

- reproducing the `kM=2.5`, `ell=160` Table-I required-radius blocker;
- classifying the complete high-frequency Fig.5/Fig.6 review-grid radial set;
- converting the remaining required-radius BVP plus bidirectional fallback
  failures into structured fail-closed paths;
- validating the complete measured 1618-record transition set with the direct
  experimental Riccati/log-amplitude oracle;
- adding a narrow explicit opt-in production adapter named
  `q018_tablei_review_grid_transition`.

T8 conservative review-grid and Fig.5/Fig.6 production remain blocked until
T7bq independently reviews and accepts this T4y implementation.

## Required Context For Next Thread

Must read:

1. `status.md`
2. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
3. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
4. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
5. `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
6. `src/schwgw/numerics/radial_solver.py`
7. `tests/physics/test_radial_solver.py`
8. `tests/physics/test_q018_production_integration_design.py`
9. `docs/prompts/phase5_t4y_fig5_fig6_review_grid_radial_gate.md`

Useful prior context:

1. `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
2. `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
3. `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`
4. `docs/q018_rescaled_radial_architecture_spike.md`
5. `references/notes/q018_spin2_tail_bound.md`
6. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`

## Implementation Summary

Changed:

- `src/schwgw/numerics/radial_solver.py`
  - added structured `evanescent_tail_required_radius_solver_failed` recovery
    for required radii covered by the local tail certificate but not by a
    finite production BVP/fallback solution;
  - added exact review-grid constants and compressed measured transition-set
    membership for `kM=2.5..4.0`;
  - added opt-in adapter `q018_tablei_review_grid_transition`;
  - preserved old `q018_riccati` and `q018_tablei_km4_transition` envelopes.
- `tests/physics/test_radial_solver.py`
  - added regression coverage for the `k=2.5`, `ell=160`,
    `far_axis_x20_z30` required-radius solver-failure path.
- `tests/physics/test_q018_production_integration_design.py`
  - added review-grid adapter anchor tests;
  - added direct-oracle agreement tests;
  - added default-covered mode tests proving ordinary modes stay on the normal
    production path;
  - added out-of-envelope fail-closed coverage for `M`, `k`, radius, `r_out`,
    `rtol`, and `atol`.

Created:

- `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
- `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
- `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
- `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`

Updated:

- `docs/handoffs/T4_current.md`
- `status.md`

## Review-Grid Classification

Stage B default no-oracle scan:

```text
M=1
kM=[2.5,2.75,3.0,3.25,3.5,3.75,4.0]
Table-I radii x=[0,1,2,3,10,15,20,25], z=30
sector=odd/even
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
```

Result:

| classification | count |
|---|---:|
| default_covered | 6156 |
| default_fail_closed_uncovered | 1582 |
| default_fail_closed_solver_failed | 36 |
| default_error_other | 0 |

Measured transition set:

```text
1618 records across kM=2.5..4.0, odd/even sectors, and exact Table-I radii.
```

## Oracle Validation

Direct experimental oracle validation on the full measured transition set:

| diagnostic | value |
|---|---:|
| oracle_validated | 1618 |
| max_effective_residual | 8.062852725174548e-16 |
| max_outer_boundary_residual | 8.062852725174548e-16 |
| max_normalization_residual | 5.564226404572962e-16 |
| max_log_derivative_match_residual | 4.1656245120705334e-16 |
| max_match_condition_number | 4.02684563758389 |
| max_abs_A_in_minus_one | 0.0 |

## Adapter Envelope

New opt-in adapter:

```text
experimental_required_radius_oracle="q018_tablei_review_grid_transition"
```

Allowed only for:

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

The adapter warning code is:

```text
q018_tablei_review_grid_transition_oracle_used
```

Out-of-envelope requests fail closed with
`q018_experimental_oracle_out_of_envelope`.

The older `q018_riccati` R60_K2 and `q018_tablei_km4_transition` envelopes
remain unchanged.

## Resume Preflight

Radial-only Stage E preflight:

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

This was radial-only. T4y did not start T8 and did not generate Fig.5/Fig.6
NPZ/PDF/PNG or Kirchhoff artifacts.

## Verification

Passed:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
```

```text
317 passed, 108 warnings, 16 subtests passed
```

Passed:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

```text
549 passed, 117 skipped, 1 xfailed, 108 warnings, 79 subtests passed
```

Warnings are expected SciPy overflow/invalid warnings from deliberately
exercised fail-closed BVP/bidirectional basis paths before the opt-in adapter
is invoked.

## Remaining Gates

- T7bq must independently review this implementation before T8 can resume.
- Do not start T8 conservative review-grid, Kirchhoff implementation, dense
  Fig.5/Fig.6 production, plotting, fixtures, NPZ/HDF5 generation, or Weyl
  scalar work from T4y alone.
- Do not broaden `q018_tablei_review_grid_transition` beyond the exact
  measured envelope above.
- Do not broaden `q018_tablei_km4_transition`; it remains the T4x single
  radius adapter.

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Radial phase convention remains `exp(-i k r_star)` ingoing and
  `exp(+i k r_star)` outgoing.
- `A_in` remains the outer `exp(-i k r_star)` incoming coefficient.
- High-ell radial failures are not hidden by partial-wave truncation.
