# T12b Current Handoff

Date: 2026-07-09

Thread: T12b, Fig.5/Fig.6 pipeline continuation after accepted kM=4 adapter gate.

## Current Status

T12b stopped in Stage 1 with:

```text
YELLOW / FIG5-FIG6 PIPELINE PARTIAL - NEXT GATE IDENTIFIED
```

No Kirchhoff baseline, review-grid diagnostic plots, 40-frequency production-like
scan, or paper-style Fig.5/Fig.6 candidate artifacts were generated.

## Completed Work

- Created Goal mode objective for strict execution of
  `docs/prompts/phase5_t12b_fig5_fig6_after_adapter_goal.md`.
- Read the required project status, handoffs, physics/numerics/validation
  docs, Table-I/Kirchhoff notes, T4x/T7bp adapter evidence, and relevant
  source/tests.
- Used applicable skills:
  - `using-superpowers`
  - `test-driven-development`
  - `systematic-debugging`
  - `verification-before-completion`
  - `scientific-visualization` was read for downstream plotting gates, but
    plotting was not reached.
- Stage 0 passed:
  - Confirmed `ACCEPT GREEN / KM4 TABLE-I TRANSITION ADAPTER GATE PASSED`.
  - Smoked `q018_tablei_km4_transition` at `k=4`, `ell=177`, odd/even,
    `required_eval_radius=39.051248`, `r_out=300`, `r_in_eps=1e-6`,
    `rtol=1e-10`, `atol=1e-12`.
  - Both sectors were finite at the required radius and carried
    `q018_tablei_km4_transition_oracle_used`.
- Stage 1 started the conservative eight-point Table-I review-grid scan:
  - `z/M=30`, `x/M=[0,1,2,3,10,15,20,25]`;
  - pointwise amplification against the flat/no-lens denominator;
  - no Kirchhoff denominator/correction/mask/normalization;
  - accepted lmax seed and anchor policy.
- Frequencies through `kM=2.25` passed final adjacent-pair convergence.

## Blocker

Stage 1 stopped at `kM=2.5`, `L=180`, first failing mode:

```text
k=2.5, ell=160, sector=odd
```

Recorded blocker:

```text
runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json
```

Primary structured error:

```text
evanescent_tail_required_radius_uncovered
```

Key metadata:

```text
required_eval_radius = 39.05124837953327
valid_until_r        = 36.13325252073037
barrier_action       = 705.8410688795467
local_tail_action    = 55.00904923048529
suppression_bound    = 1.2878742634499614e-24
```

A focused retry showed the problem is not limited to the final x=25 point:

- `far_axis_x20_z30`, `ell=160`, odd/even: stabilized BVP failed and
  bidirectional fallback failed.
- `far_axis_x25_z30`, `ell=160`, odd/even: structured
  `evanescent_tail_required_radius_uncovered`.

This is outside the T7bp-reviewed `q018_tablei_km4_transition` envelope. It is
not a final-pair convergence failure, so the prompt's `+24/+48` lmax extension
repair does not apply.

## Frozen Decisions

- Do not broaden `q018_tablei_km4_transition` beyond `k=4`,
  `ell=177..240`, odd/even, and the reviewed Table-I radius envelope.
- Do not lower `lmax`, relax thresholds, skip failed points/modes, or hide
  failed radial solves.
- Do not use Kirchhoff Eq. (47) as denominator, correction, mask, or
  production normalization.
- Do not change frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B,
  Q014/Q015/Q018, boundary, or branch conventions.

## Changed Files And Artifacts

- `status.md`
- `docs/handoffs/T12b_current.md`
- `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`

No `src/`, `tests/`, or `configs/` files were changed.

## Must-Read Files For Next Thread

1. `status.md`
2. `docs/handoffs/T12b_current.md`
3. `docs/prompts/phase5_t12b_fig5_fig6_after_adapter_goal.md`
4. `runs/phase5/fig5_fig6_dense_review_grid/stage1_yellow_error.json`
5. `docs/phase5_km4_tablei_transition_error_structuring_adapter.md`
6. `docs/phase5_km4_tablei_adapter_closeout.md`
7. `runs/phase5/km4_tablei_adapter_validation/t4x_default_classification_metadata.json`
8. `runs/phase5/km4_tablei_adapter_validation/t4x_oracle_validation_metadata.json`
9. `src/schwgw/numerics/radial_solver.py`
10. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
11. `tests/physics/test_radial_solver.py`
12. `tests/physics/test_q018_production_integration_design.py`

## Exact Next Task

Open a focused radial-method gate for the `kM=2.5`, `ell=160`, Table-I
required-radius blocker. Candidate directions are a reviewed target-radius
conservative bound or a rescaled/log-amplitude radial architecture. Do not
continue Fig.5/Fig.6 artifact generation until that gate is resolved.

## Verification Commands And Results

Stage 0 smoke passed for `q018_tablei_km4_transition` at `k=4`, `ell=177`,
odd/even.

Stage 1 scan stopped with the recorded YELLOW blocker after completing
frequencies through `kM=2.25`.

Focused diagnostic command checked `k=2.5`, `ell=160`, x20/x25 Table-I radii,
odd/even. Result: x20 BVP/fallback failure; x25 structured
`evanescent_tail_required_radius_uncovered`.

