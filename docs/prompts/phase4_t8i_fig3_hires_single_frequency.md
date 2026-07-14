# Phase 4 T8i Prompt: Fig.3-Lite High-Resolution Single-Frequency Grid

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8i`。

## 启动条件

- T8g `R60_K1_LI_FIG3_LITE_XZ` saved benchmark 已完成并由 T7p 接受。
- T8h `plot-fig3-panel` read-only visual panel 已完成并由 T7q 接受。
- Q014 remains closed。
- Q015 remains separate non-blocking structured radial diagnostic metadata。
- Q016 remains resolved。

## 背景和裁决

T8g/T8h 的图像链路正确，但现有 saved x-z grid 只有 `21x21`，范围为
`x/M,z/M in [-30,30]`，步长 `3M`。对于 `kM=1`，波长为
`2*pi*M`，每个波长只有约 `2.09` 个空间采样点。因此当前 panel 是
pipeline/benchmark-lite 图，不是高空间分辨率图。

本 slice 的目标是生成同一物理参数下的 **single-frequency high-sampling
Fig.3-lite saved result**，并让绘图 metadata 明确记录 grid spacing 与
interpolation。不要启动 multi-frequency Fig.3、R60_K2/R60_K4 或
transmission。

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/prompts/phase4_t8g_li_fig3_lite_xz_benchmark.md`
10. `docs/prompts/phase4_t7p_li_fig3_lite_xz_review.md`
11. `docs/prompts/phase4_t8h_fig3_visual_panel.md`
12. `docs/prompts/phase4_t7q_fig3_visual_panel_review.md`
13. `references/manifest.md`
14. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
15. `configs/r60_k1_li_fig3_lite_xz.yaml`
16. `src/schwgw/io/config.py`
17. `src/schwgw/io/results.py`
18. `src/schwgw/viz/results.py`
19. `src/schwgw/cli.py`
20. relevant tests under `tests/unit/` and `tests/regression/`

## 允许修改

- `configs/r60_k1_li_fig3_lite_xz_hires.yaml`
- `src/schwgw/viz/results.py`
- `src/schwgw/cli.py`
- `tests/unit/test_viz_results.py`
- `tests/regression/test_plot_cli.py`
- `docs/architecture.md`
- `docs/validation_plan.md`
- `status.md`

如果 high-resolution run can be done with existing code, keep source edits
limited to the plotting metadata/interpolation enhancement.

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 `src/schwgw/scattering/*`。
- 不修改 `src/schwgw/numerics/*`。
- 不修改 `src/schwgw/angular/*`。
- 不修改 `src/schwgw/perturbations/*`。
- 不改变 Fourier/harmonic/tetrad/RW-Zerilli/polarization conventions。
- 不改变 convergence thresholds 来隐藏失败。
- 不把 plotting code 改成重新运行 solver。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor。
- 不生成 four-frequency paper-scale Fig.3 panel。
- 不提交大型 binary artifacts。

## Config

Create `configs/r60_k1_li_fig3_lite_xz_hires.yaml` by copying the accepted
T8g physics parameters and changing only case id, output path, and grid:

