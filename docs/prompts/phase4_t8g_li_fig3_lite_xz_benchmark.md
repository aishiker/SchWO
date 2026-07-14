# Phase 4 T8g Prompt: Li Fig.3-Lite x-z Saved Benchmark

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8g`。

## 启动条件

- T8f x-z plane schema + smoke output 已完成。
- T7o independent x-z plane schema review 已通过。
- T8e/T7n 已通过 `R60_K1_LI_FIG4_LITE` cached saved benchmark review。
- Q014 remains closed。
- Q015 remains separate non-blocking structured radial diagnostic metadata。
- Q016 remains resolved。

## 背景和裁决

本 slice 开始第一张 **Li Fig.3-lite x-z wave-field benchmark**，但只做单频 `kM=1`。

Li-Hou-Zhao Fig.3 显示 `+` 和 `x` 极化在 `60M x 60M` 区域的 real wave fields，并覆盖多个频率。本文本 slice 只要求：

- `kM=1.0`；
- `x/M,z/M in [-30,30]` 的中等分辨率 saved grid；
- `h_plus` 和 `h_cross` 的 saved complex data；
- `real(h_plus)` 和 `real(h_cross)` 的 read-only plots；
- saved convergence metadata；
- no transmission factor；
- no R60_K2/R60_K4；
- no four-frequency paper-scale panel。

不要把本 slice 称为完整论文 Fig.3 复刻。它是 benchmark-grade saved result 的第一步，视觉分辨率仍是 lite。

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/prompts/phase4_t8f_xz_plane_schema.md`
10. `docs/prompts/phase4_t7o_xz_plane_schema_review.md`
11. `docs/prompts/phase4_t8e_cached_benchmark_runner.md`
12. `docs/prompts/phase4_t7n_cached_benchmark_review.md`
13. `references/manifest.md`
14. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
15. `configs/r60_k1_li_fig4_lite.yaml`
16. `configs/r60_k1_xz_plane_smoke.yaml`
17. `src/schwgw/io/config.py`
18. `src/schwgw/io/results.py`
19. `src/schwgw/viz/results.py`
20. `src/schwgw/cli.py`

## 允许修改

- `configs/r60_k1_li_fig3_lite_xz.yaml`
- `src/schwgw/viz/results.py` only for read-only x-z horizon/light-ring overlay support, if needed
- `tests/unit/test_viz_results.py` only if adding overlay metadata/tests
- `tests/regression/test_plot_cli.py` only if adding overlay metadata/tests
- `docs/architecture.md`
- `docs/validation_plan.md`
- `status.md`

If the existing plotter is sufficient for this slice, do not modify `src/`.

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
- 不生成四频 paper-scale Fig.3 panel。
- 不提交大型 binary artifacts。

## Config

Create `configs/r60_k1_li_fig3_lite_xz.yaml`:

```yaml
case_id: R60_K1_LI_FIG3_LITE_XZ
output: /tmp/r60_k1_li_fig3_lite_xz.npz
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
  x_values: [-30.0, -27.0, -24.0, -21.0, -18.0, -15.0, -12.0, -9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0]
  z_values: [-30.0, -27.0, -24.0, -21.0, -18.0, -15.0, -12.0, -9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0]
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

Expected grid shape is `(n_z,n_x)=(21,21)`. Because the grid includes the black-hole center, invalid/masked points are expected. Do not require all points to be valid.

## Plotting Requirements

Generate at least:

- `real(h_plus)` plot;
- `real(h_cross)` plot;
- convergence plot.

If the current x-z plotter does not show horizon/light-ring context, you may add a read-only overlay using saved metadata only:

- event horizon: black disk with radius `2M`;
- light ring: gray disk or ring with radius `3M`;
- no solver imports;
- no physics recomputation;
- sidecar JSON records whether overlays were drawn.

If this overlay is not implemented in T8g, record it as a non-blocking visualization polish item. Do not block the numerical benchmark solely on missing overlay.

## Metadata Checks

After the run, inspect `/tmp/t8g_r60_k1_li_fig3_lite_xz.npz` and record:

- array keys and shapes;
- valid/invalid point counts;
- finite `h_plus/h_cross` on valid points;
- `diagnostics.final_lmax_pair`;
- `diagnostics.lmax_convergence_policy.final_pair_passed`;
- final adjacent pair max relative change and near-axis max relative change;
- `diagnostics.run_radial_cache`;
- radial diagnostic warning count;
- numeric diagnostic maxima if present.

The final adjacent pair `[96,108]` must pass both selected and near-axis thresholds for this slice to be considered benchmark-grade. Early adjacent pairs may fail and should be recorded as diagnostics.

## Required Commands

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_li_fig3_lite_xz.yaml --out /tmp/t8g_r60_k1_li_fig3_lite_xz.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --component h_plus --quantity real --out /tmp/t8g_fig3_lite_hplus_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --component h_cross --quantity real --out /tmp/t8g_fig3_lite_hcross_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --out /tmp/t8g_fig3_lite_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If HDF5 runtime is acceptable after the NPZ benchmark:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_li_fig3_lite_xz.yaml --out /tmp/t8g_r60_k1_li_fig3_lite_xz.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.h5 --component h_plus --quantity real --out /tmp/t8g_fig3_lite_hplus_real_h5.png
```

Run a metadata inspection script and record the key values in `status.md`.

## Stop Conditions

Stop and update `status.md` if:

- NPZ run cannot complete in a reasonable interactive runtime, roughly 15 minutes.
- final adjacent pair `[96,108]` does not pass thresholds.
- valid `h_plus/h_cross` values contain NaN/Inf.
- run-scoped radial cache is missing or unique solves scale with grid size rather than with `(sector,ell)`.
- radial warnings are not structured JSON-safe metadata.
- plotting imports or calls physics solver code.
- existing angular result compatibility breaks.
- implementing this requires changing T2-T6 formulas, conventions, radial solver, or angular code.
- tests fail outside this slice's allowed files.

Do not lower `lmax`, shrink the grid, or relax thresholds while keeping the same `case_id`. If a fallback is necessary, stop and ask T0 to define a new explicitly named fallback slice.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- runtime;
- artifact paths;
- grid shape and valid/invalid counts;
- final pair and convergence pass/fail;
- cache statistics;
- radial warnings;
- plotting/read-only boundary;
- relation to Li Fig.3 and limitations;
- open issues;
- next action:

```text
Send T7: 你现在是 T7p。请读取并严格执行 docs/prompts/phase4_t7p_li_fig3_lite_xz_review.md。
```
