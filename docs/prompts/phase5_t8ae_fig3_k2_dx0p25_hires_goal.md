# Phase 5 T8ae Goal Prompt: Fig.3 kM=2 dx=0.25 High-Resolution Pilot

You are T8ae: visualization/CLI production-run thread for a bounded Fig.3 high-resolution saved-data pilot.

Use Codex Goal mode for this task.

Goal objective:

```text
Generate and validate one bounded Fig.3 high-resolution production pilot at kM=2.0, dx=dz=0.25M, x/M,z/M in [-30,30], using the existing Route B/M4 production path, with saved NPZ, provenance JSON, read-only plots, dx=0.5M comparison metadata, status update, and T8 handoff. Do not expand to four frequencies, dx=0.2M, kM=4, R60, Fig.2 strict Psi4, fixtures, or paper-level claims.
```

## Required Reads

Read, in order:

1. `project.md`
2. `status.md`
3. `docs/handoffs/README.md`
4. `docs/handoffs/T0_current.md`
5. `docs/handoffs/T7_current.md`
6. `docs/handoffs/T8_current.md`
7. `docs/handoffs/T10_current.md`
8. `docs/physics_spec.md`
9. `docs/equation_map.md`
10. `docs/numerics.md`
11. `docs/validation_plan.md`
12. `docs/phase4_production_closeout.md`
13. `docs/m4_production_plan.md`
14. `references/notes/t10d_li_hou_zhao_figure_inventory.md`
15. `references/notes/t10h_fig2_fig3_journal_readiness.md`
16. `configs/li_fig3_xz_production_k2p0_dx0p5.yaml`
17. `runs/phase4/m4_production_first_pass/manifest.md`
18. `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz`

Before task actions, check installed plugins/connectors/skills. Use only directly relevant skills. For figure export/layout, use `scientific-visualization` if available and record it in `status.md`.

## Allowed Scope

You may create:

- `configs/li_fig3_xz_production_k2p0_dx0p25_pilot.yaml`
- files under `runs/phase5/fig3_k2_dx0p25_hires_pilot/`

You may update:

- `status.md`
- `docs/handoffs/T8_current.md`

You may modify source/tests only if a blocking bug in existing CLI/config handling prevents the authorized run. If you modify source/tests, keep changes minimal, add focused tests, and run full pytest. Prefer no source changes.

## Required Config

Create the config from the accepted `dx=0.5M` kM=2 config, changing only:

```yaml
case_id: LI_FIG3_XZ_K2P0_DX0P25_HIRES_PILOT
output: runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz
observer:
  kind: xz_plane
  x_range:
    start: -30.0
    stop: 30.0
    step: 0.25
    endpoint: true
  z_range:
    start: -30.0
    stop: 30.0
    step: 0.25
    endpoint: true
  invalid_radius_policy: mask
```

Keep:

- `M=1.0`
- `kM=2.0`
- `A_plus=0.9+1.1i`
- `A_cross=0.4+0.6i`
- `lmax=180`
- `lmax_values=[108,132,156,180]`
- boundary tolerances and convergence thresholds from the accepted `dx=0.5M` config.

Expected grid shape:

```text
241 x 241
```

Expected maximum domain radius:

```text
rmax = sqrt(30^2 + 30^2) = 42.42640687119285 M
```

## Required Outputs

Create under:

```text
runs/phase5/fig3_k2_dx0p25_hires_pilot/
```

Minimum required files:

```text
t8ae_li_fig3_xz_k2p0_dx0p25.npz
t8ae_li_fig3_xz_k2p0_dx0p25.run.json
t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png
t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png.json
t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png
t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png.json
t8ae_li_fig3_xz_k2p0_dx0p25_vs_dx0p5_common_grid_comparison.json
t8ae_li_fig3_xz_k2p0_dx0p25_manifest.md
```

Nearest is the audit plot. Bilinear is a labeled display-only publication-style render; it is not numerical evidence.

## Required Run Commands

Run the solver once, with timing:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run \
  configs/li_fig3_xz_production_k2p0_dx0p25_pilot.yaml \
  --out runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz
