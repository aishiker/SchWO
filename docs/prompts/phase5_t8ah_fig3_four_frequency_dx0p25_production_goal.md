# Phase 5 T8ah Prompt: Fig.3 Four-Frequency dx=0.25M Production Goal

你现在是 **T8ah：Fig.3 four-frequency dx=0.25M production run**。

## Mode

Use Goal mode. This is a long-running production task. Continue until all required artifacts are generated and checked, or until a stop condition is reached.

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/phase5_fig3_four_frequency_dx0p25_production_plan.md`
7. `docs/phase5_fig3_k2_dx0p25_hires_pilot_closeout.md`
8. `docs/prompts/phase5_t8ag_fig3_four_frequency_dx0p25_production_plan.md`
9. `docs/prompts/phase5_t7bi_fig3_four_frequency_dx0p25_plan_review.md`
10. `configs/li_fig3_xz_production_k0p5_dx0p25.yaml`
11. `configs/li_fig3_xz_production_k1p0_dx0p25.yaml`
12. `configs/li_fig3_xz_production_k1p5_dx0p25.yaml`
13. `configs/li_fig3_xz_production_k2p0_dx0p25.yaml`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that are actually helpful for this local production/artifact task.

## Goal

Run the reviewed **Option A** production path:

```text
kM = [0.5, 1.0, 1.5, 2.0]
dx = dz = 0.25M
x/M, z/M in [-30, 30]
Route B/M4 production path
output dir = runs/phase5/fig3_four_frequency_dx0p25_production/
```

All four frequencies must be freshly generated under the unified output directory. Do not reuse the accepted `kM=2` pilot by reference unless T0/T7 explicitly changes this prompt.

## Strict Scope

Allowed:

- Run only these solver configs:
  - `configs/li_fig3_xz_production_k0p5_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k1p0_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k1p5_dx0p25.yaml`
  - `configs/li_fig3_xz_production_k2p0_dx0p25.yaml`
- Generate artifacts only under:
  - `runs/phase5/fig3_four_frequency_dx0p25_production/`
- Generate per-frequency:
  - NPZ;
  - run JSON;
  - nearest audit PNG plus sidecar;
  - bilinear display-only PNG plus sidecar if nearest path is healthy.
- Generate archive-level:
  - four-frequency nearest audit PNG plus sidecar;
  - four-frequency bilinear display-only PNG plus sidecar if nearest archive panel is healthy;
  - `manifest.md`.
- Update:
  - `status.md`
  - `docs/handoffs/T8_current.md`

Forbidden:

- Do not modify `src/`.
- Do not modify tests.
- Do not modify configs.
- Do not modify accepted Phase 4 artifacts.
- Do not modify `runs/phase5/fig3_k2_dx0p25_hires_pilot/`.
- Do not use Option B/by-reference reuse of the T8ae/T8af `kM=2` pilot.
- Do not run `dx=0.2M`.
- Do not run `kM=4`.
- Do not run R60/R60_K4.
- Do not generate Fig.2 strict `Psi4`.
- Do not create fixtures.
- Do not run dense Fig.5/Fig.6 scans.
- Do not implement Kirchhoff or Appendix D/E curves.
- Do not change Fourier, harmonic, tetrad, RW/Zerilli, Route B polarization, thresholds, `lmax`, or boundary tolerances.
- Do not make paper-level or final journal-grade claims.

## Required Production Commands

Use `/usr/bin/time -p` for each solver run and record real/user/sys times.

Run in increasing frequency order:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k0p5_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k1p0_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k1p5_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k2p0_dx0p25.yaml --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz
```

After each frequency, immediately inspect the new NPZ and run JSON before starting the next solver run.

## Required Per-Frequency Checks

For every frequency, verify and record:

- NPZ exists and is project-local;
- run JSON exists;
- `case_id` matches config;
- `M=1.0`;
- `kM` matches the intended frequency;
- amplitudes are `A_plus=0.9+1.1i`, `A_cross=0.4+0.6i`;
- grid shape is `(241,241)`;
- x/z range is `[-30,30]`;
- x/z spacing is `0.25M`;
- valid/invalid mask exactly follows `r > 2M`;
- valid `h_plus/h_cross` are finite complex values;
- invalid `h_plus/h_cross` are complex NaN;
- final adjacent pair is `[156,180]`;
- final pair passed;
- radial cache metadata is present;
- Q018/radial warnings are present as structured metadata, even when warning count is zero;
- any `evanescent_tail_suppressed` warning covers `rmax=42.42640687119285M`;
- any missing Q018 summary, uncovered warning, unknown warning code, or final-pair failure is a stop condition.

## Plotting Commands

After all four NPZ/run JSON pairs pass per-frequency checks, generate read-only plots from saved NPZs only.

