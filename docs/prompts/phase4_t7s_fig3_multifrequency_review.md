# Phase 4 T7s Prompt: Fig.3 Multi-Frequency Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7s`。

## 启动条件

- T8j has completed or stopped with a recorded result.
- `status.md` contains the T8j record.
- If the T8j artifacts are missing, do not implement them yourself; record a
  blocker and return to T8/T0.

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8j_fig3_multifrequency_panel.md`
8. `docs/prompts/phase4_t8i_fig3_hires_single_frequency.md`
9. `docs/prompts/phase4_t7r_fig3_hires_review.md`
10. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
11. T8j-changed configs, `src/schwgw/viz/results.py`,
    `src/schwgw/cli.py`, and tests

Also inspect the local PDF-rendered Fig.3 if useful. The intended frequencies
for this review are:

```text
kM = [0.5, 1.0, 1.5, 2.0]
```

## 任务

Independently review that T8j produced a valid multi-frequency Fig.3-lite
saved-result and plotting slice without changing physics conventions:

1. Confirm the three new configs use the same amplitudes, grid, boundary
   tolerances, and thresholds as T8i, except for `kM`, `case_id`, output path,
   and lmax window.
2. Confirm T8j reuses the accepted T8i `kM=1` saved result rather than
   overwriting it.
3. Load all four result files and verify:
   - shape `(61,61)`;
   - matching `x/z` coordinates;
   - valid/invalid mask matches `r > 2M`;
   - finite valid `h_plus/h_cross`;
   - complex NaN invalid fields;
   - final adjacent pair pass/fail and thresholds;
   - bounded radial cache metadata;
   - structured JSON-safe radial warnings.
4. Verify samples per wavelength are recorded or computable:
   - `kM=0.5`: about `12.57`;
   - `kM=1.0`: about `6.28`;
   - `kM=1.5`: about `4.19`;
   - `kM=2.0`: about `3.14`.
5. Regenerate the multi-frequency nearest panel from saved data only.
6. Inspect sidecar metadata for source paths, case ids, `kM`, grid spacing,
   samples per wavelength, final convergence metadata, row-wise color scales,
   overlays, and conventions.
7. Confirm `src/schwgw/viz` remains read-only over saved results and does not
   import or call solver/physics modules.
8. Confirm no `R60_K2`/`R60_K4` regression fixtures, transmission artifacts,
   or `kM=4` stress benchmark were generated.

## 允许修改

Prefer not to modify source. You may update only:

- `status.md`
- `docs/validation_plan.md` or `docs/architecture.md` for small documentation
  corrections if T8j left a clear typo
- tests only if a T8j test needs a trivial review-scope fix and the fix does
  not change behavior

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 radial solver、angular/Wigner-D、RW/Zerilli 或 polarization
  conventions。
- 不改变 thresholds。
- 不 rerun solver to create replacement benchmark data。
- 不生成 `R60_K2`/`R60_K4` fixtures。
- 不实现 transmission。
- 不把 interpolation 当作物理平滑或数值修复。

## Required Commands

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-fig3-multifrequency-panel /tmp/t8j_li_fig3_xz_k0p5_hires.npz /tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz /tmp/t8j_li_fig3_xz_k1p5_hires.npz /tmp/t8j_li_fig3_xz_k2p0_hires.npz --quantity real --interpolation nearest --out /tmp/t7s_li_fig3_multifrequency_panel_real_nearest.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run a metadata inspection script over:

- `configs/li_fig3_xz_k0p5_hires.yaml`;
- `configs/li_fig3_xz_k1p5_hires.yaml`;
- `configs/li_fig3_xz_k2p0_hires.yaml`;
- `/tmp/t8j_li_fig3_xz_k0p5_hires.npz`;
- `/tmp/t8i_r60_k1_li_fig3_lite_xz_hires.npz`;
- `/tmp/t8j_li_fig3_xz_k1p5_hires.npz`;
- `/tmp/t8j_li_fig3_xz_k2p0_hires.npz`;
- `/tmp/t7s_li_fig3_multifrequency_panel_real_nearest.png.json`.

Run a static read-only boundary check such as:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

Run an artifact guard such as:

```bash
find configs tests data /tmp -maxdepth 3 \( -iname '*R60_K2*' -o -iname '*R60_K4*' -o -iname '*transmission*' -o -iname '*k4*' \) -print
```

If this prints unrelated historical text files, record them; if it prints new
fixtures or benchmark outputs from T8j, treat that as a scope failure.

## Stop Conditions

Stop and record failure if:

- any required T8j NPZ artifact is missing;
- grids do not match exactly;
- any final adjacent pair fails;
- valid fields are non-finite;
- cache metadata suggests radial solves scale with grid point count;
- plotting imports or calls solver/physics modules;
- sidecar lacks required multi-frequency provenance;
- T8j generated `R60_K2`/`R60_K4` fixtures, transmission artifacts, or `kM=4`
  stress outputs;
- full pytest fails;
- review would require changing physics/convention code.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- test results;
- artifact paths;
- per-frequency convergence/cache review;
- multi-frequency sidecar review;
- read-only plotting boundary;
- scope guard result;
- visual-sampling conclusion, especially for `kM=2`;
- open issues;
- go/no-go recommendation:
  - If passed: recommend T0 decide whether Phase 4 Fig.3-lite can be marked
    complete or whether to add a `dx=0.5` high-frequency presentation slice.
  - If failed: return to T8j with exact failure mode.
