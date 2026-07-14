# Phase 5 T7ak Prompt: Review Q018 Experimental Oracle Implementation

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ak`。

只在 T4p 完成后运行。你的任务是独立复核 T4p 是否真正实现了可信的
experimental Q018 finite-radius oracle，还是只停留在 prerequisites / fake GREEN。
不要把通过的 experimental oracle 解读为 production R60_K2 readiness。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `pyproject.toml`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/q018_rescaled_radial_architecture_spike.md`
9. `references/notes/q018_spin2_tail_bound.md`
10. `docs/prompts/phase5_t4p_q018_experimental_oracle_implementation.md`
11. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
12. `src/schwgw/numerics/radial_solver.py`
13. `src/schwgw/numerics/boundary_conditions.py`
14. `tests/physics/test_q018_rescaled_oracle.py`
15. files changed by T4p

按项目规则先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion；必要时使用文献/数值方法相关 skill，但不要上传私有文件。

## 2. Review Scope

确认：

- production `solve_radial_mode(...)` default path was not changed or wired to the experimental oracle;
- `schwgw.numerics` public package does not export the experimental oracle unless T0 explicitly approved it;
- no R60_K2/R60_K4 wave-field artifacts, benchmark artifacts, or plots were generated;
- no `kM=4` run or claim was introduced;
- no frozen convention, `lmax`, partial-wave truncation policy, residual/convergence threshold, or Q018 fail-closed guard was changed;
- no hard-coded finite oracle values, mock outputs, scalar-cutoff GREEN claim, or placeholder WKB result is being used to pass tests;
- optional dependencies remain project-local/optional and are not required by default pytest.

## 3. Required Checks

Run:

```bash
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Independently call the experimental oracle for at least:

```text
M=1
k=2
r=60
r_out=300
ell=153
sector=odd
```

Inspect the returned diagnostics. Confirm:

- `psi`, `dpsi_dr`, `A_in`, `A_out` are finite complex values;
- `abs(A_in - 1) < 1e-8` or a documented stricter/credible criterion passes;
- `valid_at_required_radius` is true;
- diagnostics record method, precision/tolerances, finite checks, and a residual/Wronskian/flux or equivalent consistency proxy;
- the method is not labeled placeholder/mock/hardcoded.

Also verify production still fails closed:

```text
solve_radial_mode(..., BoundaryConfig(required_eval_radius=60.0))
```

for `M=1,k=2,r_out=300,ell=153,sector=odd` should still raise the structured
`evanescent_tail_required_radius_uncovered` error unless T0 explicitly approved a production-path change. For this review, a production-path change is a blocker.

## 4. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR EXPERIMENTAL ORACLE**:
  opt-in oracle test passes for credible numerical reasons; default full pytest
  passes; production path remains fail-closed and untouched. This allows a
  future T4/T7 discussion about whether to broaden the oracle to even sector /
  additional `ell` modes. It does not authorize T8 R60_K2 production.
- **ACCEPT YELLOW**:
  useful implementation or diagnostics were added, but the oracle is incomplete,
  too slow, not reproducible, or lacks a strong consistency proxy.
- **REJECT RED**:
  default tests fail, production path changed without approval, artifacts/plots
  were generated, thresholds/conventions were changed, or the oracle is fake /
  hard-coded / scientifically unsupported.

## 5. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- independent test results;
- independent oracle probe results;
- production fail-closed check result;
- decision label;
- open issues;
- exact next action prompt recommendation.

Do not authorize T8 R60_K2 production from this review.
