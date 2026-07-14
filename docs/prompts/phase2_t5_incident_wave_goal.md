# Phase 2 T5 Goal Prompt: 入射平面 GW 与边界系数

你现在是 `T5：入射平面波与边界系数` 线程。当前阶段是 Phase 2：径向求解与入射波边界并行。你的目标是实现 incident plane GW 的 public API：`IncidentPlaneGW`、`A_plus/A_cross`、`A_L/A_R`、`A_lm^(+)`、`A_lm^(-)`、`c_lm_even`、`c_lm_odd`，以及 flat-space `M -> 0` master functions。不要实现 radial ODE solver、Weyl scalars、metric reconstruction、plotting 或 full partial-wave assembly。

## Goal 功能

请在开始时创建 Codex goal：

```text
Objective: Complete Phase 2 T5 incident-plane-wave boundary coefficients: IncidentPlaneGW, A_plus/A_cross to A_L/A_R conversion, A_lm_even/A_lm_odd, c_lm_even/c_lm_odd, flat-space M->0 radial master functions, tests, and status.md update.
```

不要设置 token budget，除非用户明确要求。持续推进直到目标完成或触发停止条件。只有在 public API 稳定、T5/T7-relevant tests 通过、`status.md` 更新后，才把 goal 标记为 complete。只有同一阻塞条件连续出现至少 3 次且无法继续时，才标记 blocked。

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
10. T3 相关源码和测试：
    - `src/schwgw/angular/`
    - `tests/unit/test_scalar_harmonics.py`
    - `tests/unit/test_wigner.py`
    - `tests/unit/test_spin_weighted_harmonics.py`
    - `tests/unit/test_tensor_harmonics.py`
11. 现有 `src/schwgw/waves/`, `tests/unit/`, `tests/physics/`

## 依赖与范围

依赖：

- T3 已完成 angular convention wrapper。
- T1 已冻结 `A_plus/A_cross/A_L/A_R`、`m=±2` selection rule 和 `c_lm` 相位。

必须实现或稳定：

- `IncidentPlaneGW`
- `A_plus`, `A_cross`
- `A_L`, `A_R`
- `A_lm_plus` / `A_lm_even`
- `A_lm_minus` / `A_lm_odd`
- `c_lm_odd`
- `c_lm_even`
- `flat_space_master_odd`
- `flat_space_master_even`

允许修改：

- `src/schwgw/waves/__init__.py`
- `src/schwgw/waves/polarizations.py`
- `src/schwgw/waves/incident.py`
- `tests/unit/test_incident_wave.py`
- `tests/physics/test_incident_flat_space.py`
- `status.md`

禁止修改：

- `src/schwgw/numerics/`
- `src/schwgw/backgrounds/`
- `src/schwgw/perturbations/potentials.py`
- `src/schwgw/angular/`
- `src/schwgw/scattering/`
- `src/schwgw/viz/`
- `docs/physics_spec.md`，除非发现 frozen convention 明显错误；若发现，停止并在 `status.md` 记录 blocking issue。

## Convention

以 `docs/physics_spec.md` Sec. 7 和 `docs/equation_map.md` 的 T5 条目为唯一来源。

Linear/circular conversion：

```text
A_L = (A_plus + i A_cross)/sqrt(2)
A_R = (A_plus - i A_cross)/sqrt(2)

A_plus  = (A_L + A_R)/sqrt(2)
A_cross = -i (A_L - A_R)/sqrt(2)
```

Plane-wave coefficients for default `+z` propagation：

```text
sigma_l = (l-1) l (l+1) (l+2)

A_lm^(±)
  = i^l sqrt(2pi(2l+1)/sigma_l)
    (A_L delta_{m,-2} ± A_R delta_{m,2})

c_lm^(-) = -[i^(l+1)/2] A_lm^(-)
c_lm^(+) =  [i^(l+1)/k] A_lm^(+)
```

Name mapping for code:

```text
A_lm_plus  = A_lm_even = A_lm^(+)
A_lm_minus = A_lm_odd  = A_lm^(-)
c_lm_odd   = c_lm^(-)
c_lm_even  = c_lm^(+)
```

Flat-space master functions from target-paper Eq. (24):

```text
D_lm^(-)(k,r) = -k r A_lm^(-)(k) j_l(k r)
D_lm^(+)(k,r) =  2 r A_lm^(+)(k) j_l(k r)
```

## 推荐 API

建议实现以下接口。可做小幅调整，但必须保持职责等价并在 tests/status 中说明。

```python
@dataclass(frozen=True)
class IncidentPlaneGW:
    k: float
    A_plus: complex
    A_cross: complex
    incident_direction: str = "+z"

    @property
    def A_L(self) -> complex: ...

    @property
    def A_R(self) -> complex: ...

    def A_lm_plus(self, ell: int, m: int) -> complex: ...
    def A_lm_minus(self, ell: int, m: int) -> complex: ...
    def A_lm_even(self, ell: int, m: int) -> complex: ...
    def A_lm_odd(self, ell: int, m: int) -> complex: ...
    def c_lm_even(self, ell: int, m: int) -> complex: ...
    def c_lm_odd(self, ell: int, m: int) -> complex: ...

    def flat_space_master_even(self, ell: int, m: int, r): ...
    def flat_space_master_odd(self, ell: int, m: int, r): ...
```

