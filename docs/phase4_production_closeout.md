# Phase 4 M4-Production First-Pass Closeout

Date: 2026-07-06

Status: M4-production first pass is closed after T8o generated the
four-frequency `dx=dz=0.5M` saved maps and T7y independently accepted the
artifacts.  This closeout freezes the accepted manifest, validation scope, and
remaining gates.  It does not start `kM=4`, R60_K2/R60_K4 fixtures, M5
transmission, arbitrary incident direction, or larger-domain work.

## Scope

This M4-production first pass validates:

- Full-domain Fig.3-style finite-radius saved wave-field maps on
  `x/M,z/M in [-30,30]`.
- Production sampling `dx=dz=0.5M`, shape `(121,121)`, for
  `kM=[0.5,1.0,1.5,2.0]`.
- Raw complex NPZ output containing expanded x-z coordinates, `r/theta/phi`,
  `valid_mask`, complex `h_plus/h_cross`, and JSON metadata.
- Horizon/interior mask handling: points with `r <= 2M` are invalid and store
  complex NaN fields.
- Read-only PNG/PDF `2x4` Fig.3 panel generation from saved results with
  `requested_dpi=300`.
- Saved adaptive final-adjacent-pair `lmax` convergence metadata.
- Q018 structured `evanescent_tail_suppressed` metadata covering this
  `[-30,30]^2` domain.

This closeout does not validate:

- `kM=4` stress.
- R60_K2 or R60_K4 numeric regression fixtures.
- M5 transmission factors or Q005 unlensed-normalization convention.
- Arbitrary incident direction.
- Larger observer domains beyond the current Q018 `valid_until_r` coverage.
- Pixel-for-pixel reproduction of any reference-paper figure.

No frozen Fourier, harmonic, tetrad, RW/Zerilli, Route B, or polarization
convention was changed.  No threshold, `lmax` value, T2-T6 formula path,
radial solver behavior, numeric fixture, or transmission artifact was changed
or created in this closeout.

## Artifact Manifest

T7z originally inspected the accepted artifacts in place under `/tmp`.  Because
`/tmp` is temporary and resolves through `/private/tmp` on macOS, T0 later
copied the accepted artifacts into the project archive:

```text
runs/phase4/m4_production_first_pass/
```

The project archive is now the durable local record.  The original `/tmp`
paths below are retained as provenance for the T8o/T7y/T7z run history.  The
archive copy is documented in
`runs/phase4/m4_production_first_pass/manifest.md` with file sizes and SHA-256
checksums.

| `kM` | Result path | Case id | Grid / spacing | Valid / invalid | Final pair | Cache unique/key/hit | Warnings | Warning codes | Samples per wavelength |
|---:|---|---|---|---:|---|---:|---:|---|---:|
| 0.5 | `/tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz` | `LI_FIG3_XZ_K0P5_DX0P5_PRODUCTION` | `(121,121)`, `[-30,30]^2`, `dx=dz=0.5M` | `14592 / 49` | `[72,84]`, pass | `166 / 166 / 2428346` | 0 | none | `25.132741228718345` |
| 1.0 | `/tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz` | `LI_FIG3_XZ_K1P0_DX0P5_PRODUCTION` | `(121,121)`, `[-30,30]^2`, `dx=dz=0.5M` | `14592 / 49` | `[96,108]`, pass | `214 / 214 / 3132434` | 0 | none | `12.566370614359172` |
| 1.5 | `/tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz` | `LI_FIG3_XZ_K1P5_DX0P5_PRODUCTION` | `(121,121)`, `[-30,30]^2`, `dx=dz=0.5M` | `14592 / 49` | `[132,156]`, pass | `310 / 310 / 4534634` | 0 | none | `8.377580409572781` |
| 2.0 | `/tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz` | `LI_FIG3_XZ_K2P0_DX0P5_PRODUCTION` | `(121,121)`, `[-30,30]^2`, `dx=dz=0.5M` | `14592 / 49` | `[156,180]`, pass | `358 / 358 / 5237306` | 56 | `evanescent_tail_suppressed` | `6.283185307179586` |

For all four NPZ files:

- `grid.kind == "xz_plane"`.
- Saved `x` and `z` arrays are expanded coordinates
  `[-30.0, -29.5, ..., 30.0]`.
