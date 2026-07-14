# Phase 3 T6c Prompt: Weyl Scalars 与 Tetrad Transform

你现在是 `T6` 线程。本 slice 在 T6b metric reconstruction 已完成后启动。目标是实现 Weyl scalar mode components、Kinnersley tetrad、incident-wave-aligned tetrad，以及 Weyl scalars 的 tetrad transformation。不要实现最终 `h_plus/h_cross` partial-wave observable。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `references/notes/phase3_formula_audit.md`
7. `src/schwgw/perturbations/reconstruction.py`
8. `src/schwgw/angular/spin_weighted.py`
9. `src/schwgw/angular/wigner.py`
10. `tests/unit/test_metric_reconstruction.py`

## 目标

实现：

- Kinnersley tetrad in Schwarzschild coordinates。
- incident Cartesian tetrad convention。
- `Psi_0 ... Psi_4` mode components in the Kinnersley tetrad。
- 用 Wigner-D / frozen convention 转换到 incident-wave-aligned tetrad 的 `Psi_hat_n`。

## 允许修改

- `src/schwgw/scattering/tetrads.py`
- `src/schwgw/scattering/weyl.py`
- `src/schwgw/scattering/__init__.py`
- `tests/unit/test_tetrads.py`
- `tests/unit/test_weyl_modes.py`
- `docs/equation_map.md`
- `status.md`

不要修改 T2-T5 公式模块，除非只是导出缺失符号且有测试覆盖。

## 关键约定

必须使用 `docs/physics_spec.md` 中的 tetrads：

```text
l^mu = (f^(-1), 1, 0, 0)
n^mu = (1/2) (1, -f, 0, 0)
m^mu = (1/(sqrt(2) r)) (0, 0, 1, i csc(theta))
```

和：

```text
lhat^muhat = (1/sqrt(2)) (1, 0, 0,  1)
nhat^muhat = (1/sqrt(2)) (1, 0, 0, -1)
mhat^muhat = (1/sqrt(2)) (0, 1, i,  0)
```

签名为 `(-,+,+,+)`。不要改 tetrad normalization 来适配测试。

## 测试要求

新增 unit tests，至少覆盖：

- Kinnersley tetrad null inner products：
  - `l.l = n.n = m.m = 0`
  - `l.n = -1`
  - `m.mbar = 1`
- incident Cartesian tetrad null inner products。
- identity/no-rotation transformation 不改变对应 Weyl scalars。
- zero metric mode 给出零 Weyl scalars。
- mode assembly 对输入 metric components 线性。
- spin-weight labels 和 `_sY_lm` 使用相容，至少检查 `Psi_0` 与 `Psi_4` 的 spin weight sign 未互换。
- Wigner-D transform 使用 `docs/physics_spec.md` convention，可用 identity rotation 和一个低 `ell` 手算 case 测。

## 停止条件

立即停止并更新 `status.md`：

- Eq. (30)-(40) 的 `Z_{n,lm}^{(±)}` 公式不完整或无法映射到 T6b metric components。
- 发现 Kinnersley tetrad normalization 与 `docs/physics_spec.md` 冲突。
- 需要修改 spin-weighted harmonic convention 才能通过测试。
- 需要实现 final `h_plus/h_cross` 或 partial-wave sum 才能测试本 slice。
- 测试只能通过放宽到不可解释的容差。

## 完成条件

- `tetrads.py` 和 `weyl.py` 有清晰 public API。
- targeted tests 通过：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_tetrads.py tests/unit/test_weyl_modes.py
```

- full current pytest 通过。
- `docs/equation_map.md` 与 `status.md` 更新。
