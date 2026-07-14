# Phase 3 T6d Prompt: Polarization Extraction 与 Partial-Wave Assembly

你现在是 `T6` 线程。本 slice 在 T6b/T6c 完成后启动。目标是把 T2-T5 和 T6b/T6c 串成最小可用的 finite-radius gravitational-wave wave-optics solver：输入 `M, k, r, theta, phi, A_plus, A_cross, lmax`，输出 complex amplitudes `h_plus, h_cross`。

不要实现 plotting、CLI 大改、transmission factor、generic incident direction 或大型 regression fixture 生成。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `references/notes/phase3_formula_audit.md`
9. `src/schwgw/numerics/radial_solver.py`
10. `src/schwgw/waves/incident.py`
11. `src/schwgw/perturbations/reconstruction.py`
12. `src/schwgw/scattering/weyl.py`

## 目标

实现：

- `hddot_plus_tilde = Psi_hat_4_tilde + Psi_hat_0_tilde`
- `hddot_cross_tilde = i(Psi_hat_4_tilde - Psi_hat_0_tilde)`
- `h_plus_tilde = -(Psi_hat_4_tilde + Psi_hat_0_tilde)/k^2`
- `h_cross_tilde = -i(Psi_hat_4_tilde - Psi_hat_0_tilde)/k^2`
- finite-radius partial-wave sum over `ell=2..lmax`, `m=-ell..ell`。
- odd/even sectors weighted by T5 `c_lm^(-)` and `c_lm^(+)`。
- radial unit solutions cached by `(sector, ell, k, background, boundary_config)` where practical。

## 允许修改

- `src/schwgw/scattering/observables.py`
- `src/schwgw/scattering/partial_wave.py`
- `src/schwgw/scattering/__init__.py`
- `tests/unit/test_polarization_extraction.py`
- `tests/physics/test_partial_wave_observables.py`
- `docs/equation_map.md`
- `status.md`

如需轻量 adapter 从 `RadialSolution` 获取 `(psi, dpsi_dr)`，可放在 `partial_wave.py`。不要把 radial ODE 解法复制到 scattering 层。

## 推荐 API

```python
@dataclass(frozen=True)
class PolarizationResult:
    h_plus: complex
    h_cross: complex
    psi0_hat: complex
    psi4_hat: complex
    lmax: int
    diagnostics: Mapping[str, float]

def polarization_from_weyl(k: float, psi0_hat: complex, psi4_hat: complex) -> tuple[complex, complex]:
    ...

def compute_polarization(
    *,
    background: SchwarzschildBackground,
    k: float,
    r: float,
    theta: float,
    phi: float,
    A_plus: complex,
    A_cross: complex,
    lmax: int,
    boundary_config: BoundaryConfig | None = None,
) -> PolarizationResult:
    ...
```

若现有 style 更适合不同命名，可调整，但必须保持高层输入输出等价。

## 测试要求

Unit tests：

- `polarization_from_weyl` 的 sign/factor 测试，覆盖 pure `Psi0`、pure `Psi4`、`Psi0=Psi4`、`Psi0=-Psi4`。
- `k <= 0`、`ell/lmax < 2`、`r <= 2M` 错误处理。
- 输出对 `A_plus`、`A_cross` 线性。
- `A_plus=A_cross=0` 输出零场。
- partial-wave assembly 不重新求解同一 `(sector, ell)` 的 radial ODE for each `m`。

Physics smoke tests：

- 小参数 `M=1, k=0.5, r=20, lmax=4` 可稳定输出 finite complex values。
- `lmax` 从 3 到 4 的结果变化 finite 且 diagnostics 记录。
- near-axis `theta=0` 或小角度不产生 `NaN/Inf`。

不要在本 slice 强行要求最终 `1e-4` convergence；完整 convergence 交给 T7。

## 停止条件

立即停止并更新 `status.md`：

- `polarization_from_weyl` sign 与 `docs/physics_spec.md` Sec. 9 冲突。
- T6c 无法稳定输出 `Psi_hat_0` 和 `Psi_hat_4`。
- partial-wave sum 需要修改 T5 incident coefficients 或 T4 radial boundary convention。
- near-axis 发生非物理发散，且不是简单的 singular coordinate handling bug。
- 为完成本 slice 需要实现 plotting、transmission factor、generic incident direction 或 final benchmark fixtures。

## 完成条件

- 高层 API 能输出 `h_plus, h_cross`。
- targeted tests 通过：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_polarization_extraction.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_partial_wave_observables.py
```

- full current pytest 通过。
- `status.md` 记录 sample parameters、diagnostics、known risks、是否可交给 T7 做 full physics validation。
