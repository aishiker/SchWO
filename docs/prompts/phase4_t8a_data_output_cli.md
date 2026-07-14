# Phase 4 T8a Prompt: YAML-Driven Data Output and CLI

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8a`。

阶段定位：

这是 Phase 4：图像、数据输出和 CLI 的第一步。先实现数据输出，再实现正式绘图。不要从 plotting 开始，不要让图像驱动物理判断。

背景：

- T6 production path 已由 T7f/T7h 验证到可生成 `R60_K1` numeric fixture。
- T7h 已生成并验证 `tests/regression/fixtures/R60_K1.json`。
- Q012/Q013/Q014/Q016 已解除。
- Q015 是 non-blocking low-`k` radial diagnostic warning；本 slice 不处理 T4 diagnostic hardening。
- T8 可以调用 T6 的 high-level production API 做 solver run，但 plotting 代码不得重新实现或重新调用核心物理计算。

先读：

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/workstreams.md`
5. `docs/validation_plan.md`
6. `docs/numerics.md`
7. `docs/physics_spec.md`
8. `docs/equation_map.md`
9. `tests/regression/test_fixture_schema.py`
10. `tests/regression/fixtures/R60_K1.json`
11. `src/schwgw/cli.py`
12. `src/schwgw/scattering/partial_wave.py`
13. `src/schwgw/io/__init__.py`
14. `src/schwgw/viz/__init__.py`

目标：

实现最小可用的 YAML-driven solver CLI 和 data output：

```text
configs/*.yaml -> run solver -> save .npz/.h5 with complex raw data + metadata
```

本 slice 可以只做 smoke-scale grid，但必须是真实调用 production solver 的数据输出，不是从 fixture copy 数值，也不是 plotting-only wrapper。

必须实现：

1. Config reader
   - 新增 `src/schwgw/io/config.py` 或等价模块。
   - 支持 YAML config，至少字段：
     - `case_id`
     - `output`
     - `background.M`
     - `wave.kM`
     - `wave.A_plus.real/imag`
     - `wave.A_cross.real/imag`
     - `observer.r`
     - `observer.theta_values`
     - `observer.phi_values`
     - `numerics.lmax`
     - `numerics.boundary.r_in_eps`
     - `numerics.boundary.r_out`
     - `numerics.boundary.rtol`
     - `numerics.boundary.atol`
   - 明确验证错误：缺字段、非法 component、非法 `r <= 2M`、非法 `kM <= 0`。

2. Solver runner
   - 新增 `src/schwgw/io/results.py` 或 `src/schwgw/io/run.py`。
   - 用 `schwgw.scattering.partial_wave.compute_polarization(...)` 作为 production API。
   - 支持：
     - 单点计算：一个 `theta,phi`。
     - 小型二维 angular grid：`theta_values x phi_values`。
   - 保存原始 complex data：
     - `h_plus`
     - `h_cross`
   - 保存 metadata：
     - convention
     - config
     - lmax
     - boundary config
     - diagnostics returned by solver
     - creation timestamp
     - source command if available
   - 不要在 T8 复制 T6/T4/T3 的公式。

3. Data output
   - 至少支持 `.npz`。
   - 若不复杂，同时支持 `.h5`/`.hdf5`；`h5py` 已在 project dependency 中。
   - 输出 schema 必须可由 tests 读取并检查。
   - Complex arrays 可以保存为 native complex dtype；metadata 可保存为 JSON string。

4. CLI
   - 扩展 `src/schwgw/cli.py`，至少支持：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/r60_k1_smoke.npz
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/r60_k1_smoke.h5
```

   - CLI 必须返回非零 exit code 或抛出清楚错误用于 invalid config。
   - 保留未来 `plot-wavefield`, `plot-convergence` 子命令空间，但本 slice 不需要实现正式绘图。

5. Example config
   - 新增小型 smoke config，例如 `configs/r60_k1_smoke.yaml`。
   - 为避免本地测试过慢，config 可使用 R60_K1 的少量 selected angular points 或很小 angular grid。
   - 不自动生成 R60_K2/R60_K4。

6. Tests
   - 新增 tests 覆盖：
     - config parsing
     - invalid config errors
     - CLI run writes `.npz`
     - CLI run writes `.h5` if implemented
     - output contains complex `h_plus/h_cross`
     - output metadata includes convention/config/diagnostics
   - 测试应使用小型 grid 或 monkeypatch production API，避免 fast pytest 变慢。
   - 至少有一个 integration smoke 可以真实调用 production solver，但必须控制 runtime。

允许修改：

- `src/schwgw/io/*`
- `src/schwgw/cli.py`
- `configs/*.yaml`
- `examples/*`，只限简单 run example
- `tests/unit/*`
- `tests/regression/*`
- `docs/architecture.md` 或 `docs/validation_plan.md`，仅限记录 output schema
- `status.md`

禁止修改：

- 不修改 `src/schwgw/backgrounds/`
- 不修改 `src/schwgw/perturbations/`
- 不修改 `src/schwgw/angular/`
- 不修改 `src/schwgw/numerics/`
- 不修改 `src/schwgw/scattering/`
- 不修改 physics convention。
- 不生成正式 plotting 输出。
- 不实现 transmission factor。
- 不自动生成 R60_K2/R60_K4。
- 不把 plotting 作为 validation 依据。

停止条件：

- 需要改 T2-T6 production physics 才能完成 data output。
- `compute_polarization(...)` output/diagnostics 不足以形成 metadata，且需要跨线程 API 决策。
- Smoke integration run 过慢，无法纳入本地测试。
- HDF5/NPZ schema 无法明确表达 complex data + metadata。
- YAML config 需要引入新大型依赖。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/r60_k1_smoke.npz
```

如果实现 HDF5：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/r60_k1_smoke.h5
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- output file paths and file sizes
- output schema summary
- whether plotting remains unimplemented in this slice
- open issues
- next action：通常应是 T7i independent regression review，之后才进入 T8b plotting-from-results
