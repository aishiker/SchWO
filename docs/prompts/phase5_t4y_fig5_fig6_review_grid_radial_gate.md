# Phase 5 T4y Prompt: Fig.5/Fig.6 Review-Grid Radial Gate

You are T4y: focused radial-method gate for the Fig.5/Fig.6 conservative
review-grid after T12b stopped at `kM=2.5`, `ell=160`.

Use Goal mode only if helpful; otherwise execute the staged task directly and
stop at the first hard gate.

## Objective

Resolve or classify the T12b Stage 1 radial blocker without weakening any
physics/numerics policy:

```text
kM=2.5
ell=160
sector=odd first, then odd/even
Table-I required radii up to r=39.05124837953327
error=evanescent_tail_required_radius_uncovered / BVP+fallback failure
```

Do not just patch this single mode.  Measure the review-grid high-frequency
radial coverage needed for the remaining conservative Fig.5/Fig.6 review-grid
frequencies so T8 does not hit one avoidable radial blocker after another.

## Read First

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/handoffs/README.md`
5. `docs/handoffs/T0_current.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T12b_current.md`
9. `docs/prompts/phase5_t12b_fig5_fig6_after_adapter_goal.md`
10. `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`
11. `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
12. `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
13. `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`
14. `docs/q018_rescaled_radial_architecture_spike.md`
15. `references/notes/q018_spin2_tail_bound.md`
16. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`
17. `src/schwgw/numerics/radial_solver.py`
18. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
19. relevant tests under `tests/physics/`, `tests/unit/`, and `tests/regression/`.

Before editing, check installed plugins/skills. Use `systematic-debugging` for
the blocker, `test-driven-development` for code changes, and
`verification-before-completion` before claiming any pass.

## Hard Rules

- Do not lower `lmax`, skip modes, skip points, relax tolerances, or change
  convergence thresholds.
- Do not broaden the already-reviewed `q018_tablei_km4_transition` envelope.
- If a new opt-in adapter is needed, give it a separate explicit name.
- Do not use Kirchhoff Eq. (47) as denominator, correction, mask, or
  normalization.
- Do not start T8, produce Fig.5/Fig.6 NPZ/PDF/PNG artifacts, or generate
  Kirchhoff baselines.
- Preserve frozen Fourier, radial phase, harmonic, tetrad, Route B,
  RW/Zerilli, Q014/Q015/Q018, and boundary conventions.
- If an error is genuine no-go, keep it fail-closed and report YELLOW.

## Stage A: Reproduce T12b Blocker

Reproduce the recorded blocker:

```text
k=2.5
ell=160
sector=odd/even
required_eval_radius values:
  far_axis_x20_z30 r=sqrt(20^2+30^2)
  far_axis_x25_z30 r=sqrt(25^2+30^2)
r_out=300
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
```

Record:

- error code/type/message;
- valid_until_r if structured;
- barrier action;
- local tail action;
- BVP/fallback failure messages;
- whether the direct rescaled/log-amplitude oracle returns finite values.

## Stage B: Review-Grid Radial Classification

Classify the radial coverage needed for the remaining high-frequency review
grid:

```text
kM = [2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0]
Table-I radii = all eight points at z=30, x=[0,1,2,3,10,15,20,25]
sector = odd/even
lmax policy = the T12b review-grid policy for each kM
```

For each `kM`, classify every mode needed by the review-grid lmax values as:

- default-covered;
- structured `evanescent_tail_required_radius_uncovered`;
- default error other;
- already covered by the existing accepted `q018_tablei_km4_transition`
  adapter, only for `kM=4` and its reviewed envelope.

Write:

```text
runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json
```

Stop YELLOW if any default error other than structured/uncovered appears and
cannot be made structured without changing physics policy.

## Stage C: Direct Oracle Validation For Measured Transition Set

If Stage B produces a measured transition set that is not already covered by a
reviewed adapter, probe the direct Riccati/log-derivative oracle for the exact
set.

The set must be measured from Stage B. Do not assume it is a continuous interval
unless the metadata proves it.

Record for every `kM, required_radius, ell, sector`:

- finite `psi`, `dpsi_dr`, `A_in`, `A_out`;
- `abs(A_in - 1)`;
- outer-boundary residual;
- normalization residual;
- log-derivative match residual;
- match condition number;
- repeat stability for representative boundary modes;
- loose/tight sensitivity if runtime permits.

Write:

```text
runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json
```

Stop YELLOW if any required oracle point is non-finite or fails existing
residual/stability thresholds.

## Stage D: Optional Narrow Review-Grid Adapter

Only if Stages B and C pass, implement a new explicit opt-in adapter for the
measured Fig.5/Fig.6 conservative review-grid transition set.

Use a separate name, for example:

```text
q018_tablei_review_grid_transition
```

The new adapter must be exact and fail-closed:

- allowed frequencies exactly the measured reviewed `kM` values;
- allowed radii exactly the Table-I radii that require the adapter;
- allowed `ell,sector` exactly the measured/validated transition set;
- `M=1`, Schwarzschild only;
- `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`;
- ordinary default-covered modes must remain on the normal production path;
- the existing `q018_tablei_km4_transition` and `q018_riccati` behavior must
  remain unchanged.

Required tests:

- unknown oracle names fail closed;
- out-of-envelope `M`, `k`, radius, tolerances, `ell`, and sector reject;
- old `q018_tablei_km4_transition` tests still pass unchanged;
- old `q018_riccati` R60_K2 tests still pass unchanged;
- in-envelope review-grid transition modes return finite required-radius
  values with warning metadata naming the new adapter;
- default-covered modes do not call the adapter.

## Stage E: Radial-Only Resume Preflight

Do not run T8.  Do run a radial-only preflight showing whether the T12b
review-grid scan can now get past the previous `kM=2.5`, `ell=160` blocker
for all eight Table-I radii and the remaining review-grid frequencies covered
by this gate.

Write:

```text
runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json
```

## Verification

At minimum run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/physics/test_q018_production_integration_design.py tests/unit/test_radial_solver.py
```

If source/tests changed, run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Required Outputs

Create/update:

- `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
- `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
- `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
- `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
- `docs/handoffs/T4_current.md`
- `status.md`

## Decision Labels

Use exactly one:

```text
GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE READY FOR T7 REVIEW
YELLOW / FIG5-FIG6 REVIEW-GRID RADIAL GATE PARTIAL
RED / FIG5-FIG6 REVIEW-GRID RADIAL METHOD UNSOUND
```

GREEN requires:

- T12b blocker reproduced;
- remaining review-grid high-frequency radial classification completed;
- no unstructured default errors remain;
- all measured transition points validated by oracle or proven covered;
- any new adapter is exact, opt-in, tested, and separate from older envelopes;
- no T8/Kirchhoff/plot/dense artifact generation;
- required tests pass.

