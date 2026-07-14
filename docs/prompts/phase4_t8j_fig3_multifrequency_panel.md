# Phase 4 T8j Prompt: Fig.3 Multi-Frequency Saved Panel

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8j`。

## 启动条件

- T8i `R60_K1_LI_FIG3_LITE_XZ_HIRES` saved result 已完成。
- T7r independent high-resolution review 已通过。
- Q014 remains closed。
- Q015 remains separate non-blocking structured radial diagnostic metadata。
- Q016 remains resolved。

## 背景和裁决

T7r 已接受单频 `kM=1` 的 `61x61` x-z saved result。现在可以进入受控的
multi-frequency Fig.3-lite 扩展。

Li-Hou-Zhao Fig.3 的四个频率面板是：

```text
k = {0.5, 1.0, 1.5, 2.0}/M
```

本 slice 只生成这些频率的 saved x-z data 和 read-only multi-frequency
panel。它不是 transmission slice，不生成 `R60_K2`/`R60_K4` regression
fixtures，不做 `kM=4`，不实现 generic incident direction。

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/architecture.md`
7. `docs/numerics.md`
8. `docs/validation_plan.md`
9. `docs/prompts/phase4_t8i_fig3_hires_single_frequency.md`
10. `docs/prompts/phase4_t7r_fig3_hires_review.md`
11. `references/manifest.md`
12. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
13. `configs/r60_k1_li_fig3_lite_xz_hires.yaml`
14. `src/schwgw/io/config.py`
15. `src/schwgw/io/results.py`
16. `src/schwgw/viz/results.py`
17. `src/schwgw/cli.py`
18. relevant tests under `tests/unit/` and `tests/regression/`

Also confirm from the local PDF, if needed, that Fig.3 uses
`k={0.5,1.0,1.5,2.0}/M`.

## 允许修改

- New configs:
  - `configs/li_fig3_xz_k0p5_hires.yaml`
  - `configs/li_fig3_xz_k1p5_hires.yaml`
  - `configs/li_fig3_xz_k2p0_hires.yaml`
- `src/schwgw/viz/results.py`
- `src/schwgw/cli.py`
- `tests/unit/test_viz_results.py`
- `tests/regression/test_plot_cli.py`
- `docs/architecture.md`
- `docs/validation_plan.md`
- `status.md`

Do not rename or overwrite the accepted T8i `kM=1` config/result. Reuse
`/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz` as the `kM=1` source when
assembling the multi-frequency panel.

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 `src/schwgw/scattering/*`。
- 不修改 `src/schwgw/numerics/*`。
- 不修改 `src/schwgw/angular/*`。
- 不修改 `src/schwgw/perturbations/*`。
- 不改变 Fourier/harmonic/tetrad/RW-Zerilli/polarization conventions。
- 不改变 convergence thresholds 来隐藏失败。
- 不把 plotting code 改成重新运行 solver。
- 不生成 `R60_K2`/`R60_K4` regression fixtures。
- 不实现 transmission factor。
- 不生成 `kM=4` high-frequency stress benchmark。
- 不提交大型 binary artifacts。

## Configs

Use the same x-z grid as T8i:

```text
x_values = z_values = [-30.0, -29.0, ..., 29.0, 30.0]
shape = (61, 61)
invalid_radius_policy = mask
```

Use the same physical amplitudes:

```text
M = 1.0
A_plus = 0.9 + 1.1j
A_cross = 0.4 + 0.6j
r_out = 300.0
rtol = 1.0e-10
atol = 1.0e-12
selected_threshold = 1.0e-4
near_axis_threshold = 1.0e-3
```

Create the following new configs:

```yaml
case_id: LI_FIG3_XZ_K0P5_HIRES
output: /tmp/li_fig3_xz_k0p5_hires.npz
wave.kM: 0.5
numerics.lmax: 84
convergence.lmax_values: [48, 60, 72, 84]
```

```yaml
case_id: LI_FIG3_XZ_K1P5_HIRES
output: /tmp/li_fig3_xz_k1p5_hires.npz
wave.kM: 1.5
numerics.lmax: 156
convergence.lmax_values: [84, 108, 132, 156]
```

```yaml
case_id: LI_FIG3_XZ_K2P0_HIRES
output: /tmp/li_fig3_xz_k2p0_hires.npz
wave.kM: 2.0
numerics.lmax: 180
convergence.lmax_values: [108, 132, 156, 180]
```

The snippets above are field summaries, not complete YAML. The actual YAML
files must be complete and must parse with the existing config reader. Reuse
the explicit `x_values` and `z_values` lists from the accepted T8i config.

## Saved Runs

