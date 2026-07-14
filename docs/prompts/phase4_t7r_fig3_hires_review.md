# Phase 4 T7r Prompt: Fig.3-Lite High-Resolution Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7r`。

## 启动条件

- T8i has completed or stopped with a recorded result.
- `status.md` contains the T8i record.
- If `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz` is missing, do not implement
  the benchmark yourself; record blocker and return to T8/T0.

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8i_fig3_hires_single_frequency.md`
8. `docs/prompts/phase4_t8g_li_fig3_lite_xz_benchmark.md`
9. `docs/prompts/phase4_t8h_fig3_visual_panel.md`
10. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
11. T8i-changed `configs/`, `src/schwgw/viz/results.py`,
    `src/schwgw/cli.py`, and tests

## 任务

Independently review that T8i produced a higher spatial-sampling
single-frequency Fig.3-lite result without changing physics conventions:

1. Confirm `configs/r60_k1_li_fig3_lite_xz_hires.yaml` uses the same physics
   parameters as T8g except case id, output, and `61x61` grid.
2. Confirm `x_values` and `z_values` run from `-30.0` to `30.0` with step
   `1.0`.
3. Load `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz` and verify shape
   `(61,61)`, finite valid `h_plus/h_cross`, expected invalid count `13`,
   and saved metadata consistency.
4. Verify final adjacent pair `[96,108]` passes both selected and near-axis
   thresholds.
5. Verify run-scoped radial cache statistics remain bounded by radial mode
   count, not by grid point count.
6. Verify radial warning metadata, if any, is structured and JSON-safe.
7. Run `plot-fig3-panel` with `--interpolation nearest`; verify sidecar
   records `interpolation`, `grid_spacing`, and samples per wavelength.
8. Confirm `src/schwgw/viz` remains read-only over saved results and does not
   import or call solver/physics modules.
9. Compare to the old T8g result only at the metadata level:
   - old grid `21x21`, `dx=dz=3M`, about `2.09` samples per wavelength;
   - new grid `61x61`, `dx=dz=1M`, about `6.28` samples per wavelength.
   Do not require pixel-by-pixel agreement, because the grids are different.

## 允许修改

Prefer not to modify source. You may update only:

- `status.md`
- `docs/validation_plan.md` or `docs/architecture.md` for small documentation
  corrections if T8i left a clear typo
- tests only if a T8i test needs a trivial review-scope fix and the fix does
  not change behavior

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 radial solver、angular/Wigner-D、RW/Zerilli 或 polarization
  conventions。
- 不改变 thresholds。
- 不 rerun solver to create a replacement benchmark。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission。
- 不把 interpolation 当作物理平滑或数值修复。

## Required Commands

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz --quantity real --interpolation nearest --out /tmp/t7r_fig3_lite_hires_panel_real_nearest.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run a metadata inspection script over:

- `configs/r60_k1_li_fig3_lite_xz_hires.yaml`;
- `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz`;
- `/tmp/t7r_fig3_lite_hires_panel_real_nearest.png.json`.

Run a static read-only boundary check such as:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

## Stop Conditions

Stop and record failure if:

- the T8i NPZ artifact is missing;
- grid shape is not `(61,61)` or spacing is not `1.0`;
- final adjacent pair fails;
- valid fields are non-finite;
- cache metadata suggests radial solves scale with grid point count;
- plotting imports or calls solver/physics modules;
- sidecar lacks interpolation/grid-spacing metadata after T8i claimed support;
- full pytest fails;
- review would require changing physics/convention code.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- test results;
- artifact paths;
- grid and sampling review;
- convergence and cache review;
- read-only plotting boundary;
- visual-sampling conclusion;
- open issues;
- go/no-go recommendation:
  - If passed: recommend T0 decide between multi-frequency Fig.3 extension and
    remaining Phase 4 CLI/output polish.
  - If failed: return to T8i with exact failure mode.
