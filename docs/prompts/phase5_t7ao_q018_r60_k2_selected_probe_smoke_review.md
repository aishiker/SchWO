# Phase 5 T7ao Prompt: Review Q018 R60_K2 Selected-Probe Smoke

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ao`。

只在 T8t/T8u 生成 saved selected-probe artifact 后运行。你的任务是独立复核 T8 的 bounded R60_K2 selected-probe/smoke：
schema 是否正确传递 Q018 opt-in，saved metadata 是否包含 radial oracle provenance，adaptive `lmax`
final adjacent pair 是否通过，以及 T8 是否仍没有越界到 full production。不要把本 review 通过解读为
full R60_K2 production、R60_K4、`kM=4`、larger-domain 或 arbitrary incident direction readiness。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_production_integration_design.md`
8. `docs/prompts/phase5_t8t_q018_r60_k2_selected_probe_smoke.md`
9. `docs/prompts/phase5_t8u_q018_r60_k2_selected_probe_smoke_retry.md`
10. `docs/prompts/phase5_t7an_q018_optin_production_oracle_review.md`
11. `src/schwgw/io/config.py`
12. `src/schwgw/io/results.py`
13. `src/schwgw/cli.py`
14. `src/schwgw/numerics/radial_solver.py`
15. `src/schwgw/scattering/partial_wave.py`
16. `tests/regression/test_io_cli.py`
17. `tests/unit/test_io_config.py`
18. T8t/T8u changed files and generated output listed in `status.md`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion。不要上传私有文件；本 review 不需要外部文献检索，除非发现新的
physics convention 冲突。

## 2. Review Scope

独立确认：

- T8t only added minimal schema/CLI/output support for optional `BoundaryConfig` fields;
- old configs without `required_eval_radius` / `experimental_required_radius_oracle` still work;
- `run_solver_grid(...)` passes the optional fields into `BoundaryConfig`;
- radial cache key includes the optional fields and cannot collide with a default boundary config;
- saved metadata records the optional boundary fields under both config/boundary metadata where applicable;
- output is a bounded angular selected-probe smoke at `r=60`, `kM=2`, not a full x-z grid;
- output lives under `runs/phase5/q018_r60_k2_selected_probe_smoke/`;
- no plots, regression fixtures, R60_K4, `kM=4`, larger-domain outputs, or arbitrary-direction runs were generated;
- T8/viz/scattering/CLI public layers do not directly import `schwgw.numerics.experimental`;
- frozen conventions, thresholds, suppression policy, and `lmax` policy are unchanged.

## 3. Required Artifact Checks

Load:

```text
runs/phase5/q018_r60_k2_selected_probe_smoke/r60_k2_q018_selected_probe_smoke.npz
```

Inspect:

- `case_id == "R60_K2_Q018_SELECTED_PROBE_SMOKE"`;
- grid kind is `angular`;
- observer radius is exactly `60.0`;
- grid has 6 theta values and 2 phi values, for 12 selected points;
- `lmax == 180`;
- `config.numerics.boundary.required_eval_radius == 60.0`;
- `config.numerics.boundary.experimental_required_radius_oracle == "q018_riccati"`;
- saved `h_plus/h_cross` arrays have shape `(6, 2)` and finite complex values;
- `diagnostics.lmax_convergence_history` contains adjacent pairs `[108,132]`, `[132,156]`, `[156,180]`;
- `diagnostics.final_lmax_pair == [156, 180]`;
- `diagnostics.lmax_convergence_policy.final_pair_passed` is true for GREEN;
- final pair selected max change is `<=1e-4`;
- final pair near-axis max change is `<=1e-3`;
- `diagnostics.radial_diagnostic_warnings` contains Q018 oracle provenance records with
  `code="q018_required_radius_oracle_used"`;
- provenance records include at least the reviewed suppressed modes reached by final `lmax=180`:
  `ell=[153,156,168,180]`, odd/even, with `required_eval_radius=60.0`,
  `experimental_required_radius_oracle="q018_riccati"`, `valid_at_required_radius=True`, and
  `unit_incoming_at_infinity=True`.

If final pair did not pass, classify as **ACCEPT YELLOW / smoke artifact diagnostic only**, not GREEN.

## 4. Independent Consistency Probes

Run one direct selected point recomputation for at least:

```text
r=60, theta=0.05, phi=0, k=2, lmax=180,
BoundaryConfig(required_eval_radius=60.0, experimental_required_radius_oracle="q018_riccati",
               r_out=300.0, r_in_eps=1e-6, rtol=1e-10, atol=1e-12)
```

Compare direct `compute_polarization(...)` against the saved NPZ value for that point with
`rtol=1e-10, atol=1e-12`.

Also verify a default config without the Q018 opt-in remains accepted by existing smoke tests, and verify a
same selected-probe run with default `experimental_required_radius_oracle=None` would fail closed rather than
silently compute the R60 suppressed modes.

## 5. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run static/output searches:

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering
find runs configs tests/regression/fixtures -maxdepth 6 -iname '*R60*K4*' -o -iname '*k4*'
find runs/phase5/q018_r60_k2_selected_probe_smoke -maxdepth 2 -type f
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts;
- only bounded smoke files under the Q018 selected-probe output directory.

## 6. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR R60_K2 SELECTED-PROBE SMOKE**:
  schema and CLI support are minimal and backward compatible; saved selected-probe result exists; final adjacent
  pair passes; oracle provenance is serialized; direct recomputation agrees; tests pass; no forbidden artifacts or
  imports were introduced. This allows T0 to consider a next bounded R60_K2 artifact step, but still does not
  authorize full R60 production, R60_K4, `kM=4`, larger domains, arbitrary incident direction, or threshold changes.
- **ACCEPT YELLOW / DIAGNOSTIC ONLY**:
  smoke result exists or schema improved, but convergence failed, metadata/provenance is incomplete, runtime is too
  high, or artifact scope needs tightening before any next T8 step.
- **REJECT RED**:
  full grid/plots/fixtures/R60_K4/`kM=4` were generated, default configs broke, public layers import experimental
  oracle directly, tests fail, conventions/thresholds/`lmax` policy changed, or saved metadata is not auditable.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- artifact inspection table;
- direct recomputation result;
- static/output search results;
- commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

Do not authorize full R60_K2 production from T7ao.
