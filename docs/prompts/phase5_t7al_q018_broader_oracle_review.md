# Phase 5 T7al Prompt: Review Q018 Broader Experimental Oracle Validation

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7al`。

只在 T4q 完成后运行。你的任务是独立复核 T4q 是否把 Q018 experimental
oracle 从最低 odd target 扩展到 R60_K2 相关 odd/even suppressed-mode matrix。
不要把 experimental matrix 通过解读为 production R60_K2 readiness。

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
10. `docs/prompts/phase5_t4q_q018_broader_experimental_oracle_validation.md`
11. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
12. `src/schwgw/numerics/radial_solver.py`
13. `src/schwgw/numerics/boundary_conditions.py`
14. `tests/physics/test_q018_rescaled_oracle.py`
15. files changed by T4q

按项目规则先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion；必要时使用文献/数值方法相关 skill，但不要上传私有文件。

## 2. Review Scope

确认：

- production `solve_radial_mode(...)` default path was not changed or wired to the experimental oracle;
- `schwgw.numerics` public package does not export the experimental oracle;
- no R60_K2/R60_K4 wave-field artifacts, benchmark artifacts, fixtures, or plots were generated;
- no `kM=4` run or claim was introduced;
- no frozen convention, `lmax`, partial-wave truncation policy, residual/convergence threshold, or Q018 fail-closed guard was changed;
- no hard-coded finite oracle values, mock outputs, scalar-cutoff GREEN claim, or placeholder WKB result is used;
- optional dependencies remain project-local/optional and are not required by default pytest.

## 3. Required Independent Checks

Run:

```bash
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Independently call the experimental oracle for:

```text
M=1
k=2
required_radius=60
r_out=300
ell=[153, 156, 168, 180]
sector=[odd, even]
```

For every mode, confirm:

- finite complex `psi`, `dpsi_dr`, `A_in`, and `A_out`;
- `abs(A_in - 1) < 1e-8`;
- `valid_at_required_radius=True`;
- method is not placeholder/mock/hardcoded;
- residual proxies are finite and satisfy documented thresholds;
- diagnostics include method, sector, ell, k, tolerances, runtime/steps, finite flags, and `experimental=True`.

Also independently verify production still fails closed for the same 8 modes with
`BoundaryConfig(required_eval_radius=60.0)`, returning structured
`evanescent_tail_required_radius_uncovered` metadata.

## 4. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR BROADER EXPERIMENTAL ORACLE MATRIX**:
  all 8 experimental modes pass credible finite/residual checks; default full
  pytest passes; production remains fail-closed and untouched. This permits a
  future T0 decision about a production-integration design slice, but does not
  itself authorize T8 R60_K2 production.
- **ACCEPT YELLOW**:
  some useful broader validation was added, but one or more modes are missing,
  unstable, too slow, or lack credible diagnostics.
- **REJECT RED**:
  default tests fail, production path changed without approval, artifacts/plots
  were generated, thresholds/conventions changed, or oracle values are fake /
  hard-coded / scientifically unsupported.

## 5. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- independent test results;
- independent 8-mode oracle probe summary;
- production fail-closed check summary;
- decision label;
- open issues;
- exact next action prompt recommendation.

Do not authorize T8 R60_K2 production from this review.
