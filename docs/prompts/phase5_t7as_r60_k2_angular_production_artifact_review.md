# Phase 5 T7as Prompt: Review R60_K2 Angular Production Artifact

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7as`。

只在 T8x 生成 saved R60_K2 angular production artifact 后运行。你的任务是独立复核该 artifact：
schema 是否正确，saved metadata 是否包含 Q018 provenance，selected-convergence final adjacent pair 是否通过，
saved field 是否 finite，direct selected-point recomputation 是否一致，default no-opt-in 是否仍 fail closed，以及
T8 是否没有越界生成 plots、fixtures、R60_K4、`kM=4`、larger-domain 或 arbitrary-direction outputs。

本 review 通过只接受这个 R60_K2 angular production NPZ。不要把它解读为 R60_K4、`kM=4`、arbitrary incident
direction、larger-domain、plotting 或 fixture readiness。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_production_integration_design.md`
8. `docs/q018_r60_k2_angular_production_readiness.md`
9. `docs/prompts/phase5_t8x_r60_k2_angular_production_run.md`
10. `configs/r60_k2_q018_angular_production_first_pass.yaml`
11. `src/schwgw/io/config.py`
12. `src/schwgw/io/results.py`
13. `src/schwgw/cli.py`
14. `src/schwgw/numerics/radial_solver.py`
15. `src/schwgw/scattering/partial_wave.py`
16. `tests/unit/test_io_config.py`
17. `tests/regression/test_io_cli.py`
18. T8x changed/generated files listed in `status.md`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion。不要上传私有文件；本 review 不需要外部文献检索，除非发现新的 physics
convention 冲突。

## 2. Required Artifact Checks

Load:

```text
runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz
```

Inspect:

- `case_id == "R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS"`;
- grid kind is `angular`;
- observer radius is exactly `60.0`;
- `theta.shape == (65,)`;
- `phi.shape == (64,)`;
- `phi` excludes duplicate `2pi`;
- `h_plus/h_cross.shape == (65,64)`;
- all saved valid `h_plus/h_cross` values are finite complex numbers;
- `lmax == 180`;
- `config.numerics.boundary.required_eval_radius == 60.0`;
- `config.numerics.boundary.experimental_required_radius_oracle == "q018_riccati"`;
- saved `diagnostics.lmax_convergence_history` contains adjacent pairs `[108,132]`, `[132,156]`, `[156,180]`;
- `diagnostics.final_lmax_pair == [156,180]`;
- `diagnostics.lmax_convergence_policy.final_pair_passed` is true for GREEN;
- final pair selected max change is `<=1e-4`;
- final pair near-axis max change is `<=1e-3`;
- metadata makes clear that convergence probes are the selected `17 x 8` subset, not full-grid convergence;
- `diagnostics.radial_diagnostic_warnings` contains `q018_required_radius_oracle_used` records for continuous
  `ell=153..180`, odd/even;
- provenance records include at least `ell=[153,156,168,180]`, odd/even, with `required_eval_radius=60.0`,
  `experimental_required_radius_oracle="q018_riccati"`, `valid_at_required_radius=True`, and
  `unit_incoming_at_infinity=True`;
- run radial cache metadata is present and records `unique_solution_count`, `key_count`, and `hit_count`.

If final pair did not pass, classify as **ACCEPT YELLOW / diagnostic only**, not GREEN.

## 3. Independent Consistency Probes

Run at least two direct selected-point recomputations:

1. Near-axis point included in the convergence subset:

```text
r=60, theta=0.0, phi=0.0, k=2, lmax=180,
BoundaryConfig(required_eval_radius=60.0, experimental_required_radius_oracle="q018_riccati",
               r_out=300.0, r_in_eps=1e-6, rtol=1e-10, atol=1e-12)
```

2. Non-axis point included in the convergence subset:

```text
r=60, theta=1.5707963267948966, phi=1.5707963267948966, k=2, lmax=180,
same BoundaryConfig
```

Compare direct `compute_polarization(...)` against the saved NPZ value for those points with `rtol=1e-10, atol=1e-12`.

Also verify a same selected point with default `experimental_required_radius_oracle=None` fails closed rather than
silently computing the R60 suppressed modes.

## 4. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run static/output searches:

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' \) -print
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 2 -type f -print
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts;
- only the R60_K2 angular production NPZ under the production output directory.

## 5. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR R60_K2 ANGULAR PRODUCTION ARTIFACT**:
  production NPZ exists and is scoped; metadata/provenance is auditable; selected final adjacent pair passes; direct
  recomputations agree; default fail-closed behavior remains; tests pass; no forbidden artifacts/imports/scope changes
  occurred. This accepts only this NPZ artifact, not plotting, fixtures, R60_K4, `kM=4`, arbitrary direction, or larger
  domains.
- **ACCEPT YELLOW / DIAGNOSTIC ONLY**:
  artifact exists but convergence failed, metadata/provenance is incomplete, runtime evidence is concerning, or scope
  needs tightening before acceptance.
- **REJECT RED**:
  forbidden outputs were generated, default configs broke, public layers import experimental oracle directly, tests
  fail, conventions/thresholds/`lmax` policy changed, or saved metadata is not auditable.

## 6. status.md Update

Update `status.md` with:

- changed/generated files;
- files read;
- plugin/skill check;
- artifact inspection table;
- convergence result;
- direct recomputation results;
- default fail-closed result;
- static/output search results;
- commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

Do not authorize plotting, fixtures, R60_K4, `kM=4`, larger-domain artifacts, or arbitrary incident direction from T7as.
