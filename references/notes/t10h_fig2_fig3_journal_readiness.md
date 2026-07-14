# T10h Fig.2 / Fig.3 Journal-Grade Readiness Audit

Date: 2026-07-08

Thread: T10h, literature / numerical-method planning support.

Status label: **YELLOW / FIG2 NOT READY; FIG3 PRODUCTION FIRST PASS ACCEPTED BUT NOT FINAL JOURNAL-GRADE**

Scope: audit and planning only.  No solver was run, no source/test/config file
was modified, no plot was generated, and no new artifact was created.

## 1. Bottom-Line Readiness

| Figure | Current readiness | Decision |
|---|---|---|
| Fig.2 strict `Psi4` partial-wave convergence | Not paper-level.  The project has convergence metadata for packaged observables and angular fields, but it does not yet have a reviewed strict/paper `Psi4` convergence-output path. | **RED for paper-level Fig.2** |
| Fig.3 plus/cross x-z wavefield | Accepted as M4-production first pass for `kM=[0.5,1.0,1.5,2.0]`, `[-30,30]^2`, `dx=dz=0.5M`, `121x121`, nearest, 300 DPI.  It is a valid Fig.3-style production artifact, but it is not final journal-grade if the target is publication polish or saved-data resolution convergence. | **YELLOW for final journal-grade Fig.3** |

Interpretation:

- Fig.2 still needs T6/T1 convention/API work before T8 should generate data.
- Fig.3 is scientifically usable within its closed scope, but a journal-grade
  claim should add either a resolution-refinement study or a reviewed decision
  that `dx=0.5M` is intentionally the final saved-data resolution.

## 2. Evidence Read

Required project sources:

- `project.md`
- `status.md`
- `docs/phase4_production_closeout.md`
- `docs/m4_production_plan.md`
- `docs/validation_plan.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`

Additional read-only context used for estimates:

- `docs/handoffs/T10_current.md`
- `runs/phase4/m4_production_first_pass/manifest.md`
- local archive listing under `runs/phase4/m4_production_first_pass/`
- `src/` / docs text search for strict `Psi4`, strict NP, and convergence labels

## 3. Fig.2 Readiness: Strict `Psi4` Convergence

### 3.1 What Paper Fig.2 Requires

From the figure inventory, Fig.2 is a validation / angular-convergence figure:

- observer radius `r=60M`;
- frequencies `kM={0.5,1.0,1.5,2.0}`;
- angles `theta={0, pi/6, pi/3, pi/2}` with fixed `phi` convention, likely
  `phi=0` unless the paper states otherwise;
- x-axis is `ell_max`;
- plotted quantity is partial-wave convergence for paper `Psi4`, not packaged
  `h_plus/h_cross`;
- expected plot type is 1D convergence curves vs `ell_max`.

The current project has saved convergence metadata for finite-radius
observables, but those are not automatically the paper's strict `Psi4`
convergence curves.

### 3.2 Missing Convention Gate

The project now enforces strict NP / packaged-polarization separation:

- strict NP scalars are tensor/tetrad contractions;
- packaged `Psi0_pack/Psi4_pack` are tidal-projection containers used for
  `h_plus/h_cross`;
- `polarization_from_weyl(...)` accepts packaged scalars, not raw strict NP
  `Psi0_NP/Psi4_NP`.

Before Fig.2 data generation, T1/T6/T7 must freeze exactly what "paper
`Psi4`" means in the post-Q014 project convention:

1. Is Fig.2 `Psi4` the strict Kinnersley-tetrad scalar before the incident
   tetrad transform?
2. Is it the strict incident-tetrad `Psi4` after
   `transform_strict_np_weyl_to_incident_tetrad(...)`?
3. Does the paper's notation include a normalization or reference field not
   represented by the current saved convergence metadata?
4. What phase/sign convention is plotted under `exp(-i k t)`?
5. What is the reference value in the convergence ratio: final `ell_max`,
   a highest available `ell_max=180`, or an independently converged target?

