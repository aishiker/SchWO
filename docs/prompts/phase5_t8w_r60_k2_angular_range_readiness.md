# Phase 5 T8w Prompt: R60_K2 Angular-Range Schema And Production Readiness

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8w`。

只在 T7aq 返回 **ACCEPT GREEN FOR BOUNDED R60_K2 ANGULAR-GRID PILOT ONLY** 后运行。本 slice 的目标是为
未来 R60_K2 angular production 做 schema/readiness 准备：支持 angular observer 的 `theta_range` /
`phi_range`，创建小型 range-schema smoke config 和一个不运行的 production config draft，并写明 runtime /
storage / acceptance gates。

本 slice 不运行 full R60 production，不生成 production NPZ，不生成 plots，不生成 regression fixtures，不运行
R60_K4、`kM=4`、larger-domain 或 arbitrary incident direction。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `docs/physics_spec.md`
4. `docs/equation_map.md`
5. `docs/numerics.md`
6. `docs/validation_plan.md`
7. `docs/q018_production_integration_design.md`
8. `docs/q018_larger_domain_readiness.md`
9. `docs/m4_production_plan.md`
10. `docs/prompts/phase5_t8v_q018_r60_k2_angular_pilot.md`
11. `docs/prompts/phase5_t7aq_q018_r60_k2_angular_pilot_review.md`
12. `configs/r60_k2_q018_angular_pilot.yaml`
13. `src/schwgw/io/config.py`
14. `src/schwgw/io/results.py`
15. `src/schwgw/cli.py`
16. `tests/unit/test_io_config.py`
17. `tests/regression/test_io_cli.py`

按项目规则，先检查已安装 plugin/skill。使用 test-driven-development、systematic debugging 和
verification-before-completion。此任务不需要外部文献检索；如出现 convention 冲突，停止并交 T0/T1。

## 2. Scope

允许修改：

- `src/schwgw/io/config.py`
- `tests/unit/test_io_config.py`
- `tests/regression/test_io_cli.py` only if an existing CLI smoke needs range-config coverage
- `configs/r60_k2_q018_angular_range_schema_smoke.yaml`
- `configs/r60_k2_q018_angular_production_first_pass.yaml`
- `docs/q018_r60_k2_angular_production_readiness.md`
- `status.md`

禁止：

- 修改 T2-T6 physics formulas、Route B/Q005/Q014 convention、radial thresholds、Q018 suppression/oracle policy 或
  `lmax` policy。
- 修改 `src/schwgw/numerics/radial_solver.py`、`src/schwgw/scattering/partial_wave.py` 或 plotting code。
- 运行 full R60 production config。
- 生成 production NPZ、plots、fixtures、R60_K4、`kM=4`、larger-domain outputs 或 arbitrary-direction artifacts。
- 把 readiness/config draft 表述成 production acceptance。

## 3. Required Schema Work

Extend angular observer config parsing to support either explicit values or ranges:

```yaml
observer:
  kind: angular
  r: 60.0
  theta_range:
    start: 0.0
    stop: 3.141592653589793
    step: 0.04908738521234052
    endpoint: true
  phi_range:
    start: 0.0
    stop: 6.283185307179586
    step: 0.09817477042468103
    endpoint: false
```

Requirements:

- Preserve old explicit `theta_values` / `phi_values` behavior exactly.
- Reject configs that provide both `theta_values` and `theta_range`, or both `phi_values` and `phi_range`.
- Reject missing angular theta/phi specification.
- Reject nonpositive `step`.
- Reject ranges whose generated arrays are empty.
- `endpoint: true` includes the stop value within floating tolerance.
- `endpoint: false` excludes the stop value and is suitable for periodic `phi`.
- Save expanded arrays in the existing result schema; do not add a new result schema variant.
- `SolverConfig.to_dict()` should preserve enough original range metadata for audit while still saving expanded arrays.

If convergence config currently requires explicit `theta_values` / `phi_values`, add the same optional range support there too.  Do not silently make convergence probes default to the full observer grid unless that is already established behavior; keep the behavior explicit and test it.

## 4. Required Configs

Create a small smoke config that may be run:

```text
configs/r60_k2_q018_angular_range_schema_smoke.yaml
```

Use a small bounded grid, for example `5 x 4`, with the same physics and Q018 opt-in boundary as T8v.  Output path:

```text
runs/phase5/q018_r60_k2_angular_range_schema_smoke/r60_k2_q018_angular_range_schema_smoke.npz
```

Create but do not run a production config draft:

```text
configs/r60_k2_q018_angular_production_first_pass.yaml
```

Use this intended grid:

- `case_id: R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS`
- output under `runs/phase5/q018_r60_k2_angular_production_first_pass/`
- `r=60.0`, `kM=2.0`, `lmax=180`
- `theta_range`: `0..pi`, `step=pi/64`, `endpoint=true` -> `65` theta values
- `phi_range`: `0..2pi`, `step=2pi/64`, `endpoint=false` -> `64` phi values
- boundary: `required_eval_radius=60.0`, `experimental_required_radius_oracle=q018_riccati`,
  `r_out=300.0`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`