```

Generate plots read-only from the saved NPZ:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel \
  runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz \
  --quantity real \
  --interpolation nearest \
  --dpi 300 \
  --out runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_nearest_300dpi.png

PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel \
  runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25.npz \
  --quantity real \
  --interpolation bilinear \
  --dpi 300 \
  --out runs/phase5/fig3_k2_dx0p25_hires_pilot/t8ae_li_fig3_xz_k2p0_dx0p25_panel_real_bilinear_300dpi.png
```

Create comparison metadata by comparing the new `dx=0.25M` NPZ against the accepted source:

```text
runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
```

Compare only common grid points where both files have finite valid `h_plus` and `h_cross`. Record at minimum:

- common point count;
- max/median/RMS absolute difference for `h_plus` real part;
- max/median/RMS absolute difference for `h_cross` real part;
- max/median/RMS relative difference using `max(abs(dx0p25), abs(dx0p5), 1e-12)` denominator;
- separate invalid/mask consistency counts;
- whether the visible field changes qualitatively on the common grid.

## Required Metadata Checks

Inspect the NPZ and record:

- grid kind;
- shape `(241,241)`;
- x/z min/max/spacing;
- valid/invalid counts;
- horizon mask consistency with `r <= 2M`;
- finite valid `h_plus/h_cross`;
- complex NaNs in invalid fields;
- final adjacent pair and pass flag;
- radial cache unique/key/hit counts;
- radial warning count/codes;
- for Q018/suppressed modes, minimum `valid_until_r` and whether it covers `42.42640687119285M`;
- runtime from `/usr/bin/time`;
- file sizes and SHA-256 for every output file.

## Tests And Verification

Always run focused IO/viz tests after output generation:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
```

Run full pytest if you changed any source/test code:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run static read-only plotting check:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

## Stop Conditions

Stop and update `status.md` with a YELLOW/RED result if:

- the solver run exceeds `3 h` wall time without producing the NPZ;
- expected shape is not `(241,241)`;
- final adjacent pair fails;
- valid fields contain nonfinite values;
- invalid fields are not complex NaN under the mask policy;
- Q018 `valid_until_r` does not cover `42.42640687119285M`;
- radial warnings include an unreviewed uncovered/fail-closed code;
- the comparison against `dx=0.5M` shows a qualitative physical change that cannot be explained as resolution refinement;
- plots require solver recomputation;
- focused tests fail and cannot be fixed without source changes;
- any task would require changing T2-T6 physics, frozen conventions, thresholds, `lmax` policy, or radial solver behavior;
- any output or status text claims final journal-grade or paper-level Fig.3 acceptance.

If partial artifacts exist when stopping, label them partial and do not call them accepted.

## Forbidden Actions

Do not:

- run `kM=0.5,1.0,1.5` at `dx=0.25M`;
- run `dx=0.2M`;
- run `kM=4`;
- run R60/R60_K4;
- generate Fig.2 strict `Psi4` data;
- generate fixtures;
- modify frozen Fourier/harmonic/tetrad/RW/Zerilli/Route B conventions;
- change thresholds or `lmax_values`;
- label the result as final journal-grade or paper-level.

## Status And Handoff

Update `status.md` with:

- changed files;
- commands run;
- runtime;
- artifact paths and hashes;
- metadata summary;
- focused/full test results;
- open issues;
- next action.

Update `docs/handoffs/T8_current.md` with:

- current status;
- generated artifacts;
- hashes;
- required reads for the next T8;
- forbidden actions;
- exact next task for T7.

If all required outputs exist and checks pass, final next action:

```text
你现在是 T7bg。请读取并严格执行 docs/prompts/phase5_t7bg_fig3_k2_dx0p25_hires_review.md。
```

## Final Labels

Use one of:

- `GREEN / READY FOR T7bg FIG3 K2 DX0.25 HIRES PILOT REVIEW`
- `YELLOW / PARTIAL FIG3 K2 DX0.25 HIRES PILOT WITH NAMED RISKS`
- `RED / FIG3 K2 DX0.25 HIRES PILOT BLOCKED`
