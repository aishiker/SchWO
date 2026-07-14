# Phase 4 T7n Prompt: Cached Benchmark Runner Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7n`。

## 启动条件

- 只在 T8e 完成后启动。
- 如果 T8e 未生成 `/tmp/t8e_r60_k1_li_fig4_lite.npz`，不要代替 T8 实现或跑 benchmark；记录 blocker 并交回 T8/T0。

## 先读

1. `project.md`
2. `status.md`
3. `docs/phase3_closeout.md`
4. `docs/architecture.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8e_cached_benchmark_runner.md`
8. `configs/r60_k1_li_fig4_lite.yaml`
9. `tests/regression/fixtures/R60_K1.json`
10. T8e-changed `src/schwgw/io/results.py`
11. T8e-changed tests
12. `src/schwgw/viz/results.py`

## 目标

独立复核 T8e 是否真正解除 T8d runtime blocker，而没有改变物理：

- run-scoped radial cache is active and correctly scoped;
- saved result contains benchmark fields and convergence metadata;
- selected points match the R60_K1 fixture after boundary alignment;
- structured radial warning metadata is preserved;
- plotting remains read-only over saved result;
- Q014/Q015/Q016 statuses remain unchanged.

## 允许修改

- `tests/regression/*` for lightweight metadata/regression checks only
- `docs/validation_plan.md` for review checklist wording only
- `status.md`

原则上不要修改 `src/` 或 `configs/`。若发现 implementation issue，record failure and return to T8e.

## 禁止修改

- 不修改 T2-T6 physics code。
- 不修改 radial solver equations/boundaries/thresholds。
- 不修改 Wigner-D/angular code。
- 不改变 conventions。
- 不降低 benchmark `lmax`。
- 不生成 R60_K2/R60_K4。
- 不实现 full Fig.3 x-z spatial grid。
- 不实现 transmission factor。

## 复核任务

1. Config review
   - Confirm `configs/r60_k1_li_fig4_lite.yaml` uses:
     - `case_id=R60_K1_LI_FIG4_LITE`
     - `M=1`, `kM=1`, `r=60`
     - `A_plus=0.9+1.1j`, `A_cross=0.4+0.6j`
     - `lmax_values=[60,72,84,96,108]`
     - `numerics.lmax=108`
     - boundary matches R60_K1 fixture-generation record: `r_out=300`, `rtol=1e-10`, `atol=1e-12`

2. Cache implementation review
   - Inspect T8e code and tests.
   - Confirm cache key includes physics/numerics identity, not just `ell`.
   - Confirm cache is run-scoped, not a persistent global cache.
   - Confirm fake/non-production solvers remain compatible.
   - Confirm metadata includes `diagnostics.run_radial_cache`.
   - Confirm warning metadata is JSON-safe and separate from numeric scalar diagnostics.

3. Saved result review
   - Re-run or inspect `/tmp/t8e_r60_k1_li_fig4_lite.npz`.
   - Confirm:
     - `h_plus.shape == (9,1)`
     - `h_cross.shape == (9,1)`
     - all values finite
     - `diagnostics.lmax_convergence_history` exists
     - `diagnostics.final_lmax_pair == [96,108]`
     - `diagnostics.lmax_convergence_policy.final_pair_passed is true`
     - `diagnostics.run_radial_cache.unique_solution_count` is not multiplied by grid/probe count
     - `diagnostics.radial_diagnostic_warnings` exists and is a list

4. Selected-point regression against fixture
   - Compare `theta=0.0,0.05,0.2,1.0`, `phi=0.0` values in the saved result against `tests/regression/fixtures/R60_K1.json`.
   - Use strict but realistic complex tolerances, for example `rtol=1e-8`, `atol=1e-10`, unless numerical evidence supports a different documented tolerance.
   - If boundary settings differ or values disagree, do not bless the benchmark.

5. Plot review
   - Generate from saved result:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8e_r60_k1_li_fig4_lite.npz --component h_plus --quantity abs --out /tmp/t7n_r60_k1_hplus_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8e_r60_k1_li_fig4_lite.npz --component h_cross --quantity abs --out /tmp/t7n_r60_k1_hcross_abs.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8e_r60_k1_li_fig4_lite.npz --out /tmp/t7n_r60_k1_convergence.png
```

   - Confirm PNGs and sidecar JSON files exist and are non-empty.
   - Confirm sidecars record source result path, `case_id`, `kM`, observer radius, lmax values/final pair where relevant, and pass/fail status.

6. Read-only plotting boundary
   - Scan `src/schwgw/viz/*`.
   - Confirm no imports from:
     - `schwgw.scattering`
     - `schwgw.perturbations`
     - `schwgw.angular`
     - `schwgw.numerics`
     - `schwgw.backgrounds`
   - Confirm `plot-convergence` does not call `compute_polarization(...)` or `run_solver_grid(...)`.

## 必须运行

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_results.py tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/unit/test_wigner.py tests/unit/test_spin_weighted_harmonics.py tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run an explicit metadata/fixture comparison script or one-liner and record:

- benchmark runtime if rerun
- final pair
- final pair pass/fail
- max relative change
- near-axis max relative change
- cache unique count and hit count
- radial warning count
- selected-point max absolute/relative difference against R60_K1 fixture

If HDF5 artifact exists:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8e_r60_k1_li_fig4_lite.h5 --out /tmp/t7n_r60_k1_convergence_h5.png
```

## 停止条件

Stop and report to T0 if:

- final adjacent pair does not pass thresholds;
- selected-point values disagree with R60_K1 fixture;
- cache key is physically under-specified;
- cache is global/persistent in a way that can contaminate later runs;
- warning metadata is missing or not JSON-safe;
- plotting imports/calls physics solver;
- tests fail outside this review scope;
- rerun is still too slow for repeatable local review.

## 完成后

Update `status.md` with:

- changed files
- commands run
- test results
- cache review result
- saved-result metadata result
- selected-point regression result
- plot/read-only boundary result
- open issues
- go/no-go:
  - If passed: T0 may proceed to a later T8 spatial-grid schema slice for Li Fig.3-lite.
  - If failed: return to T8e with the exact failure mode.

