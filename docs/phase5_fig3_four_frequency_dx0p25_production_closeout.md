# Phase 5 Fig.3 Four-Frequency dx=0.25M Production Closeout

Date: 2026-07-09

Decision:

```text
ACCEPT GREEN / FOUR-FREQUENCY DX0.25 PRODUCTION ARCHIVE ACCEPTED
```

Archive:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

## Accepted Scope

This closeout records the T7bj-accepted Fig.3 four-frequency `dx=0.25M`
production archive.

Accepted scope:

- Option A fresh four-frequency archive.
- Frequencies `kM=[0.5,1.0,1.5,2.0]`.
- Saved-data spacing `dx=dz=0.25M`.
- Domain `x/M,z/M in [-30,30]`.
- Route B/M4 saved-result path.
- Not by-reference reuse of the T8ae/T8af `kM=2` pilot.

## Artifact Inventory

Manifest:

- `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`

NPZ files:

- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz`

Run JSON files:

- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.run.json`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.run.json`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.run.json`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.run.json`

Per-frequency nearest audit PNGs and sidecars:

- `t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_nearest_300dpi.png` and `.png.json`
- `t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_nearest_300dpi.png` and `.png.json`
- `t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_nearest_300dpi.png` and `.png.json`
- `t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png` and `.png.json`

Per-frequency bilinear display-only PNGs and sidecars:

- `t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_bilinear_300dpi.png` and `.png.json`
- `t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_bilinear_300dpi.png` and `.png.json`
- `t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_bilinear_300dpi.png` and `.png.json`
- `t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png` and `.png.json`

Archive-level PNGs and sidecars:

- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png.json`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png.json`

## Key Hashes

```text
adfc8b3079fb0d37863b00ac02b3e021c7127e6bebf811d5562e84e414b02d2e  runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz
0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz
1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz
b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz
220c8e25187aa760015c92f82a0a5fd5a797765027b492e28d0e636b1cd53b4c  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png
777a0d451db5dc332fa57fcd74cb059412238d98c459bb268374b7fbcbd943ab  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png
```

## Numerical Evidence

All four frequencies passed the T7bj numerical review:

- Shape: `(241,241)`.
- Valid/invalid count: `57884/197`.
- Mask policy: `valid_mask == (r > 2M)`.
- Valid `h_plus/h_cross` fields are finite.
- Invalid `h_plus/h_cross` fields are complex NaN.
- Final adjacent pair `[156,180]` passed for all four frequencies.
- Radial cache metadata is present for all four frequencies.

Radial cache metadata in the accepted archive:

- enabled `True`.
- `key_count=358`.
- `unique_solution_count=358`.
- `hit_count=20735842`.

## Q018 Evidence

Q018 acceptance is same-domain only for:

```text
rmax=42.42640687119285
```

Per-frequency Q018 summary:

- `kM=0.5`: warning count `0`, structured metadata present, covers `rmax`.
- `kM=1.0`: warning count `0`, structured metadata present, covers `rmax`.
- `kM=1.5`: warning count `0`, structured metadata present, covers `rmax`.
- `kM=2.0`: warning count `56`, code `evanescent_tail_suppressed`, ell `153..180`, sectors `even/odd`, `valid_until_r_min=42.472089355131786`, margin `0.045682483938932705`, covers `rmax=42.42640687119285`.

No unknown or uncovered Q018 warning code was accepted by T7bj.

## Plot And Sidecar Policy

Nearest plots:

- audit/numerical provenance;
- nearest-neighbor display exposes the saved grid without smoothing;
- sidecars record them as numerical evidence plots.

Bilinear plots:

- display-only smoothing;
- not numerical evidence;
- not a paper-level or final-journal-grade claim.

All accepted PNG sidecars contain:

- source NPZ path, SHA-256, and size;
- run JSON provenance;
- Q018 summary;
- interpolation policy;
- final-pair status;
- grid spacing;
- requested DPI;
- valid/invalid counts;
- convention metadata;
- `not_paper_level_claim=true`;
- `not_final_journal_grade=true`;
- false flags for `dx02_production`, `kM4_production`, `R60_production`, and `fig2_strict_psi4_artifact`.

## Verification Evidence

T7bj verification evidence:

- Focused pytest: `58 passed in 6.20s`.
- Static viz dependency check: no output.
- Source/test timestamp check: no output.
- Config timestamp check: no output.
- Outside-output check for `t8ah_li_fig3*`: no output.
- Independent Python inspection: `PASS`, with `file_count=29`, `png_count=10`, and `sidecar_count=10`.

T7bj did not run full pytest because no `src/` or `tests/` changes were found.

## Explicit Non-Claims

This closeout does not claim:

- paper-level Fig.3 reproduction;
- final journal-grade Fig.3 readiness;
- `dx=0.2M`;
- `kM=4`;
- R60/R60_K4;
- Fig.2 strict `Psi4`;
- fixtures;
- dense Fig.5/Fig.6 scans;
- Kirchhoff implementation;
- Appendix D/E curves.

## Remaining Gates

Before any paper-level Fig.3 claim:

- A separate T10/T7 figure-quality and literature-comparison review is required.
- `dx=0.2M` should only be considered if a later review decides the accepted `dx=0.25M` archive remains visually or scientifically insufficient.
- `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, Kirchhoff, and Appendix D/E remain separate gates.
- Physics conventions, thresholds, `lmax`, and boundary tolerances remain frozen unless explicitly reviewed by the appropriate threads.

## Next-Step Options

T0 may choose one of:

- Schedule a T10/T7 figure-quality comparison and reproduction-readiness review for the accepted Fig.3 `dx=0.25M` archive.
- Pause Fig.3 and return to Fig.2 strict `Psi4` or another separately gated workstream.

No production rerun, plotting rerun, fixture generation, or artifact mutation is authorized by this closeout.
