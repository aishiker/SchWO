# Phase 4 T7q Prompt: Fig.3-Lite Visual Panel Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7q`。

## 启动条件

- 只在 T8h 完成后启动。
- 如果 `/tmp/t8h_fig3_lite_panel_real.png` 或 its sidecar is missing, do not implement the plotter yourself; record blocker and return to T8/T0.

## 先读

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/numerics.md`
5. `docs/validation_plan.md`
6. `docs/prompts/phase4_t8h_fig3_visual_panel.md`
7. `docs/prompts/phase4_t8g_li_fig3_lite_xz_benchmark.md`
8. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
9. T8h-changed `src/schwgw/viz/results.py`
10. T8h-changed `src/schwgw/cli.py`
11. T8h-changed tests

## 目标

Independently review that T8h added a read-only Fig.3-lite visual panel without changing physics:

- panel reads saved `.npz`/`.h5` results only;
- no solver or physics imports in `src/schwgw/viz/*`;
- panel shows `real(h_plus)` and `real(h_cross)` from x-z saved result;
- invalid points are masked;
- color scale is shared and symmetric around zero;
- event horizon and light-ring overlays are derived from saved `M`;
- sidecar JSON records plot provenance, overlays, color scale, and conventions;
- existing plot commands still work.

## 允许修改

- `tests/regression/*` only for lightweight review tests if useful
- `docs/validation_plan.md` only for review checklist wording
- `status.md`

原则上不要修改 `src/`、configs、or artifacts. If implementation is wrong, record exact failure and return to T8h/T0.

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 IO schema unless T8h already did and you are documenting a failure.
- 不修改 radial solver equations/boundaries/thresholds。
- 不修改 Wigner-D/angular code。
- 不改变 conventions。
- 不运行 solver。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor。
- 不生成 multi-frequency Fig.3 panel。

## Review Checklist

1. CLI and output review
   - Confirm `plot-fig3-panel` or equivalent documented command exists.
   - Run it on `/tmp/t8g_r60_k1_li_fig3_lite_xz.npz`.
   - If HDF5 artifact exists, run it on `/tmp/t8g_r60_k1_li_fig3_lite_xz.h5`.
   - Confirm PNGs and sidecars exist and are non-empty.

2. Sidecar review
   - Confirm sidecar includes:
     - `plot_type="fig3_lite_panel"`;
     - `grid_kind="xz_plane"`;
     - `components=["h_plus","h_cross"]`;
     - `quantity="real"`;
     - `case_id`;
     - `kM`;
     - `lmax`;
     - x/z ranges;
     - valid/invalid counts;
     - `symmetric_color_scale=true`;
     - finite `color_vmin/color_vmax` with `color_vmin < 0 < color_vmax`;
     - overlay metadata with event horizon radius `2M` and light-ring radius `3M`;
     - convention metadata.

3. Visual sanity
   - Open or inspect PNG dimensions and file size.
   - Confirm it is a two-panel figure, not a single component plot.
   - Confirm axes are x and z.
   - Confirm a central masked/overlay region is visible for the accepted T8g result.

4. Read-only boundary
   - Scan `src/schwgw/viz/*`.
   - Confirm no imports from:
     - `schwgw.scattering`
     - `schwgw.perturbations`
     - `schwgw.angular`
     - `schwgw.numerics`
     - `schwgw.backgrounds`
   - Confirm plot command does not call `compute_polarization(...)`, `run_solver_grid(...)`, or radial solver functions.

5. Regression safety
   - Existing `plot-wavefield` and `plot-convergence` still pass.
   - Fast tests do not depend on real `/tmp/t8g...` artifacts.
   - No T2-T6 source changes occurred.

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --quantity real --out /tmp/t7q_fig3_lite_panel_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If HDF5 artifact exists:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8g_r60_k1_li_fig3_lite_xz.h5 --quantity real --out /tmp/t7q_fig3_lite_panel_real_h5.png
```

Run a sidecar inspection script and record:

- PNG sizes;
- plot type;
- components;
- color limits;
- overlay radii;
- read-only scan result.

## Stop Conditions

Stop and report to T0 if:

- panel command is missing or requires solver recomputation;
- PNG/sidecar missing or empty;
- sidecar omits overlay/color-scale/provenance metadata;
- color scale is not symmetric for real fields;
- event horizon/light-ring radii are not derived from saved `M`;
- plotting imports/calls physics solver;
- tests fail outside T7q review scope;
- docs/status overstate this as full multi-frequency Fig.3 reproduction.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- test results;
- plot artifact review;
- sidecar metadata review;
- read-only boundary result;
- open issues;
- go/no-go:
  - If passed: T0 may consider multi-frequency Fig.3 extension as a later expensive benchmark slice.
  - If failed: return to T8h with exact failure mode.
