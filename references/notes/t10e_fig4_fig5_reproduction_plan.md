# T10e Fig.4/Fig.5/Fig.6 Reproduction Plan

Date: 2026-07-07

Decision label: **GREEN / PLAN READY FOR T7at REVIEW**

Scope: plan the minimal reproducible artifact/schema/plotting path for Li-Hou-Zhao Fig.4 exact angular curves and Fig.5/Fig.6 Table-I point-frequency scans. This note does not run a solver, generate figures, modify `src/`, modify configs, change physics conventions, or authorize new production.

Primary inputs:

- Accepted R60_K2 angular production artifact:
  `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz`
- Accepted M4 Fig.3-style x-z archive:
  `runs/phase4/m4_production_first_pass/`
- Accepted M5 four-frequency pointwise amplification archive:
  `runs/phase5/m5_four_frequency_amplification_artifacts/`
- Planning inventory:
  `references/notes/t10d_li_hou_zhao_figure_inventory.md`

## A. Fig.4 exact angular curves

### A1. What the accepted R60_K2 NPZ supports now

The accepted artifact supports a **single-frequency exact finite-radius angular curve extraction**:

```text
path = runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz
sha256 = 065b2d3dacd5ab8657d0aa8e95fe3ee8b149efd3dd7d1d8b7375ac5df6cfadb2
case_id = R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS
r = 60M
kM = 2
lmax = 180
theta.shape = (65,)
phi.shape = (64,)
h_plus.shape = h_cross.shape = (65,64)
theta = 0..pi with step pi/64, endpoint included
phi = 0..2pi with step 2pi/64, endpoint excluded
```

The fields are production `h_plus` and `h_cross` from the Route B finite-radius electric-tidal packaged-polarization path. The NPZ does **not** contain strict `Psi4`, strict NP scalars, asymptotic amplitudes, phase shifts, or Kirchhoff data.

Accepted convergence evidence:

```text
lmax_values = [108,132,156,180]
final_lmax_pair = [156,180]
final selected max relative change = 2.0272571360273772e-07
final near-axis max relative change = 1.3676928945796113e-09
selected threshold = 1e-4
near-axis threshold = 1e-3
```

Important caveat: the convergence check used an explicit selected `17 x 8 = 136` probe subset, not full `65 x 64` grid convergence.

Q018 provenance:

```text
radial warning count = 56
warning code = q018_required_radius_oracle_used
ell coverage = continuous 153..180
sectors = odd/even
required_eval_radius = 60.0
experimental_required_radius_oracle = q018_riccati
valid_at_required_radius = true
unit_incoming_at_infinity = true
run radial cache unique/key/hit = 358 / 358 / 1644506
```

### A2. What cannot be claimed now

Do not claim:

- all-frequency Fig.4 reproduction;
- `kM=0.5,1.0,1.5` R60 angular coverage;
- `kM=4` readiness;
- R60_K4 readiness;
- arbitrary incident-direction support;
- conventional asymptotic comparison curves from Appendix D/E;
- strict `Psi4` convergence curves for paper Fig.2;
- full-grid `65 x 64` convergence acceptance;
- Kirchhoff baseline or point-frequency Fig.5/Fig.6 reproduction.

The accepted NPZ supports only the exact finite-radius `kM=2` production-polarization angular curves.

### A3. Read-only plotting policy for T8y

The paper Fig.4 is a 1D angular plot against `theta/pi`. The caption/text does not justify averaging over `phi`. Because the project field is stored as `h_plus(theta,phi)` and `h_cross(theta,phi)`, and because `+`/`cross` are tied to the incident-frame polarization basis, a silent `phi` average would hide possible azimuthal structure and is not justified by the local source material.

T8y policy:

```text
primary extraction = fixed phi cut
primary phi = 0.0
theta axis = saved theta array
plotted quantities = abs(h_plus(theta, phi=0)), abs(h_cross(theta, phi=0))
labels = exact finite-radius |h_plus| and |h_cross| at r=60M, kM=2
```

Optional diagnostic for T8y only if kept clearly secondary:

```text
representative phi cuts = [0, pi/2, pi, 3pi/2]
purpose = expose phi dependence, not average it away
```

Minimum accepted T8y plot should be the fixed `phi=0` curve only. It should not average over `phi`, and it should not label either curve as `Psi4`, asymptotic amplitude, scattering amplitude, or conventional Appendix D result.

### A4. Future T8y output names

Future read-only plot outputs should live under:

```text
runs/phase5/q018_r60_k2_angular_production_first_pass/plots/
```

Minimum files:

```text
r60_k2_fig4_exact_phi0_curves.png
r60_k2_fig4_exact_phi0_curves.png.json
```

Optional, if project policy wants a vector format:

```text
r60_k2_fig4_exact_phi0_curves.pdf
r60_k2_fig4_exact_phi0_curves.pdf.json
```

Optional secondary diagnostic, not required for the minimal T8y slice:

```text
r60_k2_fig4_exact_representative_phi_cuts.png
r60_k2_fig4_exact_representative_phi_cuts.png.json
```

No CSV/NPZ/HDF5 should be generated in T8y unless T0 explicitly expands scope. The plot should read from the accepted NPZ only.

### A5. Required plot sidecar fields

The T8y sidecar must include:

```text
plot_type = fig4_exact_angular_curves
source_npz_path
source_npz_sha256
source_npz_size_bytes
source_case_id
source_grid_kind = angular
source_r = 60.0
source_kM = 2.0
source_lmax = 180
field_names = ["h_plus", "h_cross"]
plotted_quantities = ["abs_h_plus", "abs_h_cross"]
curve_extraction_policy = fixed_phi_cut
phi_selected = 0.0
phi_selected_index = 0
theta_count = 65
phi_count = 64
theta_range = {start: 0.0, stop: pi, step: pi/64, endpoint: true}
phi_range = {start: 0.0, stop: 2pi, step: 2pi/64, endpoint: false}
no_phi_average = true
no_solver_rerun = true
no_field_recomputation = true
no_strict_psi4 = true
no_asymptotic_comparison = true
convergence_caveat = selected_17x8_final_pair_only_not_full_grid
final_lmax_pair = [156,180]
final_selected_max_relative_change
final_near_axis_max_relative_change
selected_threshold
near_axis_threshold
q018_oracle_warning_count = 56
q018_oracle_warning_code = q018_required_radius_oracle_used
q018_oracle_ell_range = [153,180]
q018_oracle_ell_count = 28
q018_oracle_sectors = ["even","odd"]
q018_required_eval_radius = 60.0
q018_opt_in = q018_riccati
q018_valid_at_required_radius = true
radial_cache_unique_solution_count = 358
radial_cache_key_count = 358
radial_cache_hit_count = 1644506
created_by_cli
created_at
```

If the workspace remains outside a Git repository, the sidecar should record:

```text
git_commit = null
git_status_available = false
source_code_sha_policy = unavailable_not_git_repository
```

It should still record the source NPZ SHA-256 and, if a plotting config is introduced later, the plotting config SHA-256.

## B. Fig.4 all-frequency extension

This section is a plan only. T10e does not authorize these runs.

Target common setup:

```text
observer kind = angular
r = 60M
theta_range = 0..pi, step pi/64, endpoint true
phi_range = 0..2pi, step 2pi/64, endpoint false
A_plus = 0.9 + 1.1i
A_cross = 0.4 + 0.6i
incident_direction = +z
fields = h_plus, h_cross
```

Recommended lower-frequency artifacts:

| kM | proposed case id | expected output path | initial lmax_values / final-pair strategy | Q018 oracle expected? |
|---:|---|---|---|---|
| 0.5 | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz` | Start from `[36,48,60,72,84]`; require final adjacent pair pass; may stop earlier only if policy explicitly supports adaptive early stop. | No. The reviewed Q018 oracle envelope is `kM=2` only. |
| 1.0 | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz` | Use established R60_K1-style window `[60,72,84,96,108]`; require final adjacent pair pass. | No. |
| 1.5 | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz` | Start from `[84,108,132,156]` or the reviewed production equivalent; require final adjacent pair pass. | No, unless T4/T7 create a separate reviewed envelope. |

Rationale:

- `ell_max ~ k r` gives rough scales `30`, `60`, and `90`, but the project requires adaptive final-pair convergence, not a scalar cutoff assertion.
- The proposed maxima align with previously accepted M4 first-pass final pairs: `[72,84]`, `[96,108]`, and `[132,156]` for `kM=0.5,1.0,1.5`.
- Lower-frequency angular R60 artifacts should not inherit the `kM=2` Q018 opt-in by default. If ordinary radial coverage fails at R60 for any lower-frequency run, stop and return to T4/T7.

Required T4/T7 checks before T8 production:

1. T4 or T8 preflight must ensure the requested boundary config has `required_eval_radius=60.0`.
2. No `experimental_required_radius_oracle` should be used for `kM=0.5,1.0,1.5` unless T4/T7 review a frequency-specific envelope.
3. Selected radial probes should cover the highest proposed `ell` values in odd/even sectors before a long angular production run.
4. T7 must review final adjacent-pair convergence, finite fields, metadata, and any radial warnings.
5. Any run producing warning metadata must serialize JSON-safe warning records and must not silently drop invalid points.

Stop conditions:

- Any `evanescent_tail_required_radius_uncovered` or radial failure at `r=60` without a reviewed opt-in path.
- Final adjacent pair does not pass selected `<1e-4` and near-axis `<1e-3` thresholds.
- Non-finite `h_plus` or `h_cross` at any valid angular point.
- Missing source metadata, boundary metadata, convergence metadata, or warning provenance.
- Any attempt to include `kM=4`, R60_K4, arbitrary incident direction, larger-domain data, asymptotic curves, or Kirchhoff baseline in the same slice.

## C. Fig.5/Fig.6 Table-I point-frequency scans

### C1. Table-I points

Use these points in the x-z plane with `y=0`:

| panel group | x/M | z/M | r/M | theta | phi |
|---|---:|---:|---:|---:|---:|
| near-axis | 0 | 30 | 30.0 | 0.0 | 0.0 by convention |
| near-axis | 1 | 30 | `sqrt(901)` | `atan2(1,30)` | 0.0 |
| near-axis | 2 | 30 | `sqrt(904)` | `atan2(2,30)` | 0.0 |
| near-axis | 3 | 30 | `sqrt(909)` | `atan2(3,30)` | 0.0 |
| far-axis | 10 | 30 | `sqrt(1000)` | `atan2(10,30)` | 0.0 |
| far-axis | 15 | 30 | `sqrt(1125)` | `atan2(15,30)` | 0.0 |
| far-axis | 20 | 30 | `sqrt(1300)` | `atan2(20,30)` | 0.0 |
| far-axis | 25 | 30 | `sqrt(1525)` | `atan2(25,30)` | 0.0 |

The paper also reports `xi/xi0`; store it as metadata for comparison, but do not use it to define the project observer coordinates.

### C2. Minimal exact scan artifact schema

Future exact project finite-radius ratio scans should use a dedicated point-frequency schema, not an image-grid plot schema. Minimum fields:

```text
case_id
schema_version
quantity_kind = pointwise_wave_optics_amplification_scan
normalization_kind = pointwise_wave_optics_amplification
baseline_api = compute_flat_no_lens_polarization
incident_direction = +z
fourier = exp(-i k t)
A_plus
A_cross
points:
  point_id
  group = near_axis or far_axis
  x
  y = 0
  z
  r = sqrt(x^2 + z^2)
  theta = atan2(abs(x), z)
  phi = 0 for x >= 0; explicit convention at x=0
  paper_theta_deg
  paper_xi_over_xi0
frequencies:
  kM_values
arrays:
  F_plus_complex[frequency, point]
  F_cross_complex[frequency, point]
  abs_F_plus[frequency, point]
  abs_F_cross[frequency, point]
  arg_F_plus_principal[frequency, point]
  arg_F_cross_principal[frequency, point]
  arg_F_plus_unwrapped[frequency, point]
  arg_F_cross_unwrapped[frequency, point]
masks:
  valid_ratio_plus_mask[frequency, point]
  valid_ratio_cross_mask[frequency, point]
  valid_ratio_norm_mask[frequency, point]
  valid_field_mask[frequency, point]
metadata_per_frequency_point:
  lmax
  lmax_values
  final_lmax_pair
  selected_max_relative_change
  near_axis_max_relative_change
  radial_warning_count
  radial_warning_codes
  q018_required_eval_radius
  q018_oracle_name_or_null
  radial_cache_key_or_mode_count_summary
  max_boundary_residual
  max_wronskian_residual
  nonfinite_reason_or_null
source:
  config_path
  config_sha256
  source_command
  source_npz_paths_or_per_frequency_artifact_paths
  source_npz_sha256
  source_code_git_commit_or_null
  source_code_status_available
  relevant_source_file_hashes_if_no_git