This is a convention gate, not a plotting issue.  Do not use packaged
`h_plus/h_cross`, `Psi0_pack/Psi4_pack`, or M5 amplification as substitutes.

### 3.3 Missing API

Required future API/data capabilities:

- A public or internal diagnostic function that returns strict NP partial sums
  by `ell_max`, with an explicit frame label such as `kinnersley` or
  `incident`.
- The ability to request strict `Psi4` at fixed `(r,theta,phi)` without
  converting it into packaged polarization.
- A saved-result schema for strict `Psi4` convergence rows:

```text
kM_values
theta_values
phi_value
ellmax_values
strict_psi4_partial_sum[k, theta, ellmax]
strict_psi4_reference[k, theta]
relative_or_absolute_error[k, theta, ellmax]
strict_np_frame
strict_psi4_convention_label
```

- Metadata that records whether all five strict NP scalars were available or
  whether only `Psi4` was accumulated.
- A plotting helper that reads saved strict-`Psi4` data only; it must not call
  the radial solver or packaged-polarization path.

### 3.4 Missing Data

No accepted paper-level Fig.2 dataset currently exists.

Current related assets are not sufficient:

- R60 angular production artifacts validate finite packaged observables and
  angular saved fields, not strict Fig.2 `Psi4` convergence curves.
- Existing `lmax_convergence_history` is not labeled as strict paper `Psi4`.
- Existing Fig.3/M4 x-z artifacts are finite-radius `h_plus/h_cross`
  wavefields, not `Psi4` convergence data.

Minimum future data matrix:

| Axis | Required values |
|---|---|
| `kM` | `0.5, 1.0, 1.5, 2.0` |
| radius | `r=60M` |
| angles | `theta=0, pi/6, pi/3, pi/2`; fixed reviewed `phi` |
| `ellmax` | dense sequence sufficient to reproduce the paper-style x-axis; include all accepted final-pair windows and likely extend/display to `ellmax=180` |
| output | strict `Psi4` partial sum and reference/error per angle/frequency |

Q018 note:

- `kM=2`, `r=60M`, high-ell modes require the reviewed Q018 opt-in boundary.
- Lower frequencies do not automatically require the same Q018 branch, but
  their strict `Psi4` data still need radial diagnostics and final-pair
  convergence metadata.

### 3.5 Missing Images

Required future image products:

- One paper-style convergence panel set with four frequencies and four angles,
  or an equivalent layout that preserves the paper's information.
- Log-scale convergence axis if matching paper Fig.2.
- Sidecar records for `strict_psi4_convention_label`, `strict_np_frame`,
  `ellmax_values`, reference definition, and no-packaging/no-M5 flags.
- Read-only plotting proof that the plot code consumes saved strict-`Psi4`
  data and does not call solver/scattering code.

### 3.6 Fig.2 Stop Conditions

Stop and return to T1/T6/T7 if:

- the strict `Psi4` frame/convention cannot be frozen;
- any code path silently packages strict NP scalars into polarization before
  producing Fig.2 data;
- `kM=2`, `r=60` triggers uncovered Q018 radial modes;
- final reference value changes materially when the highest `ellmax` is
  extended;
- metadata cannot distinguish strict `Psi4` from packaged `Psi4_pack`.

## 4. Fig.3 Current State

### 4.1 Accepted Scope

The accepted M4-production first pass covers:

- `kM=[0.5,1.0,1.5,2.0]`;
- `x/M,z/M in [-30,30]`;
- `dx=dz=0.5M`;
- grid shape `(121,121)`;
- default `+z` incident direction;
- saved complex `h_plus/h_cross`;
- read-only PNG/PDF multi-frequency panels;
- `requested_dpi=300`;
- interpolation mode `nearest`;
- event-horizon and light-ring overlays;
- final adjacent-pair convergence metadata.

This is a strong Fig.3-style production artifact, and it is already archived
under:

```text
runs/phase4/m4_production_first_pass/
```

### 4.2 Numerical Convergence

Current numerical-convergence evidence is good within the accepted scope:

