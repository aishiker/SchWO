# Phase 5 T4r Prompt: Q018 Production-Integration Design

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4r`。

T7al 已经接受 T4q 的 **BROADER EXPERIMENTAL ORACLE MATRIX**：`M=1,k=2,r=60,
r_out=300,ell=[153,156,168,180]` odd/even experimental oracle 全部返回 finite
unit-incoming fields，且同一 8-mode production path 仍 fail-closed。

T4r 的任务不是接入 production，也不是生成 R60 artifact。你的任务是提出可复核的
production-integration policy design：如果未来要让 production 使用这个 oracle，
应该如何显式 opt-in、如何记录 metadata、如何保持默认 fail-closed、以及需要哪些
测试先变 RED。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_rescaled_radial_architecture_spike.md`
8. `references/notes/q018_spin2_tail_bound.md`
9. `docs/prompts/phase5_t4q_q018_broader_experimental_oracle_validation.md`
10. `docs/prompts/phase5_t7al_q018_broader_oracle_review.md`
11. `src/schwgw/numerics/radial_solver.py`
12. `src/schwgw/numerics/boundary_conditions.py`
13. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
14. `tests/physics/test_q018_rescaled_oracle.py`
15. `tests/physics/test_radial_solver.py`
16. `src/schwgw/scattering/partial_wave.py`
17. `tests/regression/fixtures/R60_K1.json`

按项目规则先检查已安装 plugin/skill。此任务是设计/测试边界任务，使用
systematic debugging、TDD、verification-before-completion；不要跳过 RED evidence。

## 2. Scope

允许修改：

- `docs/q018_production_integration_design.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `tests/physics/test_q018_production_integration_design.py` 或现有相关测试文件
- `status.md`

只在有强理由时允许修改：

- `src/schwgw/numerics/boundary_conditions.py`
- `src/schwgw/numerics/radial_solver.py`

如果修改源代码，只能添加 inert dataclass/enum/config placeholder 或 explicit
`NotImplementedError` / fail-closed guard；不得实际调用 experimental oracle。

禁止：

- 不要把 experimental oracle 接入默认 `solve_radial_mode(...)`。
- 不要让 production `required_eval_radius=60` 变 GREEN。
- 不要从 `schwgw.numerics` public package export experimental oracle。
- 不要生成 R60_K2/R60_K4 wave-field artifact、benchmark artifact、fixtures 或 plots。
- 不要运行 `kM=4`。
- 不要修改 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 `lmax`、改变 partial-wave truncation policy，或放宽 residual/convergence/suppression thresholds。
- 不要把 experimental oracle matrix 通过直接表述成 production readiness。

## 3. Required Design Document

创建：

```text
docs/q018_production_integration_design.md
```

必须包含：

1. Problem statement：为什么 experimental oracle matrix 通过后仍不能直接跑 T8 R60。
2. Current evidence summary：
   - T7al accepted 8-mode experimental oracle matrix；
   - production path still fail-closed；
   - accepted scope is `M=1,k=2,r=60,r_out=300,ell=[153,156,168,180]` odd/even only。
3. Proposed production policy, at design level only：
   - explicit opt-in name and location, e.g. `BoundaryConfig.experimental_required_radius_oracle="q018_riccati"` or a better local design;
   - default remains `None` / fail-closed;
   - allowed parameter envelope;
   - rejection behavior outside envelope;
   - metadata fields required in `RadialDiagnostics` / warnings;
   - provenance fields linking to experimental method, test matrix, tolerances, and residual proxies.
4. API boundary:
   - whether production should call the experimental module directly, wrap it in an internal adapter, or move the method after review;
   - how to avoid silently exporting experimental API;
   - how to keep T8 artifacts self-describing.
5. Test plan:
   - default fail-closed tests;
   - opt-in RED tests for future implementation;
   - regression fixture policy;
   - partial-wave convergence criteria that must pass before any T8 R60 run.
6. Stop/go gates:
   - what future T4 implementation must prove;
   - what future T7 review must independently rerun;
   - what T8 is still forbidden to do.
7. Explicit non-validation:
   - no `kM=4`;
   - no R60_K4;
   - no arbitrary incident direction;
   - no larger-domain artifact;
   - no scalar-cutoff-only proof.

## 4. RED / Contract Tests

Add tests that lock the design boundary without implementing production wiring.

At minimum:

- default `solve_radial_mode(... required_eval_radius=60)` for the Q018 8-mode matrix still raises `evanescent_tail_required_radius_uncovered`;
- if a future opt-in config placeholder is introduced, it currently raises a clear `NotImplementedError` or `RuntimeError` saying production integration is design-only;
- tests assert no experimental oracle public export from `schwgw.numerics`;
- tests assert no default path silently calls `solve_q018_rescaled_oracle`.

If adding a new `BoundaryConfig` field, keep it inert and default `None`.
Do not make default tests depend on optional dependencies.

## 5. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

If you add a new design-boundary test file, run it explicitly as well.

## 6. Stop Conditions

Stop and report **YELLOW / design only** if:

- the design reveals production integration needs more than a narrow adapter;
- default fail-closed behavior cannot be preserved;
- metadata requirements require broad schema changes;
- partial-wave convergence requirements are not clear enough for future T8;
- implementation would require convention, threshold, or `lmax` policy changes.

Stop and report **REJECT RED** if any default production path becomes GREEN for R60
or experimental oracle is silently wired into production.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- design summary;
- RED/contract tests added;
- commands and test results;
- open issues;
- exact next prompt recommendation for T7am review.

Do not authorize T8 R60_K2 production from this slice.
