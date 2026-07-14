# Phase 5 T7ab Prompt: M5 API and Saved-Schema Review

你现在是 `T7：验证与基准` 线程，slice 名称为 `T7ab`。

## 0. 任务定位

T6m 应实现 M5 pointwise amplification core API，T8p 应实现 saved-output
schema and CLI smoke path。你的任务是独立复核这两步，不生成 production
artifacts，不画 transmission 图。

This is the review gate before any M5 plotting or benchmark runs.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/m5_transmission_normalization.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/validation_plan.md`
7. `docs/phase4_production_closeout.md`
8. `docs/prompts/phase5_t6m_m5_amplification_api.md`
9. `docs/prompts/phase5_t8p_m5_saved_output_schema.md`
10. T6m/T8p changed files listed in `status.md`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Review Checklist

Verify:

1. Q005 convention is implemented as pointwise wave-optics amplification, not
   radial horizon transmission/absorption.
2. `F_plus_complex/F_cross_complex` are complex ratios and are not silently
   replaced by magnitudes.
3. `F_pol_norm/I_pol_ratio` follow the M5a definitions.
4. Component denominator masks are independent.
5. Invalid ratios are NaN, not zero/one/clipped values.
6. Metadata includes baseline API, Fourier convention, Route B bridge,
   denominator thresholds, mask names, and radial-transmission exclusion.
7. The flat/no-lens denominator does not call `solve_radial_mode`, tiny-`M`,
   Schwarzschild horizon boundary, or `A_in/A_out` matching.
8. Saved NPZ/HDF5 schema preserves arrays, masks, NaNs, metadata, and remains
   backward compatible with existing wave-field outputs.
9. CLI smoke does not run expensive production grids.
10. `src/schwgw/viz` remains read-only and does not recompute ratios or solver
    physics.

## 3. Verification Commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "solve_radial_mode|tiny_M|tiny-M|A_in|A_out|radial_horizon_transmission|radial_absorption" src/schwgw/scattering/transmission.py src/schwgw/io src/schwgw/cli.py tests || true
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification" src/schwgw/viz || true
```

Also run a tiny independent NPZ metadata inspection on the T8p smoke artifact
if T8p created one under `/tmp`. Do not create a new production artifact.

## 4. Pass Conditions

Pass only if:

- all review checklist items pass;
- targeted tests and full pytest pass;
- no convention drift or hidden radial baseline dependency is found;
- `status.md` records changed files, commands, test results, open issues, and
  next action.

If passed, recommend the next slice as:

```text
T8q M5 read-only plotting smoke, then T7ac plotting review.
```

## 5. Stop Conditions

Stop and update `status.md` if:

- M5 implementation mixes pointwise amplification with radial absorption;
- denominator masks/NaN policy is wrong;
- saved schema breaks existing wave-field output;
- plotting recomputes solver or ratio physics;
- tests fail.