| `kM` | final pair | cache unique/key/hit | warnings |
|---:|---|---:|---|
| `0.5` | `[72,84]`, pass | `166 / 166 / 2428346` | none |
| `1.0` | `[96,108]`, pass | `214 / 214 / 3132434` | none |
| `1.5` | `[132,156]`, pass | `310 / 310 / 4534634` | none |
| `2.0` | `[156,180]`, pass | `358 / 358 / 5237306` | 56 `evanescent_tail_suppressed` |

For `kM=2`, Q018 coverage is same-domain only:

```text
rmax = sqrt(30^2 + 30^2) = 42.42640687119285 M
min valid_until_r = 42.472089355131786 M
margin = 0.045682483938932705 M
max suppression bound = 1.2994970680433635e-24
```

This validates the current domain, not larger domains and not `kM=4`.

### 4.3 Saved-Data Resolution

At `dx=0.5M`, samples per wavelength are:

| `kM` | samples per wavelength |
|---:|---:|
| `0.5` | `25.1327` |
| `1.0` | `12.5664` |
| `1.5` | `8.3776` |
| `2.0` | `6.2832` |

This is adequate for a first-pass field map, especially because the highest
frequency still has about `2*pi` samples per wavelength.  It is not, by itself,
a saved-data resolution-convergence study.  A final journal-grade claim should
either:

- add a `dx=0.25M` or `dx=0.2M` resolution comparison; or
- explicitly state that `dx=0.5M` is the chosen production resolution and that
  the published figure is a Fig.3-style reproduction rather than a
  pixel-level reference match.

### 4.4 Display Interpolation

Current panel uses `nearest`.

This is good for audit because it exposes the actual saved grid.  It also
means the rendered raster can look blocky at publication scale.  Changing to
bilinear/bicubic interpolation would improve visual smoothness but would not
increase saved-data resolution.  Any smoothed publication rendering must record
the interpolation mode in the sidecar and caption and must not be used as
numerical evidence.

### 4.5 Publication Rendering

Current rendering is already credible:

- PNG: `3360 x 1680`, approximately 300 DPI.
- PDF: one-page vector container with embedded raster heatmaps.
- Source sidecars record color scales, grid spacing, interpolation, overlays,
  final pairs, and conventions.

Remaining publication-level checks are cosmetic / presentation checks, not
new physics:

- panel label consistency with the paper;
- colorbar readability after journal scaling;
- grayscale/color-vision accessibility;
- caption stating `exp(-i k t)`, `G=c=M=1`, `+z` incidence, `real(h_plus)` and
  `real(h_cross)`, horizon mask, and interpolation policy.

## 5. Fig.3 Staged Higher-Resolution Production Plan

Do not jump directly to `dx=0.2M` full four-frequency production.  Use staged
resolution refinement.

### 5.1 Baseline: Current `dx=0.5M`

Known archived sizes:

| `kM` | NPZ size |
|---:|---:|
| `0.5` | `14.634761 MB` |
| `1.0` | `14.577593 MB` |
| `1.5` | `14.810149 MB` |
| `2.0` | `15.142425 MB` |

Total NPZ size is about `59.165 MB`.

Observed T8o runtimes:

| `kM` | runtime |
|---:|---:|
| `0.5` | `425.70 s` |
| `1.0` | `616.32 s` |
| `1.5` | `1063.89 s` |
| `2.0` | `1342.32 s` |

Total observed runtime: `3448.23 s = 0.958 h`.

### 5.2 Stage A: Read-Only Publication Re-Render From Existing Data

Goal: decide how much of the perceived limitation is rendering rather than
saved-data resolution.

Allowed future T8 action:

- read existing accepted `dx=0.5M` NPZ files;
- produce alternative read-only panels, for example nearest and explicitly
  labeled bilinear versions;
- no solver calls;
- no new numerical claim.

T7 should review whether a clean publication layout from existing data is
already acceptable.  If yes, no higher-resolution numerical run is needed.

### 5.3 Stage B: `dx=0.25M` Pilot

