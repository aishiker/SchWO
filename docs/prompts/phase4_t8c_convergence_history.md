# Phase 4 T8c Prompt: Saved Convergence History and Convergence Plot

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8c`。

阶段定位：

T8a/T7i 已完成 data output + IO/CLI regression。T8b/T7j 已完成 plotting-from-results，并验证 `plot-wavefield` 只读 saved `.npz/.h5` results。当前 Phase 4 的主要缺口是：结果文件还没有保存 `lmax` convergence history，因此 `plot-convergence` 只能清楚失败，不能生成 convergence plot。

本 slice 只补 saved convergence history 和 `plot-convergence`。不要启动 Li Fig.3/Fig.4 大网格，不要做 transmission factor。

背景：

- Q012/Q013/Q014/Q016 已解除。
- Q015 是 non-blocking low-`k` radial diagnostic warning；本 slice 不处理 Q015。
- T7j 已验证 `src/schwgw/viz/*` 没有核心物理依赖；继续保持该边界。
- `docs/numerics.md` 已规定 adaptive convergence loop：early adjacent pairs 是 diagnostics，final adjacent pair 过阈值才通过；不要把 `lmax≈kr` 写成充分条件。

先读：

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/workstreams.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. `docs/prompts/phase4_t8b_plotting_from_results.md`
10. `docs/prompts/phase4_t7j_plot_regression.md`
11. `src/schwgw/io/config.py`
12. `src/schwgw/io/results.py`
13. `src/schwgw/viz/results.py`
14. `src/schwgw/cli.py`
15. `tests/regression/test_plot_cli.py`
16. `tests/regression/fixtures/R60_K1.json`

目标：

实现：

```text
solver run with selected convergence probes
  -> saved .npz/.h5 metadata contains lmax_convergence_history
  -> plot-convergence reads that saved history
  -> PNG + sidecar metadata
```

核心原则：

- `plot-convergence` 仍然不能重新运行 solver。
- convergence history 必须在 `run` 阶段保存进 result metadata。
- fast tests 使用 small/fake solver；真实 solver smoke 只能用很小的 `lmax` 和少量 probes。

必须实现：

1. Backward-compatible config extension
   - 在 YAML schema 中新增可选 `convergence` mapping。缺省时 T8a/T8b 行为完全不变。
   - 建议字段：

```yaml
convergence:
  enabled: true
  lmax_values: [2, 3, 4]
  theta_values: [0.0, 0.05]
  phi_values: [0.0]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

   - `lmax_values` 必须是严格递增 integer list，全部 `>=2`。
   - 如果 `convergence.enabled=true`，建议要求 `numerics.lmax == lmax_values[-1]`，避免 main grid 和 convergence metadata 使用不同 final `lmax` 而没有记录。
   - `theta_values`/`phi_values` 是 convergence probes，不一定等于 main output grid。
   - 验证错误要清楚：缺字段、非法阈值、非法 `lmax_values`、非法 angle list。

2. Saved convergence history
   - 在 `run_solver_grid(...)` 或邻近 helper 中，若 config 开启 convergence，额外对 selected probes 和每个 `lmax` 调用 production solver。
   - 保存到 metadata：

```text
metadata["diagnostics"]["lmax_convergence_history"]
metadata["diagnostics"]["lmax_convergence_policy"]
metadata["diagnostics"]["final_lmax_pair"]
```

   - History 至少包含每个 adjacent pair 的：
     - `previous_lmax`
     - `current_lmax`
     - `max_relative_change`
     - `near_axis_max_relative_change`
     - probe count
     - optional worst probe metadata: `theta`, `phi`, `component`
   - 可以保存各 `lmax` 的 probe values，但 complex values 必须 JSON-safe，例如 `{real, imag}`；不要把大数组塞进 metadata。
   - relative-change 定义必须明确、稳定处理零幅值；建议 denominator 使用 `max(abs(new), abs(old), tiny)`。
   - final adjacent pair 是否 pass 要写成 metadata field，但 T8c 不要为了通过而自动增加 `lmax` 或改物理。

3. `plot-convergence`
   - 修改 `src/schwgw/viz/results.py` 中 `plot_convergence_from_result(...)`：
     - 若 metadata 没有 `lmax_convergence_history`，保持当前清楚失败，不重跑 solver。
     - 若存在 history，画 adjacent-pair max relative change vs current `lmax`。
     - 如果 metadata 有 selected/near-axis threshold，画 threshold reference line。
     - 输出 PNG 和 sidecar JSON。
   - Sidecar 至少记录：
     - source result path
     - case_id
     - `kM`
     - observer `r`
     - `lmax_values`
     - final adjacent pair
     - final pass/fail status
     - thresholds
     - convention summary。

4. Smoke config
   - 新增一个很小的 config，例如 `configs/r60_k1_convergence_smoke.yaml`。
   - 使用真实 Li-style amplitudes 和 `r=60M,kM=1`，但 `lmax_values` 可很小，例如 `[2,3,4]`，只作为 IO/plot smoke，不作为 physics benchmark。
   - 不生成 R60_K2/R60_K4。

5. Tests
   - Config parsing tests：
     - no `convergence` preserves old behavior；
     - valid convergence config parses；
     - invalid `lmax_values` fails。
   - Metadata tests：
     - fake solver run writes `lmax_convergence_history`；
     - history is JSON serializable in `.npz` and `.h5`。
   - Plot tests：
     - synthetic result with convergence history produces nonempty PNG + sidecar；
     - no-history result still fails clearly and does not call solver。
   - CLI regression：
     - run convergence smoke config to `.npz`；
     - `plot-convergence` generates PNG；
     - `plot-wavefield` still works on same file。

允许修改：

- `src/schwgw/io/config.py`
- `src/schwgw/io/results.py`
- `src/schwgw/io/__init__.py` if needed
- `src/schwgw/viz/results.py`
- `src/schwgw/viz/__init__.py` if needed
- `src/schwgw/cli.py`
- `configs/*.yaml`
- `tests/unit/*`
- `tests/regression/*`
- `docs/architecture.md` or `docs/validation_plan.md`，仅限记录 convergence-history schema/plot contract
- `status.md`

禁止修改：

- 不修改 `src/schwgw/backgrounds/`
- 不修改 `src/schwgw/angular/`
- 不修改 `src/schwgw/numerics/`
- 不修改 `src/schwgw/perturbations/`
- 不修改 `src/schwgw/scattering/` production physics。
- 不修改 frozen physics convention。
- 不生成 R60_K2/R60_K4。
- 不启动 Li Fig.3/Fig.4 大型网格。
- 不实现 transmission factor。
- 不在 plotting code 中调用 `compute_polarization(...)` 或 `run_solver_grid(...)`。

停止条件：

- 保存 convergence history 需要改变 T6 production API 或 physics convention。
- 真实 solver smoke 运行时间失控，无法保持 fast test 边界。
- 当前 output schema 无法以 JSON-safe metadata 表示 convergence history。
- `plot-convergence` 需要重新运行 solver 才能工作。
- 新增 convergence path 破坏 T8a/T8b 的 no-convergence config backward compatibility。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_convergence_smoke.yaml --out /tmp/t8c_r60_k1_convergence_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8c_r60_k1_convergence_smoke.npz --out /tmp/t8c_convergence.png
```

如果 HDF5 可用：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_convergence_smoke.yaml --out /tmp/t8c_r60_k1_convergence_smoke.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-convergence /tmp/t8c_r60_k1_convergence_smoke.h5 --out /tmp/t8c_convergence_h5.png
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- convergence history schema summary
- plot output paths and file sizes
- whether no-history `plot-convergence` still fails clearly
- confirmation that plotting reads saved results only
- open issues
- next action：通常应是 T7k independent convergence-history regression review
