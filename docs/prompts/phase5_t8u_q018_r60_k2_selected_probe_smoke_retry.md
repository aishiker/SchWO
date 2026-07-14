# Phase 5 T8u Prompt: Retry Q018 R60_K2 Selected-Probe Smoke

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8u`。

只在 T7ap 返回 **ACCEPT GREEN FOR CONTINUOUS R60_K2 RADIAL COVERAGE** 后运行。本 slice 不是新的 schema
开发任务；T8t 已经添加了可携带 Q018 opt-in 的 YAML/metadata/cache-key 支持，但当时没有生成 saved
smoke artifact。T8u 的目标是用已经存在的 bounded config 重新跑正式 T8 data-output path，生成一个
project-local R60_K2 selected-probe NPZ，供 T7ao 独立 review。

不要运行 full R60 production，不要生成 plots，不要生成 regression fixtures，不要运行 R60_K4、`kM=4`、
larger-domain 或 arbitrary incident direction。

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
9. `docs/prompts/phase5_t7ap_q018_continuous_r60_k2_coverage_review.md`
10. `configs/r60_k2_q018_selected_probe_smoke.yaml`
11. `src/schwgw/io/config.py`
12. `src/schwgw/io/results.py`
13. `src/schwgw/cli.py`
14. `src/schwgw/numerics/boundary_conditions.py`
15. `src/schwgw/numerics/radial_solver.py`
16. `src/schwgw/scattering/partial_wave.py`
17. `tests/unit/test_io_config.py`
18. `tests/regression/test_io_cli.py`
19. `tests/physics/test_q018_production_integration_design.py`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion；如果需要修改代码，使用 test-driven-development。此任务不需要外部文献
检索；如出现 convention 冲突，停止并交 T0/T1。

## 2. Scope

默认允许：

- 运行已有 config；
- 生成 project-local selected-probe NPZ：
  `runs/phase5/q018_r60_k2_selected_probe_smoke/r60_k2_q018_selected_probe_smoke.npz`；
- 如 CLI 需要自动创建输出目录，做最小修复并加测试；
- 更新 `status.md`。

只有在 bounded smoke run 因 T8 schema/CLI bug 失败时，才允许最小修改：

- `src/schwgw/io/config.py`
- `src/schwgw/io/results.py`
- `src/schwgw/cli.py`
- `tests/unit/test_io_config.py`
- `tests/regression/test_io_cli.py`

禁止：

- 修改 T2-T6 physics formulas、Route B/Q005/Q014 convention、radial thresholds、suppression policy 或
  `lmax` policy；
- 修改 `src/schwgw/numerics/radial_solver.py`，除非发现 T8 无法传递已存在的 `BoundaryConfig` 字段；若发生，
  必须停止并交 T0/T4，而不是在 T8u 中修 radial logic；
- 生成 plots、regression fixtures、full x-z grids、R60_K4、`kM=4`、larger-domain outputs；
- 把 selected-probe smoke 表述成 full R60_K2 production readiness。

## 3. Required Smoke Run

使用现有 config：

```text
configs/r60_k2_q018_selected_probe_smoke.yaml
```

确认它仍是 bounded angular selected-probe：

- `case_id: R60_K2_Q018_SELECTED_PROBE_SMOKE`
- observer kind `angular`
- `r=60`
- 6 个 `theta_values` 和 2 个 `phi_values`，共 12 个点
- `lmax=180`
- `required_eval_radius=60.0`
- `experimental_required_radius_oracle=q018_riccati`
- convergence `lmax_values=[108,132,156,180]`

运行：

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run \
  configs/r60_k2_q018_selected_probe_smoke.yaml \
  --out runs/phase5/q018_r60_k2_selected_probe_smoke/r60_k2_q018_selected_probe_smoke.npz
```

如果运行超过 90 分钟，停止并报告 **YELLOW / runtime too high**。不要扩大并行、不要改阈值、不要降低
`lmax` 或删点来强行通过。

## 4. Required Artifact Inspection

若 NPZ 写出，立刻检查：

- output path 在 `runs/phase5/q018_r60_k2_selected_probe_smoke/` 下；
- grid kind 是 `angular`；
- observer radius 是 `60.0`；
- saved `h_plus/h_cross` shape 是 `(6, 2)`；
- saved valid `h_plus/h_cross` 都是 finite complex；
- metadata 中记录 `config.numerics.boundary.required_eval_radius == 60.0`；
- metadata 中记录 `config.numerics.boundary.experimental_required_radius_oracle == "q018_riccati"`；
- `diagnostics.lmax_convergence_history` 至少包含 adjacent pairs `[108,132]`, `[132,156]`, `[156,180]`；
- final adjacent pair 是 `[156,180]`；
- `diagnostics.lmax_convergence_policy.final_pair_passed` 已记录；
- `diagnostics.radial_diagnostic_warnings` 包含 Q018 oracle provenance，至少覆盖 final run 中触发的
  reviewed suppressed modes；
- provenance records JSON-safe，并包含 `ell`, `sector`, `k`, `required_eval_radius`,
  `experimental_required_radius_oracle`, `method`, `valid_at_required_radius`,
  `unit_incoming_at_infinity`；
- 没有 plot、fixture、R60_K4、`kM=4` 或 larger-domain artifact。

如果 final adjacent pair 没通过，不要删除 NPZ；保留作为 diagnostic artifact，报告
**YELLOW / convergence not accepted**，交 T7ao review。

## 5. Validation Commands

至少运行：

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

并运行静态/输出范围检查：

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' \) -print
find runs/phase5/q018_r60_k2_selected_probe_smoke -maxdepth 2 -type f -print
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers；
- no R60_K4 or `kM=4` artifacts；
- only bounded selected-probe smoke files under the Q018 selected-probe output directory。

## 6. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7ao ARTIFACT REVIEW**:
  bounded NPZ exists; schema metadata is present; final pair passes; oracle provenance is serialized; finite complex
  fields are saved; tests pass; no forbidden artifacts/imports/scope changes occurred.
- **YELLOW / DIAGNOSTIC ARTIFACT ONLY**:
  bounded NPZ exists but final pair fails, metadata/provenance is incomplete, runtime is too high, or tests reveal a
  limited T8 issue that needs review.
- **REJECT RED**:
  full grid/plots/fixtures/R60_K4/`kM=4` were generated, default configs broke, public layers directly import the
  experimental oracle, tests fail broadly, or conventions/thresholds/`lmax` policy changed.

## 7. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- command/runtime;
- output path and artifact inspection table;
- convergence final-pair result;
- Q018 provenance summary;
- static/output search results;
- commands and test results;
- decision label;
- open issues;
- exact next action.

If artifact exists, next action is:

```text
你现在是 T7ao。请读取并严格执行 docs/prompts/phase5_t7ao_q018_r60_k2_selected_probe_smoke_review.md。
```

Do not authorize full R60_K2 production from T8u.
