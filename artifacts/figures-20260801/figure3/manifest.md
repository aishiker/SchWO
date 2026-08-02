# Phase 5 T8ah Fig.3 Four-Frequency dx=0.25M Production Manifest
Created UTC: 2026-07-08T15:58:43.991145+00:00

## Scope And Non-Claims
- Scope: Fig.3 x-z plane four-frequency production, `kM=[0.5,1.0,1.5,2.0]`, `dx=dz=0.25M`, `x/M,z/M in [-30,30]`, Route B/M4 saved-result path.
- Execution route: T7bi-reviewed Option A; all four frequencies are fresh outputs in this unified directory.
- Not reused by reference: the accepted `kM=2` pilot remains prior evidence only and was not promoted as a member artifact.
- Non-claims: not `dx=0.2M`; not `kM=4`; not R60/R60_K4; not Fig.2 strict `Psi4`; not fixtures; not dense Fig.5/Fig.6; not Kirchhoff/Appendix D/E; not paper-level; not final journal-grade.

## Solver Commands And Runtimes
- `LI_FIG3_XZ_K0P5_DX0P25_PRODUCTION`: `/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k0p5_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz`; runtime real/user/sys = 3856.02/3831.23/16.11 s.
- `LI_FIG3_XZ_K1P0_DX0P25_PRODUCTION`: `/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k1p0_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz`; runtime real/user/sys = 3903.89/3891.06/8.5 s.
- `LI_FIG3_XZ_K1P5_DX0P25_PRODUCTION`: `/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k1p5_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz`; runtime real/user/sys = 4031.59/4026.43/5.02 s.
- `LI_FIG3_XZ_K2P0_DX0P25_PRODUCTION`: `/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k2p0_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz`; runtime real/user/sys = 4137.05/4132.5/4.68 s.
- Total solver real time: 15928.55 s.

