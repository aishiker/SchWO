# Phase 5 T7bc Prompt: Table-I Plotting/Reporting Review

You are T7bc: independent validation/review for the T8ad read-only Table-I plotting/reporting pilot.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are relevant. This is a review task; use local project notes, closeouts, handoffs, sidecars, and artifacts first.

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
- `docs/prompts/phase5_t7bc_tablei_plotting_reporting_review.md`
- accepted Table-I extraction NPZ/JSON;
- T8ad reporting outputs under `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/`.

## Scope

Review only T8ad's read-only plotting/reporting implementation and generated reporting artifacts.

You may update only:

- `status.md`
- `docs/handoffs/T7_current.md`

Do not modify code, tests, configs, source artifacts, extraction artifacts, reporting artifacts, plots, or `runs/` during review.

## Review Checklist

Verify:

- The reporting directory contains exactly the expected CSV, Markdown, two PNGs, and two JSON sidecars.
- The sidecars source the accepted Table-I extraction NPZ/JSON by path, size, and SHA.
- CSV and Markdown values match the accepted extraction NPZ values for all four frequencies and eight points.
- PNG sidecars record plotted quantities, point IDs, phase policy, mask policy, and all no-solver/no-dense/no-Kirchhoff flags.
- PNGs are nonblank and have stable dimensions.
- Plot labels say four-frequency read-only pilot and do not claim paper-level Fig.5/Fig.6 reproduction.
- No Kirchhoff, `kM=4`, dense scan, interpolation, smoothing, filling, clipping, fixtures, HDF5, strict `Psi4`, or arbitrary-direction artifacts were introduced.
- New plotting/reporting code path has no solver/scattering/radial/baseline recomputation calls.
- T8ad updated `docs/handoffs/T8_current.md`.

## Required Commands

Run:

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/*
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz src/schwgw/io src/schwgw/cli.py || true
```

Write and run a read-only Python inspection script inline to:

- load accepted extraction NPZ;
- parse CSV/Markdown or at least CSV;
- verify numeric values match the accepted extraction arrays;
- inspect PNG dimensions and pixel variation;
- verify sidecar source hashes and scope flags.

If T8ad changed code/tests, run targeted tests for the changed path and full pytest:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Decision Labels

Use:

- **ACCEPT GREEN FOR TABLE-I FOUR-FREQUENCY READ-ONLY PLOTTING/REPORTING ONLY**
  - The reporting artifacts are correct for the narrow pilot scope.
- **ACCEPT YELLOW / REPORTING USABLE WITH RECORDED CAVEATS**
  - Numerical data match but sidecar/cosmetic metadata needs follow-up.
- **REJECT RED**
  - Values mismatch, source provenance is wrong, forbidden computation occurred, or outputs claim dense/paper-level reproduction.

## Status And Handoff

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

Record files read, commands run, test results, artifact hashes, decision label, remaining gates, and exact next action for T0.

If GREEN, recommend:

```text
T0 may close out the Table-I four-frequency plotting/reporting pilot, or separately schedule dense Mk scan planning, Kirchhoff convention freeze, or pause. Do not schedule kM=4, dense scan production, Kirchhoff implementation, fixtures, or paper-level Fig.5/Fig.6 reproduction without a new gate.
```
