# Phase 3 T4h Prompt: Optional Radial Diagnostic Classification Hardening

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4h`。

这是可选 hardening 任务，不是当前 benchmark blocker。除非 T0 明确要求，不要和 `T7g` regression fixture slice 并行运行，因为两者都会更新 `status.md`，且 T7g 可能先定义 fixture metadata 需要的 diagnostic 字段。

背景：

- Q012 high-ell radial instability 已解决。
- Q014 polarization bridge 已关闭。
- Q015 已被 T4-lite triage 为 `k=0.2, ell=3` transition-regime raw-Wronskian warning。
- 当前证据不支持真实 radial solver 错误；不要重写 solver。

先读：

1. `project.md`
2. `status.md`
3. `docs/numerics.md`
4. `docs/validation_plan.md`
5. `references/notes/q012_high_ell_radial_methods.md`
6. `src/schwgw/numerics/radial_solver.py`
7. `tests/physics/test_radial_solver.py`
8. `tests/unit/test_radial_solver.py`

目标：

让 radial diagnostics 更可读、更适合 fixture metadata，而不是改变物理解或边界条件。

建议任务：

1. 扩展 `RadialDiagnostics`
   - 增加显式字段，例如：
     - `raw_wronskian_residual`
     - `stabilized_residual`
     - `diagnostic_branch`
     - `expected_flux_scale`
     - `absolute_wronskian_drift`
   - 保留现有 `wronskian_residual` 的兼容语义，除非 T0 明确批准 breaking API change。

2. 明确 diagnostic classification
   - `outward_raw`
   - `bvp_raw`
   - `bvp_stabilized`
   - `transition_warning`
   - `transition_warning` 只应在 raw relative residual 偏高、但 boundary residual、collocation/flux residual、finite radial data、condition number、field convergence 均健康时出现。

3. 增加测试
   - 保持现有 high-ell tests 通过。
   - 给 `k=0.2, ell=3` odd/even 添加 targeted diagnostic-classification test，确认它被记录为 transition warning，而不是 hard failure。
   - 测试必须确认没有放宽全局 `<1e-7` Wronskian target；Q012 high-barrier stabilized tests 仍需通过。

4. 更新文档
   - 更新 `docs/numerics.md` 和 `docs/validation_plan.md` 中的 diagnostic 字段说明。
   - 更新 `status.md`。

禁止修改：

- 不改变 `_requires_stabilized_solver` 的阈值 `8.0`，除非本 slice 先证明阈值本身是根因并在 `status.md` 标记需要 T0 决策。
- 不改变 boundary condition convention。
- 不改变 BVP normalization。
- 不改变 T6/T7 polarization 或 partial-wave assembly。
- 不生成 regression fixtures。
- 不做 plotting。
- 不放宽全局 validation thresholds。

停止条件：

- 需要改变 physics convention 或 boundary condition。
- 需要重写 radial solver architecture。
- 新 diagnostic 字段导致 T6/T7 public API 大面积破坏。
- `k=0.2, ell=3` warning 伴随 boundary residual 变大、非有限 radial data、field convergence failure、或 condition number 异常。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

完成时更新 `status.md`：

- changed files
- commands run
- test results
- old/new diagnostic fields
- Q015 classification status
- open issues
- next action，特别说明 T7 fixture metadata 是否应改用新增字段
