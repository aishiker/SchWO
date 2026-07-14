# Phase 5 Fig.3 kM=2 dx=0.25M High-Resolution Pilot Closeout
Date: 2026-07-08
Decision state: T7bg accepted the numerical pilot YELLOW; T8af sidecar provenance hardening is complete and pending T7bh review.
## Artifact List
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz`
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.run.json`
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png`
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png.json`
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png`
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png.json`
- `runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_vs_dx0p5_common_grid_comparison.json`
## Integrity
- NPZ SHA/size: `5edddc1326a9f756c2507d3c3ac2285b067ca81333d300de7f2bca1c023bbbe2`, `59539269` bytes.
- Nearest PNG unchanged SHA: `b52cfc1a58dcfa5f06c3edd55781f520f2ad5a3aaa0d4d61a45896d140da3ce1`.
- Bilinear PNG unchanged SHA: `c8c93b391f15f768c9817f8d8ec2a11045c889abef20d9e03ad798161db2f286`.
- Updated nearest sidecar SHA: `ea60be7f26a9b6175e0fbbbdaa367b12597fa3a4caec1425c0d820a3a5591a63`.
- Updated bilinear sidecar SHA: `04698afa681dbf5d406d0fc239c595a365402b67992785537f739c1170c74bf0`.
## Q018 Summary
- Warning count `56`, codes `['evanescent_tail_suppressed']`, ell range `153..180`, sectors `['even', 'odd']`.
- `rmax=42.42640687119285`, min `valid_until_r=42.472089355131786`, margin `0.045682483938932705`, covers rmax `True`.
- Max suppression bound `1.2994970680433635e-24`.
## Explicit Non-Claims
- Not four-frequency `dx=0.25M`.
- Not `dx=0.2M`.
- Not `kM=4`.
- Not R60/R60_K4.
- Not Fig.2 strict `Psi4`.
- Not paper-level or final journal-grade.
## Sidecar Hardening Result
- Both PNG sidecars independently carry source NPZ path/SHA/size, run JSON path, Q018 warning summary, non-claim flags, interpolation policy, final pair, grid spacing, requested DPI, and valid/invalid counts.
