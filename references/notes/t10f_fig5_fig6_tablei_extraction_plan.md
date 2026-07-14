# T10f Fig.5/Fig.6 Table-I Extraction Plan

Date: 2026-07-08

Decision label: **GREEN / PLAN READY FOR T7az REVIEW**

Scope: planning-only note for a future read-only extraction of Li-Hou-Zhao Fig.5/Fig.6 Table-I point-frequency values from the already accepted M5 four-frequency amplification archive. This note does not run a solver, does not create extraction artifacts, does not create plots, does not modify code/configs/tests, and does not authorize dense scans, `kM=4`, or Kirchhoff baselines.

Primary local inputs:

- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10e_fig4_fig5_reproduction_plan.md`
- `docs/phase5_m5_four_frequency_closeout.md`
- `runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md`
- read-only metadata inspection of the four existing `*_amplification.npz` files

No raw PDF or web lookup was needed because the local figure inventory already records Table I and the M5 closeout/manifest record the accepted artifact scope.

## Established Result

The existing M5 archive supports a read-only four-frequency Table-I extraction pilot:

```text
archive = runs/phase5/m5_four_frequency_amplification_artifacts/
kM = [0.5, 1.0, 1.5, 2.0]
x/M,z/M in [-30,30]
dx = dz = 0.5M
shape = (121,121)
quantity_kind = pointwise_wave_optics_amplification
```

The authoritative complex ratios are:

```text
F_plus_complex  = h_plus_lensed  / h_plus_unlensed
F_cross_complex = h_cross_lensed / h_cross_unlensed
```

Invalid ratios follow the accepted M5 policy: independent masks, NaN where invalid, and no fill/clip/smooth/regularization/interpolation.

The NPZ inspection found these relevant keys in all four files:

```text
x, z, r, theta, phi, valid_mask
F_plus_complex, F_cross_complex
amplification_plus, amplification_cross
F_pol_norm, I_pol_ratio
valid_ratio_plus_mask, valid_ratio_cross_mask, valid_ratio_norm_mask
metadata_json
```

`x` and `z` are one-dimensional axes of length `121`. Ratio arrays and masks have shape `(121,121)` and should be indexed as `[z_index, x_index]`.

## Three Separate Scopes

### 1. Read-only four-frequency Table-I pilot

Allowed future scope if T0 schedules T8:

- Read only the four accepted M5 amplification NPZ files.
- Extract exactly the eight Table-I points listed below.
- Use exact grid-index selection only.
- Preserve complex ratios as the authoritative values.
- Record source artifact SHA-256, size, source M4 provenance, selected indices, masks, and scope flags.

This is only a schema/provenance pilot. It is not a paper-level reproduction of Fig.5/Fig.6 because it has only four frequencies, no dense `Mk` curves to about `4`, no `kM=4`, and no Kirchhoff dashed baseline.

### 2. Future dense `Mk` scan to about `4`

Not authorized here.

A paper-level Fig.5/Fig.6 exact-dot reproduction requires a separate production plan that defines:

- frequency grid from low `Mk` to about `4`;
- explicit `kM=4` gate;
- adaptive `lmax`/final-pair convergence policy per frequency;
- radial/Q018 preflight for high-frequency and high-ell modes;
- runtime and storage estimate;
- artifact layout and sidecar schema;
- T7 review gates before any dense output is promoted.

The existing four-frequency archive must not be cited as dense-scan readiness.

### 3. Future Kirchhoff baseline

Not authorized here.

Kirchhoff Eq. (47) needs a separate T1/T10 convention freeze before implementation. That review must settle:

- sign of `gamma` under project `exp(-i k t)`;
- branch of `(-gamma)^(-i gamma)`;
- numerical and phase convention for `Gamma(1+i gamma)`;
- Kummer `1F1(-i gamma,1,-i gamma (xi/xi0)^2)` branch/implementation;
- phase convention for plotted `theta_F`;
- whether the scalar Kirchhoff comparison applies identically to packaged `plus/cross` ratios or only as a scalar/eikonal comparison baseline;
- metadata label making Kirchhoff a comparison curve, not the production denominator.

## Table-I Points

Use `y=0`, `phi=0`, and project finite-radius coordinates

```text
r = sqrt(x^2 + z^2)
theta = atan2(abs(x), z)
```

For these positive-`x` points, this agrees with the M5 metadata convention `phi=0 if x>=0 else pi`.

| point_id | group | x/M | y/M | z/M | r/M | theta_rad | theta_deg(project) | paper_theta_deg | paper_xi_over_xi0 | x_index | z_index |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `near_axis_x0_z30` | Fig.5 near-axis | 0 | 0 | 30 | 30 | 0 | 0 | 0 | 0 | 60 | 120 |
| `near_axis_x1_z30` | Fig.5 near-axis | 1 | 0 | 30 | 30.0166620396 | 0.0333209958782 | 1.9091524 | 1.90915 | 0.0913 | 62 | 120 |
| `near_axis_x2_z30` | Fig.5 near-axis | 2 | 0 | 30 | 30.0665927567 | 0.0665681637758 | 3.8140748 | 3.81407 | 0.1828 | 64 | 120 |
| `near_axis_x3_z30` | Fig.5 near-axis | 3 | 0 | 30 | 30.1496268634 | 0.0996686524912 | 5.7105931 | 5.71059 | 0.2745 | 66 | 120 |
| `far_axis_x10_z30` | Fig.6 far-axis | 10 | 0 | 30 | 31.6227766017 | 0.321750554397 | 18.434949 | 18.4349 | 0.9372 | 80 | 120 |
| `far_axis_x15_z30` | Fig.6 far-axis | 15 | 0 | 30 | 33.5410196625 | 0.463647609001 | 26.565051 | 26.5651 | 1.4479 | 90 | 120 |
| `far_axis_x20_z30` | Fig.6 far-axis | 20 | 0 | 30 | 36.0555127546 | 0.588002603548 | 33.690068 | 33.6901 | 2.0015 | 100 | 120 |
| `far_axis_x25_z30` | Fig.6 far-axis | 25 | 0 | 30 | 39.0512483795 | 0.694738276197 | 39.805571 | 39.8056 | 2.6038 | 110 | 120 |

The exact index formula for the current archive is:

```text
x_index = round((x + 30) / 0.5)
z_index = round((z + 30) / 0.5)
```

Future extraction must still verify these indices in every source NPZ rather than assuming the grid.

## Proposed Future Output

Do not create these files in T10f. If T0 schedules a T8 implementation, use:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/
  tablei_four_frequency_amplification_values.npz
  tablei_four_frequency_amplification_values.npz.json
```

