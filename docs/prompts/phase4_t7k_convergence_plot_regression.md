# Phase 4 T7k Prompt: Convergence-History Regression Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7k`。

启动条件：

- 只在 T8c 完成 saved convergence history 和 `plot-convergence` 后启动。
- 如果 T8c 尚未完成，不要补写 implementation；记录 expected-failing review 并交回 T8/T0。

先读：

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/workstreams.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8c_convergence_history.md`
8. `configs/r60_k1_convergence_smoke.yaml`
9. T8c 修改过的 `src/schwgw/io/*`
10. T8c 修改过的 `src/schwgw/viz/*`
11. T8c 修改过的 `src/schwgw/cli.py`
12. T8c 新增或修改的 tests

目标：

独立验证 T8c 的 convergence-history contract，而不是重写 T8。重点是保证：

- convergence history 在 solver `run` 阶段保存；
- `plot-convergence` 只读 saved metadata；
- no-history result 仍然清楚失败且不重跑 solver；
- no-convergence config 的 T8a/T8b backward compatibility 未破坏。

任务：

1. Config/schema regression
   - 检查旧 `configs/r60_k1_smoke.yaml` 仍能运行并生成原 schema。
   - 检查新 `configs/r60_k1_convergence_smoke.yaml` 生成的 `.npz` 和 `.h5` 包含：
     - `diagnostics.lmax_convergence_history`
     - `diagnostics.lmax_convergence_policy`
     - `diagnostics.final_lmax_pair`
   - 检查 metadata JSON 可解析，complex values 若存在必须是 JSON-safe，不依赖 pickle。

2. Plot regression
   - 从新 `.npz` 运行 `plot-convergence`，生成 PNG + sidecar JSON。
   - 若 HDF5 可用，从 `.h5` 运行 `plot-convergence`。
   - 检查 PNG 非空、sidecar 含 source path、case_id、`kM`、observer `r`、`lmax_values`、final adjacent pair、thresholds、pass/fail status。
   - 同一 result 上 `plot-wavefield` 仍可生成 PNG。

3. Read-only physics boundary
   - 扫描 `src/schwgw/viz/*`，确认没有 import：
     - `schwgw.scattering`
     - `schwgw.perturbations`
     - `schwgw.angular`
     - `schwgw.numerics`
     - `schwgw.backgrounds`
   - 确认 `plot-convergence` 不调用 `compute_polarization(...)` 或 `run_solver_grid(...)`。
   - 可以用 monkeypatch 或 source scan 辅助确认 plotting path 不触发 solver。

4. Backward compatibility
   - 对没有 convergence history 的 old smoke result，确认 `plot-convergence` 仍返回非零 exit code 和清楚错误，不写 PNG。
   - 旧 `plot-wavefield` tests 仍通过。

5. Numerical policy check
   - 检查 T8c 文档/status 是否明确：small convergence smoke 不是 Li Fig.2/3/4 physics benchmark。
   - 若 T8c 声称 convergence physically passed，必须确认它基于 final adjacent pair policy，而不是 early pair 或 `lmax≈kr`。

允许修改：

- `tests/unit/*`
- `tests/regression/*`
- `docs/validation_plan.md`，仅限 convergence-history regression checklist/test policy
- `status.md`

原则上不要修改：

- `src/schwgw/io/*`
- `src/schwgw/viz/*`
- `src/schwgw/cli.py`

只有在发现 tiny test/wiring issue 时可做最小修正；如果涉及 schema design、physics convention、solver API 或 plotting architecture，停止并交回 T8/T0。

禁止修改：

- 不修改 T2-T6 physics code。
- 不修改 radial solver。
- 不修改 Wigner-D/angular code。
- 不生成 R60_K2/R60_K4。
- 不启动 Li Fig.3/Fig.4 大型网格。
- 不实现 transmission factor。
- 不把 small smoke convergence 当作 physics benchmark proof。

停止条件：

- `plot-convergence` 调用 solver 或重新扫 `lmax`。
- History metadata 无法追踪 final adjacent pair、threshold 或 pass/fail status。
- `.npz/.h5` metadata schema 不一致。
- no-convergence result 的旧 behavior 被破坏。
- T8c 大幅改变 physics API 或 convention。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t7k_r60_k1_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t7k_r60_k1_smoke.npz --out /tmp/t7k_no_history_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_convergence_smoke.yaml --out /tmp/t7k_r60_k1_convergence_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t7k_r60_k1_convergence_smoke.npz --out /tmp/t7k_convergence.png
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t7k_r60_k1_convergence_smoke.npz --component h_plus --quantity abs --out /tmp/t7k_hplus_abs.png
```

其中 no-history `plot-convergence` 应 expected-fail with exit code `2` and no PNG。

如果 HDF5 可用：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_convergence_smoke.yaml --out /tmp/t7k_r60_k1_convergence_smoke.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t7k_r60_k1_convergence_smoke.h5 --out /tmp/t7k_convergence_h5.png
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- convergence artifact inspection summary
- read-only plotting boundary result
- backward compatibility result
- open issues
- next action：若通过，可进入 T8d Li Fig.3/Fig.4-lite saved benchmark grid slice；若未通过，交回 T8c 修复
