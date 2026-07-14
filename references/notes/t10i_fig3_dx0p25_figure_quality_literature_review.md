# T10i Fig.3 dx=0.25M Figure-Quality And Literature Review

Date: 2026-07-09

Thread: T10i, literature / numerical-method support.

Recommendation label: **NEEDS_READONLY_RENDER_POLISH**

Scope: review only.  No solver was run, no production/scattering API was
called, no plot was regenerated, and no accepted artifact was mutated.

## 1. Bottom-Line Decision Recommendation

The accepted archive matches the Li-Hou-Zhao Fig.3 physical content and is
scientifically adequate as a `dx=0.25M` Fig.3 production data archive within
the current project conventions.

The next lowest-risk branch is **read-only publication-style rendering from
the accepted NPZ files**, followed by T7 image review.  A `dx=0.2M` numerical
run is **not justified now** because the current evidence points to rendering,
layout, and caption/sidecar presentation as the remaining limitation, not
saved-data numerical resolution.

This is not a final journal-grade claim.  It is a recommendation to move the
accepted numerical archive into a read-only publication-rendering/polish stage.

## 2. Evidence Read

Required files:

- `project.md`
- `status.md`
- `docs/handoffs/README.md`
- `docs/handoffs/T0_current.md`
- `docs/handoffs/T7_current.md`
- `docs/handoffs/T8_current.md`
- `docs/handoffs/T10_current.md`
- `docs/phase5_fig3_four_frequency_dx0p25_production_closeout.md`
- `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
- `references/manifest.md`
- `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
- `references/notes/t10d_li_hou_zhao_figure_inventory.md`
- `references/notes/t10h_fig2_fig3_journal_readiness.md`

Additional read-only checks:

- Inspected archive-level nearest and bilinear PNG dimensions/DPI.
- Inspected archive-level PNG sidecars for interpolation policy, Q018 summary,
  final-pair status, grid spacing, convention, and non-claim flags.
- Inspected NPZ metadata for `kM`, amplitudes, coordinate ranges, field shapes,
  masks, and final-pair status.
- Used the local `scientific-visualization` skill for publication-figure
  criteria: 300 DPI minimum, readable labels, color/greyscale considerations,
  and multi-panel layout discipline.

Local notes were sufficient.  No PDF reread, external literature tool, or web
lookup was needed.

## 3. Comparison To Li-Hou-Zhao Fig.3

### 3.1 Physical Content Match

The accepted archive corresponds to the Fig.3 physical content recorded in the
local Li-Hou-Zhao notes:

| Required Fig.3 item | Accepted archive evidence |
|---|---|
| Physical plus/cross wavefield | Saved complex `h_plus` and `h_cross`; plots show `real(h_plus)` and `real(h_cross)` |
| Four paper frequencies | `kM=[0.5,1.0,1.5,2.0]` |
| `x/M,z/M in [-30,30]` | NPZ `x` and `z` arrays each have shape `(241,)`, range `[-30,30]` |
| Fig.3-style `60M x 60M` region | Same `[-30,30]^2` region |
| Event horizon and light-ring overlays | Sidecars record overlays drawn with radii `2M` and `3M` |
| Paper amplitudes | NPZ metadata records `A_plus=0.9+1.1i`, `A_cross=0.4+0.6i` |
| Project / paper Fourier convention | Sidecars record `exp(-i k t)` |
| Physical route | Route B / incident-frame electric tidal packaged scalar polarization bridge |

Therefore the archive is correctly scoped as a Fig.3 physical plus/cross
wavefield archive, not an apparent-mode Fig.7 archive and not a strict `Psi4`
Fig.2 archive.

### 3.2 Differences That Remain

Supported comparison:

- "Fig.3-style physical wavefield data with matching main parameters."

Not supported:

- pixel-for-pixel reproduction of the paper raster;
- final journal-grade figure layout;
- exact paper color normalization or typography;
- `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, Fig.5/Fig.6 transmission, or
  Appendix D/E asymptotic outputs.

## 4. Numerical-Resolution Assessment

### 4.1 Saved-Data Grid

The accepted production archive uses:

```text
dx = dz = 0.25M
grid = 241 x 241
valid / invalid = 57884 / 197
domain = [-30,30]^2
```

Samples per wavelength at `dx=0.25M`:

| `kM` | samples per wavelength |
|---:|---:|
| `0.5` | about `50.27` |
| `1.0` | about `25.13` |
| `1.5` | about `16.76` |
| `2.0` | about `12.57` |

These values are comfortably above the current `dx=0.5M` first-pass archive
and leave the highest paper frequency, `kM=2`, with about `4*pi` samples per
wavelength.  Within the present project conventions, this is scientifically
adequate for a Fig.3 production archive.

### 4.2 Partial-Wave / Radial Convergence

All four frequencies have final adjacent pair `[156,180]` passing.  This is
stronger and more uniform than the earlier `dx=0.5M` first-pass archive, where
lower frequencies used smaller final pairs.

Q018 status:

- `kM=0.5,1.0,1.5`: zero-warning structured metadata, covers `rmax`.
- `kM=2.0`: 56 structured warnings with code
  `evanescent_tail_suppressed`, `ell=153..180`, sectors `even/odd`,
  `valid_until_r_min=42.472089355131786`, and margin
  `0.045682483938932705` over `rmax=42.42640687119285`.

This Q018 evidence is same-domain only.  It supports the accepted
`[-30,30]^2` archive, but it must not be generalized to larger domains,
R60/R60_K4, or `kM=4`.

### 4.3 Scientific Adequacy

The numerical-resolution evidence is adequate for the next review step:

- the saved grid resolves the shortest plotted wavelength well;
- final adjacent-pair convergence passed for every frequency;
- radial/Q018 metadata are structured and T7-accepted;
- nearest and bilinear renderings show the same physical stripe pattern, so
  remaining visual roughness is not strong evidence of under-resolved saved
  data.

## 5. Rendering And Layout Assessment

### 5.1 What The Existing Plots Are

The archive contains:

- nearest audit panel: `3360 x 1680`, RGBA, about 300 DPI;
- bilinear display-only panel: `3360 x 1680`, RGBA, about 300 DPI;
- per-frequency nearest and bilinear panels;
- sidecars that explicitly distinguish numerical audit rendering from
  display-only smoothing.

Nearest policy:

- numerical/provenance view;
- exposes the saved grid;
- sidecar has `numerical_evidence_plot=true` and
  `display_only_smoothing=false`.

Bilinear policy:

- display-only smoothing;
- not numerical evidence;
- sidecar has `display_only_smoothing=true` and
  `numerical_evidence_plot=false`.

### 5.2 Visual Roughness Diagnosis

The current visual roughness, if any, is primarily a rendering/layout issue:

- nearest display can look blocky because it intentionally exposes grid cells;
- bilinear display smooths the blockiness without changing the apparent
  physical wave pattern;
- the archive-level panel is an audit plot with compact labels and colorbars,
  not a tuned journal layout;
- panel spacing, typography, colorbar sizing, caption text, and accessibility
  checks remain publication tasks.

There is no local evidence that the `dx=0.25M` saved-data resolution is the
limiting factor for the current Fig.3 archive.

### 5.3 Publication-Style Rendering Requirements

A future T8 read-only rendering pass should:

- read only the accepted NPZ files;
- preserve source SHA/provenance in sidecars;
- produce a publication-layout candidate without solver/scattering calls;
- keep nearest as numerical audit evidence;
- use bilinear or other smoothing only as explicitly labeled display
  interpolation;
- retain event-horizon and light-ring overlays;
- keep axes in `x/M`, `z/M`;
- make panel labels, colorbars, and row labels readable at final print size;
- preserve row-wise symmetric color scales or justify any change;
- include caption/sidecar language stating that interpolation is display-only.

## 6. Is dx=0.2M Justified Now?

No.  A `dx=0.2M` run should remain gated.

Reasons:

- `dx=0.25M` already gives about `12.57` samples per wavelength at the
  highest current Fig.3 frequency `kM=2`.
- All four final adjacent pairs pass.
- The only Q018 warnings are the known same-domain `kM=2` suppressed-tail
  records, and they cover the current domain.
- The nearest/bilinear visual comparison points to display/layout as the
  remaining limitation.
- The current accepted archive already cost about `15928.55 s` solver real
  time, roughly `4.43 h`; `dx=0.2M` would be a new production campaign and is
  not justified without concrete evidence of numerical saved-data deficiency.

`dx=0.2M` planning could become justified only if a read-only publication
rendering review finds a persistent artifact that:

- appears in both nearest and display-smoothed views;
- is tied to saved-grid sampling rather than color scaling/layout;
- cannot be addressed by rendering choices or captioning;
- has a plausible physical/numerical reason to require finer saved-data
  sampling.

## 7. Supported Claims And Non-Claims

### Supported Now

- The accepted archive is a four-frequency `dx=0.25M` Fig.3 physical
  plus/cross production data archive.
- It matches the local Li-Hou-Zhao Fig.3 parameter content:
  `h_plus/h_cross`, `kM=[0.5,1.0,1.5,2.0]`, `[-30,30]^2`, paper amplitudes,
  and horizon/light-ring overlays.
- `dx=0.25M` saved-data resolution is scientifically adequate for current
  Fig.3 production evidence.
- Nearest is the audit plot; bilinear is display-only smoothing.
- The next lowest-risk branch is read-only publication-style rendering.

### Explicit Non-Claims

- not final journal-grade readiness;
- not paper-level / pixel-level reproduction;
- not `dx=0.2M`;
- not `kM=4`;
- not R60/R60_K4 or larger-domain readiness;
- not Fig.2 strict `Psi4`;
- not fixtures;
- not dense Fig.5/Fig.6;
- not Kirchhoff or Appendix D/E;
- not a frozen change to physics conventions, thresholds, `lmax`, or boundary
  policy.

## 8. Allowed Next Branch

Recommended next prompt:

```text
你现在是 T7bl。请读取并严格执行 docs/prompts/phase5_t7bl_fig3_dx0p25_figure_quality_review.md。
```

If T7bl agrees with this note, the next execution branch should be T8
read-only publication rendering from the accepted NPZ archive, followed by a
T7 image review.

That T8 branch should not:

- run the solver;
- regenerate accepted archive artifacts in place;
- modify accepted NPZ/run JSON/manifest files;
- claim final journal-grade status by itself;
- start `dx=0.2M`.

## 9. Hard Stops And Open Risks

Hard stops:

- any source/test/config or accepted-artifact mutation in a review-only task;
- any hidden solver/scattering call during figure-quality review;
- any proposal to use bilinear smoothing as numerical evidence;
- any missing sidecar provenance for a future publication-rendering candidate;
- any attempt to generalize Q018 beyond the accepted same-domain archive;
- any claim of final journal-grade readiness before T7bl and subsequent
  read-only rendering review.

Open risks:

- The project has not yet produced the final publication-style figure layout.
- Color scale and typography may still need journal-specific adjustment.
- The sidecars currently carry the correct non-claim flags; a future rendering
  pass must decide which claim flags remain true and which are replaced by a
  reviewed publication-rendering status.
- Pixel-level agreement with Li-Hou-Zhao remains unsupported unless a later
  task defines and reviews that standard.
