# Phase 2 T7 Goal Prompt: T4/T5 物理测试同步

你现在是 `T7：验证与基准` 线程。当前阶段是 Phase 2：径向求解与入射波边界并行。你的任务是同步设计并维护 T4/T5 的 physics tests：可以在 T4/T5 尚未完成时先根据本文件和对应 prompt 写 expected-failing tests；最终复核必须在 T4/T5 public API 存在后运行。不要实现新的 solver 或 incident-wave 功能，除非是为了修正明显的测试导入路径或小型 API wiring 错误。

## Goal 功能

请在开始时创建 Codex goal：

```text
Objective: Complete Phase 2 T7 physics-test synchronization for T4/T5: verify radial ODE/matching diagnostics and incident-plane-wave boundary coefficients, add or repair physics/unit tests, run targeted and full pytest, and update status.md with readiness judgment for the next phase.
```

不要设置 token budget，除非用户明确要求。持续推进直到测试复核完成或触发停止条件。若 T4/T5 API 尚未实现，先写清晰的 expected-failing tests 和 status pending 记录，不要把“实现尚未到位”本身当成 blocking condition。只有在 T4/T5 API 均被测试覆盖、当前 pytest 通过、`status.md` 更新后，才把 goal 标记为 complete。只有同一真实阻塞条件连续出现至少 3 次且无法继续时，才标记 blocked。

## 必读文件

按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/prompts/phase2_t4_radial_solver_goal.md`
9. `docs/prompts/phase2_t5_incident_wave_goal.md`
10. T4/T5 修改过的 `src/` 文件
11. 现有 `tests/unit/`, `tests/physics/`, `tests/regression/`

## 启动模式

T7 有两种合法启动模式：

1. **Parallel test-design mode**：T4/T5 还在进行中。此时 T7 可先根据 `docs/prompts/phase2_t4_radial_solver_goal.md` 和 `docs/prompts/phase2_t5_incident_wave_goal.md` 写 tests。允许这些 tests 因 API 尚未实现而失败，但必须在 `status.md` 明确标为 expected-failing / pending implementation，不得声称 Phase 2 验证完成。
2. **Final verification mode**：T4/T5 已声明完成。此时 T7 必须运行 targeted tests、`tests/unit`、`tests/physics`、`tests/regression` 和 full pytest，并给出是否可进入 T6 的明确判断。

## 范围

允许修改：

- `tests/unit/test_radial_solver.py`
- `tests/physics/test_radial_solver.py`
- `tests/unit/test_incident_wave.py`
- `tests/physics/test_incident_flat_space.py`
- `tests/regression/test_fixture_schema.py` 仅当 schema 测试因 API-independent 问题损坏
- `docs/validation_plan.md` 仅当需要记录测试阈值/命令边界变更
- `status.md`

原则上不要修改 `src/`。如果发现 T4/T5 的实现有明显 bug：

1. 先写失败测试证明问题。
2. 如果是小的导出/API wiring 错误，可最小修复。
3. 如果涉及 physics convention、phase sign、radial boundary condition、matching convention、Wigner-D/incident coefficient signs、Wronskian definition 等实质问题，停止并在 `status.md` 标为 blocking issue，交回对应线程。

禁止修改：

- `docs/physics_spec.md`
- `docs/equation_map.md`
- `references/notes/`
- 非 T7 范围的 Weyl、metric reconstruction、plotting 或 full partial-wave assembly code

## T4 测试覆盖清单

必须确认有测试覆盖：

- `BoundaryConfig` default values and validation。
- horizon `r_in = 2M(1+eps)`。
- horizon ingoing condition：

```text
dpsi_dr / psi = -i k / f(r_in)
```

- ODE smoke tests for both odd and even sectors。
- ODE residual test on the returned radial solution。
- Wronskian stability test using:

```text
W = f(r) [psi^* dpsi/dr - psi dpsi^*/dr]
```

- Outer asymptotic matching test:

```text
psi(r_out)      ~= A_in exp(-i k r_star) + A_out exp(+i k r_star)
dpsi/dr(r_out) ~= (-i k/f) A_in exp(-i k r_star)
                 +(+i k/f) A_out exp(+i k r_star)
