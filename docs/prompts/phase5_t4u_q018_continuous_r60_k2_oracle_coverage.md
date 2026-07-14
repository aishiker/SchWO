# Phase 5 T4u Prompt: Q018 Continuous R60_K2 Oracle Coverage

你现在是 `T4：径向 ODE 与匹配` 线程，slice 名称为 `T4u`。

T8t 已经证明 T8 schema/metadata/cache-key 支持是可用的，但 R60_K2 selected-probe smoke
在真正求解前 fail-closed。根因不是 T8，也不是 plotting：`compute_polarization(..., lmax=180)`
需要连续 `ell=2..180` 的 radial modes；当前 T4s/T7an reviewed oracle 只覆盖
`ell={153,156,168,180}`，而 `ell=154,155,157,...` 等中间 suppressed modes 在 R60 仍无
reviewed oracle。

本 slice 的目标是修正径向层的连续覆盖和 run-level opt-in dispatch。不要生成 T8 artifact。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_production_integration_design.md`
8. `docs/q018_rescaled_radial_architecture_spike.md`
9. `references/notes/q018_spin2_tail_bound.md`
10. `docs/prompts/phase5_t4s_q018_reviewed_optin_production_oracle.md`
11. `docs/prompts/phase5_t7an_q018_optin_production_oracle_review.md`
12. `docs/prompts/phase5_t8t_q018_r60_k2_selected_probe_smoke.md`
13. `src/schwgw/numerics/radial_solver.py`
14. `src/schwgw/numerics/boundary_conditions.py`
15. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
16. `src/schwgw/scattering/partial_wave.py`
17. `configs/r60_k2_q018_selected_probe_smoke.yaml`
18. `tests/physics/test_q018_production_integration_design.py`
19. `tests/physics/test_q018_rescaled_oracle.py`
20. `tests/physics/test_radial_solver.py`
21. `tests/unit/test_radial_solver.py`

按项目规则先检查已安装 plugin/skill。使用 systematic debugging、TDD、
verification-before-completion。不要上传私有 PDF；如发现新的 convention 问题，停止并交 T0/T1。

## 2. Scope

允许修改：

- `src/schwgw/numerics/radial_solver.py`
- `tests/physics/test_q018_production_integration_design.py`
- `tests/physics/test_q018_rescaled_oracle.py`
- `docs/q018_production_integration_design.md`
- `docs/numerics.md`
- `docs/validation_plan.md`
- `status.md`

只在确有必要时允许修改：

- `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`

禁止：

- 不要修改 T8 schema/CLI files，除非发现 T8t 的 schema 破坏了径向接口；若发现，记录原因后停止或最小修正。
- 不要生成 R60_K2 selected-probe NPZ、plots、fixtures、full x-z grids、R60_K4、`kM=4`、larger-domain artifacts。
- 不要改变 Fourier/harmonic/tetrad/RWZ/Route B/Q005/Q014 convention。
- 不要降低 thresholds、改变 `lmax` policy，或用不连续 `ell` 集合冒充 full partial-wave coverage。
- 不要把本 slice 表述成 full R60 production readiness。

## 3. Required Root-Cause Fix

Fix run-level opt-in semantics:

- `BoundaryConfig.experimental_required_radius_oracle="q018_riccati"` is a run-level permission to use the reviewed
  oracle when needed; it must not make ordinary low-`ell` modes fail as out-of-envelope.
- For a mode outside the oracle envelope:
  - if the normal production path can solve it and covers `required_eval_radius`, return the normal production
    `RadialSolution`;
  - if the normal production path fails with `evanescent_tail_required_radius_uncovered`, then the mode requires
    reviewed oracle coverage and must fail closed unless it is in the reviewed continuous envelope.
- Unknown opt-in names must still raise `ValueError`.
- Default `experimental_required_radius_oracle=None` behavior must remain unchanged.

This means `ell=2` with the T8t config should use the ordinary production path, not
`q018_experimental_oracle_out_of_envelope`.

## 4. Required Continuous Coverage Work

Determine the exact R60_K2 continuous coverage set:

```text
M=1, k=2.0, required_eval_radius=60.0, r_out=300.0,
r_in_eps=1e-6, rtol=1e-10, atol=1e-12,
ell=2..180, sector=odd/even.
```

For each `(ell, sector)`:

1. Run the default production path with `required_eval_radius=60.0` and no experimental oracle.
2. Classify it as:
   - default-covered;
   - default fail-closed with `evanescent_tail_required_radius_uncovered`;
   - other failure.
3. For every default fail-closed mode needed by `lmax=180`, run/validate the `q018_riccati` oracle.
4. Expand the reviewed opt-in production envelope only for modes that have direct finite oracle evidence.
5. Record a compact table in `status.md`: default-covered range, oracle-covered range, and any missing modes.

Expected shape: the oracle set is probably a continuous high-`ell` band near the previous threshold, but do not
assume the endpoints. Measure it.

If any mode required by `ell=2..180` cannot be certified, stop **YELLOW** with the exact missing mode list.

## 5. Required Tests

Use TDD. Add or update tests for:

- With the T8t boundary config, `solve_radial_mode(Sector.ODD, 2, ...)` and
  `solve_radial_mode(Sector.EVEN, 2, ...)` return ordinary finite production solutions and do not raise
  `q018_experimental_oracle_out_of_envelope`.
- Default `experimental_required_radius_oracle=None` still fail-closes for R60 suppressed modes that are not
  default-covered.
- The explicit opt-in returns finite `RadialSolution` with provenance for every reviewed continuous suppressed
  mode required by `lmax=180`.
- Unknown opt-in names still raise `ValueError`.
- True out-of-scope requests still fail closed, including at least `k=4.0`, `required_eval_radius=80.0`, and an
  `ell` beyond the reviewed continuous envelope.
- `schwgw.numerics` still does not export `solve_q018_rescaled_oracle`.
- T8/viz/scattering/CLI public layers still do not directly import `schwgw.numerics.experimental`.

Add a direct no-artifact smoke check if runtime is reasonable:

```text
compute_polarization(M=1, k=2, r=60, theta=0.05, phi=0,
                     A_plus=0.9+1.1j, A_cross=0.4+0.6j,
                     lmax=180, BoundaryConfig(required_eval_radius=60,
                     experimental_required_radius_oracle="q018_riccati",
                     r_out=300, r_in_eps=1e-6, rtol=1e-10, atol=1e-12))