Suggested array shape:

```text
frequency_count = 4
point_count = 8
array shape = (frequency, point)
```

Minimum NPZ arrays:

```text
kM_values
point_ids
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

Minimum JSON sidecar fields:

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
```

## Phase Policy

Principal phases:

```text
arg_F_plus_principal  = angle(F_plus_complex)  in (-pi, pi]
arg_F_cross_principal = angle(F_cross_complex) in (-pi, pi]
```

Unwrapped phases:

- Sort by increasing `kM`.
- Unwrap independently for each point and component.
- Do not unwrap across invalid or masked values.
- Restart unwrap after every mask/NaN gap.
- Store unwrapped phases in radians.
- Treat the four-frequency unwrap as diagnostic only; it is too sparse for paper-level phase curves.

The complex arrays remain authoritative. Magnitudes and phases are derived summaries.

## Mask And NaN Policy

Future T8 extraction must carry masks from the M5 archive:

- `valid_ratio_plus_mask` for plus component ratios.
- `valid_ratio_cross_mask` for cross component ratios.
- `valid_ratio_norm_mask` for norm summaries.
- `source_valid_mask` or equivalent field-valid mask for finite saved fields.

Invalid component ratios must be stored as NaN and masked. Do not fill, clip, floor, smooth, regularize, or interpolate invalid values. Do not substitute `F_pol_norm` for a missing component ratio.

