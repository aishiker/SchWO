# Phase 5 T8ac Prompt: Fig.5/Fig.6 Table-I Read-Only Extraction

You are T8ac: read-only data extraction and CLI/schema implementation for the
Fig.5/Fig.6 Table-I four-frequency pilot.

## Mandatory Context

Before doing anything else, check whether installed plugins or skills are
relevant. Use local project notes and accepted manifests first; no web lookup
or raw PDF read is needed unless local sources conflict.

Read:

- `project.md`
- `status.md`
- `docs/handoffs/README.md`
- `docs/handoffs/T0_current.md`
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
- `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`

## Scope

Implement and run a read-only Table-I extraction from the accepted M5 archive.

Allowed outputs:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

Allowed code/test changes are limited to read-only extraction plumbing, CLI
entrypoint if needed, focused unit/regression tests, `status.md`, and
`docs/handoffs/T8_current.md`.

Do not modify physics convention docs, solver/radial/angular/scattering
formula modules, source M4/M5 artifacts, or existing plot artifacts.

## Forbidden Actions

- Do not run `schwgw run`.
- Do not call or import solver/physics computation paths from the extraction
  helper: `compute_polarization`, `run_solver_grid`, `solve_radial`,
  `compute_pointwise_amplification`, or flat no-lens recomputation.
- Do not interpolate Table-I points.
- Do not generate plots, fixtures, HDF5 files, dense scans, `kM=4` artifacts,
  Kirchhoff baselines, Appendix D/E curves, strict `Psi4`, or arbitrary
  incident-direction outputs.
- Do not fill, clip, smooth, regularize, or replace invalid component ratios.
- Do not describe this pilot as paper-level Fig.5/Fig.6 reproduction.

## Required Extraction

Use the four source files in:

```text
runs/phase5/m5_four_frequency_amplification_artifacts/
```

Frequencies:

```text
kM = [0.5, 1.0, 1.5, 2.0]
```

Table-I points:

```text
near_axis_x0_z30   x=0,  z=30, x_index=60,  z_index=120
near_axis_x1_z30   x=1,  z=30, x_index=62,  z_index=120
near_axis_x2_z30   x=2,  z=30, x_index=64,  z_index=120
near_axis_x3_z30   x=3,  z=30, x_index=66,  z_index=120
far_axis_x10_z30   x=10, z=30, x_index=80,  z_index=120
far_axis_x15_z30   x=15, z=30, x_index=90,  z_index=120
far_axis_x20_z30   x=20, z=30, x_index=100, z_index=120
far_axis_x25_z30   x=25, z=30, x_index=110, z_index=120
```

Verify these indices against each source file's `x` and `z` arrays. Source
ratio arrays are indexed as `[z_index, x_index]`.

## Required NPZ Schema

Use array shape `(frequency, point)` for ratio-like arrays.

Minimum arrays:

```text
kM_values
point_ids
point_group
point_x
point_y
point_z
point_r
point_theta
point_phi
paper_theta_deg
paper_xi_over_xi0
x_indices
z_indices

F_plus_complex
F_cross_complex
abs_F_plus
abs_F_cross
arg_F_plus_principal
arg_F_cross_principal
arg_F_plus_unwrapped
arg_F_cross_unwrapped

valid_ratio_plus_mask
valid_ratio_cross_mask
valid_ratio_norm_mask
valid_field_mask
source_valid_mask
```

Principal phase convention:

```text
angle in (-pi, pi]
```

Unwrap policy:

- unwrap independently along increasing `kM`;
- separately for each point and component;
- do not unwrap across invalid/masked/NaN values;
- four-frequency unwrap is diagnostic only.

## Required JSON Sidecar

Include at least:

```text
case_id = FIG5_FIG6_TABLEI_FOUR_FREQUENCY_READONLY
schema_version
quantity_kind = pointwise_wave_optics_amplification_tablei_four_frequency
normalization_kind = pointwise_wave_optics_amplification
baseline_api = compute_flat_no_lens_polarization
incident_direction = +z
fourier = exp(-i k t)
polarization_bridge = Route B incident-frame electric tidal packaged scalars

source_npz_paths
source_npz_size_bytes
source_npz_sha256
source_case_ids
source_kM_values
source_lmax_values
source_m4_paths
source_m4_size_bytes
source_m4_sha256
source_q018_warning_count
source_q018_warning_codes

point_metadata
frequency_metadata
selected_grid_indices
array_axis_order = ratio_arrays_indexed_as_z_then_x_before_extraction
extraction_array_shape = [frequency, point]

no_interpolation = true
no_solver_rerun = true
no_field_recomputation = true
no_kirchhoff_baseline = true
not_paper_level_dense_scan = true
no_kM4 = true
no_dense_Mk_scan = true
no_new_physics_convention = true
no_plotting = true
```

Record source SHA-256 values from the actual files, not from memory.

## Tests

Add focused tests using temporary small NPZ fixtures to verify exact index
extraction, `[z_index, x_index]` ordering, complex-ratio preservation,
mask/NaN preservation, phase policy, absent-point failure without
interpolation, and sidecar scope flags.

## Required Commands

Run targeted tests you added/changed, then:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run read-only/static checks:

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz src/schwgw/io src/schwgw/cli.py || true
```

If the extraction helper is placed outside `viz/io/cli`, extend the static
search to that file.

## Status And Handoff

Update:

- `status.md`
- `docs/handoffs/T8_current.md`

Record changed files, generated files, files read, commands run, test results,
artifact SHA-256 values, open issues, and exact next action:

```text
你现在是 T7ba。请读取并严格执行 docs/prompts/phase5_t7ba_fig5_fig6_tablei_extraction_review.md。
```

## Decision Label

Use:

- **GREEN / READY FOR T7ba TABLE-I EXTRACTION REVIEW** if extraction, tests,
  sidecar, and artifact provenance are complete.
- **YELLOW / EXTRACTION ARTIFACT NEEDS REVIEW BEFORE USE** if output exists but
  non-blocking metadata or cosmetic schema issues remain.
- **RED / STOP** if exact Table-I extraction cannot be performed without
  interpolation, solver rerun, new physics conventions, or unsupported source
  artifacts.
