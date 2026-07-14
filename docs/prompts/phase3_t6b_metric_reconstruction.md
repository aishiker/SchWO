# Phase 3 T6b Prompt: RW-Gauge Metric Reconstruction

你现在是 `T6` 线程。本 slice 只实现 RW-gauge metric reconstruction operators。不要实现 Weyl scalars、polarization extraction、partial-wave sum 或 plotting。

## 前置条件

只有在 `phase3_t6a_formula_interface_audit.md` 已完成并且 `status.md` 没有 blocking issue 时启动。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `references/notes/phase3_formula_audit.md`
7. `references/notes/li_hou_zhao_2025_spin_wave_optics.md`
8. `src/schwgw/numerics/radial_solver.py`
9. `src/schwgw/perturbations/sectors.py`
10. `tests/unit/`

## 目标

实现单个 `(sector, ell, m, k, r)` master radial mode 到 RW-gauge metric harmonic components 的转换：

```text
h_tilde^{(a)}_{lm}(k,r) = J_l^{(a)}(k,r) psi_tilde_{lm}^{(±)}
```

要求：

- odd sector 只输出 RW-gauge radiative components `Bt`, `B1`。
- even sector 只输出 RW-gauge radiative components `tt`, `Rt`, `L0`, `T0`。
- 明确区分 `dpsi/dr` 与 `dpsi/dr_star = f dpsi/dr`。
- 所有 reconstruction 公式只放在 `src/schwgw/perturbations/reconstruction.py`。
- 不在 `weyl.py`、tests 或 plotting 中复制 reconstruction 公式。

## 允许修改

- `src/schwgw/perturbations/reconstruction.py`
- `src/schwgw/perturbations/__init__.py`
- `tests/unit/test_metric_reconstruction.py`
- `docs/equation_map.md`
- `status.md`

如需小型 helper，可放在同一模块或已有 perturbations package 内。不要新增大型依赖。

## 推荐数据结构

```python
@dataclass(frozen=True)
class MetricModeComponents:
    sector: Sector
    ell: int
    k: float
    r: float
    components: Mapping[str, complex]
```

推荐提供：

```python
def reconstruct_metric_mode(
    sector: Sector,
    ell: int,
    k: float,
    r: float,
    psi: complex,
    dpsi_dr: complex,
    background: SchwarzschildBackground,
) -> MetricModeComponents:
    ...
```

若公式需要二阶导数，优先用 master equation 和 potential 消去；若不能可靠消去，停止并记录 API 缺口，不要临时 finite-difference。

## 测试要求

新增 unit tests，至少覆盖：

- `ell < 2`、`k <= 0`、`r <= 2M` 的错误处理。
- odd/even 输出 component labels 与 RW gauge 一致。
- reconstruction 对 `psi` 和 `dpsi_dr` 线性。
- 输入为零时所有 components 为零。
- `dpsi/dr_star = f dpsi/dr` 使用正确，可用构造输入触发 sign/factor 错误。
- 公式 smoke test：选定 `M=1, ell=2, k=0.7, r=20`，用审计 notes 中的手算或独立表达式比较。

不要在这个 slice 写依赖 T4 ODE 数值解的大型 physics tests；只做公式和接口 unit tests。

## 停止条件

立即停止并更新 `status.md`：

- reconstruction 公式在 notes 中不完整或与 `docs/physics_spec.md` 冲突。
- 需要修改 `docs/physics_spec.md v0.1-frozen`。
- 需要实现 Weyl scalar 或 polarization 才能测试 reconstruction。
- 需要 finite-difference radial derivatives 才能让公式工作。
- T4 `RadialSolution` derivative convention 与本 slice 需求冲突。

## 完成条件

- `src/schwgw/perturbations/reconstruction.py` 实现并导出。
- targeted tests 通过：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_metric_reconstruction.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit
```

- full current pytest 通过：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

- `docs/equation_map.md` 和 `status.md` 更新。
