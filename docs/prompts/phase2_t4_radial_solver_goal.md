# Phase 2 T4 Goal Prompt: 径向 ODE、边界匹配与 Wronskian diagnostics

你现在是 `T4：径向 ODE 与匹配` 线程。当前阶段是 Phase 2：径向求解与入射波边界并行。你的目标是实现 Schwarzschild RW/Zerilli radial solver 的第一版：给定 `(sector, ell, k, background, boundary_config)` 可以稳定输出径向 master function、导数、outer matching 系数、phase-shift 信息和 Wronskian diagnostics。不要实现 incident plane wave coefficients、Weyl scalars、metric reconstruction、plotting 或 full partial-wave assembly。

## Goal 功能

请在开始时创建 Codex goal：

```text
Objective: Complete Phase 2 T4 radial ODE and matching foundation: solve_radial_mode(sector, ell, k, background, boundary_config), ingoing horizon boundary condition, outer asymptotic matching, interpolation/derivative evaluation, phase-shift extraction, Wronskian diagnostics, tests, and status.md update.
```

不要设置 token budget，除非用户明确要求。持续推进直到目标完成或触发停止条件。只有在 public API 稳定、T4/T7-relevant tests 通过、`status.md` 更新后，才把 goal 标记为 complete。只有同一阻塞条件连续出现至少 3 次且无法继续时，才标记 blocked。

## 必读文件

按顺序阅读：

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/architecture.md`
8. `docs/validation_plan.md`
9. `references/manifest.md`
10. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
11. T2 相关源码和测试：
    - `src/schwgw/backgrounds/`
    - `src/schwgw/perturbations/potentials.py`
    - `src/schwgw/perturbations/sectors.py`
    - `tests/unit/test_schwarzschild_background.py`
    - `tests/unit/test_rwz_potentials.py`
12. 现有 `src/schwgw/numerics/`, `tests/unit/`, `tests/physics/`

## 依赖与范围

依赖：

- T2 已完成：`SchwarzschildBackground`, `df_dr`, `r_star`, `drstar_dr`, `V_RW`, `V_Zerilli`, `Sector` 可用。
- T1 frozen convention 不得修改。

必须实现或稳定：

- `BoundaryConfig`
- `RadialDiagnostics`
- `RadialSolution`
- `solve_radial_mode(sector, ell, k, background, boundary_config)`
- horizon ingoing initialization
- radial ODE RHS in Schwarzschild `r`
- outer 2x2 matching to `A_in exp(-ikr_star) + A_out exp(+ikr_star)`
- phase-shift extraction from `A_out/A_in`
- Wronskian diagnostic
- radial interpolation:
  - `psi_at(r)`
  - `dpsi_dr_at(r)`
  - `dpsi_drstar_at(r)`

允许修改：

- `src/schwgw/numerics/__init__.py`
- `src/schwgw/numerics/boundary_conditions.py`
- `src/schwgw/numerics/matching.py`
- `src/schwgw/numerics/radial_solver.py`
- 可新增 `src/schwgw/numerics/diagnostics.py`，但只有在能减少重复和保持接口清晰时才新增。
- `tests/unit/test_radial_solver.py`
- `tests/physics/test_radial_solver.py`
- `status.md`

禁止修改：

- `src/schwgw/waves/`
- `src/schwgw/angular/`
- `src/schwgw/scattering/`
- `src/schwgw/viz/`
- `docs/physics_spec.md`，除非发现 frozen convention 明显错误；若发现，停止并在 `status.md` 记录 blocking issue。
- T2 已稳定公式，除非测试证明存在局部 API bug；涉及 formula/convention 时必须停止。

## 设计约定

以 `docs/numerics.md` 为数值策略起点。径向方程：

```text
d^2 psi/dr_star^2 + [k^2 - V_l(r)] psi = 0
```

在 Schwarzschild `r` 变量中写成：

```text
y0 = psi
y1 = dpsi/dr

