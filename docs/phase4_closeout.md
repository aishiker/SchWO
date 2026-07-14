# Phase 4 M4-Lite Closeout

Date: 2026-07-06

Status: M4-lite / validation-grade is closed by T7v after T7u accepted the
T8l/Q018 four-frequency Fig.3-lite saved artifacts.  This document records the
accepted artifact manifest, scope boundary, and remaining gates.  It is not a
journal-grade production-map closeout and it does not start transmission-factor
work.

## Scope

M4-lite validates:

- YAML-driven saved computation through the Phase 4 runner.
- Raw complex NPZ output and the HDF5-capable result path exercised by the IO
  tests.
- X-z finite-radius wave-field schema with explicit coordinates, radius/angle
  conversion metadata, horizon masking, and complex NaN invalid fields.
- Read-only plotting over saved results, including the four-frequency
  Fig.3-lite panel.
- Saved adaptive `lmax` final-pair convergence metadata.
- Q018 structured `evanescent_tail_suppressed` warning metadata for the current
  `61x61` saved grid.

M4-lite does not validate:

- Journal-grade high-resolution production maps.
- The `kM=4` stress benchmark.
- `R60_K2` / `R60_K4` numeric regression fixtures.
- Transmission factors or Q005 transmission normalization.
- Arbitrary observer grids beyond the saved `valid_until_r` coverage.
- Arbitrary incident direction.

No frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B, or polarization
convention was changed in this closeout.  No threshold or `lmax` value was
changed, and no new numeric fixture was created.

## Artifact Manifest

All accepted artifacts remain in `/tmp`; they were inspected in place and were
not moved.

| `kM` | Result path | Case id | Grid / spacing | Valid / invalid | Final pair | Warnings | Samples per wavelength |
|---:|---|---|---|---:|---|---:|---:|
| 0.5 | `/tmp/t8j_li_fig3_xz_k0p5_hires.npz` | `LI_FIG3_XZ_K0P5_HIRES` | `(61,61)`, `dx=dz=1M` | `3708 / 13` | `[72,84]`, pass | 0 | `12.566370614359172` |
| 1.0 | `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz` | `R60_K1_LI_FIG3_LITE_XZ_HIRES` | `(61,61)`, `dx=dz=1M` | `3708 / 13` | `[96,108]`, pass | 0 | `6.283185307179586` |
| 1.5 | `/tmp/t8j_li_fig3_xz_k1p5_hires.npz` | `LI_FIG3_XZ_K1P5_HIRES` | `(61,61)`, `dx=dz=1M` | `3708 / 13` | `[132,156]`, pass | 0 | `4.1887902047863905` |
| 2.0 | `/tmp/t8j_li_fig3_xz_k2p0_hires.npz` | `LI_FIG3_XZ_K2P0_HIRES` | `(61,61)`, `dx=dz=1M` | `3708 / 13` | `[156,180]`, pass | 56 | `3.141592653589793` |

For all four NPZ files:

- `grid.kind == "xz_plane"`.
- `x` and `z` are the integer grid `[-30,30]` with spacing `1`.
- `valid_mask` matches `sqrt(x^2+z^2) > 2M`.
- Valid `h_plus` and `h_cross` entries are finite complex values.
- Invalid entries are complex NaN.
- The saved final adjacent `lmax` pair passes the saved policy thresholds.
- Run-scoped radial cache metadata is enabled and bounded by unique radial
  solution keys rather than grid-point count.

## Q018 Metadata

For `kM=2.0`, the saved result records 56 structured radial warnings.  All have
code and solver `evanescent_tail_suppressed`, cover both odd/even sectors, and
span `ell=153..180`.

The current x-z grid has maximum valid radius
`42.42640687119285`.  The minimum saved suppressed-mode
`valid_until_r` is `42.472089355131786`, so the warning metadata covers this
grid.  The maximum saved suppression bound is
`1.2994970680433635e-24`.

This resolves/narrows Q018 only for the current Fig.3-lite finite-radius grid.
Future larger observer grids must re-check every suppressed mode's
`valid_until_r` and should continue to carry the structured warning metadata.
This policy is not an `ell_max` reduction and not a threshold relaxation.

## Panel Manifest

Accepted panel:

- PNG: `/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png`
- Sidecar: `/tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png.json`

The PNG is a `2015 x 1007` RGBA image.  The sidecar records:

- `plot_type = "fig3_multifrequency_panel"`.
- Source paths in `kM=[0.5,1.0,1.5,2.0]` order.
- Components `["h_plus", "h_cross"]`, `quantity="real"`,
  `interpolation="nearest"`.
- Grid spacing `{"x": 1.0, "z": 1.0}`.
- Valid counts `[3708,3708,3708,3708]` and invalid counts
  `[13,13,13,13]`.
- Final pairs `[[72,84],[96,108],[132,156],[156,180]]`, all passing.
- Row-wise symmetric color scales:
  - `h_plus`: `[-3.686623500517077, 3.686623500517077]`.
  - `h_cross`: `[-4.037188238909385, 4.037188238909385]`.
- Event-horizon and light-ring overlays with radii `2M` and `3M`.
- Samples per wavelength
  `[12.566370614359172, 6.283185307179586, 4.1887902047863905, 3.141592653589793]`.
- Convention metadata including Fourier `exp(-i k t)`, units `G=c=M=1`,
  Regge-Wheeler gauge, and Route B packaged polarization bridge.

`src/schwgw/viz` was statically scanned for solver/physics-layer imports and
no `schwgw.scattering`, `schwgw.perturbations`, `schwgw.angular`,
`schwgw.numerics`, `schwgw.backgrounds`, `compute_polarization`,
`run_solver_grid`, or `solve_radial` reference was found.

## Verification

T7v used standard local inspection and tests only.  No additional plugin,
connector, or skill was directly useful for this closeout slice before the
final verification skill check.

Commands run:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
# Independent metadata inspection over the four NPZ files and panel sidecar.
# The script loaded saved result files only and did not call solver or physics code.
PY
file /tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png /tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png.json
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Results:

- Static read-only plotting scan: no matches.
- Independent artifact metadata inspection: passed.
- PNG/JSON file inspection: PNG image data and JSON data.
- Plot/viz regression subset: `29 passed in 2.79s`.
- Full suite: `183 passed, 1 skipped, 1 xfailed, 75 subtests passed in 9.82s`.

## Closeout Decision

M4-lite / validation-grade is closed.  The recommended next action is:

`M4-lite closed; T0 may choose M4-production high-resolution maps next`

M4-production high-resolution maps, `kM=4`, `R60_K2` / `R60_K4`, and M5
transmission-normalization work remain gated until T0 opens a separate slice.
