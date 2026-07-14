# Phase 4 T7w Prompt: M4-Production Readiness Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7w`。

## 0. 前置条件

Only start after T8m has updated `status.md` and created
`docs/m4_production_plan.md`. If T8m stopped or did not create the plan, record
the blocker and do not pass the slice.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/phase4_closeout.md`
4. `docs/m4_production_plan.md`
5. `docs/architecture.md`
6. `docs/numerics.md`
7. `docs/validation_plan.md`
8. `docs/prompts/phase4_t8m_m4_production_readiness_pilot.md`
9. T8m changed files and artifact paths listed in `status.md`

Before task actions, check installed plugins/connectors/skills. Use directly
relevant ones only and record them in `status.md`.

## 2. Review Goals

Independently assess whether the project is ready to open a full
M4-production high-resolution map run.

Check:

- M4-lite, M4-production, and M5 transmission remain clearly separated.
- No frozen physics convention, T2-T6 formula, Route B bridge, threshold, or
  accepted `lmax` policy was changed.
- Production sampling recommendations are physically and visually justified.
- Runtime/file-size/cache estimates are plausible and grounded in accepted
  artifact metadata.
- Q018 `valid_until_r` implications are handled for same-domain denser grids
  and future larger domains.
- If a pilot artifact exists, it passes metadata/finiteness/convergence checks.
- Plotting remains read-only.

## 3. Required Verification

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Run an independent static scan of `src/schwgw/viz` for solver/physics imports.
If T8m produced pilot artifacts, run independent metadata inspection over them.

## 4. Pass Conditions

Pass only if:

- `docs/m4_production_plan.md` is clear and consistent with
  `docs/phase4_closeout.md`;
- no scope creep into M5 transmission or `kM=4` stress occurred;
- no hidden threshold/lmax/convention changes occurred;
- production readiness conclusion is actionable;
- tests pass.

## 5. Stop Conditions

Stop and update `status.md` if the plan is missing, estimates are not grounded
in saved metadata, scope boundaries are blurred, tests fail, or plotting imports
solver/physics code.

## 6. status.md Update Requirements

Record changed files, commands, test results, review findings, open issues, and
one next-action recommendation:

1. full M4-production high-resolution Fig.3 run may be opened;
2. first implement config/range or output-layout hardening;
3. do not proceed; blocker is ...
