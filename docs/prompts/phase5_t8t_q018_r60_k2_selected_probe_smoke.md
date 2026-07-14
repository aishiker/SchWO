# Phase 5 T8t Prompt: Q018 R60_K2 Selected-Probe Opt-In Smoke

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8t`。

只在 T7an **ACCEPT GREEN FOR REVIEWED OPT-IN PRODUCTION ORACLE** 后运行。本 slice 的目标是
通过正式 T8 data-output path 做一个 bounded R60_K2 selected-probe/smoke，验证 saved-result
schema 可以携带 Q018 opt-in provenance 和 adaptive `lmax` convergence metadata。它不是 full
R60 production，不生成 plots，不生成 regression fixtures，不运行 R60_K4、`kM=4`、larger-domain 或
arbitrary incident direction。

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
12. `src/schwgw/io/config.py`
13. `src/schwgw/io/results.py`
14. `src/schwgw/cli.py`
15. `src/schwgw/numerics/boundary_conditions.py`
16. `src/schwgw/numerics/radial_solver.py`
17. `src/schwgw/scattering/partial_wave.py`
18. `tests/regression/test_io_cli.py`
19. `tests/unit/test_io_config.py`
20. `tests/physics/test_q018_production_integration_design.py`

按项目规则，先检查已安装 plugin/skill。使用 TDD、systematic debugging、
verification-before-completion。此任务不需要外部文献插件；如出现 convention 问题，停止并交 T0/T1。

## 2. Scope

允许修改：

- `src/schwgw/io/config.py`
- `src/schwgw/io/results.py`
- `src/schwgw/cli.py` only if required by existing CLI path
- `tests/regression/test_io_cli.py`
- `tests/unit/test_io_config.py`
- `configs/r60_k2_q018_selected_probe_smoke.yaml`
- `status.md`

只在确有必要时允许修改：

- `docs/numerics.md`
- `docs/validation_plan.md`

禁止：

- 不要修改 T2-T6 physics formulas、Route B/Q005/Q014 convention、radial thresholds、suppression policy 或
  `lmax` policy。
- 不要修改 `src/schwgw/numerics/radial_solver.py`，除非发现 T8 schema 无法传递已存在的
  `BoundaryConfig` 字段；若需要修改，必须先记录原因并保持 T4s/T7an contract 不变。
- 不要生成 plots、regression fixtures、full x-z grids、R60_K4、`kM=4`、larger-domain outputs。
- 不要把 selected-probe smoke 表述成 full R60_K2 production readiness。

## 3. Required Schema Work

现有 YAML config 的 `numerics.boundary` 只包含 `r_in_eps/r_out/rtol/atol`。本 slice 需要最小扩展：

```yaml
numerics:
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
    required_eval_radius: 60.0
    experimental_required_radius_oracle: q018_riccati
```

Implementation requirements:

- Extend `BoundarySettings` with optional `required_eval_radius: float | None` and
  `experimental_required_radius_oracle: str | None`.
- Parse and validate the optional fields in `load_config(...)` / `parse_config(...)`.
- Include both optional fields in `SolverConfig.to_dict()` and saved metadata when present.
- Pass both fields into `BoundaryConfig(...)` inside `run_solver_grid(...)`.
- Update `_radial_cache_key(...)` to include `required_eval_radius` and
  `experimental_required_radius_oracle`, so future mixed-boundary runs cannot collide in the run cache.
- Add tests proving old configs without these fields still parse and run unchanged.
- Add tests proving the new optional fields are serialized into saved metadata and passed to the solver.

Do not add a broad plugin system or new file format.

## 4. Required Smoke Config

Create:

```text
configs/r60_k2_q018_selected_probe_smoke.yaml
```

Use exactly this bounded scope unless a T0-visible reason is recorded:

```yaml
case_id: R60_K2_Q018_SELECTED_PROBE_SMOKE
output: runs/phase5/q018_r60_k2_selected_probe_smoke/r60_k2_q018_selected_probe_smoke.npz
background:
  M: 1.0
