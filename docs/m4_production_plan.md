# M4 Production Readiness Plan

Date: 2026-07-06

Status: readiness pilot complete; full M4-production maps are still gated.

This document plans the next journal-grade Fig.3 production-map slice after
M4-lite.  It does not close production, does not start a full production
matrix, and does not change any T2-T6 physics convention, radial solver
threshold, `lmax` policy, or plotting formula.

## Scope and Non-Scope

In scope:

- Define the first production target matrix for the Li-Hou-Zhao Fig.3-style
  x-z maps.
- Estimate runtime, storage, memory pressure, and cache behavior from accepted
  M4-lite artifacts and one bounded pilot.
- Record figure and sidecar metadata requirements for a journal-grade output.
- Check whether the current config/result/plot schema can express production
  grids.

Out of scope:

- Full four-frequency production run.
- `kM=4`, `R60_K2`, `R60_K4`, or transmission-factor work.
- Any relaxation of convergence thresholds or `lmax`.
- Any change to T2-T6 physics/convention code or T4 radial behavior.

## Production Target Matrix

The first production target should keep the accepted M4-lite physical and
convergence settings, but increase saved-data sampling on the same x-z domain.

| Target | Frequencies | Domain | Spacing | Grid | Status |
|---|---:|---|---:|---:|---|
| Fig.3 production first pass | `kM=[0.5,1.0,1.5,2.0]` | `x/M,z/M in [-30,30]` | `dx=dz=0.5M` | `121 x 121` | recommended next production target |
| Future stress candidate | `kM=4.0` only | not opened | `dx=dz=0.25M` | depends on domain | future slice only |

The `dx=dz=0.5M` target gives at least `2*pi` samples per wavelength at
`kM=2`, matching the accepted `kM=1, dx=1M` sampling density.

| `kM` | Wavelength `lambda/M` | M4-lite samples/wavelength (`dx=1M`) | Production samples/wavelength (`dx=0.5M`) |
|---:|---:|---:|---:|
| 0.5 | `12.566370614359172` | `12.566370614359172` | `25.132741228718345` |
| 1.0 | `6.283185307179586` | `6.283185307179586` | `12.566370614359172` |
| 1.5 | `4.1887902047863905` | `4.1887902047863905` | `8.377580409572781` |
| 2.0 | `3.141592653589793` | `3.141592653589793` | `6.283185307179586` |

For a future `kM=4`, `dx=0.25M` would again give
`6.283185307179586` samples per wavelength.  That is a separate stress
benchmark and should not be bundled with the first production pass.

## Accepted Baseline

The accepted M4-lite artifacts are the input baseline for this plan.

| `kM` | Result path | Grid | Valid/invalid | Runtime | File size | Cache unique | Final pair | Warnings |
|---:|---|---:|---:|---:|---:|---:|---|---:|
| 0.5 | `/tmp/t8j_li_fig3_xz_k0p5_hires.npz` | `61 x 61` | `3708 / 13` | `122.65 s` | `3,731,745 bytes` | `166` | `[72,84]`, pass | 0 |
| 1.0 | `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz` | `61 x 61` | `3708 / 13` | `215.76 s` | `3,718,253 bytes` | `214` | `[96,108]`, pass | 0 |
| 1.5 | `/tmp/t8j_li_fig3_xz_k1p5_hires.npz` | `61 x 61` | `3708 / 13` | `459.09 s` | `3,776,529 bytes` | `310` | `[132,156]`, pass | 0 |
| 2.0 | `/tmp/t8j_li_fig3_xz_k2p0_hires.npz` | `61 x 61` | `3708 / 13` | `628.54 s` | `3,978,197 bytes` | `358` | `[156,180]`, pass | 56 |

The `dx=0.5M` full-domain grid has `121 x 121 = 14641` points, with
`14592` valid points and `49` masked points under the current
`sqrt(x^2+z^2) > 2M` policy.  The point-count scale factor is
`14641/3721 = 3.934694974469229`.

## Cost Estimate

Runtime is expected to scale close to valid grid points for field assembly,
while radial cache unique solves stay tied to `(sector, ell, k, boundary)` and
do not scale with the number of x-z points.

| `kM` | Baseline runtime | `dx=0.5M` point-scaled estimate |
|---:|---:|---:|
| 0.5 | `122.65 s` | `482.59 s` (`8.0 min`) |
| 1.0 | `215.76 s` | `848.95 s` (`14.1 min`) |
| 1.5 | `459.09 s` | `1806.38 s` (`30.1 min`) |
| 2.0 | `628.54 s` | `2473.11 s` (`41.2 min`) |

The full four-frequency `dx=0.5M` production pass is therefore likely an
order-`1.5 h` run on the current machine, before any repeated plotting or
manual reruns.  This is acceptable only as an explicitly scheduled production
slice, not an interactive validation smoke test.

