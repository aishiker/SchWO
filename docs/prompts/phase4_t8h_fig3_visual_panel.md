# Phase 4 T8h Prompt: Fig.3-Lite Read-Only Visual Panel

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8h`。

## 启动条件

- T8g `R60_K1_LI_FIG3_LITE_XZ` saved benchmark 已完成。
- T7p independent review 已通过。
- `/tmp/t8g_r60_k1_li_fig3_lite_xz.npz` exists and is accepted as the first single-frequency Li Fig.3-lite x-z benchmark.
- Q014 remains closed。
- Q015 remains separate non-blocking structured radial diagnostic metadata。
- Q016 remains resolved。

## 背景和裁决

本 slice 只做 **read-only visualization polish**，不重新运行 solver。

T7p 接受了数值 benchmark，但指出 horizon/light-ring overlay 和 paper-style panel layout 仍是 open visualization polish。Li-Hou-Zhao Fig.3 展示 `real(h_plus)` 与 `real(h_cross)` 的 x-z wave fields，并用黑色区域表示 event horizon、灰色区域表示 light ring。

目标是把 T8g saved data 画成一个更接近 Fig.3 风格的单频 panel：

- read `/tmp/t8g_r60_k1_li_fig3_lite_xz.npz` or `.h5`;
- plot `real(h_plus)` and `real(h_cross)` side by side;
- use x horizontal and z vertical;
- use a diverging colormap centered at zero for real-valued fields;
- draw event horizon radius `2M` as black disk;
- draw light ring radius `3M` as gray disk/ring behind the horizon;
- save sidecar JSON documenting source path, grid kind, overlays, color scale, and conventions.

This remains single-frequency Fig.3-lite only. Do not run multi-frequency Fig.3 and do not compute transmission.

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8g_li_fig3_lite_xz_benchmark.md`
8. `docs/prompts/phase4_t7p_li_fig3_lite_xz_review.md`
9. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
10. `src/schwgw/viz/results.py`
11. `src/schwgw/cli.py`
12. `tests/unit/test_viz_results.py`
13. `tests/regression/test_plot_cli.py`

## 允许修改

- `src/schwgw/viz/results.py`
- `src/schwgw/cli.py`
- `tests/unit/test_viz_results.py`
- `tests/regression/test_plot_cli.py`
- `docs/architecture.md`
- `docs/validation_plan.md`
- `status.md`

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 `src/schwgw/io/results.py` unless a tiny reader metadata compatibility fix is absolutely necessary; prefer not to touch it.
- 不修改 `src/schwgw/scattering/*`。
- 不修改 `src/schwgw/numerics/*`。
- 不修改 `src/schwgw/angular/*`。
- 不修改 `src/schwgw/perturbations/*`。
- 不改变 Fourier/harmonic/tetrad/RW-Zerilli/polarization conventions。
- 不运行 solver 或 radial solver。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor。
- 不生成 four-frequency paper-scale Fig.3 panel。
- 不提交 binary PNG/NPZ/HDF5 artifacts。

## Implementation Target

Add a read-only plotting entry point. Recommended CLI:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --quantity real --out /tmp/t8h_fig3_lite_panel_real.png
```

If you choose a different command name, it must be explicit, documented, and covered by tests.

Expected behavior:

- Load saved result with `load_results(...)`.
- Reject non-`xz_plane` results with a clear error.
- Reject missing `x`, `z`, or `valid_mask` arrays.
- Only support `quantity=real` in this slice unless implementing other quantities is trivial and tested.
- Plot two panels: `h_plus` and `h_cross`.
- Mask invalid points and NaN values.
- Use a shared symmetric color scale across both panels:

```text
vmax = max(abs(valid quantity values for h_plus and h_cross))
vmin = -vmax
```

- Use a diverging colormap such as `RdBu_r` or equivalent.
- Determine `M` from saved metadata:

```python
M = metadata["config"]["background"]["M"]
```

- Draw light ring before event horizon:

```text
light_ring_radius = 3M
event_horizon_radius = 2M
```

- If `M` is missing, skip overlays and record `overlays.drawn=false` in the sidecar; do not fail solely on missing overlay metadata for old results.
- Preserve existing `plot-wavefield` and `plot-convergence` behavior.

Sidecar JSON should include:

```json
{
  "source_result_path": "...",
  "case_id": "R60_K1_LI_FIG3_LITE_XZ",
  "plot_type": "fig3_lite_panel",
  "grid_kind": "xz_plane",
  "quantity": "real",
  "components": ["h_plus", "h_cross"],
  "kM": 1.0,
  "lmax": 108,
  "x_range": [-30.0, 30.0],
  "z_range": [-30.0, 30.0],
  "valid_point_count": 440,
  "invalid_point_count": 1,
  "symmetric_color_scale": true,
  "color_vmin": -...,
  "color_vmax": ...,
  "overlays": {
    "drawn": true,
    "event_horizon_radius": 2.0,
    "light_ring_radius": 3.0
  },
  "convention": {...}
}
```

## Tests

Add tests proving:

1. `plot-fig3-panel` writes a PNG and JSON sidecar from a synthetic x-z `GridResult`.
2. Sidecar records overlay radii from metadata `M`.
3. Sidecar records `symmetric_color_scale=true` and finite color limits.
4. Invalid/masked point does not crash the plotter.
5. Non-x-z result fails clearly.
6. Existing `plot-wavefield` and `plot-convergence` tests still pass.
7. Plotting code remains read-only and has no imports from solver/physics modules.

Use small synthetic results in tests; do not require the real `/tmp/t8g...` benchmark for fast tests.

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --quantity real --out /tmp/t8h_fig3_lite_panel_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If `/tmp/t8g_r60_k1_li_fig3_lite_xz.h5` exists:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-panel /tmp/t8g_r60_k1_li_fig3_lite_xz.h5 --quantity real --out /tmp/t8h_fig3_lite_panel_real_h5.png
```

Run a sidecar inspection script and record:

- PNG sizes;
- sidecar `plot_type`;
- `grid_kind`;
- `components`;
- color limits;
- overlay radii;
- valid/invalid counts.

## Stop Conditions

Stop and update `status.md` if:

- plotting requires solver recomputation;
- `src/schwgw/viz/*` imports physics/solver modules;
- saved x-z result cannot be plotted without changing IO schema;
- existing plot commands regress;
- tests fail outside this slice's allowed files;
- implementation requires touching T2-T6 physics/convention code;
- the real T8g artifact is missing.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- test results;
- artifact paths;
- sidecar metadata summary;
- read-only boundary result;
- open issues;
- next action:

```text
Send T7: 你现在是 T7q。请读取并严格执行 docs/prompts/phase4_t7q_fig3_visual_panel_review.md。
```
