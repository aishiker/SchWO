# Phase 5 T7bg Prompt: Fig.3 kM=2 dx=0.25 High-Resolution Pilot Review

You are T7bg: independent validation/review for the T8ae Fig.3 high-resolution production pilot.

This is a review-only slice. Do not rerun the solver. Do not modify `src`, tests, configs, artifacts, or `runs/`.

## Required Reads

Read, in order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T7_current.md`
5. `docs/handoffs/T8_current.md`
6. `docs/handoffs/T10_current.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. `docs/numerics.md`
10. `docs/validation_plan.md`
11. `docs/phase4_production_closeout.md`
12. `docs/m4_production_plan.md`
13. `references/notes/t10h_fig2_fig3_journal_readiness.md`
14. `docs/prompts/phase5_t8ae_fig3_k2_dx0p25_hires_goal.md`
15. `configs/li_fig3_xz_production_k2p0_dx0p25_pilot.yaml`
16. T8ae output files under `runs/phase5/fig3_k2_dx0p25_hires_pilot/`
17. Accepted comparison source `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz`

Before task actions, check installed plugins/connectors/skills. Use only directly relevant skills and record them in `status.md`.

## Allowed Updates

You may update only:

- `status.md`
- `docs/handoffs/T7_current.md`

## Required Artifacts

Review exactly these expected outputs:

```text
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.run.json
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png.json
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png.json
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_vs_dx0p5_common_grid_comparison.json
runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_manifest.md
```

## Review Checklist

For the config and NPZ:

- `case_id == LI_FIG3_XZ_K2P0_DX0P25_HIRES_PILOT`.
- `kM=2.0`, `M=1.0`, `A_plus=0.9+1.1i`, `A_cross=0.4+0.6i`.
- `x/z` domain is exactly `[-30,30]`.
- spacing is exactly `0.25M`.
- shape is `(241,241)`.
- valid/invalid mask matches `r > 2M`.
- valid `h_plus/h_cross` values are finite complex values.
- invalid `h_plus/h_cross` values are complex NaN.
- final adjacent pair and pass flag are present and pass.
- radial cache metadata is plausible and does not scale as if a new radial solve occurred for every grid point.
- Q018/suppressed-mode metadata, if present, covers `rmax=42.42640687119285M`.

For plots:

- both nearest and bilinear PNGs exist and are nonblank;
- nearest is labeled/recorded as the audit plot;
- bilinear is labeled/recorded as display-only, not numerical evidence;
- sidecars record source NPZ path/SHA/size, interpolation, requested DPI, quantity, components, grid spacing, final pair, Q018 summary, and no-paper-level/no-final-journal flags.

For comparison:

- comparison JSON references the accepted `dx=0.5M` source by path/SHA/size.
- common-grid point count is correct for `dx=0.5M` valid points.
- max/median/RMS absolute and relative differences are finite.
- mask consistency is reported.
- qualitative-change statement is present and defensible from the numbers.

For scope:

- no `kM=0.5,1.0,1.5` `dx=0.25M` artifacts were generated;
- no `dx=0.2M`;
- no `kM=4`;
- no R60/R60_K4;
- no Fig.2 strict `Psi4` data;
- no fixtures;
- no final journal-grade or paper-level acceptance claim.

## Required Commands

Run:

```bash
find runs/phase5/fig3_k2_dx0p25_hires_pilot -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig3_k2_dx0p25_hires_pilot/*
rg -n "kM=4|dx=0\\.2|strict Psi4|paper-level|final journal-grade|R60|fixture" runs/phase5/fig3_k2_dx0p25_hires_pilot docs/handoffs/T8_current.md status.md || true
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Run an independent Python inspection script over the NPZ, plot sidecars, run JSON, and comparison JSON. Do not call project solver APIs from the inspection script.

Run full pytest only if T8ae changed source/tests:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Stop Conditions

Stop and mark RED if:

- any required artifact is missing;
- shape/domain/spacing is wrong;
- final adjacent pair fails;
- valid fields are nonfinite;
- invalid fields are not masked/NaN as required;
- Q018 coverage does not cover `rmax`;
- comparison metadata is missing or nonfinite;
- forbidden scope artifacts exist;
- tests fail;
- source/convention/threshold/lmax policy changed without authorization;
- output claims final journal-grade or paper-level acceptance.

## Decision Labels

Use one of:

- `ACCEPT GREEN / FIG3 K2 DX0.25 HIRES PILOT ACCEPTED AS RESOLUTION EVIDENCE ONLY`
- `ACCEPT YELLOW / FIG3 K2 DX0.25 HIRES PILOT ACCEPTED WITH NAMED RISKS`
- `REJECT RED / FIG3 K2 DX0.25 HIRES PILOT FAILED`

If GREEN/YELLOW, recommend whether T0 should:

1. schedule a read-only closeout of the single-frequency pilot;
2. schedule a four-frequency `dx=0.25M` production plan;
3. request a publication-rendering-only pass over accepted `dx=0.5M`/`dx=0.25M` data;
4. pause and return to Fig.2 strict `Psi4` convention/API design.