## Plot Commands
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_nearest_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz --quantity real --interpolation bilinear --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_bilinear_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_nearest_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz --quantity real --interpolation bilinear --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_bilinear_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_nearest_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz --quantity real --interpolation bilinear --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_bilinear_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz --quantity real --interpolation bilinear --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png --dpi 300`
- `PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz --quantity real --interpolation bilinear --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png --dpi 300`

## Per-Frequency Gate Summary
| kM | case_id | shape | valid/invalid | final pair | final pass | Q018 warnings | Q018 coverage | radial cache keys | NPZ SHA256 |
|---:|---|---|---:|---|---|---:|---|---:|---|
| 0.5 | `LI_FIG3_XZ_K0P5_DX0P25_PRODUCTION` | `(241, 241)` | 57884/197 | `[156, 180]` | True | 0 | True | 358 | `b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873` |
| 1.0 | `LI_FIG3_XZ_K1P0_DX0P25_PRODUCTION` | `(241, 241)` | 57884/197 | `[156, 180]` | True | 0 | True | 358 | `0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132` |
| 1.5 | `LI_FIG3_XZ_K1P5_DX0P25_PRODUCTION` | `(241, 241)` | 57884/197 | `[156, 180]` | True | 0 | True | 358 | `1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2` |
| 2.0 | `LI_FIG3_XZ_K2P0_DX0P25_PRODUCTION` | `(241, 241)` | 57884/197 | `[156, 180]` | True | 56 | True | 358 | `b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc` |

## Grid Mask Finite NaN Policy
- `LI_FIG3_XZ_K0P5_DX0P25_PRODUCTION`: `valid_mask == (r > 2M)` True; valid fields finite h_plus/h_cross = True/True; invalid complex NaN h_plus/h_cross = True/True; rmax = 42.42640687119285.
- `LI_FIG3_XZ_K1P0_DX0P25_PRODUCTION`: `valid_mask == (r > 2M)` True; valid fields finite h_plus/h_cross = True/True; invalid complex NaN h_plus/h_cross = True/True; rmax = 42.42640687119285.
- `LI_FIG3_XZ_K1P5_DX0P25_PRODUCTION`: `valid_mask == (r > 2M)` True; valid fields finite h_plus/h_cross = True/True; invalid complex NaN h_plus/h_cross = True/True; rmax = 42.42640687119285.
- `LI_FIG3_XZ_K2P0_DX0P25_PRODUCTION`: `valid_mask == (r > 2M)` True; valid fields finite h_plus/h_cross = True/True; invalid complex NaN h_plus/h_cross = True/True; rmax = 42.42640687119285.

## Q018 And Radial Cache
- `LI_FIG3_XZ_K0P5_DX0P25_PRODUCTION`: warnings=0, codes=[], ell range=None..None, sectors=[], valid_until_r_min=None, margin=None, covers_rmax=True, suppression_bound_max=None; radial cache enabled=True, key_count=358, unique_solution_count=358, hit_count=20735842.
- `LI_FIG3_XZ_K1P0_DX0P25_PRODUCTION`: warnings=0, codes=[], ell range=None..None, sectors=[], valid_until_r_min=None, margin=None, covers_rmax=True, suppression_bound_max=None; radial cache enabled=True, key_count=358, unique_solution_count=358, hit_count=20735842.
- `LI_FIG3_XZ_K1P5_DX0P25_PRODUCTION`: warnings=0, codes=[], ell range=None..None, sectors=[], valid_until_r_min=None, margin=None, covers_rmax=True, suppression_bound_max=None; radial cache enabled=True, key_count=358, unique_solution_count=358, hit_count=20735842.
- `LI_FIG3_XZ_K2P0_DX0P25_PRODUCTION`: warnings=56, codes=['evanescent_tail_suppressed'], ell range=153..180, sectors=['even', 'odd'], valid_until_r_min=42.472089355131786, margin=0.045682483938932705, covers_rmax=True, suppression_bound_max=1.2994970680433635e-24; radial cache enabled=True, key_count=358, unique_solution_count=358, hit_count=20735842.

## Plotting Interpolation Policy
- `nearest`: audit plot; nearest-neighbor display exposes saved grid without smoothing and is the numerical/provenance inspection plot.
- `bilinear`: display-only smoothing; not numerical evidence and not a paper-level/final-journal-grade claim.
- All plotting commands read saved NPZ files only.

## File Records
| Path | SHA256 | Size bytes |
|---|---:|---:|
| `configs/li_fig3_xz_production_k0p5_dx0p25.yaml` | `89e5adff7750cde2404f6f477e3cefe91c4f135466157f1b92df9d258785fff8` | 777 |
| `configs/li_fig3_xz_production_k1p0_dx0p25.yaml` | `4b714db46cc92488db95417d7211ec2f05d0ffc383867d680f5b403e13904971` | 777 |
| `configs/li_fig3_xz_production_k1p5_dx0p25.yaml` | `203bb880a6cb8839d7b21ddaac6263b510d80a66ee79304ec25ce9c4915c289c` | 777 |
| `configs/li_fig3_xz_production_k2p0_dx0p25.yaml` | `4b1457a49cd6dfafb37071b9049370e7f52cf1aab005103ec2990e2cc5ab5135` | 777 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz` | `b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873` | 58224065 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.run.json` | `8ab251f32b3d5f8ab13cdc3351ea86050b97ff9353219b9cdcedbf75ce342a08` | 4482 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_nearest_300dpi.png` | `7e528b40e39ae694d8b56905b6358a1ae33ce633050e8f29fcee80b7dbaa6704` | 144611 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_nearest_300dpi.png.json` | `138e55a39f3764136a1b7d90242008f63c8d1c2b1f38b1686faf3731131c0129` | 2729 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_bilinear_300dpi.png` | `3c26eed115add361be3ef126498ff4f3826d82fe7c06ed8d62c12e9e5a476ee2` | 241653 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_bilinear_300dpi.png.json` | `ea103c364ba6dc44391a3e08b56f430070d1f9b9a077c92cf5ad3211445f741a` | 2729 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz` | `0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132` | 57760985 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.run.json` | `68d5f8b4b9a465c8749b7d88b296518959e662aad352aa4ab758f0662379170c` | 4480 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_nearest_300dpi.png` | `b8c9ec7626017325238518553f7a972676059a87542c2be58ff024cc79d15244` | 198174 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_nearest_300dpi.png.json` | `2bed5937b9dea7bd075a5aea56196140e6a4f491de1e01a85a2c56e162f89b92` | 2730 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_bilinear_300dpi.png` | `3ecdf6ee84c112e097a9f2a6fe61d85a5b461c1a639bccb86d2a8d118b633b5e` | 450970 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_bilinear_300dpi.png.json` | `b1911973760e5c1ce652f0e837673d417255595f24ddd26382337de790895ea0` | 2730 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz` | `1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2` | 58687353 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.run.json` | `4dfcbdd6e27354b718481108a24ed4f115ffc1329abf4ddfe0590e79cc924aad` | 4533 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_nearest_300dpi.png` | `80683cc2b59e945bb7c4fc9011b2fb33514930791c38b79e547b3fec5e9b055a` | 225148 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_nearest_300dpi.png.json` | `af0c4c7dbeb492c5eee065c40b0a70e7ff73a716c7864b45f0f39b803df55f1e` | 2729 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_bilinear_300dpi.png` | `d747b3cac8a58c943d83c27cfd6e1197cfcff5f15d0ed3a3213f03ed49e11ffa` | 569142 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_bilinear_300dpi.png.json` | `547701a013e1cd9bd3d38b4dde5ebed82ce7d7d7edc6e15424d95c92b6b43595` | 2729 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz` | `b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc` | 59539325 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.run.json` | `e65facb6ecd0f22f8a2011897354393cff574d87b526d59fa2eaec32296c565a` | 4700 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png` | `b52cfc1a58dcfa5f06c3edd55781f520f2ad5a3aaa0d4d61a45896d140da3ce1` | 238233 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png.json` | `fed7f36737083daab4ad0f295608f56131a85d895f53f9b17ca2c1d218d5c884` | 2861 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png` | `c8c93b391f15f768c9817f8d8ec2a11045c889abef20d9e03ad798161db2f286` | 628031 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png.json` | `03bca8ff2ba3e05b8ec3a55e06e0dda9bdfabcf76f5cbb8897e251bd2c2958c6` | 2861 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png` | `220c8e25187aa760015c92f82a0a5fd5a797765027b492e28d0e636b1cd53b4c` | 624465 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png.json` | `a560716365202fce608ddb5454ddd4ee39fdae4af92c2dc4d5ddbfea1dd18208` | 7789 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png` | `777a0d451db5dc332fa57fcd74cb059412238d98c459bb268374b7fbcbd943ab` | 1775756 |
| `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png.json` | `47ebf23551847ed12f2e4ff9008f7b346db06c6c8ec0f706916fc8c258039e14` | 7789 |

## Manifest Self Record
- This manifest is included in the mandatory `shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*` verification output after final write. A literal self-hash embedded in the same file would change the file digest; the verification section below is the authoritative current manifest hash check.

## Verification Commands To Run
```bash
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*
rg -n "schwgw\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

## Open Issues
- These are production artifacts for review, not final paper/journal claims.
- No source, tests, configs, physics conventions, thresholds, lmax, or accepted Phase 4/pilot artifacts were intentionally modified in T8ah.

## Exact Next T7bj Prompt
```text
你现在是 T7bj。请读取并严格执行 docs/prompts/phase5_t7bj_fig3_four_frequency_dx0p25_production_review.md。
重点审查 T8ah 生成的 runs/phase5/fig3_four_frequency_dx0p25_production/ 是否满足 four-frequency dx=0.25M production artifact gate：四个频率是否 fresh 生成且未复用 kM=2 pilot；NPZ/run JSON/grid/mask/finite/NaN/final-pair/Q018/radial-cache 是否完整；nearest audit 与 bilinear display-only sidecar provenance 是否足以阻止误用；plotting 是否 read-only；manifest/hash/test/evidence 是否完整；并给出 GREEN/YELLOW/RED 结论。
```
