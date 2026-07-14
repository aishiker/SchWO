# T7 Archive: Fig.3 dx0.25 Production Review Pre-Closeout

Archived: 2026-07-09

Thread: T7, validation and benchmark review.

Reason for archive: T7bk is a closeout boundary. This file preserves the T7bj current-handoff state before `docs/handoffs/T7_current.md` was advanced to the T7bk closeout state.

## Current Status At Archive Time

T7bj independently reviewed the T8ah Fig.3 four-frequency `dx=0.25M` production archive:

```text
docs/prompts/phase5_t7bj_fig3_four_frequency_dx0p25_production_review.md
```

Decision:

```text
ACCEPT GREEN / FOUR-FREQUENCY DX0.25 PRODUCTION ARCHIVE ACCEPTED
```

## Accepted Archive

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

Accepted scope:

- Option A fresh archive.
- `kM=[0.5,1.0,1.5,2.0]`.
- `dx=dz=0.25M`.
- `x/M,z/M in [-30,30]`.
- Route B/M4 saved-result path.
- Not by-reference reuse of the accepted `kM=2` pilot.

## Core Evidence At Archive Time

- Top-level file count: `29`.
- Four NPZ files and four run JSON files were present.
- Ten PNGs and ten PNG sidecars were present.
- Manifest path: `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`.
- Manifest SHA256: `adfc8b3079fb0d37863b00ac02b3e021c7127e6bebf811d5562e84e414b02d2e`.
- All four frequencies passed shape `(241,241)`, valid/invalid `57884/197`, `valid_mask == (r > 2M)`, valid finite fields, invalid complex NaN fields, final pair `[156,180]`, Q018, radial-cache, sidecar, manifest, and focused-test review.

## Key Hashes

```text
b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz
0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz
1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz
b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz
220c8e25187aa760015c92f82a0a5fd5a797765027b492e28d0e636b1cd53b4c  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png
777a0d451db5dc332fa57fcd74cb059412238d98c459bb268374b7fbcbd943ab  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png
```

## Q018 At Archive Time

- `kM=0.5,1.0,1.5`: zero-warning structured metadata, covers `rmax=42.42640687119285`.
- `kM=2.0`: warning count `56`, code `evanescent_tail_suppressed`, ell `153..180`, sectors `even/odd`, `valid_until_r_min=42.472089355131786`, margin `0.045682483938932705`, covers `rmax=42.42640687119285`.

## Commands Run In T7bj

```bash
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
find src tests -type f -newer docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md -print | sort
find configs -type f -newer docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md -print | sort
find runs/phase5 -path 'runs/phase5/fig3_four_frequency_dx0p25_production' -prune -o -name 't8ah_li_fig3*' -print | sort
shasum -a 256 runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Results:

- Static viz dependency check: no output.
- Source/test timestamp check: no output.
- Config timestamp check: no output.
- Outside-output check: no output.
- Independent Python inspection: `PASS`.
- Focused pytest: `58 passed in 6.20s`.

## Remaining Gates At Archive Time

- No paper-level or final journal-grade Fig.3 claim.
- No `dx=0.2M`.
- No `kM=4`.
- No R60/R60_K4.
- No Fig.2 strict `Psi4`.
- No fixtures.
- No dense Fig.5/Fig.6 scans.
- No Kirchhoff or Appendix D/E curves.
- No source/test/convention/threshold/`lmax` changes.

## Next Step At Archive Time

T0 scheduled T7bk to create a formal closeout document for this accepted production archive.
