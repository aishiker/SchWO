# Phase 5 T4s Prompt: Q018 Reviewed Opt-In Production Oracle Implementation

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4s`。

T7am 已经接受 T4r 的 **PRODUCTION-INTEGRATION DESIGN**。这只授权一个非常窄的
implementation slice：把已经通过 T4q/T7al 复核的 Q018 experimental
`riccati_log_derivative_match` oracle 接到 production `solve_radial_mode(...)` 的显式
opt-in 路径中。它不授权 T8 R60 artifact、`kM=4`、R60_K4、larger-domain run、任意入射方向、
阈值调整或 `lmax` policy 变更。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_rescaled_radial_architecture_spike.md`
8. `docs/q018_production_integration_design.md`
9. `references/notes/q018_spin2_tail_bound.md`
10. `docs/prompts/phase5_t4q_q018_broader_experimental_oracle_validation.md`
11. `docs/prompts/phase5_t7al_q018_broader_oracle_review.md`
12. `docs/prompts/phase5_t4r_q018_production_integration_design.md`
13. `docs/prompts/phase5_t7am_q018_production_integration_design_review.md`
14. `src/schwgw/numerics/radial_solver.py`
15. `src/schwgw/numerics/boundary_conditions.py`
16. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
17. `tests/physics/test_q018_production_integration_design.py`
18. `tests/physics/test_q018_rescaled_oracle.py`
19. `tests/physics/test_radial_solver.py`
20. `tests/unit/test_radial_solver.py`
21. `src/schwgw/scattering/partial_wave.py`

按项目规则，先检查已安装的 plugin/skill；本任务至少使用 TDD、systematic debugging、
verification-before-completion。若发现需要文献核对，只读本地 `references/manifest.md` 和
`references/notes/`，不要上传私有 PDF。

## 2. 允许修改范围

允许修改：

