# T7 Current Handoff

Last updated: 2026-07-08

Thread: T7, validation and benchmark review.

## Current Status

T7bc independently reviewed the T8ad read-only Table-I plotting/reporting pilot.

Decision:

```text
ACCEPT GREEN FOR TABLE-I FOUR-FREQUENCY READ-ONLY PLOTTING/REPORTING ONLY
```

This acceptance is narrow. It covers only CSV, Markdown, and two pilot PNG reporting artifacts generated from the accepted Table-I four-frequency extraction NPZ/JSON.

## Completed Work

- Read `docs/prompts/phase5_t7bc_tablei_plotting_reporting_review.md`.
- Re-read project handoff rules in `project.md` and `docs/handoffs/README.md`.
- Reviewed the accepted Table-I extraction closeout:
  - `docs/phase5_tablei_extraction_closeout.md`
- Reviewed T8ad handoff/status records.
- Reviewed T8ad implementation and tests:
  - `src/schwgw/viz/results.py`
  - `src/schwgw/viz/__init__.py`
  - `src/schwgw/cli.py`
  - `tests/unit/test_viz_results.py`
  - `tests/regression/test_plot_cli.py`
- Verified the reporting directory contains exactly the six expected artifacts:
  - `tablei_four_frequency_values.csv`
  - `tablei_four_frequency_values.md`
  - `fig5_near_axis_tablei_four_frequency_pilot.png`
  - `fig5_near_axis_tablei_four_frequency_pilot.png.json`
  - `fig6_far_axis_tablei_four_frequency_pilot.png`
  - `fig6_far_axis_tablei_four_frequency_pilot.png.json`
- Verified CSV numeric values against the accepted extraction NPZ arrays for all 32 `(kM, point_id)` rows.
- Verified sidecar source extraction NPZ/JSON path, size, and SHA-256.
- Verified plotted point IDs, plotted quantities, phase policy, mask policy, and no-solver/no-dense/no-Kirchhoff scope flags.
- Verified PNG dimensions, nonblank pixel variation, and visual labels.
- Re-ran focused tests and full pytest.
- Updated `status.md`.
- Updated this T7 current handoff.

## Accepted Reporting Artifact Hashes

```text
a134657d37d5a3efd4b72777fb357ae1d7eacdfe486715926032eae6e13b9d88  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png
1e5611893ff400ff7f2d9df74b57841e6979da61796e48f3256ed1b21bf31ef2  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png.json
0b5b5986a809354b739fb2c2c35fdb67a7acb26aa9c6ec2501248568e8bcf9ff  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png
e283e0ad3feab2395467482aaebb5992cec608bd3b0d731711293aa0fe2414c9  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png.json
5ec531025bb2549da41e915617e7dfd4a1e5acdee5c5eb0a32dbc0dbf841ad2f  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.csv
61c88f197f1426e0ca69d3763e8dc6d6d8a79193ee68604a0fc9ac9b67ac393a  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.md
```

## Source Extraction Hashes

```text
69b2e449ba24bdc17fb6f85f0450d38daae6ce16f551381f19b13717c836ad2d  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz
8a64c50ae96f75dc9a9ed4db2191098fe6d92418e4877b8752f87c7ca434f3f8  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

## Reporting Facts

- Frequencies: `[0.5, 1.0, 1.5, 2.0]`.
- Point count: 8.
- CSV rows: 32 data rows plus header.
- Near-axis plotted point IDs:
  - `near_axis_x0_z30`
  - `near_axis_x1_z30`
  - `near_axis_x2_z30`
  - `near_axis_x3_z30`
- Far-axis plotted point IDs:
  - `far_axis_x10_z30`
  - `far_axis_x15_z30`
  - `far_axis_x20_z30`
  - `far_axis_x25_z30`
- Plotted quantities:
  - `abs_F_plus`
  - `abs_F_cross`
  - `arg_F_plus_unwrapped`
  - `arg_F_cross_unwrapped`
- Four-frequency unwrapped phases are diagnostic only.
- Visual labels say `Four-frequency read-only pilot`.
- Markdown states the output is not a paper-level Fig.5/Fig.6 reproduction and includes no Kirchhoff comparison curves.

## Commands Run

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/*
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz src/schwgw/io src/schwgw/cli.py || true
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting -maxdepth 1 -type f \( -iname '*.h5' -o -iname '*.hdf5' -o -iname '*.npz' -o -iname '*k4*' -o -iname '*R60*K4*' -o -iname '*fixture*' \) -print | sort
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Results:

- Reporting listing: exactly the six expected files.
- Reporting hashes: matched the accepted hashes above.
- Static forbidden-call search: no hits in `src/schwgw/viz`; broader hits are existing non-reporting CLI `run`, `compute-amplification`, and IO runner/export paths.
- Forbidden-output search in the reporting directory: no output.
- Inline Python inspection: `CHECK_RESULT ok`.
- Focused tests: `58 passed in 5.46s`.
- Full tests: `380 passed, 117 skipped, 1 xfailed, 75 subtests passed in 99.23s`.

PNG inspection from the independent script:

```text
fig5_near_axis_tablei_four_frequency_pilot.png size=(2100, 1560) shape=(1560, 2100, 4) std=34.8049819438 unique_rgba=4389
fig6_far_axis_tablei_four_frequency_pilot.png size=(2100, 1560) shape=(1560, 2100, 4) std=36.4157065074 unique_rgba=2446
```

## Incomplete Work

- No closeout document has been written for the Table-I plotting/reporting pilot.
- No dense `Mk` scan plan has been scheduled.
- No Kirchhoff convention freeze has been scheduled.

## Blocking Issues

None for the accepted four-frequency read-only Table-I plotting/reporting pilot.

## Non-Blocking Warnings

- This is a sparse four-frequency pilot only.
- It is not a paper-level Fig.5/Fig.6 reproduction.
- Four-frequency phase unwrapping is diagnostic only and too sparse for paper-level phase curves.
- The artifacts do not include dense `Mk` scan coverage.
- The artifacts do not include `kM=4`.
- The artifacts do not include Kirchhoff comparison curves.

## Must-Read Files For Next T7

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/phase5_tablei_extraction_closeout.md`
6. `docs/prompts/phase5_t7bc_tablei_plotting_reporting_review.md`
7. `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json`
8. `src/schwgw/viz/results.py`
9. `tests/unit/test_viz_results.py`
10. `tests/regression/test_plot_cli.py`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Route B packaged polarization remains the production path.
- M5 complex ratios `F_plus_complex` and `F_cross_complex` remain authoritative.
- M5 quantity is pointwise wave-optics amplification, not radial horizon transmission or absorption.
- Invalid ratio policy remains masks/NaN; no filling, clipping, smoothing, flooring, regularization, or interpolation.
- Table-I extraction indexes source arrays as `[z_index, x_index]`.
- Four-frequency unwrapped phases are diagnostic only.
- The extraction and reporting pilots are not paper-level Fig.5/Fig.6 reproduction.