Expected NPZ size is modest but not negligible.  Direct point scaling from the
accepted artifacts gives about `15-16 MB` per frequency; the bounded pilot
suggests per-point metadata overhead can push a `kM=2` full-domain result
toward `20-22 MB`.  The four-frequency result set should be budgeted at
roughly `60-85 MB`, plus PNG/PDF sidecars and any regenerated HDF5 mirrors.

Raw numerical arrays are small: for `121 x 121`, the saved complex
`h_plus/h_cross` arrays, `r/theta/phi`, mask, and coordinate vectors are below
`1 MB` before metadata.  In-memory pressure is instead dominated by the radial
solution cache and the Python diagnostics list.  A future production run should
record peak memory explicitly; this T8m pilot did not profile RSS.

## Cache Behavior

The accepted and pilot runs confirm that run-scoped radial cache keys are
mode-based, not grid-point-based:

- `kM=0.5`: `166` unique radial solutions.
- `kM=1.0`: `214` unique radial solutions.
- `kM=1.5`: `310` unique radial solutions.
- `kM=2.0`: `358` unique radial solutions.
- T8m `kM=2` pilot: also `358` unique radial solutions on only `392` valid
  x-z points.

For full-domain `kM=2, dx=0.5M`, cache hits should scale from the accepted
`1,340,834` to about `5.28 million`, while unique radial solves should remain
`358` if the same `lmax=180`, boundary settings, and Q018 policy apply.

## Q018 Coverage

The current full domain has

```text
rmax = sqrt(30^2 + 30^2) = 42.42640687119285 M
```

For accepted `kM=2`, the minimum saved suppressed-mode
`valid_until_r` is `42.472089355131786`, leaving only
`0.045682483938932705 M` of radial margin.  The `dx=0.5M` grid keeps the
same domain corners, so its maximum radius is unchanged and the existing Q018
coverage implication is favorable for the same domain.

This is a narrow-domain statement only.  Any expansion beyond the current
`[-30,30]^2` domain, even with the same spacing, must re-check every
suppressed mode's `valid_until_r` before acceptance.

## Bounded Pilot

T8m ran one non-final pilot:

- Config: `configs/li_fig3_xz_k2p0_dx0p5_pilot.yaml`
- Result: `/tmp/t8m_li_fig3_xz_k2p0_dx0p5_pilot.npz`
- Panel: `/tmp/t8m_li_fig3_xz_k2p0_dx0p5_pilot_panel_real_nearest.png`
- Sidecar: `/tmp/t8m_li_fig3_xz_k2p0_dx0p5_pilot_panel_real_nearest.png.json`

Pilot parameters:

- `kM=2.0`, `lmax=180`, `lmax_values=[108,132,156,180]`.
- Same amplitudes, boundary settings, and convergence thresholds as accepted
  T8l `kM=2.0`.
- Small x-z subdomain `[-5,5] x [-5,5]`, `dx=dz=0.5M`.
- Runtime: `real 399.10 s`, below the 30 minute cap.

Pilot verification:

| Field | Value |
|---|---:|
| Saved shape | `21 x 21` |
| Valid/invalid | `392 / 49` |
| Max valid radius | `7.0710678118654755` |
| Samples/wavelength | `6.283185307179586` |
| Finite valid fields | yes |
| Final adjacent pair | `[156,180]`, pass |
| Radial cache unique/hit/key | `358 / 153706 / 358` |
| Q018 warnings | `56` |
| Q018 min `valid_until_r` | `42.472089355131786` |
| Q018 max suppression bound | `1.2994970680433635e-24` |
| PNG size | `1296 x 612`, RGBA |
| Sidecar grid spacing | `{"x": 0.5, "z": 0.5}` |
| Sidecar interpolation | `nearest` |
| Sidecar overlays | event horizon `2M`, light ring `3M` |

The pilot confirms that the current explicit-array config schema can express a
small `dx=0.5M` x-z grid and that read-only plotting records spacing,
sampling, interpolation, source path, and overlay metadata.

It also exposes a production-readiness gap: `plot-fig3-panel` sidecars do not
currently include the saved `final_lmax_pair` / `final_pair_passed`, while
`plot-fig3-multifrequency-panel` sidecars do.  A production single-frequency
figure sidecar should include convergence final-pair metadata too.

## Schema Assessment

Current schema status:

- Result files already store explicit `x`, `z`, `r`, `theta`, `phi`,
  `valid_mask`, complex fields, convention metadata, convergence history,
  radial cache metadata, and radial warning metadata.
- Multi-frequency Fig.3 sidecars already record source paths, row-wise color
  scales, grid spacing, samples per wavelength, overlays, and convergence
  final pairs.