```

### C3. Phase policy

Store both principal and unwrapped phases:

```text
arg_F_principal = angle(F) in (-pi, pi]
arg_F_unwrapped = unwrap(arg_F_principal along increasing kM)
```

Unwrapping policy:

- unwrap independently for each point and component;
- sort by increasing `kM` before unwrapping;
- do not unwrap across invalid or masked entries;
- restart unwrapping after any NaN/mask gap;
- store the mask used for each unwrapped segment;
- record the units as radians;
- preserve complex `F_plus_complex` and `F_cross_complex` as authoritative.

Plotting must not recompute phases from magnitudes or summaries. The exact complex ratio is the source.

### C4. Masks and NaN policy

Use the accepted M5 policy:

- `F_plus_complex = h_plus_lensed / h_plus_unlensed`;
- `F_cross_complex = h_cross_lensed / h_cross_unlensed`;
- component masks are independent;
- invalid denominators produce NaN/masked values;
- invalid ratios are not zero-filled, one-filled, clipped, floored, or regularized;
- `F_pol_norm`/intensity summaries may be derived separately but must not replace component ratios.

### C5. Three separate scopes

#### Scope 1: currently available four-frequency archive

Available now:

```text
kM = [0.5,1.0,1.5,2.0]
x/M,z/M in [-30,30]
dx=dz=0.5M
accepted M5 archive = runs/phase5/m5_four_frequency_amplification_artifacts/
```

The Table-I points lie on this grid. A future read-only extraction can report sparse four-frequency values for these eight points from the existing M5 archive. This is useful as a schema/provenance pilot, but it is not a paper-level Fig.5/Fig.6 reproduction because:

- the paper curves scan `Mk` continuously up to about `4`;
- `kM=4` is not authorized;
- no Kirchhoff baseline is included;
- no phase-unwrapped panel has been reviewed for Table-I scans.

#### Scope 2: dense `Mk` scan up to `4.0`

Dense Fig.5/Fig.6 reproduction requires a separate production plan:

- explicit frequency grid, likely covering `0.1 <= kM <= 4.0`;
- per-frequency adaptive `lmax` strategy;
- per-frequency radial coverage checks;
- `kM=4` gate and likely Q018/radial stress review;
- runtime/storage estimate;
- T4/T7 preflight for any high-frequency/high-ell radial coverage;
- T8 production only after T0 authorization.

Do not infer dense-scan readiness from the accepted four-frequency M5 archive.

#### Scope 3: Kirchhoff Eq. (47) baseline

Kirchhoff comparison is a separate T1/T10 convention-freeze task before implementation. It must freeze:

- `gamma = -2 M k` sign under project `exp(-i k t)`;
- branch convention for `(-gamma)^(-i gamma)`;
- `Gamma(1+i gamma)` implementation;
- Kummer `1F1(-i gamma,1,-i gamma (xi/xi0)^2)` implementation;
- phase convention for plotting `theta_F`;
- whether the same baseline applies identically to plus/cross or is only a scalar/weak-field comparison;
- metadata warning that Kirchhoff is a comparison baseline, not a production denominator.

No T8 implementation should introduce Kirchhoff Eq. (47) until T1/T10 freeze these conventions.

## D. Thread handoff plan

Stage 1: T7at review of this plan.

```text
你现在是 T7at。请读取并严格执行 docs/prompts/phase5_t7at_fig4_fig5_plan_review.md。
```

T7at should check that this note:

- cleanly separates accepted `kM=2` Fig.4 exact plotting from all-frequency data generation;
- does not authorize lower-frequency angular runs;
- does not authorize dense Fig.5/Fig.6 scans;
- does not implement or authorize Kirchhoff Eq. (47);
- records the selected-subset convergence caveat;
- keeps Q018 R60_K2 provenance scoped to the accepted NPZ.

Stage 2: if T7at returns GREEN, T8y read-only Fig.4 exact `kM=2` plot.

Allowed T8y scope:

- read only `r60_k2_q018_angular_production_first_pass.npz`;
- produce only plot files and JSON sidecars under the `plots/` subdirectory;
- fixed `phi=0` extraction;
- `|h_plus|` and `|h_cross|` vs `theta/pi`;
- no solver calls;
- no field recomputation;
- no strict `Psi4`;
- no asymptotic comparison;
- no lower-frequency artifacts;
- no Fig.5/Fig.6 extraction.

Stage 3: T7au review of T8y plot sidecars and source-boundary checks.

T7au should verify:

- source NPZ SHA and case id match accepted T7as artifact;
- no solver/scattering/radial imports in plotting path;
- sidecar records fixed-phi extraction and selected-subset convergence caveat;
- plot labels do not claim strict `Psi4`, asymptotic amplitudes, or all-frequency reproduction.

Stage 4: only after T7au, T0 decides next direction.

Options:

1. Lower-frequency Fig.4 exact angular data generation.
2. Read-only Table-I sparse four-frequency extraction from the accepted M5 archive.
3. Separate dense Fig.5/Fig.6 scan planning.
4. T1/T10 Kirchhoff Eq. (47) convention freeze.

These options should not be bundled unless T0 explicitly creates a combined plan with separate acceptance gates.

## Open issues

- Accepted R60_K2 Fig.4 plot will be based on `h_plus/h_cross`, not strict `Psi4`.
- Full Fig.4 all-frequency exact reproduction still needs `kM=0.5,1.0,1.5` angular artifacts.
- Conventional asymptotic comparison curves require a separate Appendix D/E diagnostic path.
- Dense Fig.5/Fig.6 reproduction requires a separate `kM=4` gate.
- Kirchhoff Eq. (47) branch and phase conventions are not frozen.
- Workspace-level Git metadata is unavailable in this project root, so future sidecars should record source/config hashes and explicitly mark git commit unavailable unless repository context changes.