```

This check must not save a result file. If it is too slow, stop YELLOW and report runtime/last mode.

## 6. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run:

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' \) -print
find runs/phase5/q018_r60_k2_selected_probe_smoke -maxdepth 1 -type f -print
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts;
- no selected-probe NPZ generated by T4u.

## 7. Stop Conditions

Stop **REJECT RED** if:

- default no-oracle behavior changes;
- ordinary low-`ell` modes become routed through the experimental oracle;
- true out-of-scope modes pass silently;
- public API exports the experimental oracle;
- T8 artifacts, plots, fixtures, R60_K4, `kM=4`, or larger-domain outputs are generated;
- conventions, thresholds, or `lmax` policy change.

Stop **YELLOW** if:

- continuous `ell=2..180` coverage cannot be certified;
- direct finite oracle evidence is missing for any suppressed mode needed by `lmax=180`;
- runtime is too high for continuous validation;
- fixing run-level dispatch requires broad architecture changes.

Report **GREEN / ready for T7ap review** only if continuous R60_K2 radial coverage for `ell=2..180`
is certified, run-level opt-in dispatch is corrected, targeted/full tests pass, and no artifacts were generated.

## 8. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- root-cause summary;
- default-covered vs oracle-covered mode table/ranges;
- direct no-artifact smoke result if run;
- commands and test results;
- open issues;
- exact next prompt:
  `你现在是 T7ap。请读取并严格执行 docs/prompts/phase5_t7ap_q018_continuous_r60_k2_coverage_review.md。`

Do not authorize T8 R60_K2 artifact generation from T4u.
