# Phase 4 T7p Prompt: Li Fig.3-Lite x-z Benchmark Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7p`。

## 启动条件

- 只在 T8g 完成后启动。
- 如果 `configs/r60_k1_li_fig3_lite_xz.yaml` 或 `/tmp/t8g_r60_k1_li_fig3_lite_xz.npz` 不存在，不要代替 T8 实现或运行 benchmark；记录 blocker 并交回 T8/T0。

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
10. `references/manifest.md`
11. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
12. `configs/r60_k1_li_fig3_lite_xz.yaml`
13. T8g-changed source/tests/docs, if any
14. `src/schwgw/io/results.py`
15. `src/schwgw/viz/results.py`

## 目标

Independently review whether T8g produced a valid first Li Fig.3-lite x-z saved benchmark:

- config matches the intended single-frequency `kM=1` `60M x 60M` x-z region;
- x-z saved data schema is intact and JSON-safe;
- valid grid values are finite and invalid/horizon points are masked;
- final adjacent pair `[96,108]` passes thresholds;
- run-scoped radial cache is active and not grid-size scaled;
- read-only plotting boundary still holds;
- no T2-T6 physics/convention changes occurred;
- result is correctly described as single-frequency Fig.3-lite, not a full paper reproduction.

## 允许修改

- `tests/regression/*` only for lightweight metadata/plot review tests if useful
- `docs/validation_plan.md` only for review checklist wording
- `status.md`

原则上不要修改 `src/`、configs、or artifacts. If an implementation issue is found, record failure and return to T8g/T0.

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 radial solver equations/boundaries/thresholds。
- 不修改 Wigner-D/angular code。
- 不改变 conventions。
- 不降低 `lmax` 或修改 thresholds。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor。
- 不生成 four-frequency paper-scale Fig.3 panel。
- 不把 T8f smoke result 当 benchmark。

## Review Checklist

1. Config review
   - Confirm `case_id=R60_K1_LI_FIG3_LITE_XZ`.
   - Confirm `M=1`, `kM=1`, `A_plus=0.9+1.1j`, `A_cross=0.4+0.6j`.
   - Confirm `observer.kind=xz_plane`.
   - Confirm `x_values` and `z_values` span `[-30,30]` and define a `21 x 21` grid.
   - Confirm boundary matches R60_K1 high-ell settings: `r_out=300`, `rtol=1e-10`, `atol=1e-12`.
   - Confirm `lmax=108`, `lmax_values=[60,72,84,96,108]`.

2. Saved result review
   - Inspect `/tmp/t8g_r60_k1_li_fig3_lite_xz.npz`.
   - Confirm arrays:
     - `x`, `z`, `r`, `theta`, `phi`, `valid_mask`, `h_plus`, `h_cross`, `metadata_json`.
   - Confirm shapes:

```text
x.shape == (21,)
z.shape == (21,)
r/theta/phi/valid_mask/h_plus/h_cross shape == (21,21)
```

   - Confirm all valid `h_plus/h_cross` values are finite.
   - Confirm invalid points have `valid_mask=False` and complex NaN fields.
   - Confirm metadata has `grid.kind == "xz_plane"` and valid/invalid counts.

3. Convergence and diagnostics
   - Confirm `diagnostics.lmax_convergence_history` exists.
   - Confirm `diagnostics.final_lmax_pair == [96,108]`.
   - Confirm `diagnostics.lmax_convergence_policy.final_pair_passed is true`.
   - Record final-pair max relative change and near-axis max relative change.
   - Confirm `diagnostics.run_radial_cache.enabled is true`.
   - Confirm `unique_solution_count` is consistent with `(sector,ell)` solves and not multiplied by grid points.
   - Confirm `diagnostics.radial_diagnostic_warnings` is a JSON-safe list.

4. Plot review
   - Generate plots from the saved NPZ:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --component h_plus --quantity real --out /tmp/t7p_fig3_lite_hplus_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --component h_cross --quantity real --out /tmp/t7p_fig3_lite_hcross_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --out /tmp/t7p_fig3_lite_convergence.png
```

   - Confirm PNGs and sidecar JSON files exist and are non-empty.
   - Confirm sidecars record source path, grid kind, case id, component/quantity, `kM`, `lmax`, coordinate ranges, valid/invalid counts, convention, and any overlay metadata if implemented.

5. Read-only plotting boundary
   - Scan `src/schwgw/viz/*`.
   - Confirm no imports from:
     - `schwgw.scattering`
     - `schwgw.perturbations`
     - `schwgw.angular`
     - `schwgw.numerics`
     - `schwgw.backgrounds`
   - Confirm plotting does not call `compute_polarization(...)`, `run_solver_grid(...)`, or radial solver functions.

6. Scope review
   - Confirm no T2-T6 source files changed for T8g.
   - Confirm no R60_K2/R60_K4 fixture or artifact was generated.
   - Confirm no transmission-factor code was added.
   - Confirm docs/status call this single-frequency Fig.3-lite, not full Fig.3 reproduction.

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/unit/test_wigner.py tests/unit/test_spin_weighted_harmonics.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --component h_plus --quantity real --out /tmp/t7p_fig3_lite_hplus_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --component h_cross --quantity real --out /tmp/t7p_fig3_lite_hcross_real.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8g_r60_k1_li_fig3_lite_xz.npz --out /tmp/t7p_fig3_lite_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run a metadata inspection script and record:

- grid shape;
- valid/invalid counts;
- finite valid field check;
- final pair and pass/fail;
- final max relative changes;
- cache stats;
- warning count;
- plot sidecar fields.

If HDF5 artifact exists:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8g_r60_k1_li_fig3_lite_xz.h5 --component h_plus --quantity real --out /tmp/t7p_fig3_lite_hplus_real_h5.png
```

## Stop Conditions

Stop and report to T0 if:

- saved result file is missing;
- final adjacent pair failed;
- fields contain non-finite values on valid points;
- invalid points are not masked;
- cache stats scale with grid size;
- plotting imports/calls physics solver;
- T8g changed T2-T6 physics/conventions;
- tests fail outside T7p review scope;
- docs/status overstate the result as full paper Fig.3 reproduction.

## 完成后

Update `status.md` with:

- changed files;
- commands run;
- test results;
- metadata review;
- convergence review;
- cache review;
- plot/read-only boundary result;
- scope review;
- open issues;
- go/no-go:
  - If passed: T0 may decide between a visualization-polish slice for Fig.3 overlays/panels or a multi-frequency Fig.3 extension.
  - If failed: return to T8g with exact failure mode.
