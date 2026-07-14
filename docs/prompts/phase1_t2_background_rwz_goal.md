# Phase 1 T2 Goal Prompt: 背景与 RW/Zerilli 主方程基础模块

你现在是 `T2：背景与主方程` 线程。当前阶段是 Phase 1 / M1 的基础物理模块并行开发。你的目标是稳定 Schwarzschild background 与 RW/Zerilli potentials 的 public API，并让相关 unit tests 全部通过。不要实现径向 ODE solver、incident wave、angular harmonics、Weyl scalars 或 plotting。

## Goal 功能

请在开始时创建 Codex goal：

```text
Objective: Complete Phase 1 T2 background/RWZ foundation: stable public API for SchwarzschildBackground, f, df/dr, r_star, inverse tortoise, RW/Zerilli potentials, odd/even sector enum, unit tests, and status.md update.
```

不要设置 token budget，除非用户明确要求。持续推进直到目标完成或触发停止条件。只有在 public API 稳定、测试通过、`status.md` 更新后，才把 goal 标记为 complete。只有同一阻塞条件连续出现至少 3 次且无法继续时，才标记 blocked。

## 必读文件

按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/architecture.md`
7. `docs/validation_plan.md`
8. `references/manifest.md`
9. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
10. `references/notes/regge1957.md`
11. `references/notes/moncrief1974.md`
12. 现有 `src/schwgw/backgrounds/`, `src/schwgw/perturbations/`, `tests/unit/`

## 范围

必须实现或确认稳定：

- `SchwarzschildBackground`
- `f(r)`
- `df_dr(r)`
- `drstar_dr(r) = 1/f`
- `r_star(r)`
- `r_from_r_star(r_star)`
- `V_RW(ell, r)`
- `V_Zerilli(ell, r)`
- `Sector` enum: `odd`, `even`

允许修改：

- `src/schwgw/backgrounds/base.py`
- `src/schwgw/backgrounds/schwarzschild.py`
- `src/schwgw/backgrounds/__init__.py`
- `src/schwgw/perturbations/potentials.py`
- `src/schwgw/perturbations/sectors.py`
- `src/schwgw/perturbations/__init__.py`
- `tests/unit/test_schwarzschild_background.py`
- `tests/unit/test_rwz_potentials.py`
- 可新增 `tests/unit/test_sectors.py`
- `status.md`

禁止修改：

- `src/schwgw/angular/`
- `src/schwgw/waves/`
- `src/schwgw/scattering/`
- `src/schwgw/viz/`
- `docs/physics_spec.md`，除非发现 frozen convention 错误；若发现，停止并在 `status.md` 记录 blocking issue。

## TDD 任务链

按小步循环执行。每一步先写/扩展测试，看到预期失败，再改实现。

### Task T2.1: Schwarzschild background API

测试要求：

- `f(r) = 1 - 2M/r`
- `df_dr(r) = 2M/r^2`
- `f(r) -> 0` as `r -> 2M+`
- `f(r) -> 1` as `r -> infinity`
- `drstar_dr(r) = 1/f(r)`
- `r_from_r_star(r_star(r)) ~= r`

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_schwarzschild_background.py
```

实现要求：

- 标量输入返回 Python `float` 或可比较标量。
- array-like 输入返回 NumPy array。
- `r <= 2M` 对 `r_star` 和 exterior-only inverse checks 应显式报错。
- `M <= 0` 应显式报错。
- `r_from_r_star` 可用 `scipy.special.lambertw` 的 Schwarzschild exterior branch，返回实数；必须测试 round-trip。

### Task T2.2: RW/Zerilli potentials

测试要求：

- `V_RW -> 0` at horizon。
- `V_Zerilli -> 0` at horizon。
- `V_RW ~ ell(ell+1)/r^2` at infinity。
- `V_Zerilli ~ ell(ell+1)/r^2` at infinity。
- `ell < 2` 报错。
- scalar/array 输入行为一致。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_rwz_potentials.py
```

实现要求：

- 公式严格以 `docs/physics_spec.md` Sec. 5 为准。
- 不引入 Moncrief 变量 normalization。
- 不实现 radial RHS 或 ODE integration，除非用户后续明确启动 T4。

### Task T2.3: Sector enum

新增 `src/schwgw/perturbations/sectors.py`。

推荐 public API：

```python
from enum import Enum

class Sector(str, Enum):
    ODD = "odd"
    EVEN = "even"
```

测试要求：

- `Sector.ODD.value == "odd"`
- `Sector.EVEN.value == "even"`
- enum 可由字符串构造：`Sector("odd")`, `Sector("even")`
- package import 暴露 `Sector`

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_sectors.py
```

### Task T2.4: Full local verification and status

运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
```

更新 `status.md`：

- changed files
- public API
- commands run
- test results
- remaining open issues
- whether M1/T2 slice is complete

## 停止条件

立即停止并更新 `status.md`，不要继续猜测：

- 发现 `docs/physics_spec.md v0.1-frozen` 与文献 notes 明显冲突，需要改 convention。
- `r_from_r_star` 的 inverse convention 或 branch 无法确定。
- 为通过测试需要改变 T1 frozen convention。
- 同一测试失败经 3 次独立 root-cause 尝试仍不能解释。
- 需要修改 T3/T5/T6/T8 范围文件才能继续。
- 数值容差必须放宽超过 `docs/validation_plan.md` 当前 Tier 0 策略。

## 完成条件

- T2 public API 稳定并从 package-level imports 可用。
- T2 unit tests 通过。
- 全部当前 pytest 通过。
- `status.md` 已更新。
- 未实现径向 solver、incident wave、angular harmonics、Weyl 或 plotting。