Run the three missing frequencies one at a time:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k0p5_hires.yaml --out /tmp/t8j_li_fig3_xz_k0p5_hires.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k1p5_hires.yaml --out /tmp/t8j_li_fig3_xz_k1p5_hires.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k2p0_hires.yaml --out /tmp/t8j_li_fig3_xz_k2p0_hires.npz
```

For each result, inspect and record:

- shape and valid/invalid counts;
- finite valid `h_plus/h_cross`;
- invalid fields are complex NaN;
- final adjacent pair and final pass/fail;
- max selected and near-axis relative changes for the final pair;
- run radial cache unique/key/hit counts;
- radial diagnostic warnings;
- samples per wavelength implied by `dx=dz=1M`.

Expected samples per wavelength:

```text
kM=0.5 -> 12.566370614359172
kM=1.0 -> 6.283185307179586
kM=1.5 -> 4.1887902047863905
kM=2.0 -> 3.141592653589793
```

The `kM=2.0` grid is a controlled Fig.3-lite extension, not a final
publication-grade high-sampling image. If the visual panel shows clear
sampling artifacts, record that as an open issue; do not hide it with
interpolation.

## Multi-Frequency Plotting

Add a read-only plotting entry point, recommended CLI:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel \
  /tmp/t8j_li_fig3_xz_k0p5_hires.npz \
  /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz \
  /tmp/t8j_li_fig3_xz_k1p5_hires.npz \
  /tmp/t8j_li_fig3_xz_k2p0_hires.npz \
  --quantity real \
  --interpolation nearest \
  --out /tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png
```

Expected behavior:

- read saved results only with `load_results(...)`;
- reject non-`xz_plane` results clearly;
- reject mixed grids unless the coordinates match exactly;
- require exactly four inputs in increasing `kM` order for this slice;
- support only `quantity=real` in this slice;
- render a `2 x 4` panel:
  - top row: `real(h_plus)`;
  - bottom row: `real(h_cross)`;
  - columns: `kM=0.5,1.0,1.5,2.0`;
- draw event horizon `2M` and light ring `3M` overlays from saved metadata;
- use row-wise symmetric color scales across all four frequencies:
  - one scale for `h_plus`;
  - one scale for `h_cross`;
- default display interpolation is `nearest`;
- optional `bilinear` comparison is allowed, but acceptance is the `nearest`
  plot and saved data metadata.

Sidecar JSON must record:

- plot type `fig3_multifrequency_panel`;
- source result paths;
- case ids;
- `kM` values;
- components and quantity;
- interpolation;
- grid ranges, grid spacing, valid/invalid counts per source;
- samples per wavelength per source;
- final lmax pairs and final convergence pass/fail per source;
- row-wise color scale limits;
- overlay radii;
- convention metadata.

## Tests

Use synthetic saved results for fast tests. Add tests proving:

1. `plot-fig3-multifrequency-panel` writes PNG and sidecar from four synthetic
   x-z results.
2. The sidecar records all four source paths, case ids, `kM`, interpolation,
   grid spacing, and samples per wavelength.
3. Mixed grids fail clearly.
4. Non-x-z input fails clearly.
5. Wrong number of inputs fails clearly.
6. Plotting code remains read-only and has no imports/calls from solver or
   physics modules.
7. Existing `plot-wavefield`, `plot-convergence`, and `plot-fig3-panel`
   behavior remains unchanged.

## Required Commands

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k0p5_hires.yaml --out /tmp/t8j_li_fig3_xz_k0p5_hires.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k1p5_hires.yaml --out /tmp/t8j_li_fig3_xz_k1p5_hires.npz
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/li_fig3_xz_k2p0_hires.yaml --out /tmp/t8j_li_fig3_xz_k2p0_hires.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel /tmp/t8j_li_fig3_xz_k0p5_hires.npz /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz /tmp/t8j_li_fig3_xz_k1p5_hires.npz /tmp/t8j_li_fig3_xz_k2p0_hires.npz --quantity real --interpolation nearest --out /tmp/t8j_li_fig3_multifrequency_panel_real_nearest.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Optional comparison:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel /tmp/t8j_li_fig3_xz_k0p5_hires.npz /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz /tmp/t8j_li_fig3_xz_k1p5_hires.npz /tmp/t8j_li_fig3_xz_k2p0_hires.npz --quantity real --interpolation bilinear --out /tmp/t8j_li_fig3_multifrequency_panel_real_bilinear.png
```

## Stop Conditions

Stop and update `status.md` if:

- any new frequency exceeds roughly 45 minutes in the current interactive
  environment;
- any final adjacent pair fails thresholds;
- valid `h_plus/h_cross` values contain NaN/Inf;
- run-scoped radial cache is missing or unique solves scale with grid points
  rather than radial mode count;
- radial warnings are not structured JSON-safe metadata;
- multi-frequency plotting imports or calls solver/physics code;
- mixed-grid validation would require changing IO schema or saved data;
- tests fail outside this slice's allowed files;
- implementing this requires changing T2-T6 formulas, conventions, radial
  solver, or angular code.

Do not lower `lmax`, shrink the grid, relax thresholds, or use smoothing to
hide saved-grid artifacts while keeping the same case ids. If a fallback is
necessary, stop and ask T0 to define a new explicitly named fallback slice.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- runtime per frequency;
- artifact paths;
- per-frequency grid shape, samples per wavelength, final pair, convergence,
  cache, and warnings;
- multi-frequency sidecar metadata;
- read-only plotting boundary result;
- relation to Li Fig.3 and limitations;
- open issues;
- next action:

```text
Send T7: 你现在是 T7s。请读取并严格执行 docs/prompts/phase4_t7s_fig3_multifrequency_review.md。
```