dy0/dr = y1
dy1/dr = -[f f' y1 + (k^2 - V)y0]/f^2
```

Horizon leading ingoing boundary condition：

```text
psi(r_in) = exp(-i k r_star(r_in))
dpsi/dr(r_in) = (-i k / f(r_in)) psi(r_in)
```

Outer matching：

```text
psi(r_out)      = A_in exp(-i k r_star) + A_out exp(+i k r_star)
dpsi/dr(r_out) = (-i k/f) A_in exp(-i k r_star)
                +(+i k/f) A_out exp(+i k r_star)
```

Phase-shift factor：

```text
exp(2i delta_l) = -A_out / [(-1)^ell A_in]
delta_l = -0.5i log(exp(2i delta_l))
```

这里 `delta_l` 可以是 complex，因为 Schwarzschild BH scattering 有 horizon absorption；不要强行转成实数。

Wronskian：

```text
W(r) = f(r) [psi^* dpsi/dr - psi dpsi^*/dr]
```

## 推荐 API

建议实现以下 dataclass。可做小幅调整，但必须保持职责等价并在 tests/status 中说明。

```python
@dataclass(frozen=True)
class BoundaryConfig:
    r_in_eps: float = 1e-6
    r_out: float | None = None
    rtol: float = 1e-10
    atol: float = 1e-12
    method: str = "DOP853"
    max_step: float | None = None
    dense_output: bool = True

@dataclass(frozen=True)
class RadialDiagnostics:
    boundary_residual: float
    wronskian_residual: float
    ode_n_steps: int
    ode_status: str
    r_in: float
    r_out: float
    atol: float
    rtol: float
    match_condition_number: float

@dataclass
class RadialSolution:
    sector: Sector
    ell: int
    k: float
    r_grid: np.ndarray
    psi: np.ndarray
    dpsi_dr: np.ndarray
    A_in: complex
    A_out: complex
    phase_factor: complex
    phase_shift: complex
    diagnostics: RadialDiagnostics

    def psi_at(self, r): ...
    def dpsi_dr_at(self, r): ...
    def dpsi_drstar_at(self, r): ...
```

`solve_radial_mode` 的 public signature 必须支持：

```python
solve_radial_mode(
    sector: Sector | str,
    ell: int,
    k: float,
    background: StaticSphericalBackground,
    boundary_config: BoundaryConfig | None = None,
) -> RadialSolution
```

第一版默认解为 unit horizon ingoing normalization。不要在 T4 中依赖 T5 的 `c_lm`。如果需要给后续 T5/T6 预留缩放能力，可增加 `RadialSolution.scaled_by(complex_scale)` 或 `scaled_to_incident(c_lm)`，但必须测试不改变 phase-factor 和 diagnostics 的定义。

## TDD 任务链

按小步循环执行。每一步先写/扩展测试，看到预期失败，再改实现。

### Task T4.1: BoundaryConfig and horizon ingoing data

测试要求：

- `BoundaryConfig` 默认值合法。
- `r_in = 2M(1+r_in_eps)`。
- `r_out` 若为 `None`，使用 `background.asymptotic_region_hint(k, ell)` 或更保守的正半径规则。
- `k <= 0`, `ell < 2`, `r_in_eps <= 0`, `r_out <= r_in` 报错。
- horizon initial data 满足：

```text
dpsi_dr / psi = -i k / f(r_in)
```

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
```

### Task T4.2: ODE RHS and solve_radial_mode smoke test

测试要求：

- `solve_radial_mode(Sector.ODD, 2, 0.5, bg, config)` 返回有限 complex arrays。
- even/odd sector 都可求解。
- `r_grid` strictly increasing and exterior。
- `psi`, `dpsi_dr` shape 与 `r_grid` 一致。
- invalid sector string 报错。

实现要求：

- 使用 `scipy.integrate.solve_ivp`，首选 `DOP853`。
- RHS 公式只从 T2 potentials 获取 `V_l(r)`，不要复制 potential 公式。
- 对 complex state 直接积分；若 SciPy 版本不支持 complex DOP853，先写清楚失败并尝试 real-imag split wrapper。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
```

### Task T4.3: Outer matching

测试要求：

- 在 `r_out` 处反代 `A_in`, `A_out` 能恢复 `psi(r_out)` 和 `dpsi/dr(r_out)`。
- `boundary_residual < 1e-8`，除非有清楚数值原因并同步 `docs/validation_plan.md` 与 `status.md`。
- matching matrix condition number 记录到 diagnostics。

实现要求：

- matching 只用 `r_star` phase，不用 `r` phase。
- `A_in` 过小导致 condition 或 phase extraction 不可信时，抛出明确异常或 diagnostics 标红；不要静默返回垃圾 phase。

### Task T4.4: Wronskian diagnostics

测试要求：

- 对代表性参数，如 `ell=2, k=0.5, r_in_eps=1e-5, r_out=80`，Wronskian relative residual 达到 `docs/validation_plan.md` 的 first-pass 阈值目标。
- Wronskian residual 在降低 `rtol/atol` 时不应恶化；若偶然小幅波动，记录实际值并解释。

推荐 physics 测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_radial_solver.py
```

### Task T4.5: Interpolation and derivative evaluation

测试要求：

- `psi_at(r_grid[i])` 与 stored `psi[i]` 一致。
- `dpsi_dr_at(r_grid[i])` 与 stored `dpsi_dr[i]` 一致。
- `dpsi_drstar_at(r) = f(r) dpsi_dr_at(r)`。
- interpolation 对 scalar 和 array-like 输入行为明确。
- 对 `r <= 2M` 或超出 solver domain 的 interpolation 输入报错。

### Task T4.6: Full verification and status

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

更新 `status.md`：

- changed files
- public API
- selected numerical defaults
- commands run
- test results
- diagnostics sample:
  - `boundary_residual`
  - `wronskian_residual`
  - `r_in`
  - `r_out`
  - method/rtol/atol
- remaining open issues
- whether Phase 2 / T4 slice is complete

## 停止条件

立即停止并更新 `status.md`，不要继续猜测：

- 为通过测试需要改变 T1 frozen Fourier/radial phase convention。
- ODE RHS 需要修改 T2 potentials 公式才能工作。
- horizon leading ansatz 在合理 `r_in_eps` sweep 下不稳定，且需要 Frobenius correction 才能继续。
- `A_in` matching convention 与 `docs/physics_spec.md` Sec. 6 或 `docs/numerics.md` 冲突。
- Wronskian residual 经 3 次独立 root-cause 尝试仍高于 first-pass 阈值且无解释。
- 需要 T5 的 incident coefficients 才能完成 T4 基础 solver。
- 为通过测试需要实现 Weyl、metric reconstruction、plotting 或 full partial-wave sum。
- 需要放宽 `docs/validation_plan.md` 阈值但无法给出数值理由。

## 完成条件

- 给定 `k, ell, sector` 可以稳定输出径向 `psi_l^(±)(r)` 和 `dpsi/dr`。
- Outer matching 返回可信 `A_in`, `A_out`, `phase_factor`, `phase_shift`。
- Wronskian diagnostics 和 boundary residual 已实现并测试。
- Interpolation/derivative evaluation 已实现并测试。
- T4 targeted tests、相关 physics tests、当前 full pytest 通过。
- `status.md` 已更新。
- 未实现 incident wave coefficients、Weyl/scattering observables 或 plotting。
