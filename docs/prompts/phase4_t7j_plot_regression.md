# Phase 4 T7j Prompt: Plotting Regression Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7j`。

启动条件：

- 只在 T8b 完成 plotting-from-results 后启动。
- 如果 T8b 尚未完成，不要补写 plotting implementation；可以只记录 expected-failing review 并交回 T8/T0。

先读：

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/workstreams.md`
5. `docs/validation_plan.md`
6. `docs/numerics.md`
7. `docs/prompts/phase4_t8b_plotting_from_results.md`
8. `configs/r60_k1_smoke.yaml`
9. T8b 修改过的 `src/schwgw/io/*`
10. T8b 修改过的 `src/schwgw/viz/*`
11. T8b 修改过的 `src/schwgw/cli.py`
12. T8b 新增或修改的 tests

目标：

独立验证 T8b 的 plotting-from-results contract，而不是重写 T8。重点是保证：

- plotting 只读 saved `.npz`/`.h5` results；
- PNG 和 sidecar metadata 可复现生成；
- plotting code 没有核心物理公式、没有 production solver 调用；
- `plot-convergence` 不在缺少 convergence history 时偷偷重跑 `lmax` sweep。

任务：

1. CLI plot regression
   - 用 `configs/r60_k1_smoke.yaml` 生成临时 `.npz`。
   - 从该 `.npz` 运行 `plot-wavefield`，生成 PNG 和 sidecar JSON。
   - 若 HDF5 可用，也生成临时 `.h5` 并从 `.h5` 运行 `plot-wavefield`。
   - 检查 PNG 文件存在且非空，sidecar JSON 包含 source path、component、quantity、case_id、`kM`、observer `r`、`lmax`、convention。

2. Read-only physics boundary
   - 扫描 `src/schwgw/viz/*`，确认没有 import：
     - `schwgw.scattering`
     - `schwgw.perturbations`
     - `schwgw.angular`
     - `schwgw.numerics`
     - `schwgw.backgrounds`
   - 确认 plotting code path 不调用 `compute_polarization(...)` 或 `run_solver_grid(...)`。
   - `src/schwgw/cli.py` 可以为 `run` subcommand 使用 production solver，但 `plot-wavefield` / `plot-convergence` branch 不能调用 solver。

3. Data consistency checks
   - 对 synthetic result 或 smoke result，独立读取 saved `h_plus/h_cross`。
   - 验证 plotted quantity 选择逻辑使用 saved data 的 `real/imag/abs/phase`，不改变 normalization。
   - 检查 invalid component/quantity 的 error path。

4. Convergence plotting policy
   - 如果 T8b 实现了 `plot-convergence`，确认它只读取 saved convergence metadata。
   - 如果当前 schema 不含 convergence history，确认 `plot-convergence` 清楚失败、返回非零 exit code，并在 `status.md` 记录后续需要 T8c/schema 扩展。

允许修改：

- `tests/unit/*`
- `tests/regression/*`
- `docs/validation_plan.md`，仅限 plotting regression checklist/test policy
- `status.md`

原则上不要修改：

- `src/schwgw/io/*`
- `src/schwgw/viz/*`
- `src/schwgw/cli.py`

只有在发现明显 tiny wiring/test import 问题时，才可做最小修正；如果涉及 plotting architecture、output schema、physics convention 或 solver API，停止并交回 T8/T0。

禁止修改：

- 不修改 T2-T6 physics code。
- 不修改 radial solver。
- 不修改 Wigner-D/angular code。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor。
- 不把 plot artifact 作为 physics correctness proof。

停止条件：

- `plot-wavefield` 需要重新运行 solver 才能生成图。
- `src/schwgw/viz/*` 直接依赖 production physics modules。
- PNG/metadata 与 saved result metadata 不一致。
- `plot-convergence` 重新扫 `lmax` 或调用 `compute_polarization(...)`。
- 发现 result schema 不足以支持 T8b 基本 wavefield plot。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t7j_r60_k1_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t7j_r60_k1_smoke.npz --component h_plus --quantity real --out /tmp/t7j_hplus_real.png
```

如果 HDF5 可用：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t7j_r60_k1_smoke.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t7j_r60_k1_smoke.h5 --component h_cross --quantity abs --out /tmp/t7j_hcross_abs.png
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- plot artifact inspection summary
- read-only physics boundary result
- convergence plotting policy result
- open issues
- next action：若通过，可进入更大 grid/benchmark plotting slice；若未通过，交回 T8b 修复
