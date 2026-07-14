# Phase 5 T7ba Prompt: Fig.5/Fig.6 Table-I Extraction Review

You are T7ba: independent validation/review for the T8ac read-only Table-I
extraction artifact.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are
relevant. This is a review task; use local project notes, manifests, sidecars,
and source NPZ metadata first.

Read:

- `project.md`
- `status.md`
- `docs/handoffs/README.md`
- `docs/handoffs/T0_current.md`
- `docs/handoffs/T8_current.md`
- `docs/physics_spec.md`
- `docs/equation_map.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `docs/phase5_m5_four_frequency_closeout.md`
- `docs/phase5_fig4_exact_angular_closeout.md`
- `references/manifest.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
- `docs/prompts/phase5_t8ac_fig5_fig6_tablei_readonly_extraction.md`
- `docs/prompts/phase5_t7ba_fig5_fig6_tablei_extraction_review.md`
- `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`

## Scope

Review only the T8ac extraction implementation and generated artifacts.

Expected generated files:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

You may update only:

- `status.md`
- `docs/handoffs/T7_current.md`

Do not modify code, tests, configs, source artifacts, extraction artifacts, or
plots during review.

## Review Checklist

Verify:

- Exactly the expected extraction NPZ and JSON sidecar exist in the output
  directory.
- No plots, fixtures, HDF5 files, dense scans, `kM=4` artifacts, Kirchhoff
  baseline files, or solver outputs were created.
- Source NPZ SHA-256 values in the sidecar match the accepted M5 source files.
- Extracted `F_plus_complex` and `F_cross_complex` values equal the source NPZ
  values at `[z_index, x_index]` for all four frequencies and eight points.
- `x_indices`, `z_indices`, point coordinates, derived `r/theta/phi`, paper
  `theta_deg`, and paper `xi_over_xi0` match T10f.
- Masks are preserved and invalid entries, if any, are NaN/masked rather than
  filled or clipped.
- Principal phases and unwrapped phases follow the T10f policy.
- Sidecar records `no_interpolation`, `no_solver_rerun`,
  `no_field_recomputation`, `no_kirchhoff_baseline`,
  `not_paper_level_dense_scan`, `no_kM4`, `no_dense_Mk_scan`,
  `no_new_physics_convention`, and `no_plotting`.
- Extraction code path does not import/call solver/scattering/radial/baseline
  recomputation functions.
- T8ac updated `docs/handoffs/T8_current.md`.

## Required Independent Checks

Run read-only checks:

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz src/schwgw/io src/schwgw/cli.py || true
```

Write and run a read-only Python inspection script inline to compare extracted
values against the four source NPZ files. Do not write output files.

If T8ac changed code/tests, run targeted tests for the changed extraction path
and then:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR FIG.5/FIG.6 TABLE-I FOUR-FREQUENCY EXTRACTION ONLY**
  - The artifact is correct for the narrow read-only four-frequency Table-I
    pilot and safe for T0 closeout or later plotting/reporting planning.
- **ACCEPT YELLOW / EXTRACTION USABLE WITH RECORDED CAVEATS**
  - Numerical values match, but metadata, handoff, or nonblocking provenance
    needs correction before closeout.
- **REJECT RED**
  - Values do not match source NPZs, source provenance is wrong, interpolation
    or solver rerun occurred, unsupported artifacts were created, or the result
    claims paper-level Fig.5/Fig.6 reproduction.

## Status And Handoff

Update:

- `status.md`
- `docs/handoffs/T7_current.md`

Record files read, commands run and results, decision label, changed files,
artifact hashes, remaining gates, and exact next action for T0.

If GREEN, recommend:

```text
T0 may close out the four-frequency Table-I extraction pilot or schedule a separate read-only plotting/reporting-planning slice. Do not schedule dense Mk scan, kM=4, Kirchhoff baseline, or paper-level Fig.5/Fig.6 reproduction without a new gate.
```
