# Phase 5 T7bj Prompt: Fig.3 Four-Frequency dx=0.25M Production Review

你现在是 **T7bj：Fig.3 four-frequency dx=0.25M production artifact review**。

## Must Read First

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/phase5_fig3_four_frequency_dx0p25_production_plan.md`
6. `docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md`
7. `runs/phase5/fig3_four_frequency_dx0p25_production/manifest.md`
8. The four reviewed configs:
   - `configs/li_fig3_xz_production_k0p5_dx0p25.yaml`
   - `configs/li_fig3_xz_production_k1p0_dx0p25.yaml`
   - `configs/li_fig3_xz_production_k1p5_dx0p25.yaml`
   - `configs/li_fig3_xz_production_k2p0_dx0p25.yaml`

Before doing task work, check whether installed plugins/skills are relevant. Use only those that help with local artifact review.

## Goal

Independently review whether T8ah produced a valid Fig.3 four-frequency `dx=0.25M` production archive under:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
```

This is review-only. Do not run production.

## Review Requirements

Verify:

1. Scope:
   - exactly `kM=[0.5,1.0,1.5,2.0]`;
   - `dx=dz=0.25M`;
   - `x/z in [-30,30]`;
   - Route B/M4 production path;
   - Option A rerun-all-four, not by-reference reuse of the T8ae/T8af pilot.
2. Artifact integrity:
   - four NPZ files exist;
   - four run JSON files exist;
   - required nearest audit PNGs and sidecars exist;
   - manifest exists and lists all hashes/sizes;
   - no output is outside the production directory.
3. Per-frequency numerical facts:
   - case IDs and config paths match;
   - shape `(241,241)`;
   - valid/invalid mask follows `r > 2M`;
   - valid `h_plus/h_cross` fields are finite;
   - invalid fields are complex NaN;
   - final adjacent pair `[156,180]`;
   - final pair passed;
   - radial cache metadata present;
   - Q018 warning summaries present.
4. Q018:
   - any `evanescent_tail_suppressed` warning covers `rmax=42.42640687119285M`;
   - unknown or uncovered warning codes are not accepted;
   - lower-frequency zero-warning cases still record explicit warning metadata.
5. Plotting:
   - plotting reads saved NPZ only;
   - nearest is audit/numerical provenance;
   - bilinear, if present, is display-only and not numerical evidence;
   - sidecars include source NPZ SHA/size, run JSON path, Q018 summary, interpolation policy, final pair, grid spacing, DPI, valid/invalid counts, convention metadata, and non-claim flags.
6. Scope boundaries:
   - no `src/` or test changes;
   - no config changes beyond already reviewed configs;
   - no accepted artifact mutation;
   - no `dx=0.2M`, `kM=4`, R60/R60_K4, Fig.2 strict `Psi4`, fixtures, Kirchhoff, Appendix D/E curves, dense Fig.5/Fig.6 scans, or paper-level/final-journal claim.

## Commands / Checks

Run:

```bash
find runs/phase5/fig3_four_frequency_dx0p25_production -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_four_frequency_dx0p25_production/*
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
find src tests -type f -newer docs/prompts/phase5_t8ah_fig3_four_frequency_dx0p25_production_goal.md -print | sort
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Run an independent Python inspection over the four NPZs, run JSONs, plot sidecars, and manifest. Do not import solver/scattering/radial/angular/physics APIs.

Full pytest is required only if source/tests changed. If source/tests changed, treat that as a scope issue and run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Decision Labels

Use one of:

- **ACCEPT GREEN / FOUR-FREQUENCY DX0.25 PRODUCTION ARCHIVE ACCEPTED**:
  all four frequencies and required artifacts pass integrity, convergence, Q018, mask, finite, plotting, sidecar, and scope checks.
- **ACCEPT YELLOW / PARTIAL OR NONFINAL PRODUCTION ARCHIVE WITH NAMED RISKS**:
  no unsafe artifact mutation occurred, but some required artifact/metadata/plot/test condition is incomplete. Say exactly what blocks closeout.
- **RED / PRODUCTION INTEGRITY OR SCOPE FAILURE**:
  source/tests/conventions changed without authorization, accepted artifacts were mutated, Q018/final-pair/mask/finite checks fail, or production scope was exceeded.

## Required Updates

Update only:

- `status.md`
- `docs/handoffs/T7_current.md`

Record:

- files inspected;
- commands/checks run;
- decision label;
- artifact hashes and key numerical facts;
- whether a future closeout prompt can be scheduled;
- remaining gates and forbidden actions.

## Next-Step Guidance

If GREEN:

- Recommend T0 schedule a closeout/documentation prompt for the four-frequency `dx=0.25M` Fig.3 archive.
- Do not claim final journal-grade or paper-level reproduction unless a later T10/T7 figure-quality review explicitly accepts that claim.

If YELLOW:

- Provide the exact narrow T8 follow-up prompt needed to fix the artifact/metadata gap.

If RED:

- Stop and recommend artifact integrity triage before any new computation.
