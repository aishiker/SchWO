# Phase 1 T7 Goal Prompt: T2/T3 基础模块同步 unit tests

你现在是 `T7：验证与基准` 线程。当前阶段是 Phase 1 / M1 的基础物理模块并行开发复核。T2 和 T3 已显示完成目标；你的任务是独立复核它们的 public API、补齐/修正 unit tests、运行验证，并更新 `status.md`。不要实现新的物理功能，除非是为了修正明显的测试导入路径或测试辅助函数。

## Goal 功能

请在开始时创建 Codex goal：

```text
Objective: Complete Phase 1 T7 unit-test synchronization for completed T2/T3 modules: verify public APIs, add or repair unit tests for Schwarzschild/RWZ and angular/Wigner-D functionality, run full pytest, and update status.md with results and remaining risks.
```

不要设置 token budget，除非用户明确要求。持续推进直到测试复核完成或触发停止条件。只有在 T2/T3 API 均被测试覆盖、当前 pytest 通过、`status.md` 更新后，才把 goal 标记为 complete。只有同一阻塞条件连续出现至少 3 次且无法继续时，才标记 blocked。

## 必读文件

按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase1_t2_background_rwz_goal.md`
8. `docs/prompts/phase1_t3_angular_goal.md`
9. T2/T3 修改过的 `src/` 文件
10. 现有 `tests/unit/`, `tests/regression/`

## 范围

允许修改：

- `tests/unit/test_schwarzschild_background.py`
- `tests/unit/test_rwz_potentials.py`
- `tests/unit/test_sectors.py`
- `tests/unit/test_scalar_harmonics.py`
- `tests/unit/test_wigner.py`
- `tests/unit/test_spin_weighted_harmonics.py`
- `tests/unit/test_tensor_harmonics.py`
- `tests/regression/test_fixture_schema.py` 仅当 schema 测试因 API-independent 问题损坏
- `docs/validation_plan.md` 仅当需要记录测试阈值/命令边界变更
- `status.md`

原则上不要修改 `src/`。如果发现 T2/T3 的实现有明显 bug：

1. 先写失败测试证明问题。
2. 如果是小的导出/API wiring 错误，可最小修复。
3. 如果涉及 physics convention、公式、Wigner-D 相位、spin-weighted harmonic 定义、inverse tortoise branch 等实质问题，停止并在 `status.md` 标为 blocking issue，交回对应线程。

禁止修改：

- `docs/physics_spec.md`
- `docs/equation_map.md`
- `references/notes/`
- 非 T7 范围的 solver、incident wave、Weyl、plotting 代码

## 测试覆盖清单

### T2 覆盖项

必须确认有测试覆盖：

- `SchwarzschildBackground(M)` rejects `M <= 0`
- `f(r) = 1 - 2M/r`
- `df_dr(r) = 2M/r^2`
- `f(r) -> 0` as `r -> 2M+`
- `f(r) -> 1` as `r -> infinity`
- `drstar_dr(r) = 1/f(r)`
- finite-difference derivative of `r_star`
- `r_from_r_star(r_star(r)) ~= r` for representative exterior radii
- invalid exterior-domain inputs raise errors where appropriate
- `V_RW -> 0` at horizon
- `V_Zerilli -> 0` at horizon
- `V_RW ~ ell(ell+1)/r^2` at infinity
- `V_Zerilli ~ ell(ell+1)/r^2` at infinity
- `ell < 2` raises errors for potentials
- `Sector("odd")`, `Sector("even")`, enum values, package-level export

### T3 覆盖项

必须确认有测试覆盖：

- `scalar_sph_harm(0,0,theta,phi) = 1/sqrt(4*pi)`
- `scalar_sph_harm(1,0,theta,phi) = sqrt(3/(4*pi))*cos(theta)`
- `scalar_sph_harm(1,1,theta,phi) = -sqrt(3/(8*pi))*sin(theta)*exp(i phi)`
- scalar `Y_lm` orthonormality on a documented quadrature grid
- scalar conjugation identity `Y_l,-m = (-1)^m conj(Y_lm)`
- `wigner_D(l,m,mp,0,0,0) = delta_mmp`
- `D^0_00 = 1`
- Wigner-D matrix unitarity for representative `ell`
- `_0Y_lm = Y_lm`
- spin-weighted harmonics orthonormality for representative `s=0, ±1, ±2`
- invalid angular indices raise errors
- tensor harmonic labels contain `{tt, Rt, L0, T0, Et, E1, Bt, B1, E2, B2}`
- tensor harmonic parity split matches `docs/physics_spec.md`
- RW-gauge radiative surviving labels match odd `{Bt, B1}` and even `{tt, Rt, L0, T0}`

## 推荐命令

先分别跑 targeted tests：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_schwarzschild_background.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_rwz_potentials.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_sectors.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_scalar_harmonics.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_wigner.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_spin_weighted_harmonics.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_tensor_harmonics.py
```

再跑聚合验证：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/regression
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## 容差要求

- Tier 0 formula tests 优先使用 `rtol <= 1e-12`，除非有限差分误差或 quadrature 误差已明确说明。
- Angular orthonormality 默认目标 `<= 1e-8`，若 quadrature grid 导致更松容差，必须在测试和 `status.md` 解释。
- 不得为通过测试静默放宽到差于 `docs/validation_plan.md` 的策略。

## 停止条件

立即停止并更新 `status.md`，不要继续猜测：

- 发现 T2/T3 实现和 `docs/physics_spec.md v0.1-frozen` 冲突。
- 发现 T2/T3 public API 不稳定，无法写清晰测试。
- Wigner-D 或 spin-weighted harmonic 相位测试无法和 frozen convention 同时满足。
- `r_from_r_star` inverse branch 测试显示不可解释的多值/branch 问题。
- 同一失败测试经 3 次独立 root-cause 尝试仍不能解释。
- 为通过测试需要修改 T1 frozen docs。
- 为通过测试需要实现 T4 radial ODE、T5 incident coefficients、T6 Weyl 或 T8 plotting。

## 完成条件

- T2/T3 测试覆盖清单均满足，或未满足项明确记录为 blocking issue。
- targeted unit tests 通过。
- `tests/unit` 通过。
- `tests/regression` 通过。
- 全部当前 pytest 通过。
- `status.md` 记录 changed files、commands run、test results、coverage gaps、remaining risks。
- 未引入新的 solver、incident-wave、Weyl 或 plotting 实现。
