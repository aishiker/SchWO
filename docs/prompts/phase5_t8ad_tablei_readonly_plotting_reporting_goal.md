# Phase 5 T8ad Goal Prompt: Table-I Read-Only Plotting/Reporting

You are T8ad. Use Codex Goal mode for this task.

Goal objective:

```text
Produce a read-only plotting/reporting pilot from the accepted Fig.5/Fig.6 Table-I four-frequency extraction artifact, with tests, sidecars, hashes, status update, and T8 handoff, without running physics solvers or expanding scope.
```

Continue autonomously until the definition of done is met or a stop condition below is triggered. Do not stop after only planning unless a stop condition applies.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are relevant. For visualization, use any available plotting/scientific-visualization skill if applicable. Use local project notes, closeouts, sidecars, and accepted artifacts first.

Read:

- `project.md`
- `status.md`
- `docs/handoffs/README.md`
- `docs/handoffs/T0_current.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/T8_current.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `docs/phase5_m5_four_frequency_closeout.md`
- `docs/phase5_fig4_exact_angular_closeout.md`
- `docs/phase5_tablei_extraction_closeout.md`
- `references/manifest.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
- `docs/prompts/phase5_t8ad_tablei_readonly_plotting_reporting_goal.md`
- `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz`
- `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json`

## Scope

Create a read-only plotting/reporting pilot from the accepted Table-I extraction artifact.

Allowed output directory:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/
```

Required generated artifacts:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.csv
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.md
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png.json
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png.json
```

Allowed code/test changes:

- plotting/reporting helper under `src/schwgw/viz/` or a small focused helper under `src/schwgw/io/`;
- export update if needed;
- CLI command if useful, e.g. `plot-tablei-four-frequency`;
- focused unit/regression tests;
- `status.md`;
- `docs/handoffs/T8_current.md`.

Forbidden changes:

- physics convention docs;
- solver, radial, angular, scattering formula modules;
- source M4/M5 artifacts;
- accepted Table-I extraction NPZ/JSON;
- fixtures;
- dense scan configs;
- `runs/` outside the reporting output directory above.

## Plot/Report Requirements

Use only the accepted extraction NPZ/JSON. Do not read source M4/M5 fields directly except for optional SHA verification.

Report files:

- CSV with one row per `(kM, point_id)` and columns for coordinates, masks, `F_plus_complex` real/imag, `F_cross_complex` real/imag, magnitudes, principal phases, and unwrapped diagnostic phases.
- Markdown summary table split into near-axis and far-axis groups.

Plots:

- `fig5_near_axis_tablei_four_frequency_pilot.png`: near-axis points only.
- `fig6_far_axis_tablei_four_frequency_pilot.png`: far-axis points only.
- Each PNG should show a compact pilot version of amplitude and phase versus `kM`.
- Plot both plus and cross components without hiding either component.
- Label clearly as a four-frequency read-only pilot.
- Do not label as paper-level Fig.5/Fig.6 reproduction.
- Do not include Kirchhoff dashed curves.
- Do not mention `kM=4`.

Sidecars must include:

- source extraction NPZ path, size, and SHA-256;
- source extraction JSON sidecar path, size, and SHA-256;
- output CSV/Markdown/PNG path, size, and SHA-256;
- plotted point IDs and groups;
- plotted quantities;
- phase policy;
- mask policy;
- `no_solver_rerun=true`;
- `no_field_recomputation=true`;
- `no_interpolation=true`;
- `no_kirchhoff_baseline=true`;
- `not_paper_level_dense_scan=true`;
- `no_kM4=true`;
- `no_dense_Mk_scan=true`;
- `no_new_physics_convention=true`;
- `read_only_from_tablei_extraction=true`.

## Forbidden Actions

- Do not run `schwgw run`.
- Do not call/import `compute_polarization`, `run_solver_grid`, `solve_radial`, `compute_pointwise_amplification`, or flat no-lens baseline recomputation from the new plotting/reporting path.
- Do not interpolate or smooth values.
- Do not fill, clip, floor, regularize, or replace invalid component ratios.
- Do not generate fixtures, HDF5 files, dense scans, `kM=4` artifacts, R60_K4 artifacts, Kirchhoff baseline, Appendix D/E curves, strict `Psi4`, arbitrary-direction outputs, or paper-level Fig.5/Fig.6 reproduction.

## Stop Conditions

Stop and record a RED/YELLOW status if any of these occur:

- `docs/phase5_tablei_extraction_closeout.md` is missing.
- Accepted extraction NPZ/JSON are missing or their SHA-256 values differ from the closeout.
- Plotting/reporting would require solver rerun, field recomputation, interpolation, dense frequency generation, `kM=4`, or Kirchhoff formulas.
- Sidecar metadata conflicts with the accepted closeout.
- The same test failure remains after three focused fix attempts.
- Full pytest fails due to changes in this slice and cannot be fixed without leaving scope.
- Any required output cannot be generated inside the allowed reporting directory.

## Verification

Run focused tests for the new helper/CLI, then full pytest:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run artifact checks:

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/*
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz src/schwgw/io src/schwgw/cli.py || true
```

Inspect PNGs programmatically for nonblank dimensions and nonzero pixel variation. If using matplotlib, keep plots deterministic.

## Status And Handoff

Update:

- `status.md`
- `docs/handoffs/T8_current.md`

Record:

- changed files;
- generated files;
- files read;
- commands run and results;
- artifact hashes;
- test results;
- open issues and remaining gates;
- exact next action:

```text
你现在是 T7bc。请读取并严格执行 docs/prompts/phase5_t7bc_tablei_plotting_reporting_review.md。
```

## Decision Labels

Use:

- **GREEN / READY FOR T7bc TABLE-I PLOTTING-REPORTING REVIEW**
  - All required reporting artifacts, tests, sidecars, and handoff are complete.
- **YELLOW / PLOTTING-REPORTING PILOT NEEDS REVIEW WITH CAVEATS**
  - Outputs exist but nonblocking metadata/cosmetic issues remain.
- **RED / STOP**
  - Scope boundary is violated or required outputs cannot be produced safely.
