# Phase 1 T3 Goal Prompt: 角向基、spin-weighted harmonics 与 Wigner-D

你现在是 `T3：角向基与旋转` 线程。当前阶段是 Phase 1 / M1 的基础物理模块并行开发。你的目标是实现并稳定 angular public API：scalar spherical harmonics、spin-weighted spherical harmonics、Wigner-D wrapper、tensor-harmonic normalization registry/checks。不要实现径向背景、RW/Zerilli potentials、incident coefficients、Weyl scalars 或 plotting。

## Goal 功能

请在开始时创建 Codex goal：

```text
Objective: Complete Phase 1 T3 angular foundation: stable public API for scalar_sph_harm, spin_weighted_sph_harm, wigner_D, tensor-harmonic normalization registry/checks, unit tests, and status.md update.
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
10. `references/notes/schwarzschild_perturbations_review.md`
11. 现有 `src/schwgw/angular/`, `tests/unit/`

## 范围

必须实现：

- `scalar_sph_harm(ell, m, theta, phi)`
- `wigner_D(ell, m, mp, alpha, beta, gamma)`
- `spin_weighted_sph_harm(s, ell, m, theta, phi)`
- tensor-harmonic normalization registry/checks

允许修改：

- `src/schwgw/angular/__init__.py`
- `src/schwgw/angular/scalar_harmonics.py`
- `src/schwgw/angular/wigner.py`
- `src/schwgw/angular/spin_weighted.py`
- `src/schwgw/angular/tensor_harmonics.py`
- `tests/unit/test_scalar_harmonics.py`
- `tests/unit/test_wigner.py`
- `tests/unit/test_spin_weighted_harmonics.py`
- `tests/unit/test_tensor_harmonics.py`
- `status.md`
- 如必须新增轻量依赖，先检查当前环境和 `pyproject.toml`，并优先使用已有 `numpy/scipy`。

禁止修改：

- `src/schwgw/backgrounds/`
- `src/schwgw/perturbations/potentials.py`
- `src/schwgw/numerics/`
- `src/schwgw/waves/`
- `src/schwgw/scattering/`
- `src/schwgw/viz/`
- `docs/physics_spec.md`，除非发现 frozen convention 错误；若发现，停止并在 `status.md` 记录 blocking issue。

## Convention

以 `docs/physics_spec.md` Sec. 1.2 为唯一来源：

```text
Y_lm(theta,phi)
  = (-1)^m sqrt((2l+1)/(4pi) * (l-m)!/(l+m)!)
    P_l^m(cos theta) exp(i m phi)

D^l_{m m'}(alpha,beta,gamma)
  = exp(-i m alpha) d^l_{m m'}(beta) exp(-i m' gamma)

_sY_lm(theta,phi)
  = (-1)^s sqrt((2l+1)/(4pi)) [D^l_{m,-s}(phi,theta,0)]^*
```

必须保证 `_0Y_lm = Y_lm`。

## TDD 任务链

按小步循环执行。每一步先写/扩展测试，看到预期失败，再改实现。

### Task T3.1: scalar_sph_harm

测试要求：

- 已知低阶值：
  - `Y_00 = 1/sqrt(4*pi)`
  - `Y_10 = sqrt(3/(4*pi)) cos(theta)`
  - `Y_11 = -sqrt(3/(8*pi)) sin(theta) exp(i phi)`
- conjugation identity：`Y_l,-m = (-1)^m conj(Y_lm)`
- 数值正交性：小 quadrature grid 上 `int Y_lm^* Y_lm sin(theta)dtheta dphi ~= 1`
- invalid `ell < 0` 或 `abs(m) > ell` 报错。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_scalar_harmonics.py
```

实现建议：

- 可用 `scipy.special.sph_harm_y` 若可用；否则使用 `scipy.special.lpmv` 按 frozen convention 自实现。
- API 参数顺序必须是 `(ell, m, theta, phi)`。
- 支持 scalar 和 NumPy array 输入。

### Task T3.2: Wigner-D wrapper

测试要求：

- identity rotation：`D^l_{m mp}(0,0,0) = delta_mmp`
- `D^0_{0,0} = 1`
- unitarity：固定 `ell` 的 D 矩阵近似 unitary
- 与 scalar harmonics 的关系支持 `_0Y_lm = Y_lm`
- invalid indices 报错。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_wigner.py
```

实现建议：

- 若无可靠库，先实现小 `ell` 所需的 Wigner small-d summation formula，并以 tests 覆盖 `ell <= 4`。
- 不要引入未登记的大型依赖。
- 若库 convention 不匹配，写 wrapper 变换，不能改 `docs/physics_spec.md`。

### Task T3.3: spin_weighted_sph_harm

测试要求：

- `_0Y_lm(theta,phi) == Y_lm(theta,phi)`
- orthonormality for representative `s=0, ±1, ±2`
- invalid `abs(s) > ell` 或 `abs(m) > ell` 报错。
- conjugation identity 使用本项目 convention，若实现前无法确定符号，先从 frozen Wigner-D definition 推导并写在 test 注释中。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_spin_weighted_harmonics.py
```

### Task T3.4: tensor-harmonic normalization registry/checks

目标不是实现完整 tensor harmonics，而是建立 normalization registry/checks，防止后续 T6 把 target-paper tensor-basis normalization 和 unit-sphere harmonics 混在一起。

建议 API：

```python
tensor_harmonic_labels() -> tuple[str, ...]
tensor_harmonic_parity(label: str) -> Literal["even", "odd"]
```

测试要求：

- labels 包含 `{tt, Rt, L0, T0, Et, E1, Bt, B1, E2, B2}`
- parity split 与 `docs/physics_spec.md` Sec. 3 一致。
- RW gauge radiative surviving labels 可查询：odd `{Bt, B1}`, even `{tt, Rt, L0, T0}`。

推荐测试命令：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_tensor_harmonics.py
```

### Task T3.5: Full local verification and status

运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
```

更新 `status.md`：

- changed files
- public API
- dependency choice and reason
- commands run
- test results
- remaining open issues
- whether M1/T3 slice is complete

## 停止条件

立即停止并更新 `status.md`，不要继续猜测：

- 无法让外部库匹配 `docs/physics_spec.md` Sec. 1.2 convention。
- spin-weighted harmonic conjugation或 Wigner-D index order 出现无法解释的相位冲突。
- 为通过测试需要改变 T1 frozen convention。
- 同一测试失败经 3 次独立 root-cause 尝试仍不能解释。
- 需要修改 T2/T4/T5/T6/T8 范围文件才能继续。
- 正交性测试需要放宽到差于 `1e-8` 且没有清楚 quadrature 误差解释。
- 需要安装大型或不稳定依赖，但未获用户确认。

## 完成条件

- T3 public API 稳定并从 package-level imports 可用。
- scalar/spin-weighted/Wigner-D/tensor registry unit tests 通过。
- 全部当前 pytest 通过。
- `status.md` 已更新。
- 未实现 radial ODE、incident coefficients、Weyl 或 plotting。
