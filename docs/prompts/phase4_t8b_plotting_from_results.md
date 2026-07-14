# Phase 4 T8b Prompt: Plotting From Saved Results

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8b`。

阶段定位：

T8a/T7i 已经完成 YAML-driven solver run、`.npz`/`.h5` raw complex output 和独立 IO/CLI regression review。本 slice 才开始正式 plotting，但 plotting 必须只读取已保存结果文件，不得重新调用核心物理计算。

背景：

- Q012/Q013/Q014/Q016 已解除。
- Q015 仍是 non-blocking low-`k` radial diagnostic warning；本 slice 不处理 Q015。
- T7i 已确认 `.npz` 与 `.h5` 输出保存 `theta`, `phi`, `h_plus`, `h_cross`, `metadata_json`。
- 旧 prompt `docs/prompts/phase4_t8_smoke_plot_cli.md` 已废弃，不得使用。
- Transmission factor normalization 仍未冻结为可实现接口；本 slice 不实现 transmission plot。

先读：

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/workstreams.md`
5. `docs/validation_plan.md`
6. `docs/numerics.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. `configs/r60_k1_smoke.yaml`
10. `src/schwgw/io/config.py`
11. `src/schwgw/io/results.py`
12. `src/schwgw/cli.py`
13. `src/schwgw/viz/__init__.py`
14. `tests/regression/test_io_cli.py`

目标：

实现 plotting-from-results 的最小可用闭环：

```text
saved .npz/.h5 results -> plot-wavefield -> PNG + plot metadata sidecar
```

`plot-convergence` 也可以接入 CLI，但只能读取结果文件中已经存在的 convergence history。如果当前 result schema 没有保存 lmax sweep/convergence history，应返回清楚错误并测试该错误；不要为了画 convergence 重新运行 solver 或重新扫 `lmax`。

必须实现：

1. Result reader
   - 在 `src/schwgw/io/results.py` 或等价模块中新增读取 helper。
   - 支持读取 T8a/T7i 格式的 `.npz` 与 `.h5/.hdf5`。
   - 返回 `theta`, `phi`, `h_plus`, `h_cross`, `metadata`，保持 complex dtype。
   - 对缺字段、非法 suffix、缺少 `h5py` 给出清楚错误。

2. Plotting module
   - 新增 `src/schwgw/viz/*`，建议集中在 `src/schwgw/viz/results.py`。
   - 使用 matplotlib non-interactive backend，例如 `Agg`。
   - 支持 component:
     - `h_plus`
     - `h_cross`
   - 支持 quantity:
     - `real`
     - `imag`
     - `abs`
     - `phase`
   - 结果为 2D angular grid 时画 field map；结果为 1x1 或 1D smoke grid 时给出稳定 fallback plot，不允许崩溃。
   - 图中只展示已保存数据的派生量，例如 `real(h_plus)`、`abs(h_cross)`；不要写入任何新的物理公式。

3. Plot metadata
   - 每个输出 PNG 旁边写一个 sidecar JSON，例如 `plot.png.json`。
   - 至少记录：
     - source result path
     - component
     - quantity
     - case_id
     - `kM`
     - observer `r`
     - `lmax`
     - convention summary
     - source result creation timestamp if available
   - Metadata 不需要包含大数组。

4. CLI
   - 扩展 `src/schwgw/cli.py`，至少支持：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8b_r60_k1_smoke.npz --component h_plus --quantity real --out /tmp/t8b_hplus_real.png
```

   - 如 HDF5 可用，也支持：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8b_r60_k1_smoke.h5 --component h_cross --quantity abs --out /tmp/t8b_hcross_abs.png
```

   - `plot-convergence RESULT --out PATH` 只能从 result metadata 中读取已保存 convergence history；若不存在，返回非零 exit code 和清楚错误。
   - 可以把 `compute_polarization` import 延迟到 `_run(...)` 内，减少 plotting code path 的物理依赖；若改动会变复杂，可以只确保 plotting branch 不调用 solver。

5. Tests
   - 新增或扩展 tests，覆盖：
     - `.npz` result reader round-trip。
     - `.h5` result reader round-trip if `h5py` available。
     - `plot-wavefield` 从 `.npz` 生成非空 PNG 和 sidecar JSON。
     - `plot-wavefield` 从 `.h5` 生成非空 PNG 和 sidecar JSON if `h5py` available。
     - invalid component/quantity 返回明确错误。
     - `plot-convergence` 在缺少 convergence history 时不重算 physics，而是清楚失败。
   - fast tests 应优先用小型 synthetic `GridResult` 或 monkeypatch，不应依赖完整 R60 adaptive rerun。

允许修改：

- `src/schwgw/io/results.py`
- `src/schwgw/io/__init__.py`
- `src/schwgw/viz/*`
- `src/schwgw/cli.py`
- `tests/unit/*`
- `tests/regression/*`
- `docs/architecture.md` 或 `docs/validation_plan.md`，仅限记录 plotting-from-results contract
- `status.md`

禁止修改：

- 不修改 `src/schwgw/backgrounds/`
- 不修改 `src/schwgw/angular/`
- 不修改 `src/schwgw/numerics/`
- 不修改 `src/schwgw/perturbations/`
- 不修改 `src/schwgw/scattering/` production physics。
- 不修改 frozen physics convention。
- 不生成 R60_K2/R60_K4。
- 不实现 transmission factor plot。
- 不把 plotting 输出作为新的 physics validation 依据。
- 不让 `src/schwgw/viz/*` import `schwgw.scattering`, `schwgw.perturbations`, `schwgw.angular`, `schwgw.numerics`, or `schwgw.backgrounds`。

停止条件：

- 需要改变 T8a output schema 才能读取基本 `theta/phi/h_plus/h_cross`。
- 为实现 plot 必须调用 `compute_polarization(...)`、`run_solver_grid(...)` 或任何 T2-T6 物理 API。
- `plot-convergence` 需要现场计算 `lmax` sweep 才能完成。
- 需要决定 transmission normalization 或新物理 convention。
- PNG 生成依赖不可用且无法用现有 matplotlib 环境解决。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t8b_r60_k1_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8b_r60_k1_smoke.npz --component h_plus --quantity real --out /tmp/t8b_hplus_real.png
```

如果 HDF5 可用：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t8b_r60_k1_smoke.h5
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli plot-wavefield /tmp/t8b_r60_k1_smoke.h5 --component h_cross --quantity abs --out /tmp/t8b_hcross_abs.png
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- plot output paths and file sizes
- plot metadata summary
- whether `plot-convergence` is implemented or intentionally returns a schema-lack error
- confirmation that plotting reads saved results only
- open issues
- next action：通常应是 T7j independent plotting regression review
