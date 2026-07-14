# Phase 3 Blocker Prompt: T6 Flat-Space No-Lens Adapter

你现在是 `T6：重构、Weyl、极化` 线程。Phase 3 T7b 未通过；当前 Q013 指出 no-lens / `M->0` oracle 不能直接用 tiny-`M` horizon-ingoing Schwarzschild solve 代替。你的任务是建立一个 flat-space no-lens adapter，用 T5 的 regular spherical-Bessel master functions 直接验证 T6b/T6c/T6d 的 polarization signs 和 Q011。

本任务目标是隔离 T6 convention，不修 T4 high-`ell` radial solver。不要使用 `solve_radial_mode` 构造 no-lens oracle。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `references/notes/phase3_formula_audit.md`
7. `src/schwgw/waves/incident.py`
8. `src/schwgw/perturbations/reconstruction.py`
9. `src/schwgw/scattering/weyl.py`
10. `src/schwgw/scattering/observables.py`
11. `src/schwgw/scattering/partial_wave.py`
12. `tests/physics/test_incident_flat_space.py`
13. `tests/physics/test_phase3_validation.py`

## 物理前提

Flat no-lens oracle 应使用 regular flat-space master functions:

```text
D_lm^(-) = -k r A_lm^(-) j_l(k r)
D_lm^(+) =  2 r A_lm^(+) j_l(k r)
```

这些已经在 T5 `IncidentPlaneGW.flat_space_master_odd/even` 中实现并测试。不要通过 `M=1e-6` Schwarzschild horizon boundary 来近似 flat no-lens；那会引入不相同的边界条件。

## 目标

建立一个只用于 validation 的 adapter：

- 对给定 `ell,m,sector,r`，从 T5 flat-space master function 得到 `psi`。
- 用 analytic derivative of `j_l(k r)` 或稳定的 SciPy derivative 得到 `dpsi/dr`。
- 把 `(psi, dpsi/dr)` 输入 T6b reconstruction 和 T6c Weyl/polarization 链。
- 组装 flat-space no-lens `h_plus/h_cross`，用于比较输入 `A_plus/A_cross` 的 polarization convention。

## 允许修改

Preferred narrow scope:

- `src/schwgw/scattering/partial_wave.py` if adding an internal reusable adapter is natural.
- Or `tests/physics/test_phase3_validation.py` if adapter can remain test-only.
- `tests/physics/test_phase3_validation.py`
- `tests/unit/test_polarization_extraction.py` only for API-independent algebraic tests.
- `docs/equation_map.md`
- `docs/validation_plan.md`
- `status.md`

Keep production API minimal. If the adapter is validation-only, it may live in tests with clear comments.

## 不允许

- Do not use `solve_radial_mode` for no-lens oracle.
- Do not change T5 incident coefficients.
- Do not change `docs/physics_spec.md` unless the flat adapter reveals a real convention conflict; stop first.
- Do not generate numeric regression fixtures.
- Do not change T4 radial solver in this task.

## Q011 Test Matrix

You must compare at least two treatments of Li-Hou-Zhao Eq. (35g)-(35h):

1. Current T6 stored positive-frequency linear treatment:

```text
Z1 = (2/f) Z3
Z0 = (2/f)^2 Z4
```

2. Literal conjugating treatment, implemented only as a local diagnostic path unless the convention is formally changed:

```text
Z1 = (2/f) conj(Z3)
Z0 = (2/f)^2 conj(Z4)
```

Do not switch production behavior until the flat no-lens oracle identifies which convention matches `docs/physics_spec.md` and the target-paper convention.

## Expected Validation

The adapter should test pure cases:

- Pure plus: `A_plus != 0`, `A_cross = 0`.
- Pure cross: `A_plus = 0`, `A_cross != 0`.
- Generic complex amplitudes.

At selected probes away from coordinate singularities first:

```text
k = 0.5
r = 20
theta = 0.4
phi = 0
lmax values = [4, 6, 8, 10] if stable in flat adapter
```

Then test near axis only after the away-from-axis sign is understood:

```text
theta = 0, 0.01, 0.05
```

## Stop Conditions

Stop and update `status.md` if:

- Flat adapter cannot be constructed without changing T5 formulas.
- Flat adapter shows both Q011 treatments fail by O(1), suggesting a deeper tetrad/Wigner-D/reconstruction issue.
- A pass requires modifying `docs/physics_spec.md`.
- Results depend strongly on arbitrary normalization not present in `docs/physics_spec.md` or `references/notes/phase3_formula_audit.md`.

## Completion Conditions

- A flat no-lens validation entrypoint exists.
- It clearly reports whether the current Q011 treatment passes or fails.
- If current T6 convention is wrong, provide a minimal failing test and do not silently rewrite convention without documentation.
- `status.md` records changed files, commands, diagnostics, and the Q011 recommendation.

Recommended verification:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_incident_flat_space.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_polarization_extraction.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_phase3_validation.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```