Run only `kM=2.0` first, because it is the highest frequency and the only
current Fig.3 frequency with Q018 warnings.

Parameters:

```text
domain = [-30,30]^2
dx = dz = 0.25M
grid = 241 x 241 = 58081 points
point-count scale relative to dx=0.5 = 3.9670
```

Expected samples per wavelength:

| `kM` | samples per wavelength at `dx=0.25M` |
|---:|---:|
| `0.5` | `50.2655` |
| `1.0` | `25.1327` |
| `1.5` | `16.7552` |
| `2.0` | `12.5664` |

Storage estimate from current archive sizes:

```text
single kM=2 NPZ ~= 60 MB
four-frequency NPZ total ~= 235 MB
```

Runtime estimate by point-count scaling from observed T8o:

| `kM` | central estimate |
|---:|---:|
| `0.5` | `28.1 min` |
| `1.0` | `40.7 min` |
| `1.5` | `70.3 min` |
| `2.0` | `88.7 min` |

Four-frequency central estimate: `3.8 h`.

Conservative budget with reruns, metadata inspection, and Q018 review:
`6-8 h`.

Q018 risk:

- Domain `rmax` is unchanged, so the existing same-domain valid-until logic is
  plausibly reusable for `kM=2` if every warning still records
  `valid_until_r > 42.42640687119285M`.
- This is not automatic acceptance.  The `dx=0.25M` artifact must still record
  Q018 warning metadata and T7 must verify it.

Stage-B acceptance should require:

- final adjacent pair still passes;
- valid/invalid mask matches the horizon policy;
- no uncovered Q018 warnings;
- sidecar records `dx=0.25M`, interpolation, final pair, and Q018 summary;
- comparison against `dx=0.5M` on common grid or selected cross-sections shows
  no qualitative change in physical wavefield.

### 5.4 Stage C: `dx=0.2M` Pilot

Run only if Stage B still looks visually insufficient or if T7 wants a stronger
resolution-convergence statement.

Parameters:

```text
domain = [-30,30]^2
dx = dz = 0.2M
grid = 301 x 301 = 90601 points
point-count scale relative to dx=0.5 = 6.1882
```

Expected samples per wavelength:

| `kM` | samples per wavelength at `dx=0.2M` |
|---:|---:|
| `0.5` | `62.8319` |
| `1.0` | `31.4159` |
| `1.5` | `20.9440` |
| `2.0` | `15.7080` |

Storage estimate:

```text
single kM=2 NPZ ~= 94 MB
four-frequency NPZ total ~= 366 MB
```

Runtime estimate by point-count scaling:

| `kM` | central estimate |
|---:|---:|
| `0.5` | `43.9 min` |
| `1.0` | `63.6 min` |
| `1.5` | `109.7 min` |
| `2.0` | `138.4 min` |

Four-frequency central estimate: `5.9 h`.

Conservative budget with reruns and review: `9-12 h`.

Recommendation: do not open a four-frequency `dx=0.2M` run unless the
`dx=0.25M` pilot is accepted but still visually inadequate.

## 6. Four Distinct Concepts

Keep these separate in status, sidecars, and captions:

| Concept | Meaning | Current Fig.3 status |
|---|---|---|
| Numerical convergence | Partial-wave and radial convergence of the computed field at saved points. | Accepted for current `dx=0.5M` scope via final adjacent pairs and Q018 same-domain metadata. |
| Saved-data resolution | Physical sampling of the field on the stored x-z grid. | `dx=0.5M`, `121x121`; not yet refined by `dx=0.25M` or `dx=0.2M`. |
| Display interpolation | How saved cells are rendered into pixels. | `nearest`; honest but potentially blocky.  Smoothing is presentation only. |
| Publication rendering | DPI, layout, labels, color scales, vector/raster export, caption metadata. | 300 DPI PNG/PDF exists; final journal polish still requires layout/colorbar/caption review. |

Do not use publication smoothness as evidence of saved-data resolution.  Do
not use saved-data resolution refinement as a substitute for final adjacent
partial-wave convergence.

