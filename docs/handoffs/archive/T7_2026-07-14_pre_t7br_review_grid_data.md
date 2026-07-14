# T7 Current Handoff

Last updated: 2026-07-09

Thread: T7bq, Fig.5/Fig.6 review-grid radial gate independent review.

## Current Status

T7bq completed the independent review of the T4y Fig.5/Fig.6 review-grid
radial gate.

Decision recorded exactly:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED
```

Meaning:

- T4y reproduced the T12b `kM=2.5`, `ell=160` Table-I required-radius blocker.
- T4y classified the high-frequency conservative review-grid radial coverage.
- The measured transition set has `1618` records and is exactly encoded by the
  production adapter's compressed transition segments.
- The new explicit opt-in adapter is
  `experimental_required_radius_oracle="q018_tablei_review_grid_transition"`.
- The adapter is separate from `q018_riccati` and
  `q018_tablei_km4_transition`.
- The default production path still does not call the experimental oracle.
- T0 may schedule a T8 resume prompt for the conservative eight-point
  review-grid scan from the T12b Stage 1 boundary.
- T7bq did not start T8 and did not generate Fig.5/Fig.6 data, plots,
  Kirchhoff baselines, fixtures, dense scans, or paper-style artifacts.

## Review Answers

1. T4y reproduced the T12b blocker at `kM=2.5`, `ell=160`, odd/even, and the
   x20/x25 Table-I required radii.

2. T4y classified the remaining high-frequency review-grid radial coverage:
   `7774` total records, `6156` default-covered, `1582`
   structured-uncovered, `36` structured solver-failed, and `0`
   default other errors.

3. All default failures are either structured no-go records or covered by the
   reviewed opt-in adapter. No unstructured default error remains in the
   reviewed high-frequency grid.

4. The new adapter is exact, opt-in, and fail-closed:
   `q018_tablei_review_grid_transition`. It is separate from the R60_K2
   `q018_riccati` adapter and the T4x `q018_tablei_km4_transition` adapter.

5. Classification transition records and oracle-validation records match
   exactly: `1618` unique `(k, point_id, ell, sector)` records on both sides,
   with zero extra and zero missing records.

6. The source compressed transition segments also match the measured metadata
   set exactly: `1618` unique records, zero extra and zero missing records.

7. All oracle values are finite and valid at the required radius. Maxima:
   - `max_effective_residual = 8.062852725174548e-16`
   - `max_outer_boundary_residual = 8.062852725174548e-16`
   - `max_normalization_residual = 5.564226404572962e-16`
   - `max_log_derivative_match_residual = 4.1656245120705334e-16`
   - `max_match_condition_number = 4.02684563758389`
   - `max_abs_A_in_minus_one = 0.0`
   - `max_loose_tight_rel_psi = 1.0038374163759307e-07`
   - `max_loose_tight_rel_dpsi_dr = 1.003844364249682e-07`
   - `max_loose_tight_rel_A_out = 1.9562971613732602e-07`

8. Ordinary default-covered modes stay on the normal radial production path
   and carry no `q018_tablei_review_grid_transition_oracle_used` warning.

9. Frozen conventions, thresholds, `lmax`, boundary policy, Q018 policy, and
   Kirchhoff policy were preserved.

10. T4y avoided T8, Kirchhoff outputs, plots, fixtures, dense production, and
    paper-style artifacts.

## Adapter Envelope

New adapter:

```text
q018_tablei_review_grid_transition
```

Allowed envelope:

```text
Schwarzschild M=1
k in {2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0}
required_eval_radius exactly one of the eight Table-I radii at z=30
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
ell/point/sector membership exactly the measured T4y transition set
```

Warning code:

```text
q018_tablei_review_grid_transition_oracle_used
```

Out-of-envelope behavior:

- Unknown opt-in names fail closed.
- Global out-of-envelope parameters reject before oracle use.
- Mode-level adapter membership rejects outside the measured transition set.
- Independent T7bq probe rejected `k=2.5`, `far_axis_x25_z30`, `ell=170` with
  `q018_experimental_oracle_out_of_envelope` and reason
  `mode is outside measured transition set`.
- Ordinary default-covered out-of-transition modes are permitted to solve
  normally and do not use the adapter.

## Metadata Summary

Reviewed files:

```text
runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json
runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json
runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json
runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json
```

Independent metadata checks:

- Stage 1 blocker records T12b's `k=2.5`, `ell=160`, odd-sector
  `evanescent_tail_required_radius_uncovered` at `far_axis_x25_z30`.
- Classification summary has `default_error_other_count = 0`.
- Transition records are exactly all non-default-covered records.
- Oracle records match transition records exactly.
- Oracle records are finite and valid at the required radius.
- Resume preflight reports `adapter_validated=1618`, `failures=0`, and
  `previous_blocker_records_validated=4`.
- Metadata declares radial-only diagnostics only, with no Fig.5/Fig.6
  NPZ/PDF/PNG, Kirchhoff baseline, field grids, or fixtures.

## Checks Run

Required fresh test commands:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Results:

```text
317 passed, 108 warnings, 16 subtests passed in 249.18s
549 passed, 117 skipped, 1 xfailed, 108 warnings, 79 subtests passed in 257.46s
```

Warnings are expected SciPy overflow/invalid warnings from deliberately
exercised fail-closed BVP/bidirectional paths before opt-in adapter use.

Forbidden downstream artifact check:

```bash
find runs/phase5/fig5_fig6_kirchhoff_baseline runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
```

Result: no output.

Additional independent checks:

- Parsed classification/oracle/preflight JSON and compared measured sets.
- Compared source compressed transition segments against metadata transition
  records.
- Probed the private review-grid envelope validator for an out-of-transition
  mode.

## Completed Work

- Read and followed:
  - `docs/prompts/phase5_t7bq_fig5_fig6_review_grid_radial_gate_review.md`
- Read required context:
  - `project.md`
  - `status.md`
  - `docs/codex_instructions.md`
  - `docs/handoffs/README.md`
  - `docs/handoffs/T0_current.md`
  - `docs/handoffs/T4_current.md`
  - `docs/handoffs/T7_current.md`
  - `docs/handoffs/T12b_current.md`
  - `docs/prompts/phase5_t4y_fig5_fig6_review_grid_radial_gate.md`
  - `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
  - T12b/T4y metadata JSON files under `runs/phase5/`
  - `src/schwgw/numerics/radial_solver.py`
  - `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
  - relevant tests under `tests/physics/`, `tests/unit/`, and
    `tests/regression/`
- Checked skills:
  - read/applied `verification-before-completion`.
- Updated:
  - `status.md`
  - `docs/handoffs/T7_current.md`

## Incomplete Work

- T7bq did not start T8 or any autonomous continuation.
- No conservative review-grid NPZ, plots, Kirchhoff baseline, dense scan,
  fixtures, or paper-style candidates were generated.

## Blocking Issues And Warnings

- `q018_tablei_review_grid_transition` is a narrow reviewed adapter for the
  measured Fig.5/Fig.6 review-grid transition set, not a general high-ell
  radial architecture.
- T0 must schedule the next T8 resume prompt explicitly. T7 should not
  silently convert this acceptance into unrestricted dense production.
- Do not hide future radial issues by truncating `ell`, relaxing thresholds,
  skipping modes/points, changing boundary policy, changing Q018 policy, or
  changing frozen conventions.

## Must-Read Files For Next Thread

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T4_current.md`
4. `docs/handoffs/T12b_current.md`
5. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
6. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
7. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
8. `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
9. `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`
10. `src/schwgw/numerics/radial_solver.py`
11. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
12. `tests/physics/test_q018_production_integration_design.py`
13. `tests/physics/test_radial_solver.py`
14. `tests/unit/test_radial_solver.py`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Radial phase convention remains `exp(-i k r_star)` ingoing and
  `exp(+i k r_star)` outgoing.
- `A_in` remains the outer `exp(-i k r_star)` incoming coefficient.
- Route B packaged polarization remains the production path for
  `h_plus/h_cross`.
- Pointwise wave-optics amplification denominator remains the flat/no-lens
  production-compatible polarization field, not Kirchhoff Eq. (47).
- Kirchhoff Eq. (47) is only a scalar comparison baseline.
- Q018 `required_eval_radius` remains fail-closed.
- Existing Wronskian/flux/lmax/near-axis thresholds remain unchanged.

## Forbidden Actions

- Do not start T8 from T7bq alone.
- Do not start dense Fig.5/Fig.6 production without the next explicit T0/T8
  scheduling prompt.
- Do not broaden `q018_tablei_review_grid_transition` beyond its reviewed
  measured envelope without a new implementation/review gate.
- Do not broaden `q018_tablei_km4_transition`; it remains the T4x kM=4
  adapter.
