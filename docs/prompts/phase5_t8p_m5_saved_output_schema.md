# Phase 5 T8p Prompt: M5 Saved-Output Schema and CLI Smoke

你现在是 `T8：可视化与 CLI` 线程，slice 名称为 `T8p`。

## 0. 任务定位

T6m 应已实现 M5 pointwise amplification core API。你的任务是把该 API 接入
saved-result schema 和 CLI 的轻量 smoke path，使 M5 ratio fields 可以保存、
读取和归档。不要做正式 benchmark、不要画 transmission 图。

This is an IO/schema slice, not a physics-convention slice.

## 1. 必读文件

1. `project.md`
2. `status.md`
3. `docs/m5_transmission_normalization.md`
4. `docs/physics_spec.md`
5. `docs/equation_map.md`
6. `docs/validation_plan.md`
7. `docs/phase4_production_closeout.md`
8. T6m changed files listed in `status.md`
9. `src/schwgw/scattering/transmission.py`
10. `src/schwgw/io/results.py`
11. `src/schwgw/cli.py`

Before task actions, check whether installed plugins/connectors/skills are
directly useful. Use only directly relevant ones and record any used skill in
`status.md`.

## 2. Implementation Scope

Likely files:

```text
src/schwgw/io/results.py
src/schwgw/cli.py
tests/unit/test_io_results.py
tests/regression/test_io_cli.py
```

Add new tests first.  Keep changes minimal and compatible with existing
`GridResult` wave-field saves.

## 3. Required Capability

Implement saved M5 amplification output that can carry:

```text
F_plus_complex
F_cross_complex
amplification_plus
amplification_cross
intensity_plus_ratio
intensity_cross_ratio
F_pol_norm
I_pol_ratio
valid_ratio_plus_mask
valid_ratio_cross_mask
valid_ratio_norm_mask
normalization metadata
```

Do this by either:

1. extending `GridResult` in a backward-compatible way with optional M5 arrays;
   or
2. adding a focused `AmplificationGridResult` plus `save/load` functions.

Choose the smaller change that fits current `src/schwgw/io/results.py`
patterns. Existing readers and plots for wave-field results must keep working.

Add a CLI smoke command, suggested:

```text
schwgw compute-amplification LENSED_RESULT --out OUT.npz
```

The command should:

- read an existing saved lensed result;
- compute the flat/no-lens baseline at each valid saved observer point using
  the T6m flat baseline helper or equivalent T6m API;
- compute M5 amplification fields with the T6m core API;
- save the amplification result as NPZ/HDF5;
- record source result path, baseline API, normalization metadata, masks, and
  source command.

For x-z grids, use saved `r/theta/phi/valid_mask`.  For angular grids, use
saved `theta/phi` plus observer radius from metadata.

## 4. Required Tests

Add tests for:

1. NPZ round trip preserves all complex ratio arrays, real scalar arrays,
   masks, NaNs, and normalization metadata.
2. HDF5 round trip does the same if `h5py` is available.
3. CLI smoke with a synthetic saved lensed result writes amplification output.
4. CLI smoke for pure plus input masks cross ratios while plus/norm remain
   finite.
5. CLI/source metadata records:
   - `normalization.kind="pointwise_wave_optics_amplification"`;
   - `baseline_api="compute_flat_no_lens_polarization"`;
   - no tiny-`M` baseline;
   - no Schwarzschild horizon boundary in baseline;
   - `source_lensed_result_path`;
   - mask field names.
6. Existing wave-field result tests and plotting tests still pass unchanged.
7. Static guard:
   - `src/schwgw/viz` remains free of solver/physics imports;
   - no plotting function recomputes M5 ratios.

## 5. Hard Limits

- Do not implement M5 plotting in this slice.
- Do not generate production or benchmark M5 artifacts.
- Do not alter T6m ratio formulas.
- Do not call `solve_radial_mode` for the unlensed denominator.
- Do not use tiny-`M` Schwarzschild baseline.
- Do not touch frozen physics conventions.
- Do not change accepted M4 artifacts.
- Do not add `kM=4`, R60_K2/R60_K4, or arbitrary incident direction work.

## 6. Verification Commands

Run:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/regression/test_io_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification" src/schwgw/viz || true
```

## 7. Stop Conditions

Stop and update `status.md` if:

- T6m API is missing or ambiguous;
- saved schema cannot preserve complex ratios and masks without breaking
  existing wave-field results;
- CLI needs expensive production runs for smoke tests;
- any baseline path calls radial solver or tiny-`M`;
- full pytest fails.

## 8. Handoff

If passed, update `status.md` and recommend:

```text
T7ab should independently review T6m/T8p M5 API/schema before any M5 plotting or production artifacts.
```