## 7. Recommendations By Thread

### T6

For Fig.2:

- Define a strict `Psi4` diagnostic route that returns strict NP partial sums
  without passing through packaged polarization.
- Freeze frame labels and metadata names:
  `strict_np_frame`, `strict_psi4_convention_label`, and reference definition.
- Ensure strict `Psi4` output cannot be confused with `Psi4_pack`.

For Fig.3:

- No new T6 physics is needed for `dx=0.25M` or `dx=0.2M` if the domain and
  frequencies remain `kM<=2` and Route B packaged plus/cross stays unchanged.

### T8

For Fig.2:

- Wait for T6/T7 convention approval before generating strict `Psi4` data.
- Implement saved strict-`Psi4` convergence artifacts and read-only plotting
  only after the convention gate closes.

For Fig.3:

- First produce read-only publication re-renders from accepted `dx=0.5M` data
  if T7 asks for visual polish.
- If higher saved-data resolution is required, run a `kM=2`, `dx=0.25M`
  pilot before any four-frequency refinement.
- Run `dx=0.2M` only after `dx=0.25M` is accepted and still insufficient.

### T7

For Fig.2:

- Review the strict `Psi4` convention before any artifact-generation prompt.
- Reject any result that uses packaged scalars or `h_plus/h_cross` as a proxy.

For Fig.3:

- Decide whether current `dx=0.5M` nearest/300dpi output is sufficient for the
  intended paper claim.
- If not, review the `dx=0.25M` `kM=2` pilot before opening all four
  frequencies.
- Require sidecar evidence for convergence, Q018 coverage, interpolation mode,
  and source hashes.

## 8. Stop Conditions

Stop Fig.2 work if:

- strict `Psi4` convention is ambiguous;
- strict/package labels are missing;
- any plotting code calls solver/scattering instead of reading saved data;
- Q018 fail-closed events appear at `r=60,kM=2`;
- highest-`ellmax` reference is unstable.

Stop Fig.3 high-resolution work if:

- any new grid changes domain or `rmax` without a fresh Q018 check;
- `kM=2` Q018 warnings no longer cover `rmax=42.42640687119285M`;
- final adjacent-pair convergence fails;
- invalid-mask policy changes;
- single-frequency `dx=0.25M` pilot exceeds `3 h` wall time;
- single-frequency `dx=0.2M` pilot exceeds `5 h` wall time;
- four-frequency `dx=0.25M` run is projected above `8 h` without T0/T7
  re-approval;
- four-frequency `dx=0.2M` run is projected above `12 h` without T0/T7
  re-approval;
- sidecars omit spacing, interpolation, final pairs, Q018 warnings, or source
  provenance.

## 9. Suggested Next Tasks

Recommended next review task:

```text
你现在是 T7bf：Fig.2/Fig.3 journal-grade readiness review。请读取 status.md、docs/phase4_production_closeout.md、docs/m4_production_plan.md、references/notes/t10d_li_hou_zhao_figure_inventory.md、references/notes/t10h_fig2_fig3_journal_readiness.md。任务：审查 T10h 对 Fig.2 strict Psi4 gate 与 Fig.3 dx refinement 的结论；决定是否先启动 T6 strict-Psi4 diagnostic design，还是先让 T8 对现有 Fig.3 dx=0.5M 数据做 read-only publication re-render。
```

If T7bf accepts Fig.2 as a priority:

```text
你现在是 T6：strict Psi4 convergence diagnostic design for Li-Hou-Zhao Fig.2。只设计/实现 strict-NP saved diagnostic route，不把 strict Psi4 传入 packaged polarization，不生成 production artifacts；完成后交 T7 review。
```

If T7bf accepts Fig.3 visual refinement as a priority:

```text
你现在是 T8：Fig.3 publication re-render from accepted dx=0.5M artifacts。只读取 runs/phase4/m4_production_first_pass/ 中已接受 NPZ，不运行 solver，不改 physics；输出 nearest 与明确标注 interpolation 的候选 publication panels 和 sidecars，供 T7 review。
```
