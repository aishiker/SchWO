# Phase 5 T7am Prompt: Review Q018 Production-Integration Design

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7am`。

只在 T4r 完成后运行。你的任务是独立复核 T4r 的 Q018 production-integration
policy design。重点是确认它是否仍保持 default production fail-closed，并且是否给
未来 implementation/review/T8 gate 提供了足够清楚的边界。不要把 design 通过解读为
T8 R60_K2 readiness。

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
10. `docs/prompts/phase5_t4r_q018_production_integration_design.md`
11. `src/schwgw/numerics/radial_solver.py`
12. `src/schwgw/numerics/boundary_conditions.py`
13. `src/schwgw/numerics/experimental/q018_rescaled_oracle.py`
14. `tests/physics/test_q018_rescaled_oracle.py`
15. T4r changed test files

按项目规则先检查已安装 plugin/skill。使用 systematic debugging 和
verification-before-completion；必要时使用文献/数值方法相关 skill，但不要上传私有文件。

## 2. Review Scope

确认：

- default `solve_radial_mode(... required_eval_radius=60)` remains fail-closed;
- no experimental oracle is silently wired into production;
- `schwgw.numerics` public package does not export the experimental oracle;
- no R60_K2/R60_K4 wave-field artifacts, benchmark artifacts, fixtures, or plots were generated;
- no `kM=4` run or claim was introduced;
- no frozen convention, `lmax`, partial-wave truncation policy, residual/convergence threshold, or Q018 fail-closed guard was weakened;
- any new opt-in placeholder is explicit, inert, documented, and tested as design-only.

## 3. Required Checks

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1 PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/physics/test_q018_rescaled_oracle.py
```

Run any new T4r design-boundary tests explicitly.

Independently probe:

- 8-mode production `required_eval_radius=60` matrix still raises structured
  `evanescent_tail_required_radius_uncovered`;
- if an opt-in placeholder exists, it fails clearly as design-only;
- no public export of experimental oracle from `schwgw.numerics`.

## 4. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR PRODUCTION-INTEGRATION DESIGN**:
  design is clear, tests lock default fail-closed behavior, opt-in policy is
  explicit, full pytest passes, and no production wiring/artifacts were added.
  This allows a future T4 implementation slice behind the reviewed opt-in, but
  does not authorize T8 R60_K2 production.
- **ACCEPT YELLOW**:
  design improved documentation/tests, but integration policy, metadata schema,
  or future T8 gate remains ambiguous.
- **REJECT RED**:
  default production became GREEN, experimental oracle was silently wired into
  production, tests fail, artifacts/plots were generated, or conventions /
  thresholds / `lmax` policy changed.

## 5. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- independent test results;
- independent fail-closed/opt-in/public-export checks;
- decision label;
- open issues;
- exact next action prompt recommendation.

Do not authorize T8 R60_K2 production from this review.
