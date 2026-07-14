# Phase 3 Blocker Prompt: T4 High-Ell Radial Stability

你现在是 `T4：径向 ODE 与匹配` 线程。Phase 3 T7b final physics validation 未通过；当前首要阻塞是 Q012：high-`ell` radial solver / Wronskian diagnostics 在 partial-wave `lmax` sweep 中失稳。

本任务不是继续调 T6 Weyl 或 plotting，而是定位并修复径向层的数值病态。不要生成 regression fixtures，不要修改 Weyl/polarization convention。

## 必读文件

1. `project.md`
2. `status.md`
3. `docs/codex_instructions.md`
4. `docs/physics_spec.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/equation_map.md`
8. `src/schwgw/numerics/radial_solver.py`
9. `src/schwgw/numerics/boundary_conditions.py`
10. `src/schwgw/numerics/matching.py`
11. `tests/physics/test_radial_solver.py`
12. `tests/physics/test_phase3_validation.py`

## 已知失败现象

T7b/T0 复核给出的典型现象：

```text
M=1, k=0.5, r_out=120
ell=8  odd:  |A_in| ~ 3.25e9,  Wronskian residual ~ 1.38e2
ell=12 odd:  |A_in| ~ 1.95e17, Wronskian residual ~ 4.45e13
ell=12 even: |A_in| ~ 1.95e17, Wronskian residual ~ 2.91e20
```

Outer matching algebraic residual remains near machine precision, while `|A_in|` and `|A_out|` both become enormous. This points to radial basis/normalization instability through the high potential barrier, not a simple 2x2 matching failure.

## 目标

Find root cause before implementing any fix. Minimum outputs:

- Per-mode diagnostic tool or test helper that reports `ell`, `sector`, `|A_in|`, `|A_out|`, Wronskian samples, max `|psi|`, ODE steps, and matching condition number.
- A reproducible failing or xfailed physics test for high-`ell` radial drift.
- A proposed and tested numerical fix, or a documented conclusion that the first solver architecture is insufficient.

## 允许修改

- `src/schwgw/numerics/radial_solver.py`
- `src/schwgw/numerics/boundary_conditions.py`
- `src/schwgw/numerics/matching.py`
- `tests/unit/test_radial_solver.py`
- `tests/physics/test_radial_solver.py`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `docs/equation_map.md`
- `status.md`

If you need a small internal helper module under `src/schwgw/numerics/`, keep it narrowly scoped and documented.

## 不允许

- Do not modify `docs/physics_spec.md` unless you stop and explicitly report a convention conflict.
- Do not change T5 incident coefficients.
- Do not modify T6 Weyl, tetrad, or polarization formulas in this task.
- Do not relax validation thresholds to pass tests.
- Do not generate benchmark/regression fixtures.

## Investigation Checklist

Run and record at least:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_phase3_validation.py
```

Then run a per-mode diagnostic sweep:

```text
M=1, k=0.5, ell=2..12, r_out=120, rtol=1e-10, atol=1e-12
sectors: odd/even
```

Also test at least one low-`k` case:

```text
M=1, k=0.2, ell=2..6, r_out=120
```

For each case inspect:

- `W(r)` near horizon, median, and at outer radius.
- Whether Wronskian drift appears before or after the potential barrier.
- Whether reducing `max_step`, moving `r_in_eps`, or increasing `r_out` gives monotonic improvement.
- Whether the outward unit-horizon solution grows exponentially in the forbidden region.
- Whether matching to `A_in/A_out` is dominated by subtracting nearly equal huge numbers.

## Candidate Fix Directions

Evaluate, but do not blindly implement all:

- Add a rescaled integration variable or periodic amplitude renormalization while preserving derivative ratios and final matching.
- Add an infinity-normalized basis solve and compute the physical radial mode by matching to the incoming coefficient, instead of relying only on unit-horizon outward integration.
- Use log-derivative/Riccati propagation through the high barrier, then recover amplitudes by stable matching.
- Add Frobenius corrections to horizon initial data only if diagnostics show the leading ansatz is the root cause.
- Improve Wronskian diagnostics to avoid misleading medians, but only if raw `W(r)` is actually conserved.

## Stop Conditions

Stop and update `status.md` if:

- Three independent root-cause attempts fail to explain high-`ell` Wronskian drift.
- A fix requires changing boundary-condition convention in `docs/physics_spec.md`.
- A fix requires changing T5/T6 formulas before radial instability is isolated.
- High-`ell` stability requires a major solver architecture change; document the proposed architecture and hand back to T0/T4 for approval.

## Completion Conditions

- High-`ell` radial diagnostic test exists and is either passing under a justified fix or explicitly xfailed with a precise blocker.
- Existing T4/T5/T6 fast tests still pass.
- `status.md` records changed files, commands, before/after diagnostics, remaining risks, and whether T7b can be rerun.

Recommended verification:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q -m physics tests/physics/test_phase3_validation.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```
