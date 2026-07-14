# Phase 5 T7an Prompt: Review Q018 Opt-In Production Oracle Implementation

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7an`。

只在 T4s 完成后运行。你的任务是独立复核 T4s 是否正确实现了 Q018 reviewed
opt-in production oracle adapter。复核通过最多只授权一个后续 T8 selected-probe / smoke 级
R60_K2 pilot；不得直接授权 full R60 production、R60_K4、`kM=4`、larger-domain run 或任意入射方向。

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
10. `docs/prompts/phase5_t4s_q018_reviewed_optin_production_oracle.md`
11. `docs/prompts/phase5_t7am_q018_production_integration_design_review.md`
12. `src/schwgw/numerics/radial_solver.py`
13. `src/schwgw/numerics/boundary_conditions.py`
14. `src/schwgw/numerics/__init__.py`
15. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
16. `src/schwgw/scattering/partial_wave.py`
17. `tests/physics/test_q018_production_integration_design.py`
18. `tests/physics/test_q018_rescaled_oracle.py`
19. T4s changed files listed in `status.md`

按项目规则，先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion；如需文献核对，优先使用本地 `references/notes/`，不要上传私有文件。

## 2. Review Scope

独立确认：

- default `solve_radial_mode(..., required_eval_radius=60, experimental_required_radius_oracle=None)`
  仍对 Q018 8-mode matrix fail closed；
- explicit opt-in
  `BoundaryConfig(required_eval_radius=60.0, experimental_required_radius_oracle="q018_riccati")`
  对 T4q/T7al 8-mode matrix 返回正常 `RadialSolution`；
- opt-in result 在 `r=60` 的 `psi` 和 `dpsi_dr` finite；
- `A_in` 仍是 outer `exp(-i k r_star)` incoming coefficient，且 unit-incoming normalization 未被破坏；
- production result 与 experimental oracle 在 `psi(60)`、`dpsi_dr(60)`、`A_in`、`A_out` 和 residual proxies
  上一致到 T4q/T7al 接受的 tolerance scale；
- out-of-envelope opt-in fails closed with structured no-go；
- unknown opt-in name raises `ValueError`；
- `schwgw.numerics` public package does not export `solve_q018_rescaled_oracle`；
- `partial_wave.py`、T6、T8、plotting 代码没有直接 import `schwgw.numerics.experimental`；
- no R60_K2/R60_K4 wave-field artifact, benchmark artifact, fixture, plot, or `kM=4` output was generated；
- no frozen convention, threshold, residual policy, suppression policy, or `lmax` policy was weakened。

## 3. Required Independent Probes

Run a small script or targeted tests to inspect all 8 reviewed modes:

```text
M=1, k=2.0, required_eval_radius=60.0, r_out=300.0,
ell=[153,156,168,180], sector=[odd,even],
r_in_eps=1e-6, rtol=1e-10, atol=1e-12
```

For each mode record:

- solver/method branch;
- `A_in`, `A_out`;
- finite `psi(60)`, finite `dpsi_dr(60)`;
- oracle provenance code;
- residual proxy maxima;
- `valid_at_required_radius`;
- `unit_incoming_at_infinity`;
- runtime if available.

Run the same 8-mode matrix with default `None` and confirm fail-closed code
`evanescent_tail_required_radius_uncovered`.

Run at least three out-of-envelope opt-in probes:

- `k=4.0`
- `ell=152`
- `required_eval_radius=80.0`

All must fail closed and must not silently use `evanescent_tail_suppressed`.

## 4. Validation Commands

Run at minimum:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_production_integration_design.py
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_radial_solver.py tests/unit/test_radial_solver.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Also search for forbidden outputs/imports:

```bash
rg -n "solve_q018_rescaled_oracle|schwgw\\.numerics\\.experimental" src tests docs
find runs configs tests/regression/fixtures -maxdepth 5 -iname '*R60*K2*' -o -iname '*R60*K4*' -o -iname '*k4*'
```

Use the search results carefully: expected references in prompt/docs/tests/experimental modules are okay;
public exports, partial-wave/T6/T8 direct imports, or new artifacts are not okay.

## 5. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR REVIEWED OPT-IN PRODUCTION ORACLE**:
  all 8 opt-in modes return normal `RadialSolution`, default path remains fail-closed, out-of-envelope is
  fail-closed, metadata/provenance is adequate, public API boundary is preserved, and targeted/full tests pass.
  This allows T0 to schedule a bounded T8 R60_K2 selected-probe or smoke artifact only, followed by another T7
  review. It does not authorize full R60 production, R60_K4, `kM=4`, larger domains, or arbitrary incident direction.
- **ACCEPT YELLOW**:
  implementation is directionally useful but only partial, too slow, under-metadataed, or not yet adequate for even
  a T8 smoke artifact.
- **REJECT RED**:
  default production path changed, experimental oracle leaked into public API, out-of-envelope silently passes,
  tests fail, artifacts/plots were generated, or conventions/thresholds/`lmax` policy changed.

## 6. status.md Update

Update `status.md` with:

- changed files;
- files read;
- plugin/skill check;
- independent 8-mode opt-in table;
- default fail-closed table;
- out-of-envelope probe results;
- public-export/import/artifact search results;
- commands and test results;
- decision label;
- open issues;
- exact next action recommendation.

Do not authorize full T8 R60_K2 production from T7an.
