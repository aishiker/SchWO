# Phase 4 T8e Prompt: Cached Saved-Benchmark Runner

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8e`。

## 背景裁决

T8d 按 stop condition 正确停止：`R60_K1_LI_FIG4_LITE` 的 `lmax=108`
production CLI run 在当前交互环境中运行 `171.24s` 仍未写出 `.npz`。

这不是 Q014/Q015/Q016 物理失败，也不是收敛失败。当前证据指向实现层性能问题：
`run_solver_grid(...)` 对每个 angular point 和 convergence probe 重复调用
`compute_polarization(...)`，而 `compute_polarization(...)` 的径向 cache 只在单次调用
内部有效。T7h 的 R60_K1 fixture 已证明同一参数窗口在共享/incremental radial cache 下可完成并通过 final pair。

## 启动条件

- Q014 remains closed。
- Q015 remains separate structured diagnostic metadata。
- Q016 remains resolved by high-`ell` Wigner-D regression。
- Do not rerun old T7m until this T8e slice produces a saved result.

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8d_li_fig4_lite_saved_benchmark.md`
8. `configs/r60_k1_li_fig4_lite.yaml`
9. `tests/regression/fixtures/R60_K1.json`
10. `src/schwgw/io/config.py`
11. `src/schwgw/io/results.py`
12. `src/schwgw/scattering/partial_wave.py`
13. `src/schwgw/numerics/radial_solver.py`
14. `tests/unit/test_io_results.py`
15. `tests/regression/test_io_cli.py`
16. `tests/regression/test_plot_cli.py`

## 目标

解除 T8d runtime blocker，但不改变物理公式或 convention：

1. 在 solver-run 层加入 run-scoped radial solution cache，使 main grid 和 convergence probes 共享径向解。
2. 在 result metadata 中记录 cache stats 与 structured radial warning records。
3. 保持 plotting read-only over saved results。
4. 用不降级的 `R60_K1_LI_FIG4_LITE` 参数生成 `.npz` saved result 和三张 read-only plot。

## 允许修改

- `src/schwgw/io/results.py`
- `tests/unit/test_io_results.py`
- `tests/regression/test_io_cli.py`
- `configs/r60_k1_li_fig4_lite.yaml`
- `docs/architecture.md`
- `docs/validation_plan.md`
- `status.md`

只有在发现 tiny CLI wiring issue 时才修改：

- `src/schwgw/cli.py`

## 禁止修改

- 不修改 `src/schwgw/scattering/*` 的 physics formulas。
- 不修改 `src/schwgw/numerics/radial_solver.py` 的 equations, boundary conditions, thresholds, or solver branch logic。
- 不修改 `src/schwgw/angular/*`。
- 不修改 frozen Fourier、harmonic、tetrad、RW/Zerilli、polarization convention。
- 不降低 `lmax=108` 或 `lmax_values=[60,72,84,96,108]`。
- 不把 smoke `lmax=[2,3,4]` 结果称作 benchmark。
- 不实现 full Fig.3 x-z spatial grid。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor。
- 不让 plotting code call solver。

## 实现要求

### 1. Align T8d config with R60_K1 fixture boundary

Update `configs/r60_k1_li_fig4_lite.yaml` to match the R60_K1 fixture-generation boundary recorded in `status.md`:

```yaml
numerics:
  lmax: 108
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
```

Keep:

