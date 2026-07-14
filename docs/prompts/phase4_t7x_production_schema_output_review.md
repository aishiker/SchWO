# Phase 4 T7x Prompt: Production Schema and Output Hardening Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7x`。

## 0. 前置条件

Only start after T8n has updated `status.md`. If T8n stopped or did not finish
the hardening slice, record the blocker and do not pass.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/phase4_closeout.md`
4. `docs/m4_production_plan.md`
5. `docs/architecture.md`
6. `docs/validation_plan.md`
7. `docs/prompts/phase4_t8n_production_schema_output_hardening.md`
8. T8n changed files and smoke artifact paths listed in `status.md`

Before task actions, check installed plugins/connectors/skills. Use directly
relevant ones only and record them in `status.md`.

## 2. Review Goals

Independently verify:

- range-based x-z config works and preserves explicit-array backward
  compatibility;
- saved results still contain expanded explicit coordinates;
- invalid/ambiguous range configs fail clearly;
- Fig.3 single-panel sidecars include final-pair convergence metadata;
- Fig.3 plotting can request and record `dpi >= 300`;
- plotting remains read-only over saved results;
- no frozen physics convention, T2-T6 formula, radial solver behavior,
  threshold, or accepted `lmax` policy changed.

## 3. Required Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_config.py tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run static scan:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

If T8n produced a smoke artifact, independently inspect its result and sidecar.

## 4. Pass Conditions

Pass only if:

- T8n changes satisfy all review goals;
- tests pass;
- no scope creep into full production, `kM=4`, R60_K2/R60_K4, or M5 occurred;
- the next full M4-production run can use range-based config and production
  sidecar metadata without hand-written 121-value arrays.

## 5. Stop Conditions

Stop and update `status.md` if config parsing is ambiguous, explicit-array
configs regress, sidecar metadata remains incomplete, plotting imports solver
or physics modules, tests fail, or any physics/convention code was changed.

## 6. status.md Update Requirements

Record changed files, commands, review findings, test results, open issues, and
one next-action recommendation:

1. open full M4-production first-pass run;
2. return to T8n with exact blocker;
3. defer production and open another hardening slice.
