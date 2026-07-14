# Phase 5 T4p Prompt: Q018 Experimental Rescaled Oracle Implementation

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4p`。

T7aj 已经将 T4o 的结果接受为 **ACCEPT GREEN FOR PREREQUISITES**。这只说明
experimental oracle 的 API、可选依赖和 opt-in RED test 边界已经建立；它不说明
R60_K2 production 已经可用。T4p 的目标是只在 experimental oracle 边界内推进
Q018 方法实现，使 opt-in oracle test 从 RED 变为可信 GREEN，或者给出明确
no-go。

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
10. `docs/prompts/phase5_t4o_q018_rescaled_oracle_prereqs.md`
11. `docs/prompts/phase5_t7aj_q018_oracle_prereq_review.md`
12. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
13. `src/schwgw/numerics/radial_solver.py`
14. `src/schwgw/numerics/boundary_conditions.py`
15. `tests/physics/test_q018_rescaled_oracle.py`
16. `tests/physics/test_radial_solver.py`

按项目规则先检查已安装 plugin/skill。此任务是数值故障修复与 RED-to-GREEN
实现，使用 systematic debugging、TDD、verification-before-completion；不要跳过
RED evidence。

## 2. Scope

允许修改：

- `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
- `tests/physics/test_q018_rescaled_oracle.py`
- `docs/q018_rescaled_radial_architecture_spike.md`
- `docs/numerics.md`
- `status.md`
- `pyproject.toml` 仅在 optional `oracle` dependency metadata 需要可复现修正时修改。

禁止：

- 不要修改 production `solve_radial_mode(...)` 默认路径。
- 不要从 `schwgw.numerics` public package export experimental oracle。
- 不要绕过 `BoundaryConfig.required_eval_radius` fail-closed guard。
- 不要生成 R60_K2/R60_K4 wave-field artifact、benchmark artifact 或 plots。
- 不要运行 `kM=4`。
- 不要修改 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 `lmax`、改变 partial-wave truncation policy，或放宽 residual/convergence/suppression thresholds。
- 不要用硬编码常数、mock result、analytic placeholder、纯 WKB guess 或 scalar-field cutoff 来让 test 假通过。
- 不要安装全局包。若需要 `mpmath`，只能使用项目本地可选依赖环境，并记录命令。

## 3. Required RED-To-GREEN Target

当前 opt-in test:

```bash
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
```

目前应因 `NotImplementedError` 失败。T4p 的目标是让它通过，且通过原因必须是
真实 experimental numerical oracle，而不是 mock。

最小目标 mode：

```text
M=1
k=2
r=60
r_out=300
ell=153
sector=odd
normalization: unit incoming-at-infinity, A_in ~= 1
```

如果只完成这个最小 mode，也必须把 limitation 写清楚：它是 experimental oracle
prototype，不是 production radial solver，也不授权 T8 R60 production。

## 4. Implementation Requirements

实现 `solve_q018_rescaled_oracle(request, background)` 时必须满足：

- return finite complex `psi(required_radius)` and `dpsi_dr(required_radius)`;
- return finite `A_in`, `A_out`, with `abs(A_in - 1) < 1e-8` unless a stricter reviewed tolerance is justified;
- diagnostics include at least:
  - `method`;
  - `required_radius`;
  - `r_out`;
  - `ell`;
  - `sector`;
  - `k`;
  - `precision_dps` or explicit double-precision statement;
  - `rtol`, `atol`;
  - `unit_incoming_at_infinity=True`;
  - `valid_at_required_radius=True`;
  - finite checks for `psi`, `dpsi_dr`, `A_in`, `A_out`;
  - Wronskian, flux, residual, or another reviewed consistency proxy;
  - runtime or step/iteration diagnostic if available;
  - `experimental=True`.
- If the method uses high precision, keep all high-precision code isolated in the experimental module.
- If the method uses rescaled/log-amplitude propagation, diagnostics must explain how phase, amplitude normalization, and derivative recovery were handled.

Strengthen `tests/physics/test_q018_rescaled_oracle.py` as needed so the test rejects hard-coded fake outputs. At minimum, add one or more checks such as:

- diagnostics method is not `placeholder`, `mock`, or `hardcoded`;
- a residual/flux/Wronskian consistency diagnostic is finite and below a documented threshold;
- changing `required_radius` by a small amount, if supported, gives finite values and not identical hard-coded output;
- repeated calls are deterministic within tolerance.

Do not overfit these checks to hidden constants. The test should enforce method credibility, not a single magic numeric answer.

## 5. Stop Conditions

Stop and report **YELLOW / not implemented** if any of these occur:

- a real implementation would require production radial solver changes;
- project-local high-precision dependency cannot be made reproducible and no double-precision rescaled method is credible;
- opt-in target mode runtime exceeds 20 minutes in the current environment;
- outputs are finite but diagnostics cannot establish a meaningful consistency proxy;
- implementation would require changing frozen conventions, thresholds, `lmax`, or Q018 fail-closed policy;
- you find that the existing API contract is scientifically wrong.

Stop and report **REJECT/RED** if the only way to pass is hard-coded or fake finite values.

## 6. Validation Commands

Run at minimum:

```bash
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If dependency installation is needed, prefer project-local reproducible commands only, and record them exactly.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- dependency/environment decision;
- implementation method and diagnostics;
- RED evidence before implementation;
- opt-in oracle test result after implementation;
- default full pytest result;
- open issues;
- exact next prompt recommendation for T7ak review.

Do not authorize T8 R60_K2 production from this slice.