## Read-Only Archive Support Check

Read-only NPZ inspection found all eight Table-I points in all four source NPZ files. All selected Table-I entries had:

```text
valid_ratio_plus_mask = true
valid_ratio_cross_mask = true
valid_ratio_norm_mask = true
source valid_mask = true
```

Source amplification NPZs:

| kM | amplification NPZ | size bytes | SHA-256 | source M4 SHA-256 |
|---:|---|---:|---|---|
| 0.5 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k0p5_dx0p5_amplification.npz` | 1607034 | `b0193570c0b0933318fe29493c57640bad7b88cce2a8fcfa47e6a978d5368e99` | `e477100337cebb7f351b2fffa423264b76b25264c1ffb46b13e8cd04da2c98e7` |
| 1.0 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k1p0_dx0p5_amplification.npz` | 1607038 | `26393c18347983a15d51f9cb5a5594493d580e1cea7a78744953c08564cfb1af` | `1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9` |
| 1.5 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k1p5_dx0p5_amplification.npz` | 1607038 | `12268ad66069ad004ed4626d7a0d30da0e89838911cab81d3db442c5e5d27abb` | `1c52852f4820aa09c2f53e456bea6674d0818aaf0d61dbffe223998a793e7c32` |
| 2.0 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k2p0_dx0p5_amplification.npz` | 1607154 | `f225d8cf5bb09d10a4d00034410bcad04af6d4a20ad79c1b8823ded889cdb276` | `a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762` |

## Future T8 Acceptance Gates

A future T8 extraction slice should pass these gates before T7 review:

- Exact Table-I grid indices verified in every source NPZ.
- Source amplification NPZ SHA-256, size, and case id recorded.
- Source M4 path/SHA/size provenance preserved from `metadata_json`.
- Extraction uses saved arrays only; no solver, radial, scattering, baseline, or polarization recomputation imports/calls.
- No interpolation, nearest-neighbor fallback, smoothing, or coordinate snapping beyond exact grid-index verification.
- Complex `F_plus_complex` and `F_cross_complex` preserved.
- Principal and diagnostic unwrapped phases derived from complex ratios only.
- Independent plus/cross/norm masks preserved.
- Sidecar records `no_interpolation`, `no_solver_rerun`, `no_kirchhoff_baseline`, `not_paper_level_dense_scan`, and `no_kM4`.
- Output labels say four-frequency Table-I read-only pilot, not dense Fig.5/Fig.6 reproduction.

## Rejected Options

- Interpolation from nearby grid points: rejected because Table-I points are exactly on the current `dx=0.5M` grid and interpolation would introduce unnecessary convention and provenance ambiguity.
- Recomputing the lensed or unlensed fields: rejected because the pilot is read-only over the accepted M5 archive.
- Plotting only `amplification_plus/amplification_cross`: rejected as the authoritative artifact because these are magnitudes; complex ratios must be preserved for phase analysis.
- Treating four-frequency unwrapped phases as paper-level curves: rejected because four samples are too sparse and do not include the paper's scan to about `Mk=4`.
- Adding Kirchhoff dashed curves in the same slice: rejected because Eq. (47) branch and phase conventions are not frozen.

## Recommendation To T7az

Review this note as a plan boundary, not an implementation. The recommended decision is GREEN if T7az confirms:

- the three scopes are separated;
- all eight points and exact grid indices are recorded;
- complex-ratio schema and mask/phase policies are concrete;
- dense scan, Kirchhoff baseline, and `kM=4` remain gated;
- no result artifact, code, test, config, or plot was created in T10f.

## Exact Next Action

If accepted, T0 should send:

```text
你现在是 T7az。请读取并严格执行 docs/prompts/phase5_t7az_fig5_fig6_tablei_plan_review.md。
```
