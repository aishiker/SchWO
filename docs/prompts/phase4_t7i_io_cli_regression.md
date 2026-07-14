# Phase 4 T7i Prompt: Data Output and CLI Regression Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7i`。

启动条件：

- 只在 T8a 完成 YAML-driven solver CLI 和 `.npz`/`.h5` data output 后启动。
- 如果 T8a 尚未完成，不要生成 fixtures 或 plotting；可以只做 expected-failing test design，并在 `status.md` 标清。

先读：

1. `project.md`
2. `status.md`
3. `docs/architecture.md`
4. `docs/workstreams.md`
5. `docs/validation_plan.md`
6. `docs/numerics.md`
7. `configs/r60_k1_smoke.yaml`
8. T8a 修改过的 `src/schwgw/io/*`
9. T8a 修改过的 `src/schwgw/cli.py`
10. `tests/regression/fixtures/R60_K1.json`

目标：

独立验证 T8a 的数据输出和 CLI，而不是重写 T8。重点是保证：

- YAML config 可复现运行；
- 输出文件保存 raw complex data 和 metadata；
- tests 能捕捉 schema drift；
- plotting 脚本未来只能读数据，不混入核心物理计算。

任务：

1. CLI/data-output regression tests
   - 运行 T8a CLI，生成临时 `.npz`，若 T8a 支持 HDF5，也生成 `.h5`。
   - 读取输出文件，检查：
     - `h_plus`, `h_cross` 存在；
     - dtype 是 complex 或可无损重建 complex；
     - grid shape 与 config 一致；
     - metadata 包含 convention/config/lmax/boundary/diagnostics。

2. Consistency checks
   - 对一个小型 selected point，将 CLI 输出与 direct production `compute_polarization(...)` 比较，容差使用当前 double precision 合理阈值。
   - 该比较属于 T7 regression check；不要把 direct call 放进 plotting code。

3. Runtime policy
   - 确认 fast pytest 不依赖大型 R60_K1 full adaptive rerun。
   - 若真实 solver integration test 太慢，应把它标为 `full_regression` 或改成 monkeypatch production API 的 unit test，并在 `status.md` 记录。

4. Plotting boundary check
   - 如果 T8a 没实现 plotting，确认 status 记录“plotting remains future T8b”。
   - 如果 T8a 意外加入 plotting，检查它是否只读 saved data；若它重新调用 `compute_polarization(...)`，标为 blocker。

允许修改：

- `tests/unit/*`
- `tests/regression/*`
- `docs/validation_plan.md`，仅限 output schema/test policy
- `status.md`

原则上不要修改：

- `src/schwgw/io/*`
- `src/schwgw/cli.py`

只有在发现明显 tiny wiring/test import 问题时，才可做最小修正；如果涉及 output schema、physics convention、solver API 或 plotting architecture，停止并交回 T8/T0。

禁止修改：

- 不修改 T2-T6 physics code。
- 不修改 radial solver。
- 不修改 Wigner-D/angular code。
- 不生成 R60_K2/R60_K4。
- 不生成正式 plot artifacts。

停止条件：

- CLI 输出与 direct production selected-point comparison 不一致且无法解释。
- Output metadata 缺少 convention/config/diagnostics。
- 输出数据无法无损表示 complex amplitudes。
- T8 plotting 或 CLI 重新实现核心物理公式。
- T8a 需要跨线程 API 决策才能修复。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t7i_r60_k1_smoke.npz
```

如果 HDF5 已实现：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run configs/r60_k1_smoke.yaml --out /tmp/t7i_r60_k1_smoke.h5
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- output inspection summary
- any schema/runtime issues
- whether T8b plotting-from-results can start