- Explicit YAML arrays can technically express the `121` x-values and `121`
  z-values needed for `dx=0.5M`.

Main schema risk:

- Production grids are verbose and error-prone as manual explicit arrays.
  The future schema should support range-based observers, for example
  `start/stop/step` with explicit endpoint policy, and the saved result should
  still record the expanded coordinate arrays for reproducibility.

Recommended future config extension:

```yaml
observer:
  kind: xz_plane
  x_range:
    start: -30.0
    stop: 30.0
    step: 0.5
    endpoint: true
  z_range:
    start: -30.0
    stop: 30.0
    step: 0.5
    endpoint: true
  invalid_radius_policy: mask
```

This should be implemented as a separate schema slice with parser tests, not
inside a production run.

## Journal-Grade Figure Requirements

Saved data requirements:

- The production accepted data must be the saved result, not an interpolated
  image.  For the first production pass, require `dx=dz=0.5M` on the full
  `[-30,30]^2` domain.
- The sidecar must record source result paths, case IDs, `kM`, `M`, amplitudes,
  `lmax`, final adjacent convergence pairs, final-pair pass flags, radial
  warning summaries, Q018 `valid_until_r` minimum for `kM=2`, and all frozen
  conventions.
- The sidecar must record grid spacing, samples per wavelength, interpolation
  mode, color scales, overlays, and source artifact creation times.

Figure rendering requirements:

- Use at least `300 DPI` for raster submission exports, or a vector container
  with embedded raster heatmaps at equivalent resolution.
- Use row-wise symmetric color scales for the `h_plus` row and the `h_cross`
  row, as in the accepted multi-frequency panel.
- Keep axes in `x/M` and `z/M`, shared limits, equal aspect ratio, and visible
  horizon/light-ring overlays at `2M` and `3M`.
- Prefer `nearest` for audit plots that expose the saved sampling.  Any
  publication smoothing or interpolation must be explicitly recorded in the
  sidecar and caption and must not be used as evidence of higher saved-data
  resolution.
- Keep panel labels and colorbars readable at journal size; minimum effective
  font size should be no smaller than about 6 pt after scaling.
- Use a diverging colormap with balanced positive/negative treatment.  Current
  `RdBu_r` is acceptable for continuity, but final submission should be checked
  for grayscale and color-vision accessibility.
- Captions must state the Fourier convention `exp(-i k t)`, units `G=c=M=1`,
  x-z plane convention, horizon mask rule, and that plotted values are
  `real(h_plus)` / `real(h_cross)`.

Current plotting-readiness gaps:

- Existing Fig.3 PNG renderers use hard-coded `dpi=180`; production export
  needs a configurable `dpi>=300` path or a vector/PDF export path.
- Single-frequency Fig.3 sidecars should include final-pair convergence
  metadata to match the multi-frequency sidecar.

## Readiness Decision

T8m conclusion: M4-production is technically plausible but should not be
started until a dedicated production slice is opened.

## T8n Hardening Addendum

T8n implements the schema and output-layout hardening recommended after T7w:

- Range-based x-z observer input is now supported through `x_range` and
  `z_range` with `start`, `stop`, `step`, and `endpoint: true`.
- The parser expands ranges into saved explicit `x_values` and `z_values`;
  explicit arrays remain backward compatible, and ambiguous `*_values` plus
  `*_range` configs are rejected.
- Production template
  `configs/li_fig3_xz_production_k2p0_dx0p5_template.yaml` records the
  `kM=2.0`, `dx=dz=0.5M`, `121x121` range schema target, but it is a template
  only and has not been run.
- `plot-fig3-panel` sidecars now include `final_lmax_pair` and
  `final_pair_passed` from saved result metadata when present, matching the
  multi-frequency audit trail.
- Single- and multi-frequency Fig.3 plotting commands accept `--dpi`; sidecars
  record `requested_dpi` and `output_format`.  PNG remains the default path,
  while PDF export is supported by the output suffix.
- A tiny range-config smoke result was generated under `/tmp` to verify
  expanded coordinates, `--dpi 300`, and sidecar provenance.  This smoke is
  not a benchmark or accepted production artifact.

After T8n, the major pre-production ergonomics gaps in this document are
closed.  Full M4-production still requires a separate scheduled run and
independent T7 review of its artifacts.

Required before full production acceptance:

- T7w independent review of this plan and the T8m pilot artifacts.
- T7x independent review of the T8n range-schema and output-layout hardening.
- Schedule the four-frequency `dx=0.5M` run as a production job with expected
  runtime around `1.5 h`.

Recommended next prompt:

```text
你现在是 T7x。请读取并严格执行 docs/prompts/phase4_t7x_production_schema_output_review.md。
```
