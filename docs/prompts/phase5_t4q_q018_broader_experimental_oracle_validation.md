# Phase 5 T4q Prompt: Q018 Broader Experimental Oracle Validation

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4q`。

T7ak 已经将 T4p 接受为 **ACCEPT GREEN FOR EXPERIMENTAL ORACLE**，但只覆盖
最低目标：

```text
M=1, k=2, r=60, r_out=300, ell=153, sector=odd
```

T4q 的目标是只在 experimental oracle 边界内扩大验证矩阵，判断同一方法是否
覆盖 R60_K2 相关 suppressed modes 的 odd/even parity。它不是 production
integration slice。

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
11. `docs/prompts/phase5_t7ak_q018_experimental_oracle_review.md`
12. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
13. `src/schwgw/numerics/radial_solver.py`
14. `src/schwgw/numerics/boundary_conditions.py`
15. `tests/physics/test_q018_rescaled_oracle.py`
16. `tests/physics/test_radial_solver.py`

按项目规则先检查已安装 plugin/skill。此任务是实验数值验证扩展，使用
systematic debugging、TDD、verification-before-completion；不要跳过失败证据。

## 2. Scope

允许修改：

- `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
- `tests/physics/test_q018_rescaled_oracle.py`
- `docs/q018_rescaled_radial_architecture_spike.md`
- `docs/numerics.md`
- `status.md`

禁止：

- 不要修改 production `solve_radial_mode(...)` 默认路径。
- 不要从 `schwgw.numerics` public package export experimental oracle。
- 不要绕过 `BoundaryConfig.required_eval_radius` fail-closed guard。
- 不要生成 R60_K2/R60_K4 wave-field artifact、benchmark artifact、fixtures 或 plots。
- 不要运行 `kM=4`。
- 不要修改 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 `lmax`、改变 partial-wave truncation policy，或放宽 residual/convergence/suppression thresholds。
- 不要使用 hard-coded finite values、mock outputs、scalar cutoff proof 或 placeholder WKB result。
- 不要安装全局包。

## 3. Required Validation Matrix

在 opt-in experimental oracle 测试中覆盖：

```text
M=1
k=2
required_radius=60
r_out=300
ell=[153, 156, 168, 180]
sector=[odd, even]
r_in_eps=1e-6
rtol=1e-10
atol=1e-12
normalization: unit incoming-at-infinity, A_in ~= 1
```

对每个 mode 检查：

- finite complex `psi(60)`;
- finite complex `dpsi_dr(60)`;
- finite complex `A_in`, `A_out`;
- `abs(A_in - 1) < 1e-8`;
- `valid_at_required_radius=True`;
- diagnostics method is `riccati_log_derivative_match` or another real reviewed method, not placeholder/mock/hardcoded;
- residual proxies are finite:
  - `outer_boundary_residual < 1e-8`;
  - `normalization_residual < 1e-8`;
  - `log_derivative_match_residual < 1e-7`;
- diagnostics include sector, ell, k, requested radius, r_out, tolerances, finite flags, step counts, runtime, and `experimental=True`.

Add deterministic repeat or tolerance-sensitivity checks for at least:

```text
(ell=153, sector=odd)
(ell=153, sector=even)
(ell=180, sector=odd)
(ell=180, sector=even)
```

If all 8 modes are cheap enough, extend tolerance-sensitivity checks to all 8.

## 4. Documentation Output

Update `docs/q018_rescaled_radial_architecture_spike.md` with a compact table:

```text
ell, sector, psi(60), dpsi_dr(60), A_in, A_out,
outer_boundary_residual, normalization_residual,
log_derivative_match_residual, runtime, status
```

Also state explicitly:

- this is experimental oracle coverage, not production solver coverage;
- production `solve_radial_mode(... required_eval_radius=60)` remains fail-closed;
- R60_K2 production still requires a separate T0/T4/T7 decision about how, or whether, to wire a reviewed method into production;
- `kM=4`, R60_K4, arbitrary incident direction, and larger domains remain unvalidated.

## 5. Stop Conditions

Stop and report **ACCEPT YELLOW / partial experimental coverage** if:

- any of the 8 modes fails or becomes non-finite;
- any mode takes more than 10 minutes;
- residual diagnostics are not credible for any mode;
- tolerance sensitivity is unstable beyond documented numerical expectations;
- implementation would require production solver changes;
- production fail-closed behavior would need to be bypassed;
- frozen conventions, thresholds, or `lmax` policy would need to change.

Stop and report **REJECT RED** if the only way to pass is hard-coded or fake values.

## 6. Validation Commands

Run at minimum:

```bash
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also directly verify that production still fails closed for all 8 matrix modes with:

```text
BoundaryConfig(required_eval_radius=60.0, r_out=300.0, rtol=1e-10, atol=1e-12)
```

Record the structured `evanescent_tail_required_radius_uncovered` metadata.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- validation matrix results;
- representative finite values and residuals;
- tolerance-sensitivity results;
- production fail-closed check;
- default and opt-in test results;
- open issues;
- exact next prompt recommendation for T7al review.

Do not authorize T8 R60_K2 production from this slice.