```

- `boundary_residual` and `match_condition_number` are recorded。
- phase-factor extraction uses:

```text
exp(2i delta_l) = -A_out / [(-1)^ell A_in]
```

- radial interpolation consistency:
  - `psi_at(r_grid[i]) == psi[i]`
  - `dpsi_dr_at(r_grid[i]) == dpsi_dr[i]`
  - `dpsi_drstar_at(r) == f(r) dpsi_dr_at(r)`
  - invalid out-of-domain interpolation raises errors。

## T5 测试覆盖清单

必须确认有测试覆盖：

- `A_L/A_R` invertibility。
- pure plus and pure cross cases。
- algebraic circular cases without relying on handedness intuition。
- `IncidentPlaneGW(k <= 0)` rejects invalid frequency。
- only `m=±2` modes excited for `+z` propagating plane GW。
- `A_lm_plus/A_lm_minus` signs match `docs/physics_spec.md` exactly。
- `c_lm_odd` and `c_lm_even` match frozen formulas and catch exponent-binding mistakes。
- flat-space `M -> 0` master functions:

```text
D_lm^(-) = -k r A_lm^(-) j_l(k r)
D_lm^(+) =  2 r A_lm^(+) j_l(k r)
```

- flat-space large-`kr` asymptotics match:

```text
D_lm^(±) -> c_lm^(±) [exp(-ikr) - (-1)^ell exp(+ikr)]
```

within a documented asymptotic tolerance。

## 推荐命令

先分别跑 targeted tests：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_incident_wave.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_incident_flat_space.py
```

再跑聚合验证：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## 容差要求

- Boundary matching residual 默认目标 `< 1e-8`。
- Wronskian residual 默认 first-pass 目标 `< 1e-7`；若第一版只能达到更松阈值，必须记录参数、原因和下一步数值改进，不得静默放宽。
- Radial interpolation at solver grid points 应接近 machine precision；若 dense output 有轻微差别，记录实际容差。
- Flat-space large-`kr` asymptotic test 应使用明确的 `kr` 和容差，并说明这是 Bessel asymptotic error，不是 coefficient formula error。
- 不得为通过测试静默放宽到差于 `docs/validation_plan.md` 的策略。

## 退出阶段判定

T7 完成后必须在 `status.md` 写出明确判断：

- Phase 2 / T4-T5 是否满足：
  - 给定 `k, ell, sector` 可以稳定输出 radial `psi_l^(±)(r)`。
  - 给定 `A_plus, A_cross` 可以稳定输出 `c_lm^(±)`。
  - `M -> 0` 或弱场 sanity check 通过。
- 是否可以启动下一阶段 T6：metric reconstruction、Weyl scalars、polarization extraction。
- 哪些风险必须在 T6 前保持可见。

## 停止条件

立即停止并更新 `status.md`，不要继续猜测：

- T4 或 T5 已声明完成，但仍未提供 prompt 中约定的可导入 public API。
- T4/T5 尚未完成时，expected-failing tests 无法根据 prompt 设计出稳定 API contract。
- 发现 T4/T5 实现和 `docs/physics_spec.md v0.1-frozen` 冲突。
- Wronskian 或 outer matching 测试失败且 3 次独立 root-cause 尝试后仍不能解释。
- `M -> 0` flat-space sanity 与 target-paper Eq. (24)-(27) 冲突。
- 为通过测试需要修改 T1 frozen docs。
- 为通过测试需要实现 T6 Weyl、metric reconstruction、observables、T8 plotting 或 full partial-wave sum。
- 需要生成 numeric regression fixtures，但 solver diagnostics 尚不可信。

## 完成条件

- T4/T5 测试覆盖清单均满足，或未满足项明确记录为 blocking issue。
- targeted radial tests 通过。
- targeted incident-wave tests 通过。
- `tests/unit` 通过。
- `tests/physics` 中当前可运行 tests 通过。
- `tests/regression` schema tests 通过。
- 全部当前 pytest 通过。
- `status.md` 记录 changed files、commands run、test results、diagnostics sample、coverage gaps、remaining risks、是否可以启动 T6。
- 未引入 Weyl、metric reconstruction、plotting 或 full partial-wave assembly 实现。