wave:
  kM: 2.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: angular
  r: 60.0
  theta_values: [0.0, 0.05, 0.2, 1.0, 2.0, 3.0]
  phi_values: [0.0, 3.141592653589793]
numerics:
  lmax: 180
  boundary:
    r_in_eps: 1.0e-6
    r_out: 300.0
    rtol: 1.0e-10
    atol: 1.0e-12
    required_eval_radius: 60.0
    experimental_required_radius_oracle: q018_riccati
convergence:
  enabled: true
  lmax_values: [108, 132, 156, 180]
  theta_values: [0.0, 0.05, 0.2, 1.0, 2.0, 3.0]
  phi_values: [0.0, 3.141592653589793]
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

This is 12 selected angular points only. Do not replace it with a full x-z grid.

## 5. Required Smoke Run

Run:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run \
  configs/r60_k2_q018_selected_probe_smoke.yaml \
  --out runs/phase5/q018_r60_k2_selected_probe_smoke/r60_k2_q018_selected_probe_smoke.npz
```

After the run, inspect the saved NPZ metadata. Required checks:

- output path is project-local under `runs/phase5/q018_r60_k2_selected_probe_smoke/`;
- grid kind is `angular`, `r=60`, 12 selected points, no x-z full grid;
- `config.numerics.boundary.required_eval_radius == 60.0`;
- `config.numerics.boundary.experimental_required_radius_oracle == "q018_riccati"`;
- `diagnostics.lmax_convergence_policy.final_pair_passed` is recorded;
- final adjacent pair is `[156, 180]`;
- selected threshold is `1e-4`, near-axis threshold is `1e-3`;
- all saved valid `h_plus/h_cross` values are finite complex numbers;
- `diagnostics.radial_diagnostic_warnings` includes per-mode Q018 oracle provenance with
  `code="q018_required_radius_oracle_used"` for the reviewed suppressed modes reached by the final run;
- radial warning/provenance records are JSON-safe and include `ell`, `sector`, `k`, `required_eval_radius`,
  `experimental_required_radius_oracle`, `method`, `valid_at_required_radius`, and
  `unit_incoming_at_infinity`;
- no plotting files, fixtures, R60_K4, `kM=4`, or larger-domain artifacts were generated.

If final adjacent pair fails, keep the saved diagnostic smoke output for T7 review, but classify this slice
as **YELLOW / convergence not accepted**. Do not tune thresholds or change `lmax_values` to force a pass.

## 6. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also run static/output checks:

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering
find runs configs tests/regression/fixtures -maxdepth 6 -iname '*R60*K4*' -o -iname '*k4*'
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts.

## 7. Stop Conditions

Stop **REJECT RED** if:

- full x-z grid, plots, fixtures, R60_K4, `kM=4`, or larger-domain artifacts are generated;
- frozen convention, threshold, suppression policy, or `lmax` policy changes;
- T8/viz/scattering/CLI public layers directly import `schwgw.numerics.experimental`;
- default configs without Q018 fields break;
- saved metadata omits the opt-in boundary fields.

Stop **YELLOW** if:

- selected-probe run exceeds 45 minutes in the current environment;
- final adjacent pair does not pass;
- Q018 oracle provenance is missing or not JSON-safe;
- only a subset of required selected points is finite;
- CLI/config schema support needs a broader refactor.

Report **GREEN / ready for T7ao review** only if schema tests pass, the bounded smoke result is saved,
selected-probe convergence metadata is present, final pair passes, oracle provenance is serialized, and full
pytest passes.

## 8. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- schema changes;
- smoke config path and output path;
- smoke runtime;
- selected-probe convergence table;
- radial oracle provenance summary;
- commands and test results;
- open issues;
- exact next prompt:
  `你现在是 T7ao。请读取并严格执行 docs/prompts/phase5_t7ao_q018_r60_k2_selected_probe_smoke_review.md。`

Do not authorize full R60_K2 production from T8t.
