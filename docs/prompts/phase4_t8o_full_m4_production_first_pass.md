# Phase 4 T8o Prompt: Full M4-Production First-Pass Fig.3 Run

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8o`。

## 0. 任务定位

T7x 已通过 production schema/output hardening review，并建议打开 full
M4-production first-pass run。本 slice 执行第一批 journal-grade Fig.3-style
finite-radius wave-field production artifacts。

Scope is strictly:

- `kM=[0.5,1.0,1.5,2.0]`;
- `x/M,z/M in [-30,30]`;
- `dx=dz=0.5M`, range-based config, expected `121x121`;
- saved complex NPZ output plus read-only `2x4` panel at `dpi=300`;
- no `kM=4`, no R60_K2/R60_K4, no transmission.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/phase4_closeout.md`
4. `docs/m4_production_plan.md`
5. `docs/architecture.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/physics_spec.md`
9. `docs/equation_map.md`
10. `docs/prompts/phase4_t8n_production_schema_output_hardening.md`
11. `docs/prompts/phase4_t7x_production_schema_output_review.md`
12. Existing production template: `configs/li_fig3_xz_production_k2p0_dx0p5_template.yaml`

Before task actions, check installed plugins/connectors/skills. For figure
export/layout requirements, use `scientific-visualization` guidance if
available and record it in `status.md`.

## 2. Required Outputs

Create or update production configs:

```text
configs/li_fig3_xz_production_k0p5_dx0p5.yaml
configs/li_fig3_xz_production_k1p0_dx0p5.yaml
configs/li_fig3_xz_production_k1p5_dx0p5.yaml
configs/li_fig3_xz_production_k2p0_dx0p5.yaml
```

The configs must use `x_range/z_range`, not hand-written coordinate arrays.
Use the same physical amplitudes, boundary settings, convergence thresholds,
and lmax windows as the accepted T8l/M4-lite runs, except for the `dx=0.5M`
range grid.

Expected outputs:

```text
/tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz
/tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz
/tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz
/tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png.json
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf
/tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf.json
```

## 3. Production Run Commands

Run sequentially and record runtime for each frequency:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k0p5_dx0p5.yaml --out /tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k1p0_dx0p5.yaml --out /tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k1p5_dx0p5.yaml --out /tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_production_k2p0_dx0p5.yaml --out /tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz
```

Then generate read-only panels:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel \
  /tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz \
  --quantity real \
  --interpolation nearest \
  --dpi 300 \
  --out /tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.png

PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel \
  /tmp/t8o_li_fig3_xz_k0p5_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k1p0_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k1p5_dx0p5.npz \
  /tmp/t8o_li_fig3_xz_k2p0_dx0p5.npz \
  --quantity real \
  --interpolation nearest \
  --dpi 300 \
  --out /tmp/t8o_li_fig3_production_panel_real_nearest_300dpi.pdf
```

## 4. Required Checks

For each NPZ:

- shape is `121x121`;
- expected valid/invalid counts are `14592/49`;
- valid `h_plus/h_cross` are finite complex values;
- invalid fields are complex NaN;
- expanded coordinate arrays are saved;
- final adjacent pair passes;
- cache unique count is plausible and does not scale with grid points;
- radial warnings are JSON-safe;
- for `kM=2.0`, `evanescent_tail_suppressed` warnings cover current
  `rmax=sqrt(30^2+30^2)`.

For panels:

- sidecar source paths are exactly the four T8o NPZ files in
  `kM=[0.5,1.0,1.5,2.0]` order;
- `requested_dpi=300`;
- `output_format` is `png` or `pdf`;
- row-wise symmetric color scales are recorded;
- final pairs and final-pair pass flags are recorded;
- horizon/light-ring overlays and frozen convention metadata are recorded;
- plotting is read-only over saved results.

## 5. Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a metadata inspection script over all T8o artifacts and a static scan:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

## 6. Stop Conditions

Stop and update `status.md` if:

- any single frequency exceeds 75 minutes without output;
- total run time exceeds 4 hours;
- a final adjacent pair fails;
- valid fields are non-finite;
- `kM=2.0` Q018 `valid_until_r` does not cover the full domain;
- plotting imports solver/physics code;
- tests fail;
- any task would require modifying T2-T6 physics, radial solver behavior,
  thresholds, or accepted `lmax` windows.

Do not substitute lower resolution or fewer frequencies and call it production.
If a partial set completes before a stop condition, record it as partial only.

## 7. status.md Update Requirements

Record changed files, configs, commands, per-frequency runtimes, artifact paths,
metadata summary, test results, open issues, and whether T7y may review.

If all required outputs are produced and checks pass, next prompt:

```text
你现在是 T7y。请读取并严格执行 docs/prompts/phase4_t7y_full_m4_production_review.md。
```