- `src/schwgw/numerics/boundary_conditions.py`
- `src/schwgw/numerics/radial_solver.py`
- `tests/physics/test_q018_production_integration_design.py`
- `tests/physics/test_q018_rescaled_oracle.py`
- `docs/q018_production_integration_design.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `status.md`

只在确有必要时允许小范围修改：

- `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`

该 experimental module 只能为 adapter 补充无歧义 helper 或修复明显 bug；不得扩大 accepted
physics envelope。

禁止：

- 不要改变 `experimental_required_radius_oracle=None` 的默认 production 行为。
- 不要把 experimental oracle 从 `schwgw.numerics` public API export 出去。
- 不要让 `partial_wave.py`、T6、T8 或 plotting 代码直接 import
  `schwgw.numerics.experimental`。
- 不要生成 R60_K2/R60_K4 wave-field artifact、benchmark artifact、fixtures 或 plots。
- 不要运行 `kM=4`。
- 不要改变 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 `lmax`、改变 partial-wave truncation policy，或放宽 residual/convergence/suppression thresholds。
- 不要把此 slice 表述成 R60_K2 production readiness；它只实现 reviewed opt-in adapter。

## 3. TDD 要求

先改测试，再改实现。

先把当前 design-only opt-in test 改成 RED production-contract test：

- 对 Q018 8-mode matrix：
  - `M=1`
  - `k=2.0`
  - `required_eval_radius=60.0`
  - `r_out=300.0`
  - `r_in_eps=1e-6`
  - `rtol=1e-10`
  - `atol=1e-12`
  - `ell in [153, 156, 168, 180]`
  - `sector in [odd, even]`
- 使用
  `BoundaryConfig(required_eval_radius=60.0, experimental_required_radius_oracle="q018_riccati")`
  时，`solve_radial_mode(...)` 必须返回正常 `RadialSolution`。
- 默认
  `BoundaryConfig(required_eval_radius=60.0, experimental_required_radius_oracle=None)`
  必须继续 fail closed，错误码为 `evanescent_tail_required_radius_uncovered`。
- unknown opt-in name 必须继续 fail closed with `ValueError`。
- out-of-envelope opt-in 必须 fail closed with structured production no-go，不得静默退回 zero-tail
  suppression 或普通 fallback。
- `schwgw.numerics` 仍不得 export `solve_q018_rescaled_oracle`。
- production path 不得在 default `None` 时调用 experimental oracle。

先运行目标测试，确认因为当前 `NotImplementedError` 或缺少 adapter 失败；把 RED evidence 写入
`status.md`。

## 4. Implementation Contract

只实现 reviewed opt-in：

```python
BoundaryConfig(
    required_eval_radius=60.0,
    experimental_required_radius_oracle="q018_riccati",
)
```

允许 envelope 精确等于 T4q/T7al 8-mode matrix：

| field | allowed value |
|---|---|
| background | Schwarzschild `M=1` |
| `k` | `2.0` |
| `required_eval_radius` | `60.0` |
| `r_out` | `300.0` |
| `r_in_eps` | `1e-6` |
| `rtol` / `atol` | `1e-10` / `1e-12` |
| `ell` | `153, 156, 168, 180` |
| sector | odd/even |
| method | `riccati_log_derivative_match` |

Implementation details:

- Add a private adapter in `src/schwgw/numerics/radial_solver.py`, or an equivalently private internal
  helper, that calls the existing experimental oracle only after all opt-in and envelope checks pass.
- Return a normal `RadialSolution` compatible with the current public solver contract.
- Preserve the existing partial-wave normalization contract:

```text
scale = coefficient / A_in
```

- `A_in` must be unit incoming at infinity within the accepted T4q/T7al tolerance scale.
- `psi(60)` and `dpsi_dr(60)` must be finite and consistent with the experimental oracle output.
- `phase_factor`, interpolation/evaluation helpers, derivative evaluation, `A_in`, `A_out`, and diagnostics
  must be mutually consistent with the existing `RadialSolution` type. Inspect the class before writing code.

## 5. Required Metadata

Every opt-in result must carry JSON-safe provenance in diagnostics or warnings. Include at minimum:

- explicit warning/diagnostic code such as `q018_required_radius_oracle_used`;
- `experimental_required_radius_oracle="q018_riccati"`;
- `method="riccati_log_derivative_match"`;
- `production_integration_review_id="T4s/T7an-pending"` before review;
- `experimental_evidence="T4q/T7al broader matrix"`;
- `sector`, `ell`, `k`, `required_eval_radius`, `r_out`;
- `r_in_eps`, `rtol`, `atol`;
- finite flags for `psi`, `dpsi_dr`, `A_in`, `A_out`;
- oracle residual proxies available from `solve_q018_rescaled_oracle(...)`;
- step counts/runtime/condition information when available;
- `valid_at_required_radius=True`;
- `unit_incoming_at_infinity=True`;
- statement that `A_in` is the outer `exp(-i k r_star)` incoming coefficient.

If current diagnostics dataclasses cannot hold all fields cleanly, add the smallest compatible field or warning
payload. Do not perform broad schema refactors in this slice.

## 6. Out-Of-Envelope Behavior

Any opt-in request outside the exact envelope must fail closed with a structured error/warning code such as
`q018_experimental_oracle_out_of_envelope`.

Examples that must fail:

- `k != 2.0`
- `r_out != 300.0`
- `required_eval_radius != 60.0`
- `ell` not in `[153, 156, 168, 180]`
- non-Schwarzschild or `M != 1`
- tolerances outside the reviewed values if the implementation cannot justify them
- `kM=4`

Do not silently fall back to `evanescent_tail_suppressed` for out-of-envelope opt-in.

## 7. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If the opt-in matrix tests take too long, stop **YELLOW** only after recording exactly which mode, runtime, and
failure reason blocked completion. Do not replace them with weaker tests.

## 8. Stop Conditions

Stop **REJECT RED** if:

- default `experimental_required_radius_oracle=None` production behavior changes;
- `required_eval_radius=60` becomes GREEN without explicit opt-in;
- experimental oracle becomes public export from `schwgw.numerics`;
- T8 artifacts/plots/fixtures or `kM=4` output are generated;
- frozen conventions, thresholds, or `lmax` policy change.

Stop **YELLOW** if:

- converting experimental output into a normal `RadialSolution` requires broad refactor;
- metadata cannot be attached without schema work larger than this slice;
- opt-in works for only a subset of the 8-mode matrix;
- runtime is too high for all 8 modes in the current environment;
- out-of-envelope fail-closed behavior cannot be made precise.

Report **GREEN / implementation ready for T7an review** only if all 8 reviewed opt-in modes return normal
`RadialSolution`, default fail-closed behavior is unchanged, out-of-envelope is fail-closed, and the validation
commands pass.

## 9. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- RED evidence before implementation;
- implementation summary;
- exact 8-mode opt-in results;
- default fail-closed and out-of-envelope checks;
- commands and test results;
- open issues;
- exact next prompt recommendation:
  `你现在是 T7an。请读取并严格执行 docs/prompts/phase5_t7an_q018_optin_production_oracle_review.md。`

Do not authorize T8 R60_K2 production from T4s.
