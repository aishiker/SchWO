# Phase 5 T7ar Prompt: Review R60_K2 Angular-Range Readiness

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ar`。

只在 T8w 完成后运行。你的任务是独立复核 T8w 的 angular-range schema、small range-schema smoke、production
config draft 和 readiness document。不要运行 full R60 production，不要生成 plots，不要生成 fixtures。

本 review 通过也只允许 T0 考虑一个单独的 production-run slice；它本身不授权 full R60 production。

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
9. `docs/q018_r60_k2_angular_production_readiness.md`
10. `docs/prompts/phase5_t8w_r60_k2_angular_range_readiness.md`
11. `configs/r60_k2_q018_angular_range_schema_smoke.yaml`
12. `configs/r60_k2_q018_angular_production_first_pass.yaml`
13. `src/schwgw/io/config.py`
14. `src/schwgw/io/results.py`
15. `src/schwgw/cli.py`
16. `tests/unit/test_io_config.py`
17. `tests/regression/test_io_cli.py`
18. T8w changed/generated files listed in `status.md`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion。不要上传私有文件；本 review 不需要外部文献检索，除非发现新的 physics
convention 冲突。

## 2. Review Scope

独立确认：

- angular observer explicit `theta_values/phi_values` configs remain backward compatible;
- angular `theta_range/phi_range` configs expand deterministically;
- invalid combinations and invalid ranges fail with clear errors;
- convergence config range support, if added, behaves explicitly and does not silently change old behavior;
- the small range-schema smoke result exists and is bounded;
- production config draft exists but was not run;
- readiness doc records runtime/storage estimates, radial cache expectations, and acceptance gates;
- no source physics formula, radial solver, plotting code, convention, threshold, Q018 policy, or `lmax` policy changed;
- no full R60 production NPZ, plot, fixture, R60_K4, `kM=4`, larger-domain, or arbitrary-direction artifact was generated.

## 3. Required Artifact And Config Checks

Load the small smoke result:

```text
runs/phase5/q018_r60_k2_angular_range_schema_smoke/r60_k2_q018_angular_range_schema_smoke.npz
```

Inspect:

- case id matches the smoke config;
- grid kind is `angular`;
- expanded `theta` / `phi` shapes match the smoke config;
- `h_plus/h_cross` shapes match expanded grid shape;
- all saved valid `h_plus/h_cross` values are finite complex numbers;
- Q018 opt-in boundary fields are present in metadata;
- lmax convergence metadata is present;
- radial warning/provenance metadata is JSON-safe when present.

Inspect the production config draft:

- `case_id == "R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS"`;
- output path is under `runs/phase5/q018_r60_k2_angular_production_first_pass/`;
- `theta_range` expands to `65` values;
- `phi_range` expands to `64` values and excludes duplicate `2pi`;
- `lmax=180`;
- boundary opt-in fields match the reviewed R60_K2 envelope;
- convergence probe policy is explicit and documented.

Confirm no production output exists:

```bash
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 2 -type f -print 2>/dev/null || true
```

Expected: no files.

## 4. Independent Consistency Probes

Run targeted config parser tests or a short local parser script to verify:

- explicit old angular config loads unchanged;
- range smoke config expands to expected arrays;
- production config draft expands to `65 x 64`;
- `phi_range endpoint=false` does not include `2pi`;
- providing both explicit values and range for the same angular coordinate raises.

Do not run the production config.

## 5. Validation Commands

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
find runs/phase5/q018_r60_k2_angular_production_first_pass -maxdepth 2 -type f -print 2>/dev/null || true
find runs/phase5/q018_r60_k2_angular_range_schema_smoke -maxdepth 2 -type f -print
```

Expected:

- no direct experimental import in T8/viz/scattering/CLI public layers;
- no R60_K4 or `kM=4` artifacts;
- no production first-pass files;
- only the bounded range-schema smoke files under the smoke output directory.

## 6. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR R60_K2 ANGULAR PRODUCTION READINESS**:
  angular range schema is correct/backward compatible; smoke artifact is scoped and inspectable; production config draft
  and readiness doc are auditable; tests pass; no forbidden artifacts/imports/scope changes occurred. This allows T0 to
  consider a separate production-run prompt, but does not itself authorize production.
- **ACCEPT YELLOW / READINESS DIAGNOSTIC ONLY**:
  partial readiness exists but schema, doc, smoke metadata, or runtime evidence needs tightening before a production-run
  prompt can be written.
- **REJECT RED**:
  production config was run, full production artifacts/plots/fixtures/R60_K4/`kM=4` were generated, default configs
  broke, public layers import experimental oracle directly, tests fail, conventions/thresholds/`lmax` policy changed,
  or saved metadata is not auditable.

## 7. status.md Update

Update `status.md` with:

- changed/generated files;
- files read;
- plugin/skill check;
- config/schema inspection table;
- smoke artifact inspection;
- production config not-run verification;
- readiness-doc review;
- static/output search results;
- commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

Do not authorize full R60_K2 production from T7ar.