- `valid_mask` matches `sqrt(x^2+z^2) > 2M`.
- Valid `h_plus` and `h_cross` entries are finite complex values.
- Invalid `h_plus` and `h_cross` entries are complex NaN.
- The saved final adjacent `lmax` pair passes both selected-probe and
  near-axis thresholds.
- Run-scoped radial cache counts are bounded by radial solution keys, not by
  the `14641` grid points.
- Radial warning metadata is JSON-safe.

## Q018 Metadata

The production grid maximum radius is

```text
rmax = sqrt(30^2 + 30^2) = 42.42640687119285 M
```

For `kM=2.0`, the saved result records 56 structured radial warnings.  All
have `code=solver=evanescent_tail_suppressed`, cover odd/even sectors, and
span `ell=153..180`.  The minimum saved `valid_until_r` is
`42.472089355131786`, which covers the production domain.  The maximum saved
suppression bound is `1.2994970680433635e-24`.

This is a same-domain Q018 acceptance only.  Any larger observer domain must
re-check every suppressed mode's `valid_until_r`; this closeout must not be
used as evidence for domains beyond `[-30,30]^2`.

## Panel Manifest

Accepted production panels:

- PNG: `/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png`
- PNG sidecar: `/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png.json`
- PDF: `/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf`
- PDF sidecar: `/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf.json`

Durable project archive copies:

- PNG:
  `runs/phase4/m4_production_first_pass/t8o_li_fig3_production_panel_real_nearest_300dpi.png`
- PNG sidecar:
  `runs/phase4/m4_production_first_pass/t8o_li_fig3_production_panel_real_nearest_300dpi.png.json`
- PDF:
  `runs/phase4/m4_production_first_pass/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf`
- PDF sidecar:
  `runs/phase4/m4_production_first_pass/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf.json`

File inspection reports:

- PNG image data, `3360 x 1680`, RGBA.
- PDF document, version 1.4, `1` page.
- Both sidecars are JSON data.

Both sidecars record:

- `plot_type="fig3_multifrequency_panel"`.
- Source paths in `kM=[0.5,1.0,1.5,2.0]` order.
- Components `["h_plus","h_cross"]`, `quantity="real"`,
  `interpolation="nearest"`.
- `requested_dpi=300`.
- `output_format="png"` or `output_format="pdf"`.
- Grid spacing `{"x":0.5,"z":0.5}`.
- Valid counts `[14592,14592,14592,14592]` and invalid counts
  `[49,49,49,49]`.
- Final pairs `[[72,84],[96,108],[132,156],[156,180]]`, all passing.
- Row-wise symmetric color scales:
  - `h_plus`: `[-6.29725073327433, 6.29725073327433]`.
  - `h_cross`: `[-4.037188238909385, 4.037188238909385]`.
- Event-horizon and light-ring overlays with radii `2M` and `3M`.
- Convention metadata: Fourier `exp(-i k t)`, units `G=c=M=1`,
  gauge `Regge-Wheeler`, and incident-frame electric tidal packaged scalar
  polarization bridge.

## Verification

T7z used standard local inspection and tests only.  No additional plugin,
connector, or task-specific skill was directly useful for this closeout beyond
local artifact inspection and tests.  Final completion verification used the
available `verification-before-completion` skill instructions.

Commands run:

```bash
ls -lh /tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz \
  /tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png \
  /tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png.json \
  /tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf \
  /tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf.json

PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
# Independent metadata inspection over the four NPZ files and two sidecars.
# The script loaded saved files only and did not call solver, scattering,
# radial, angular, or physics code.
PY

rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true

PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Results:

- All eight required artifacts exist and are readable.
- Independent artifact metadata inspection passed.
- Static read-only plotting scan: no matches.
- Targeted IO/viz/plot regression suite: passed.
- Full pytest suite: passed.

## Closeout Decision

M4-production first pass is closed and accepted for the specified
`kM=[0.5,1.0,1.5,2.0]`, `[-30,30]^2`, `dx=dz=0.5M`, default `+z`
incident-direction scope.

Recommended next action:

```text
M4-production first pass closed. Recommended next scientific slice: M5
transmission-normalization design for Q005, unless T0 explicitly chooses
`kM=4`, R60_K2/R60_K4, or arbitrary incident direction first.
```

Remaining gates:

- `kM=4` stress remains unopened.
- R60_K2/R60_K4 regression fixtures remain ungenerated.
- M5 transmission remains gated by Q005 normalization.
- Arbitrary incident direction remains unimplemented.
- Larger observer domains must re-check Q018 `valid_until_r` coverage.
