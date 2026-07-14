# T8 Current Handoff

Last updated: 2026-07-08

## Thread Role And Status

T8ah completed the Fig.3 four-frequency `dx=0.25M` production run.

Decision:

```text
GREEN / READY FOR T7bj ARTIFACT REVIEW
```

## Completed Work

- Read and followed
  `docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md`.
- Used Goal mode.
- Read/applied the relevant local project context and the
  `scientific-visualization` and `verification-before-completion` skills.
- Ran the four reviewed configs in increasing `kM`:
  - `configs/li_fig3_xz_production_k0p5_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k1p0_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k1p5_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k2p0_dx0p25.yaml`
- Generated all artifacts under:
  - `runs/phase5/fig3_four_frequency_dx0p25_production/`
- Updated:
  - `status.md`
  - `docs/handoffs/T8_current.md`

## Scope Boundary

This was a production artifact generation slice using T7bi-reviewed Option A.
All four frequencies were freshly generated in one unified output directory.

Not done:

- did not reuse the accepted `kM=2.0` pilot by reference;
- did not modify `src/`;
- did not modify tests;
- did not modify configs;
- did not modify accepted Phase 4 artifacts;
- did not modify `runs/phase5/fig3_k2_dx0p25_hires_pilot/`;
- did not run `dx=0.2M`, `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`,
  fixtures, dense Fig.5/Fig.6, Kirchhoff, or Appendix D/E curves;
- did not make paper-level or final journal-grade claims.

Still forbidden / gated:

- `dx=0.2M`
- `kM=4`
- R60/R60_K4
- Fig.2 strict `Psi4`
- fixtures
- dense Fig.5/Fig.6 scans
- Kirchhoff / Appendix D/E curves
- source/test/convention/threshold/`lmax` changes
- paper-level or final journal-grade claims

## Solver Outputs

| kM | NPZ | run JSON | real/user/sys seconds |
|---:|---|---|---:|
| 0.5 | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz` | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.run.json` | `3856.02/3831.23/16.11` |
| 1.0 | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz` | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.run.json` | `3903.89/3891.06/8.50` |
| 1.5 | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz` | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.run.json` | `4031.59/4026.43/5.02` |
| 2.0 | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz` | `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.run.json` | `4137.05/4132.50/4.68` |

Total solver real time: `15928.55 s`, about `4.43 h`, below the `10 h`
T8ah gate.

## Numerical Gate Summary

All four NPZ/run JSON artifacts passed the following checks:

- `case_id` matches config.
- `M=1.0`.
- `kM` matches the config.
- `A_plus=0.9+1.1i`, `A_cross=0.4+0.6i`.
- `shape=(241,241)`.
- `x/M,z/M in [-30,30]`, spacing `0.25`.
- `valid_mask == (r > 2M)` exactly.
- Valid `h_plus/h_cross` fields are finite complex values.
- Invalid `h_plus/h_cross` fields are complex NaN.
- Final adjacent pair is `[156,180]` and passes.
- Radial cache metadata is present and enabled.
- Q018/radial warnings are structured even when count is zero.

Q018 details:

- `kM=0.5,1.0,1.5`: warning count `0`, codes `[]`, covers rmax `True`.
- `kM=2.0`: warning count `56`, code `evanescent_tail_suppressed`,
  ell range `153..180`, sectors `even/odd`,
  `rmax=42.42640687119285`,
  min `valid_until_r=42.472089355131786`,
  margin `0.045682483938932705`, covers rmax `True`.

Radial cache summary for all four runs:

- enabled `True`
- `key_count=358`
- `unique_solution_count=358`
- `hit_count=20735842`

## Plot Artifacts

Per-frequency nearest audit PNGs:

- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_nearest_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_nearest_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_nearest_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png`

Per-frequency bilinear display-only PNGs:

- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_bilinear_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_bilinear_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_bilinear_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png`

Archive-level panels:

- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png`
- `runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png`

All ten PNG sidecars were hardened in place. Each sidecar carries source NPZ
path/SHA/size, run JSON path, Q018 summary, interpolation policy, final-pair
status, grid spacing, requested DPI, valid/invalid counts, convention metadata,
non-claim flags, and false flags for unrelated productions. No T8ah sidecar
retains `single_frequency_resolution_evidence_only`.

## Manifest

Manifest path:

- `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`

Manifest SHA256:

```text
adfc8b3079fb0d37863b00ac02b3e021c7127e6bebf811d5562e84e414b02d2e  runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
```

The manifest includes scope/non-claims, all solver commands and runtimes,
plot commands, artifact records, per-frequency gate summaries, Q018/radial
cache summaries, interpolation policy, verification commands, open issues,
and the exact T7bj review prompt.

## Key Hashes

```text
b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz
0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz
1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz
b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz
220c8e25187aa760015c92f82a0a5fd5a797765027b492e28d0e636b1cd53b4c  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_nearest_300dpi.png
777a0d451db5dc332fa57fcd74cb059412238d98c459bb268374b7fbcbd943ab  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_four_frequency_dx0p25_panel_real_bilinear_300dpi.png
```

Full hashes for all artifacts and sidecars are in `manifest.md` and in the
`shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*` output.

## Verification Commands Run

```bash
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Additional independent Python inspection:

- checked all four NPZs;
- checked all four run JSONs;
- checked all ten PNG sidecars;
- checked manifest content;
- did not import solver, scattering, radial, or physics APIs.

Results:

- Static viz check returned no matches.
- Focused pytest: `58 passed in 5.18s`.
- Independent inspection: `PASS`.

## Incomplete Work

- T7bj independent artifact review has not been run.
- These artifacts are production candidates for review, not paper-level or
  final journal-grade claims.

## Blocking Issues

No T8ah execution blocker remains.

Remaining review gate:

- T7bj must independently review the production archive before any downstream
  paper-level use or promotion.

## Must-Read Files For T7bj

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md`
6. `docs/prompts/phase5_t7bj_fig3_four_frequency_dx0p25_production_review.md`
7. `docs/phase5_fig3_four_frequency_dx0p25_production_plan.md`
8. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
9. Four `*.run.json` files under `runs/phase5/fig3_four_frequency_dx0p25_production/`
10. Ten PNG sidecars under `runs/phase5/fig3_four_frequency_dx0p25_production/`

## Exact Next Task

Send T7:

```text
你现在是 T7bj。请读取并严格执行 docs/prompts/phase5_t7bj_fig3_four_frequency_dx0p25_production_review.md。
```

## Definition Of Done For T7bj Review

- Verify all four frequencies were freshly generated under the unified
  production directory.
- Verify the accepted `kM=2.0` pilot was not used by reference as a member.
- Verify NPZ/run JSON grid, mask, finite/NaN, final-pair, radial-cache, and
  Q018 summaries.
- Verify nearest audit and bilinear display-only sidecar provenance.
- Verify plotting remains read-only and does not import solver/radial/physics
  APIs.
- Verify manifest, hashes, focused test results, and independent evidence.
- Give a GREEN/YELLOW/RED artifact-review decision.
