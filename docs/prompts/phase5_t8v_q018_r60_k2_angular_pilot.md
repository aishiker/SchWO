# Phase 5 T8v Prompt: Q018 R60_K2 Angular-Grid Pilot

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8v`。

只在 T7ao 返回 **ACCEPT GREEN FOR R60_K2 SELECTED-PROBE SMOKE** 后运行。本 slice 是 bounded
R60_K2 angular-grid pilot：比 12-point selected-probe smoke 更接近后续 production/plotting 输入，但仍不是
full R60 production，不生成 plots，不生成 regression fixtures，不运行 R60_K4、`kM=4`、larger-domain 或
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
8. `docs/prompts/phase5_t8u_q018_r60_k2_selected_probe_smoke_retry.md`
9. `docs/prompts/phase5_t7ao_q018_r60_k2_selected_probe_smoke_review.md`
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

允许：

- 创建一个 bounded angular-grid pilot config：
  `configs/r60_k2_q018_angular_pilot.yaml`
- 运行正式 T8 data-output path，生成：
  `runs/phase5/q018_r60_k2_angular_pilot/r60_k2_q018_angular_pilot.npz`
- 如 CLI 需要自动创建输出目录，做最小修复并加测试。
- 更新 `status.md`。

禁止：

- 修改 T2-T6 physics formulas、Route B/Q005/Q014 convention、radial thresholds、suppression policy 或
  `lmax` policy。
- 修改 `src/schwgw/numerics/radial_solver.py`。若 radial logic 需要变化，停止并交 T0/T4。
- 生成 plots、regression fixtures、full x-z grids、R60_K4、`kM=4`、larger-domain outputs。
- 把本 angular pilot 表述成 full R60_K2 production readiness。

## 3. Required Pilot Config

Create:

```text
configs/r60_k2_q018_angular_pilot.yaml
```

Use this bounded scope:

```yaml
case_id: R60_K2_Q018_ANGULAR_PILOT
output: runs/phase5/q018_r60_k2_angular_pilot/r60_k2_q018_angular_pilot.npz
background:
  M: 1.0
wave:
  kM: 2.0
  A_plus: {real: 0.9, imag: 1.1}
  A_cross: {real: 0.4, imag: 0.6}
observer:
  kind: angular
  r: 60.0
  theta_values:
    - 0.0
    - 0.19634954084936207
    - 0.39269908169872414
    - 0.5890486225480862
    - 0.7853981633974483
    - 0.9817477042468103
    - 1.1780972450961724
    - 1.3744467859455345
    - 1.5707963267948966
    - 1.7671458676442586
    - 1.9634954084936207
    - 2.1598449493429825
    - 2.356194490192345
    - 2.552544031041707
    - 2.748893571891069
    - 2.945243112740431
    - 3.141592653589793
  phi_values:
    - 0.0
    - 0.7853981633974483
    - 1.5707963267948966
    - 2.356194490192345
    - 3.141592653589793
    - 3.9269908169872414
    - 4.71238898038469
    - 5.497787143782138
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
  selected_threshold: 1.0e-4
  near_axis_threshold: 1.0e-3
```

This is `17 x 8 = 136` angular points at one radius. Do not replace it with a full x-z grid or a denser angular grid.

## 4. Required Run

Run:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run \
  configs/r60_k2_q018_angular_pilot.yaml \
  --out runs/phase5/q018_r60_k2_angular_pilot/r60_k2_q018_angular_pilot.npz
```

If the run exceeds 90 minutes, stop and report **YELLOW / runtime too high**. Do not reduce `lmax`, remove points,
change thresholds, or relax Q018 policy.

## 5. Required Artifact Inspection

If NPZ writes successfully, inspect:

- output path is project-local under `runs/phase5/q018_r60_k2_angular_pilot/`;
- `case_id == "R60_K2_Q018_ANGULAR_PILOT"`;
- grid kind is `angular`;
- observer radius is `60.0`;
- `theta.shape == (17,)`, `phi.shape == (8,)`;
- `h_plus/h_cross.shape == (17, 8)`;
- all saved valid `h_plus/h_cross` values are finite complex numbers;
- `config.numerics.boundary.required_eval_radius == 60.0`;
- `config.numerics.boundary.experimental_required_radius_oracle == "q018_riccati"`;
- final adjacent pair is `[156, 180]`;
- `diagnostics.lmax_convergence_policy.final_pair_passed` is true for GREEN;
- final pair selected max change `<=1e-4`;
- final pair near-axis max change `<=1e-3`;
- `diagnostics.radial_diagnostic_warnings` contains Q018 oracle provenance records for continuous `ell=153..180`,
  odd/even;
- run-scoped radial cache metadata records finite `unique_solution_count`, `key_count`, and `hit_count`;
- no plotting files, fixtures, full x-z grids, R60_K4, `kM=4`, or larger-domain artifacts were generated.

If final adjacent pair fails, keep the NPZ as a diagnostic artifact and report
**YELLOW / convergence not accepted**. Do not tune thresholds to force a pass.

## 6. Validation Commands

At minimum run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

And run static/output checks:

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' \) -print
find runs/phase5/q018_r60_k2_angular_pilot -maxdepth 2 -type f -print
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts;
- only bounded angular-pilot files under the Q018 angular-pilot output directory.

## 7. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7aq ANGULAR-PILOT REVIEW**:
  bounded NPZ exists; metadata/provenance is present; final pair passes; finite complex fields are saved; tests pass;
  no forbidden artifacts/imports/scope changes occurred.
- **YELLOW / DIAGNOSTIC ARTIFACT ONLY**:
  bounded NPZ exists but convergence fails, metadata/provenance is incomplete, runtime is too high, or tests reveal a
  limited T8 issue.
- **REJECT RED**:
  full grid/plots/fixtures/R60_K4/`kM=4` were generated, default configs broke, public layers directly import the
  experimental oracle, tests fail broadly, or conventions/thresholds/`lmax` policy changed.

## 8. status.md Update

Update `status.md` with:

- changed/generated files;
- files read;
- plugin/skill check;
- command/runtime;
- output path and artifact inspection table;
- convergence final-pair result;
- Q018 provenance summary;
- radial cache metadata;
- static/output search results;
- commands and test results;
- decision label;
- open issues;
- exact next action.

If artifact exists, next action is:

```text
你现在是 T7aq。请读取并严格执行 docs/prompts/phase5_t7aq_q018_r60_k2_angular_pilot_review.md。
```

Do not authorize full R60_K2 production from T8v.