```yaml
convergence:
  enabled: true
  lmax_values: [60, 72, 84, 96, 108]
  theta_values: [0.0, 0.05, 0.2, 1.0]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

Do not reduce the observer line unless the config cannot parse.

### 2. Add run-scoped radial cache

In `src/schwgw/io/results.py`, add a cache used by `run_solver_grid(...)` when the solver accepts a `radial_solver` keyword.

Suggested behavior:

- Wrap the raw `solve_radial_mode(...)` in a cached callable.
- Cache key must include at least:
  - sector
  - `ell`
  - `k`
  - background name and mass
  - boundary settings
- The same cache object must be shared by:
  - all main-grid points
  - all convergence lmax/probe calls
- Preserve compatibility with tests/fake solvers:
  - If the injected `polarization_solver` does not accept `radial_solver`, call it without that keyword.
  - If it accepts `**kwargs`, passing `radial_solver` is allowed.

Record metadata under:

```python
metadata["diagnostics"]["run_radial_cache"] = {
    "enabled": True,
    "unique_solution_count": ...,
    "hit_count": ...,
    "key_count": ...,
}
```

The existing point-level numeric diagnostics must remain.

### 3. Preserve Q015 warning metadata

Because the run-scoped cache owns the actual radial solutions, collect warning records after the run:

```python
metadata["diagnostics"]["radial_diagnostic_warnings"] = [
    warning.to_metadata(),
    ...
]
```

Rules:

- The list may be empty.
- Warning records must be JSON-safe.
- Do not replace numeric scalar diagnostics such as `max_wronskian_residual`.
- Do not relax any threshold to suppress warnings.

### 4. Tests

Add focused tests proving:

1. A fake production-like solver receives a cached `radial_solver` and repeated grid/convergence calls only trigger unique radial solves once per `(sector, ell)`.
2. Metadata contains `diagnostics.run_radial_cache`.
3. Metadata contains JSON-safe `diagnostics.radial_diagnostic_warnings`.
4. Existing fake solvers and old no-convergence config behavior remain compatible.
5. `plot-wavefield` and `plot-convergence` still read saved result only; do not edit plotting code unless a tiny metadata compatibility issue appears.

### 5. Benchmark rerun

After tests pass, rerun:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_li_fig4_lite.yaml --out /tmp/t8e_r60_k1_li_fig4_lite.npz
```

Then inspect metadata and confirm:

- arrays exist and are finite;
- `h_plus.shape == (9, 1)`;
- `h_cross.shape == (9, 1)`;
- `diagnostics.lmax_convergence_history` exists;
- `diagnostics.final_lmax_pair == [96, 108]`;
- `diagnostics.lmax_convergence_policy.final_pair_passed is true`;
- `diagnostics.run_radial_cache.unique_solution_count` is close to the unique `(sector,ell)` count, not multiplied by grid/probe count;
- `diagnostics.radial_diagnostic_warnings` exists and is JSON-safe.

Generate plots only from saved result:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8e_r60_k1_li_fig4_lite.npz --component h_plus --quantity abs --out /tmp/t8e_r60_k1_hplus_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8e_r60_k1_li_fig4_lite.npz --component h_cross --quantity abs --out /tmp/t8e_r60_k1_hcross_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8e_r60_k1_li_fig4_lite.npz --out /tmp/t8e_r60_k1_convergence.png
```

Optional HDF5 mirror if runtime remains acceptable:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_li_fig4_lite.yaml --out /tmp/t8e_r60_k1_li_fig4_lite.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8e_r60_k1_li_fig4_lite.h5 --out /tmp/t8e_r60_k1_convergence_h5.png
```

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_results.py tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

And the benchmark/plot commands listed above, unless a stop condition is triggered.

## 停止条件

Stop and update `status.md` if any of these occur:

- Implementing cache requires changing T4 radial equations/boundaries or T6 physics formulas.
- Benchmark still does not produce `.npz` within a reasonable interactive runtime after cache is in place.
- Final adjacent pair fails thresholds.
- Selected values at `theta=[0,0.05,0.2,1.0]` cannot plausibly match `tests/regression/fixtures/R60_K1.json` after aligning boundary settings.
- Cache metadata cannot be made JSON-safe.
- Plotting code must call solver to succeed.
- Tests fail outside this slice's allowed scope.

## 完成后

Update `status.md` with:

- changed files
- commands run
- test results
- cache stats
- benchmark runtime
- artifact paths
- convergence metadata summary
- radial warning summary
- open issues
- next action:

```text
Send T7: 你现在是 T7n。请读取并严格执行 docs/prompts/phase4_t7n_cached_benchmark_review.md。
```

