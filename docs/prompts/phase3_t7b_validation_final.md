# Phase 3 T7b Prompt: 主物理链最终验证

你现在是 `T7：验证与基准` 线程。本 slice 只能在 T6d 声明完成后启动。任务是独立复核阶段 3 的主物理链，给出是否可以进入后续可视化/benchmark 阶段的判断。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `references/notes/phase3_formula_audit.md`
9. T6 修改过的 `src/schwgw/perturbations/reconstruction.py`
10. T6 修改过的 `src/schwgw/scattering/*.py`
11. T6/T7 新增的 tests

## 目标

独立验证阶段 3 退出条件：

- 输入 `M, k, r, theta, phi, A_plus, A_cross` 可以输出 `h_plus, h_cross`。
- partial-wave sum 随 `lmax` 收敛。
- near optical axis 不出现非物理发散。
- polarization sign 和 Fourier convention 与 `docs/physics_spec.md` 一致。
- parity sector contribution 和 incident coefficients 一致。

## 允许修改

- `tests/physics/test_phase3_validation.py`
- `tests/regression/fixtures/*.json` 仅当 T6 diagnostics 已可信且用户同意生成 selected-value numeric fixture
- `docs/validation_plan.md` 仅记录阈值或命令边界修正
- `status.md`

原则上不要修改 `src/`。如果 T6 有 bug，先写失败测试；小型 export/import/wiring 可修，公式和 convention 问题交回 T6。

## 必跑验证

Targeted tests：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_metric_reconstruction.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_tetrads.py tests/unit/test_weyl_modes.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_polarization_extraction.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_partial_wave_observables.py tests/physics/test_phase3_validation.py
```

Aggregate tests：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## 必查物理项

- Monochromatic derivative sign:
  - `h_plus = -(Psi_hat_4 + Psi_hat_0)/k^2`
  - `h_cross = -i(Psi_hat_4 - Psi_hat_0)/k^2`
- `A_plus/A_cross` linearity and zero-amplitude zero-output。
- `m=±2` selection for `+z` incident wave still holds at incident coefficient layer。
- `lmax` sweep on selected probes uses `docs/numerics.md` strategy and records relative changes。
- near-axis probes at `theta=0`, `theta=0.01`, `theta=0.05` produce finite outputs。
- `M -> 0` or weakest-field available sanity check recovers expected unlensed polarization within documented threshold。
- far-axis asymptotic comparison is treated as validation baseline, not main output definition。

## 停止条件

立即停止并更新 `status.md`：

- Any default full pytest failure not attributable to intentionally skipped unavailable feature。
- `h_plus/h_cross` sign test fails。
- near-axis output has `NaN/Inf` or grows without lmax convergence and no clear numerical explanation。
- lmax convergence fails beyond documented threshold for selected probes after 3 parameter/debug attempts。
- T6 implementation conflicts with `docs/physics_spec.md v0.1-frozen`。
- Passing tests would require relaxing validation thresholds without physical/numerical justification。
- Numeric regression fixtures are requested before diagnostics are trustworthy.

## 完成条件

- 所有当前可运行 tests 通过。
- `status.md` 记录:
  - changed files
  - commands run
  - test results
  - sample parameter set
  - max lmax convergence residual
  - near-axis finite result
  - remaining risks
  - 是否可以进入下一阶段
- 如果不能进入下一阶段，给出 blocking issue 和应交回的线程。