- convergence lmax values: `[108,132,156,180]`
- convergence probes must be explicit and documented: either the full `65 x 64` angular grid, or a named selected
  subset.  If using a subset, the readiness doc must state that it is not full-grid convergence acceptance.

## 5. Required Smoke Run

Run only the small range-schema smoke config:

```bash
/usr/bin/time -p env PYTHONPATH=src /opt/homebrew/bin/python3 -m schwgw.cli run \
  configs/r60_k2_q018_angular_range_schema_smoke.yaml \
  --out runs/phase5/q018_r60_k2_angular_range_schema_smoke/r60_k2_q018_angular_range_schema_smoke.npz
```

Do not run:

```text
configs/r60_k2_q018_angular_production_first_pass.yaml
```

Inspect the smoke NPZ metadata:

- expanded angular arrays have the expected shape;
- saved metadata records range input and expanded arrays;
- Q018 opt-in boundary fields are present;
- final adjacent pair is recorded;
- Q018 provenance records are present if final `lmax=180` reaches the suppressed band;
- no plot, fixture, R60_K4, `kM=4`, larger-domain, or production artifact was generated.

## 6. Required Readiness Document

Create:

```text
docs/q018_r60_k2_angular_production_readiness.md
```

It must include:

- T7aq accepted evidence summary and its limits.
- Proposed production artifact path and config path.
- Grid definition: `65 x 64`, `r=60`, angular coordinates, endpoint policy.
- Runtime/storage estimate using T8v observed runtime:
  - T8v `136` points, runtime about `425.48 s`;
  - production candidate `4160` points;
  - point-count scale factor `4160/136 = 30.58823529411765`;
  - rough runtime estimate `~3.6 h` if scaling linearly, before reruns/reviews.
- Radial cache expectation: unique solves remain `358` for same `k/lmax/boundary`; cache hits scale with points.
- Acceptance gates before running production:
  - T7 review of this readiness slice;
  - explicit T0 authorization;
  - production run must remain project-local;
  - final adjacent pair must pass;
  - Q018 provenance must serialize `ell=153..180`, odd/even;
  - default fail-closed behavior must remain tested;
  - no `kM=4`, R60_K4, larger-domain, arbitrary-direction, plotting, or fixture expansion.
- Clear statement that this readiness slice does not authorize production.

## 7. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Static/output checks:

```bash
rg -n "schwgw\\.numerics\\.experimental|solve_q018_rescaled_oracle" src/schwgw/io src/schwgw/viz src/schwgw/cli.py src/schwgw/scattering || true
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' \) -print
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 2 -type f -print 2>/dev/null || true
find runs/phase5/q018_r60_k2_angular_range_schema_smoke -maxdepth 2 -type f -print
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts;
- no production first-pass NPZ exists;
- only the small range-schema smoke NPZ exists in the range-smoke output directory.

## 8. Decision Labels

Use exactly one:

- **GREEN / READY FOR T7ar READINESS REVIEW**:
  angular range schema works and is backward compatible; smoke result is saved and scoped; production config draft and
  readiness doc exist; tests pass; no forbidden production artifacts/imports/scope changes occurred.
- **YELLOW / READINESS INCOMPLETE**:
  schema works but production config/readiness doc is incomplete, smoke convergence fails, runtime is too high, or
  metadata needs review.
- **REJECT RED**:
  production config was run, full production artifacts/plots/fixtures/R60_K4/`kM=4` were generated, default configs
  broke, public layers directly import the experimental oracle, tests fail broadly, or conventions/thresholds/`lmax`
  policy changed.

## 9. status.md Update

Update `status.md` with:

- changed/generated files;
- files read;
- plugin/skill check;
- schema behavior;
- smoke command/runtime and artifact summary;
- production config path and explicit "not run" record;
- readiness-doc summary;
- static/output search results;
- commands and test results;
- decision label;
- open issues;
- exact next action:

```text
你现在是 T7ar。请读取并严格执行 docs/prompts/phase5_t7ar_r60_k2_angular_range_readiness_review.md。
```

Do not authorize full R60_K2 production from T8w.
