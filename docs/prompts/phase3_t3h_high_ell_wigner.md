# Phase 3 T3h Prompt: High-Ell Wigner-D Numerical Hardening

你现在是 `T3：角向基与旋转` 线程，slice 名称为 `T3h`。

背景：

- T7g 已完成 regression fixture schema v0.2。
- R60_K1 numeric fixture 没有生成，因为 Q016 阻塞：
  `src/schwgw/angular/wigner.py` 在 `lmax=60` 的 Wigner-D / spin-weighted harmonic evaluation 中触发 `OverflowError: int too large to convert to float`。
- 这是 angular 数值实现问题，不是 T4 radial 问题。
- 不要启动或修改 T4h；Q015 已是 non-blocking radial diagnostic warning。

先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `src/schwgw/angular/wigner.py`
8. `src/schwgw/angular/spin_weighted.py`
9. `src/schwgw/angular/scalar_harmonics.py`
10. `tests/unit/test_wigner.py`
11. `tests/unit/test_spin_weighted_harmonics.py`
12. `tests/physics/test_phase3_validation.py`

目标：

修复 high-`ell` Wigner-D / spin-weighted spherical harmonic 的数值 overflow，使 benchmark-scale `ell` 至少覆盖 `ell=72`，最好覆盖到 `ell=120`，同时保持现有 frozen Wigner-D convention 不变。

必须先复现：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 - <<'PY'
from schwgw.angular import wigner_D, spin_weighted_sph_harm
for ell in (40, 50, 60, 72):
    print("ell", ell)
    print(wigner_D(ell, 2, -2, 0.0, 0.4, 0.0))
    print(spin_weighted_sph_harm(-2, ell, 2, 0.4, 0.0))
PY
```

预期当前失败点：`ell=60` 附近的 factorial prefactor overflow。

实现要求：

1. 用 TDD 增加 RED tests
   - `wigner_D(60, 2, -2, ...)` 和 `spin_weighted_sph_harm(-2, 60, 2, ...)` 不得 overflow，结果 finite。
   - 覆盖 `ell=72` 的 finite check。
   - 高 `ell` spin-0 relation 仍应复现 scalar spherical harmonic：`_0Y_lm = Y_lm`，至少测一个 `ell>=40`、非平凡 `m`、多个角点。
   - 高 `ell` conjugation identity 仍成立，容差可按数值稳定性合理设置，但必须记录。

2. 修复算法
   - 不要直接把大 factorial 乘积转成 float。
   - 可采用 `scipy.special.gammaln` / log-domain signed summation，或更稳定的 Jacobi polynomial / recurrence 实现。
   - 必须保持当前 public API 和 project convention：
     - `wigner_D(ell, m, mp, alpha, beta, gamma)`
     - `D = exp(-i m alpha) d^ell_{m,mp}(beta) exp(-i mp gamma)`
     - project small-d index order 与现有 tests 保持一致。
   - 处理 `beta=0`、`beta=pi`、`sin(beta/2)=0`、`cos(beta/2)=0` 等边界角，避免 `0**negative` 或 `nan`。
   - 允许内部 helper 拆分，但不要引入大型新依赖。

3. 性能要求
   - 单个 Wigner-D evaluation 对 `ell~100` 应可接受；不要为了测试构造 `121x121` high-ell full matrix。
   - 如果增加 cache，必须是局部且不会污染物理结果；不要把 observer angle 或 run-specific data 写入全局文件。

4. 不允许修改
   - 不改 `src/schwgw/numerics/`。
   - 不改 T4 radial solver、boundary conditions、Wronskian thresholds。
   - 不改 T6 polarization/partial-wave physics convention。
   - 不生成 regression fixture。
   - 不做 plotting。

停止条件：

- 修复需要改变 Wigner-D index convention、spin-weighted harmonic convention 或 scalar-harmonic relation。
- high-`ell` finite tests 通过但 low-`ell` unitarity / scalar relation 失败。
- 修复需要新增大型依赖。
- `ell=60/72` 仍 overflow 或返回 non-finite，且三次独立数值策略后仍不能解释。

必须运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_wigner.py tests/unit/test_spin_weighted_harmonics.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_phase3_validation.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

完成时更新 `status.md`：

- changed files
- root cause
- algorithm choice
- high-`ell` validation results
- commands run
- test results
- whether Q016 is resolved or still open
- next action：若 Q016 resolved，明确让 T7h rerun first numeric fixture slice