Per-frequency nearest audit plots:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25_panel_real_nearest_300dpi.png --dpi 300
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25_panel_real_nearest_300dpi.png --dpi 300
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25_panel_real_nearest_300dpi.png --dpi 300
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz --quantity real --interpolation nearest --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png --dpi 300
```

Archive-level nearest audit panel:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k0p5_dx0p25.npz \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p0_dx0p25.npz \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k1p5_dx0p25.npz \
  runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_k2p0_dx0p25.npz \
  --quantity real --interpolation nearest \
  --out runs/phase5/fig3_four_frequency_dx0p25_production/t8ah_li_fig3_xz_four_frequency_dx0p25_panel_real_nearest_300dpi.png \
  --dpi 300
```

Bilinear display-only plots are allowed after nearest plots pass. They must be labeled display-only and must not be treated as numerical evidence.

## Required Sidecar Hardening

The built-in plotting sidecars may not contain all T8af provenance fields. After plotting, inspect and harden every generated PNG sidecar in place so each sidecar has explicit keys for:

- `source_result_path` or `source_result_paths`;
- source result SHA-256 and size for every source NPZ;
- run JSON path for every source NPZ;
- Q018 warning summary for every source NPZ;
- interpolation policy;
- final lmax pair and pass status;
- grid spacing;
- requested DPI;
- valid/invalid counts;
- convention metadata;
- `not_paper_level_claim: true`;
- `not_final_journal_grade: true`;
- `four_frequency_dx025_production: true` for archive-level four-frequency plots;
- `dx02_production: false`;
- `kM4_production: false`;
- `R60_production: false`;
- `fig2_strict_psi4_artifact: false`.

For per-frequency sidecars, use a clear scope flag such as:

```json
"per_frequency_member_of_four_frequency_dx025_production": true
```

Do not use `single_frequency_resolution_evidence_only=true` for the new T8ah production artifacts, because these are members of the four-frequency production set.

## Manifest Requirements

Create:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md
```

It must include:

- scope and non-claims;
- all commands run;
- solver runtime per frequency;
- artifact list;
- SHA-256 and sizes for configs, NPZs, run JSONs, PNGs, sidecars, and manifest;
- per-frequency grid/mask/finite/final-pair/Q018 summaries;
- radial cache summaries;
- plotting interpolation policy;
- focused test results;
- open issues;
- exact next T7bj review prompt.

## Verification Commands

Run:

```bash
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Also run an independent Python inspection over the four NPZs, four run JSONs, generated sidecars, and manifest. The inspection must not import solver/scattering/radial/physics APIs.

Full pytest is required only if source/tests changed. Source/tests must not change in this slice.

## Stop Conditions

Stop and record YELLOW/RED if:

- any solver command exits nonzero;
- any single solver run exceeds `3 h` real time without a clear completed artifact and status record;
- total production run exceeds `10 h` real time without T0/T7 re-approval;
- final adjacent pair `[156,180]` fails for any frequency;
- Q018 coverage fails or warning metadata is missing/ambiguous;
- valid/invalid mask policy fails;
- valid fields contain nonfinite values;
- invalid fields are not complex NaN;
- output goes outside `runs/phase5/fig3_four_frequency_dx0p25_production/`;
- plotting imports or calls solver/scattering/radial/physics APIs;
- any source/test/convention/threshold/`lmax` change is needed;
- any artifact or status text claims paper-level or final journal-grade acceptance.

If a later frequency fails after earlier frequencies succeeded, keep the earlier artifacts, write a manifest/status entry clearly marking the archive incomplete, and stop for T7 review.

## Required Updates

Update `status.md` with:

- changed/generated files;
- commands run;
- solver runtimes;
- per-frequency numerical summaries;
- sidecar hardening result;
- test/check results;
- open issues;
- exact next action for T7bj.

Update `docs/handoffs/T8_current.md` with:

- current state after T8ah;
- completed artifacts or stop reason;
- hashes and core numerical facts;
- forbidden actions;
- exact T7bj review prompt;
- definition of done for T7bj.

## Definition of Done

- Four fresh NPZ/run JSON pairs exist under the unified production directory.
- All four frequencies pass final pair `[156,180]`, mask, finite/NaN, and Q018 checks.
- Required nearest audit plots and hardened sidecars exist.
- Optional bilinear plots are either generated and labeled display-only or explicitly skipped with reason.
- Manifest/status/T8 handoff are updated.
- Focused viz/plot tests pass, or a clear stop reason is recorded.
- T7 can review with:

```text
你现在是 T7bj。请读取并严格执行 docs/prompts/phase5_t7bj_fig3_four_frequency_dx0p25_production_review.md。
```
