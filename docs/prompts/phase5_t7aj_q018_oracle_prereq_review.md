# Phase 5 T7aj Prompt: Review Q018 Rescaled Oracle Prerequisites

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7aj`。

只在 T4o 完成后运行。你的任务是独立复核 T4o 是否正确建立了 Q018
rescaled/high-precision oracle 的测试边界和可选依赖边界。不要把它解读为
R60_K2 production readiness。

## 1. 必读文件

开始前先读：

1. `project.md`
2. `status.md`
3. `pyproject.toml`
4. `docs/numerics.md`
5. `docs/validation_plan.md`
6. `docs/q018_rescaled_radial_architecture_spike.md`
7. `references/notes/q018_spin2_tail_bound.md`
8. `docs/prompts/phase5_t4o_q018_rescaled_oracle_prereqs.md`
9. files changed by T4o

按项目规则先检查已安装 plugin/skill。使用 verification/systematic debugging
相关 skill（如可用）并记录。

## 2. Review Scope

确认：

- no production `solve_radial_mode(...)` default path change;
- no R60_K2 wave-field artifact;
- no plot;
- no `kM=4` run or claim;
- no frozen convention change;
- no `lmax` or threshold relaxation;
- any optional high-precision dependency is optional, not default/global;
- opt-in RED test is documented and does not break default full pytest.

## 3. Required Checks

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run the explicit opt-in oracle test command documented by T4o. Confirm whether
it fails for the expected reason (`NotImplementedError` or equivalent) or
passes if T4o implemented a valid prototype.

Inspect the experimental API contract and ensure it records:

- sector, ell, k, required radius, boundary settings;
- complex `psi`, `dpsi_dr`, `A_in`, `A_out`;
- diagnostics sufficient for future review;
- explicit experimental/non-production status.

## 4. Decision Labels

Use exactly one:

- **ACCEPT GREEN FOR PREREQUISITES**:
  default tests pass, opt-in RED/prototype test behavior is documented, and
  production remains untouched. This allows a future T4 implementation slice,
  but not T8 R60 production.
- **ACCEPT YELLOW**:
  documentation or test boundary improved, but prerequisites are incomplete.
- **REJECT RED**:
  default tests fail, production path was changed, artifacts were generated,
  optional dependency is not isolated, or claims exceed evidence.

## 5. status.md Update

Update `status.md` with:

- changed files;
- files read;
- skill/plugin check;
- independent test results;
- opt-in RED/prototype result;
- decision label;
- open issues;
- exact next action prompt recommendation.