```yaml
case_id: R60_K1_LI_FIG3_LITE_XZ_HIRES
output: /tmp/r60_k1_li_fig3_lite_xz_hires.npz
background:
  M: 1.0
wave:
  kM: 1.0
  A_plus:
    real: 0.9
    imag: 1.1
  A_cross:
    real: 0.4
    imag: 0.6
observer:
  kind: xz_plane
  x_values: explicit list from -30.0 to 30.0 inclusive with step 1.0
  z_values: explicit list from -30.0 to 30.0 inclusive with step 1.0
  invalid_radius_policy: mask
numerics:
  lmax: 108
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
convergence:
  enabled: true
  lmax_values: [60, 72, 84, 96, 108]
  theta_values: [0.0, 0.05, 0.2, 1.0, 2.0, 3.0]
  phi_values: [0.0, 3.141592653589793]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

The YAML must contain real explicit numeric lists, not the English placeholder
above and not unsupported range shorthand. After writing the config, run a
parser check and record:

- `len(x_values)=61`, `len(z_values)=61`;
- first/last values are `-30.0` and `30.0`;
- all adjacent differences are `1.0`;
- expected saved field shape is `(61,61)`;
- because `M=1` and points with `r <= 2M` are masked, the expected invalid
  point count for this integer grid is `13`.

## Plotting Enhancement

Extend `plot-fig3-panel` in a read-only way:

- add `--interpolation` with allowed values `nearest`, `bilinear`, `bicubic`;
- default to `nearest` for honest display of saved samples;
- pass the value to `imshow(interpolation=...)`;
- record `interpolation` in the sidecar JSON;
- record `grid_spacing` metadata for x and z if the saved coordinates are
  monotone and evenly spaced;
- record `samples_per_wavelength` when `kM` and grid spacing are available:
  `lambda/M = 2*pi/kM`, so for this grid and `kM=1`, samples per wavelength
  should be about `6.28`.

Do not make interpolation a physics operation. It is display metadata only.
Generate at least a `nearest` panel. Optionally also generate a `bilinear`
panel for visual comparison, but benchmark acceptance is tied to saved data,
not presentation smoothing.

## Required Commands

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_li_fig3_lite_xz_hires.yaml --out /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz --quantity real --interpolation nearest --out /tmp/t8i_fig3_lite_hires_panel_real_nearest.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz --out /tmp/t8i_fig3_lite_hires_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Optional comparison plot:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz --quantity real --interpolation bilinear --out /tmp/t8i_fig3_lite_hires_panel_real_bilinear.png
```

HDF5 is optional in this slice. Do not spend extra runtime on HDF5 if the NPZ
run already consumes the interactive budget; T8h/T7q already validated the
NPZ/HDF5 read-only plotting path.

## Metadata Checks

Inspect `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz` and record:

- array keys and shapes;
- valid/invalid point counts;
- finite `h_plus/h_cross` on valid points;
- `diagnostics.final_lmax_pair`;
- `diagnostics.lmax_convergence_policy.final_pair_passed`;
- final adjacent pair max relative change and near-axis max relative change;
- `diagnostics.run_radial_cache`;
- radial diagnostic warning count;
- plot sidecar `grid_spacing`, `samples_per_wavelength`, and `interpolation`.

The final adjacent pair `[96,108]` must pass both selected and near-axis
thresholds. Early adjacent pairs may fail and should be recorded as
diagnostics.

## Stop Conditions

Stop and update `status.md` if:

- the NPZ high-resolution run exceeds roughly 25 minutes in the current
  interactive environment;
- final adjacent pair `[96,108]` does not pass thresholds;
- valid `h_plus/h_cross` values contain NaN/Inf;
- run-scoped radial cache is missing or unique solves scale with grid size
  rather than with `(sector,ell)`;
- radial warnings are not structured JSON-safe metadata;
- plotting imports or calls physics solver code;
- the interpolation/grid-spacing metadata requires IO schema changes that
  would break existing saved results;
- tests fail outside this slice's allowed files;
- implementing this requires changing T2-T6 formulas, conventions, radial
  solver, or angular code.

Do not lower `lmax`, shrink the grid, relax thresholds, or rename the same
case as "hires" after falling back. If a fallback is necessary, stop and ask
T0 to define a new explicitly named fallback slice.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- runtime;
- artifact paths;
- grid shape, spacing, samples per wavelength, and valid/invalid counts;
- final pair and convergence pass/fail;
- cache statistics;
- radial warnings;
- plot sidecar metadata, including interpolation;
- comparison with the old `21x21` T8g grid;
- open issues;
- next action:

```text
Send T7: 你现在是 T7r。请读取并严格执行 docs/prompts/phase4_t7r_fig3_hires_review.md。
```
