# T0 Current Handoff

Date: 2026-07-09

Thread: T0, project coordination and gate scheduling.

## Current Status

T7bq completed independent review of the T4y Fig.5/Fig.6 review-grid radial
gate:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED
```

Meaning:

- T4y reproduced and resolved the T12b `kM=2.5`, `ell=160` radial blocker.
- T4y classified the high-frequency review-grid radial coverage:
  `6156` default-covered, `1582` structured-uncovered, `36` structured
  solver-failed, and `0` default other errors over `7774` records.
- The measured transition set has `1618` records and is exactly covered by the
  new opt-in adapter `q018_tablei_review_grid_transition`.
- T7bq fresh tests passed: focused radial/Q018/unit suite
  `317 passed, 108 warnings, 16 subtests passed`; full suite
  `549 passed, 117 skipped, 1 xfailed, 108 warnings, 79 subtests passed`.
- T0 may now schedule T8 to resume the conservative eight-point review-grid
  data artifact only.

## Current Scheduling Decision

The user plans to replace all threads with new threads.  T0 created:

```text
docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md
docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md
docs/prompts/phase5_new_thread_startup_T0_T10.md
```

The next implementation slice is T8aj.  It may generate only the conservative
review-grid data artifact.  It must not generate Kirchhoff baselines, plots,
40-frequency production scans, fixtures, or paper-style candidates.  T7br then
reviews that data artifact before T0 opens the Kirchhoff/plot stage.

## Exact Next Task

Send T8:

```text
你现在是 T8aj：Fig.5/Fig.6 conservative review-grid data resume 线程。请读取并严格执行 docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md。
```

After T8aj finishes, send T7:

```text
你现在是 T7br：Fig.5/Fig.6 conservative review-grid data independent review 线程。请读取并严格执行 docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md。
```

If replacing all threads, use:

```text
docs/prompts/phase5_new_thread_startup_T0_T10.md
```

## Prompt Files

- `docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md`
- `docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md`
- `docs/prompts/phase5_new_thread_startup_T0_T10.md`

Completed historical prompts that are not current next actions:

- `docs/prompts/phase5_t4y_fig5_fig6_review_grid_radial_gate.md`
- `docs/prompts/phase5_t7bq_fig5_fig6_review_grid_radial_gate_review.md`
- `docs/prompts/phase5_t12b_fig5_fig6_after_adapter_goal.md`
- `docs/prompts/phase5_autonomous_fig5_fig6_pipeline_goal.md`
- `docs/prompts/phase5_t4x_km4_tablei_transition_error_structuring_adapter.md`
- `docs/prompts/phase5_t7bp_km4_tablei_transition_adapter_review.md`
- `docs/prompts/phase5_t1j_kirchhoff_eq47_convention_freeze.md`
- `docs/prompts/phase5_t4v_km4_tablei_radial_q018_preflight.md`
- `docs/prompts/phase5_t7bn_kirchhoff_km4_preflight_batch_review.md`
- `docs/prompts/phase5_t4w_km4_tablei_transition_oracle_probe.md`
- `docs/prompts/phase5_t7bo_km4_transition_oracle_probe_review.md`

## Must-Read Files For Next T0

1. `status.md`
2. `docs/handoffs/T0_current.md`
3. `docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md`
4. `docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md`
5. `docs/prompts/phase5_new_thread_startup_T0_T10.md`
6. `docs/handoffs/T4_current.md`
7. `docs/handoffs/T7_current.md`
8. `docs/handoffs/T8_current.md`
9. `docs/handoffs/T12b_current.md`
10. `docs/phase5_fig5_fig6_review_grid_radial_gate.md`
11. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_radial_classification.json`
12. `runs/phase5/fig5_fig6_radial_gate/t4y_review_grid_oracle_validation.json`
13. `runs/phase5/fig5_fig6_radial_gate/t4y_resume_preflight.json`
14. `references/notes/t10g_fig5_fig6_dense_kirchhoff_readiness_plan.md`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Route B packaged polarization remains production path for physical
  `h_plus/h_cross`.
- Strict NP scalars and packaged polarization scalars remain separated.
- Fig.3 `dx=0.25M` bilinear PNG/PDF is accepted as current paper-draft
  rendering candidate only.
- Kirchhoff Eq. (47) is scalar comparison baseline only, never the production
  denominator.
- Q018 `required_eval_radius` remains fail-closed.
- Existing Wronskian/flux/lmax/near-axis thresholds remain unchanged.

## Forbidden Actions

Without a new T0/T7 gate, do not run or authorize:

- T8 conservative review-grid scan until T4y finishes and T7bq accepts the
  review-grid radial gate; this gate has passed, but T8 remains limited to the
  T8aj conservative review-grid data prompt;
- unrestricted T8 dense Fig.5/Fig.6 production;
- 40-frequency production-like dense scan;
- broadening the `kM=4` production adapter beyond its T7bp-reviewed envelope;
- field maps, plots, fixtures, or NPZ/HDF5 production outputs;
- Kirchhoff implementation or plotting;
- Appendix D/E curves;
- R60_K4;
- Fig.2 strict `Psi4`;
- `dx=0.2M`;
- source/test/convention/threshold/`lmax`/boundary changes outside the
  autonomous pipeline's explicit stage scopes.

## Current Open Issues

- T8aj conservative review-grid data has not run.
- T7br review has not run.
- Final journal-grade acceptance still requires independent review.
- Existing `docs/handoffs/T10_current.md` remains stale relative to T10g/T7be,
  but `status.md` and local notes contain the authoritative decision trail.

## Verification Commands For Current T0 Slice

```bash
test -f docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md
test -f docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md
test -f docs/prompts/phase5_new_thread_startup_T0_T10.md
rg -n "T8aj|T7br|T0-T10|FIG5-FIG6 REVIEW-GRID RADIAL GATE PASSED|q018_tablei_review_grid_transition|conservative review-grid" status.md docs/handoffs/T0_current.md docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md docs/prompts/phase5_t7br_fig5_fig6_review_grid_data_review.md docs/prompts/phase5_new_thread_startup_T0_T10.md
find runs/phase5/fig5_fig6_kirchhoff_baseline runs/phase5/fig5_fig6_review_grid_plots runs/phase5/fig5_fig6_dense_scan_production runs/phase5/fig5_fig6_paper_style_candidates -maxdepth 2 -type f -print 2>/dev/null | sort
find src tests configs runs/phase5 -type f -newer docs/prompts/phase5_t8aj_fig5_fig6_review_grid_resume.md -print | sort
```

## Definition Of Done For This Gate

- T8aj/T7br prompts exist.
- T0-T10 new-thread startup prompt exists.
- `status.md` and T0 handoff point to T8aj first, then T7br.
- Kirchhoff, plotting, 40-frequency production, fixtures, and paper-style
  candidates remain gated.