Also expose module-level functions where useful:

```python
linear_to_circular(A_plus, A_cross) -> tuple[complex, complex]
circular_to_linear(A_L, A_R) -> tuple[complex, complex]
sigma_l(ell) -> int
```

Do not support arbitrary incident direction in Phase 2. For any direction other than `"+z"`, raise `NotImplementedError` with a clear message that Wigner-D rotation is future scope.

## TDD 任务链

按小步循环执行。每一步先写/扩展测试，看到预期失败，再改实现。

### Task T5.1: Polarization conversion

测试要求：

- `linear_to_circular` and `circular_to_linear` are inverse maps for representative complex amplitudes。
- pure plus case。
- pure cross case。
- right/left circular special cases are checked algebraically without relying on naming intuition。
- invalid non-numeric amplitudes fail clearly if they cannot be converted to complex。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_incident_wave.py
```

### Task T5.2: IncidentPlaneGW dataclass

测试要求：

- `k > 0` required。
- default `incident_direction == "+z"`。
- any non-`"+z"` direction raises `NotImplementedError`。
- `A_L` and `A_R` properties match frozen convention。

### Task T5.3: `A_lm^(±)` and `m=±2` selection

测试要求：

- For `ell=2,3,4`, coefficients are zero for all `m` except `m=-2` and `m=+2`。
- `m=-2` term only uses `A_L`。
- `m=+2` term only uses `A_R`。
- plus/even uses `+ A_R delta_{m,2}`。
- minus/odd uses `- A_R delta_{m,2}`。
- `ell < 2` or `abs(m) > ell` raises `ValueError`。

Use exact formulas from `docs/physics_spec.md`; do not derive signs from angular-library behavior.

### Task T5.4: `c_lm_odd` and `c_lm_even`

测试要求：

- `c_lm_odd = -[i^(ell+1)/2] A_lm_minus`。
- `c_lm_even = [i^(ell+1)/k] A_lm_plus`。
- Tests must catch exponent-binding mistakes, especially `-i^(ell+1)/2` vs `-(i^(ell+1))/2`。
- Coefficients vanish for non-`m=±2` modes。

### Task T5.5: Flat-space master functions

测试要求：

- `flat_space_master_odd = -k r A_lm_minus j_l(k r)` exactly against `scipy.special.spherical_jn`。
- `flat_space_master_even = 2 r A_lm_plus j_l(k r)` exactly against `scipy.special.spherical_jn`。
- scalar and array-like `r` inputs preserve expected behavior。
- `r <= 0` raises `ValueError`。
- For large `kr`, flat-space master functions approach Eq. (26) asymptotic form:

```text
D_lm^(-) -> c_lm_odd  [exp(-ikr) - (-1)^ell exp(+ikr)]
D_lm^(+) -> c_lm_even [exp(-ikr) - (-1)^ell exp(+ikr)]
```

Use a conservative large-`kr` tolerance and record it in tests/status; the error is controlled by the spherical-Bessel asymptotic expansion.

推荐 physics 测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_incident_flat_space.py
```

### Task T5.6: Full verification and status

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_incident_wave.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_incident_flat_space.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

更新 `status.md`：

- changed files
- public API
- commands run
- test results
- representative coefficient values for one `ell,m,k,A_plus,A_cross` case
- remaining open issues
- whether Phase 2 / T5 slice is complete

## 停止条件

立即停止并更新 `status.md`，不要继续猜测：

- 为通过测试需要改变 T1 frozen `A_L/A_R`, `A_lm`, or `c_lm` convention。
- `m=±2` selection rule 与 T3 angular convention 出现不可解释冲突。
- flat-space Bessel behavior无法同时满足 Eq. (24) 和 Eq. (26)。
- 同一失败测试经 3 次独立 root-cause 尝试仍不能解释。
- 需要实现 T4 radial solver 才能完成 T5 基础 incident coefficients。
- 需要实现 Weyl、metric reconstruction、plotting 或 full partial-wave sum。
- 需要支持任意 incident direction；这是后续 Wigner-D rotation scope。

## 完成条件

- 给定 `A_plus, A_cross, k, ell, m` 可以稳定输出 `A_lm^(±)` 和 `c_lm^(±)`。
- `+z` 入射只激活 `m=±2`。
- `A_L/A_R` invertibility 测试通过。
- Flat-space `M -> 0` master functions 和 asymptotic sanity checks 通过。
- T5 targeted tests、相关 physics tests、当前 full pytest 通过。
- `status.md` 已更新。
- 未实现 radial solver、Weyl/scattering observables 或 plotting。