## Forbidden Actions

- Do not run `schwgw run` for these artifacts.
- Do not rerun solvers or recompute fields.
- Do not recompute flat/no-lens baselines or pointwise amplification for these reporting artifacts.
- Do not interpolate, smooth, fill, clip, floor, regularize, or replace invalid component ratios.
- Do not generate dense scans, `kM=4`, R60_K4, Kirchhoff baseline, Appendix D/E curves, strict `Psi4`, arbitrary incident-direction outputs, fixtures, or HDF5 files unless T0 opens a separate gated slice.
- Do not label this pilot as paper-level Fig.5/Fig.6 reproduction.

## Superseded Prompts

These prompts are complete and should not be rerun unless inconsistency is found:

- `docs/prompts/phase5_t10f_fig5_fig6_tablei_extraction_plan.md`
- `docs/prompts/phase5_t7az_fig5_fig6_tablei_plan_review.md`
- `docs/prompts/phase5_t8ac_fig5_fig6_tablei_readonly_extraction.md`
- `docs/prompts/phase5_t7ba_fig5_fig6_tablei_extraction_review.md`
- `docs/prompts/phase5_t7bb_tablei_extraction_closeout.md`
- `docs/prompts/phase5_t8ad_tablei_readonly_plotting_reporting_goal.md`
- `docs/prompts/phase5_t7bc_tablei_plotting_reporting_review.md`

Fig.4 plotting prompts must not be reused for Table-I reporting:

- `docs/prompts/phase5_t8y_fig4_exact_k2_readonly_plot.md`
- `docs/prompts/phase5_t8ab_fig4_all_frequency_readonly_plot.md`

## Exact Next Task

T0 may close out the Table-I four-frequency plotting/reporting pilot, separately schedule dense `Mk` scan planning, schedule Kirchhoff convention freeze, or pause.

Recommended T0 boundary:

```text
T0 may close out the Table-I four-frequency plotting/reporting pilot, or separately schedule dense Mk scan planning, Kirchhoff convention freeze, or pause. Do not schedule kM=4, dense scan production, Kirchhoff implementation, fixtures, or paper-level Fig.5/Fig.6 reproduction without a new gate.
```

## Allowed / Forbidden Files For Next T7 Slice

Allowed files depend on the next T0 prompt. For a T7 review-only slice, default allowed files are:

- `status.md`
- `docs/handoffs/T7_current.md`

Forbidden by default unless a new T0 prompt authorizes otherwise:

- `src/`
- `tests/`
- `configs/`
- `runs/`
- source M4/M5 artifacts
- extraction artifacts
- reporting artifacts
- plot artifacts

## Verification Commands For Future Related Review

At minimum, independently compare any reporting table values to the accepted extraction NPZ, list output files, hash artifacts, run static forbidden-call searches, inspect PNGs for nonblank dimensions, and run relevant focused tests plus full pytest if code/tests changed:

```bash
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

## Definition Of Done

- Review decision is recorded in `status.md`.
- `docs/handoffs/T7_current.md` is updated.
- Accepted artifacts have independent source-value comparison evidence.
- Commands and test results are recorded.
- Remaining gates and forbidden actions are explicit.
