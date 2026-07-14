# Phase 5 T8q Prompt: M5 Read-Only Plotting Smoke

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8q`。

## 0. 任务定位

T6m 已实现 M5 pointwise amplification core API，T8p 已实现 M5 saved-output
schema 和 `compute-amplification` CLI smoke，T7ab 已独立复核通过。

你的任务是给已经保存的 M5 amplification result 增加只读绘图 smoke。绘图层只能
读取保存好的 ratio/scalar fields 和 masks；不得重新运行求解器、不得重新计算
unlensed baseline、不得重新计算 M5 ratio。

This is a plotting-boundary slice, not a physics or production-benchmark slice.

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
10. `docs/prompts/phase5_t7ab_m5_api_schema_review.md`
11. T6m/T8p/T7ab changed files listed in `status.md`
12. `src/schwgw/io/results.py`
13. `src/schwgw/viz/results.py`
14. `src/schwgw/cli.py`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Implementation Scope

Likely files:

```text
src/schwgw/viz/results.py
src/schwgw/viz/__init__.py
src/schwgw/cli.py
tests/unit/test_viz_results.py
tests/regression/test_plot_cli.py
status.md
```

If `src/schwgw/viz/results.py` would become too broad, create a focused module
such as `src/schwgw/viz/transmission.py`.  Keep the public names explicit:
prefer `plot_amplification_*` or `plot_pointwise_amplification_*`; do not use
ambiguous bare `plot_transmission`.

Add tests first.

## 3. Required Capability

Add read-only plotting for saved `AmplificationGridResult` files produced by
T8p.  The plotting entry point should accept a saved amplification result path,
an output path, and a quantity name.

Required quantity support:

```text
F_pol_norm
I_pol_ratio
amplification_plus
amplification_cross
```

Optional quantity support, if it stays small and unambiguous:

```text
abs_F_plus
abs_F_cross
phase_plus
phase_cross
intensity_plus_ratio
intensity_cross_ratio
```

Mask policy:

- `F_pol_norm` and `I_pol_ratio` must use `valid_ratio_norm_mask`.
- plus-component quantities must use `valid_ratio_plus_mask`.
- cross-component quantities must use `valid_ratio_cross_mask`.
- invalid values must remain masked/NaN in the plot data; do not replace them
  by zero, one, clipped values, or denominator floors.

Metadata sidecar:

For every plot, write a JSON sidecar next to the image.  It must include:

```text
plot_type = "pointwise_wave_optics_amplification"
quantity
mask_field
source_amplification_result_path
source_case / source_result metadata if available
normalization metadata
baseline metadata
grid_kind
shape
valid_count
invalid_count
output_path
requested_dpi
```

If the result is an x-z grid and saved coordinate metadata are available, record
the plotted coordinate ranges.  Do not invent missing physics metadata.

Add a CLI command, suggested:

```text
schwgw plot-amplification AMPLIFICATION_RESULT --quantity F_pol_norm --out OUT.png
```

The CLI must read the saved result via `load_amplification_results(...)` or an
equivalent IO-layer reader.  It must not call:

```text
compute_pointwise_amplification
flat_no_lens_baseline_at_point
compute_polarization
run_solver_grid
solve_radial_mode
```

## 4. Required Tests

Add or update tests covering:

1. A synthetic saved amplification result can be plotted to PNG with JSON
   sidecar.
2. Sidecar records `plot_type`, `quantity`, `mask_field`, valid/invalid counts,
   normalization metadata, and source path.
3. Norm quantities use `valid_ratio_norm_mask`; plus/cross quantities use their
   component masks.
4. Invalid ratios remain NaN/masked and are not silently replaced.
5. CLI smoke writes PNG plus sidecar from a synthetic saved amplification
   result.
6. Unsupported quantity fails with a clear error.
7. Existing wave-field plotting tests still pass.
8. Static read-only boundary: `src/schwgw/viz` must not import or call solver,
   radial, angular, perturbation, scattering, baseline, or ratio-computation
   paths.

Suggested static guard:

```bash
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz
```

The expected result is no matches, except harmless comments or test strings if
they are clearly not executable code.

## 5. Hard Limits

- Do not generate production or benchmark M5 artifacts.
- Do not use accepted M4 production artifacts as new accepted M5 artifacts in
  this slice.
- Do not implement `kM=4`, R60_K2/R60_K4, or arbitrary incident direction.
- Do not alter T6m formulas, T8p saved schema semantics, Q005 convention,
  Q014/Route B bridge, T4 radial solver, thresholds, `lmax`, or accepted M4
  artifact metadata.
- Do not add plotting code that recomputes physics.
- Do not accept artifacts that exist only in `/tmp`; pytest temp files for
  smoke tests are fine.

## 6. Verification Commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_io_results.py tests/regression/test_io_cli.py tests/unit/test_transmission.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
```

## 7. Stop Conditions

Stop and update `status.md` if:

- saved amplification results cannot be plotted without recomputing ratios;
- the plotting layer needs solver/scattering/baseline imports;
- mask handling is ambiguous or invalid ratios would be replaced by finite
  defaults;
- CLI smoke requires a production run;
- full pytest fails.

## 8. Handoff

If passed, update `status.md` with changed files, commands, test results, open
issues, and next action.  Recommend:

```text
T7ac should independently review T8q M5 read-only plotting before any M5 production artifact is generated.
```
