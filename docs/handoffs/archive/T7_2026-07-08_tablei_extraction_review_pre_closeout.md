# T7 Archive: Table-I Extraction Review Pre-Closeout

Archived: 2026-07-08

Thread: T7, validation and benchmark review.

Reason for archive: T7bb is a major closeout boundary. This file preserves the T7ba current-handoff state before `docs/handoffs/T7_current.md` was advanced to the T7bb closeout state.

## Current Status At Archive Time

T7ba independently reviewed the T8ac read-only Fig.5/Fig.6 Table-I four-frequency extraction artifact.

Decision:

```text
ACCEPT GREEN FOR FIG.5/FIG.6 TABLE-I FOUR-FREQUENCY EXTRACTION ONLY
```

This acceptance was narrow. It covered only the read-only four-frequency Table-I extraction pilot from the accepted M5 archive.

## Completed Work

- Read the new project handoff rule in `project.md` and `docs/handoffs/README.md`.
- Confirmed T7 must maintain `docs/handoffs/T7_current.md`.
- Reviewed T8ac implementation and artifacts:
  - `src/schwgw/io/tablei.py`
  - `src/schwgw/io/__init__.py`
  - `src/schwgw/cli.py`
  - `tests/unit/test_tablei_extraction.py`
  - `tests/regression/test_io_cli.py`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz`
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json`
- Verified the output directory contains exactly the authorized NPZ and JSON sidecar.
- Verified source M5 SHA-256 values match the accepted M5 archive.
- Independently compared all extracted `F_plus_complex` and `F_cross_complex` values against the four source NPZs at `[z_index, x_index]`.
- Verified point metadata, `x_indices`, `z_indices`, `r/theta/phi`, paper `theta_deg`, and paper `xi_over_xi0` against T10f.
- Verified masks, phases, unwrapped diagnostic phases, and sidecar scope flags.
- Ran targeted and full pytest.
- Updated `status.md`.
- Created `docs/handoffs/T7_current.md`.

## Accepted Artifact Hashes

```text
69b2e449ba24bdc17fb6f85f0450d38daae6ce16f551381f19b13717c836ad2d  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz
8a64c50ae96f75dc9a9ed4db2191098fe6d92418e4877b8752f87c7ca434f3f8  runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

## Extraction Facts

- Frequencies: `[0.5, 1.0, 1.5, 2.0]`.
- Output shape: `(4, 8)` for both complex ratio arrays.
- Point IDs:
  - `near_axis_x0_z30`
  - `near_axis_x1_z30`
  - `near_axis_x2_z30`
  - `near_axis_x3_z30`
  - `far_axis_x10_z30`
  - `far_axis_x15_z30`
  - `far_axis_x20_z30`
  - `far_axis_x25_z30`
- Selected indices:
  - `x_indices=[60,62,64,66,80,90,100,110]`
  - `z_indices=[120,120,120,120,120,120,120,120]`
- Source Q018 warning counts: `[0,0,0,56]`.
- Source Q018 warning codes: `[[],[],[],["evanescent_tail_suppressed"]]`.
- All selected plus/cross/norm/source masks were true in the accepted artifact.

## Commands Run

```bash
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly -maxdepth 1 -type f -print | sort
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz src/schwgw/io src/schwgw/cli.py || true
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly -maxdepth 2 -type f \( -iname '*.png' -o -iname '*.pdf' -o -iname '*.h5' -o -iname '*.hdf5' -o -iname '*k4*' -o -iname '*R60*K4*' \) -print | sort
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_tablei_extraction.py tests/regression/test_io_cli.py::test_cli_extract_tablei_four_frequency_writes_npz_and_sidecar
rg -n "compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/io/tablei.py || true
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

Results:

- Output listing: exactly the NPZ and JSON sidecar.
- Artifact hashes: matched the two accepted hashes above.
- Static search: no forbidden calls in `src/schwgw/io/tablei.py`; broader hits were existing non-Table-I runner/amplification/export paths.
- Forbidden-output search in the Table-I output directory: no output.
- Independent Python source/extraction comparison: `CHECK_RESULT ok`.
- Targeted tests: `5 passed in 0.34s`.
- Full tests: `376 passed, 117 skipped, 1 xfailed, 75 subtests passed in 97.17s`.

## Incomplete Work At Archive Time

- No closeout document had been written for the Table-I extraction pilot.
- No plotting/reporting-planning slice had been scheduled.

## Blocking Issues

None for the accepted four-frequency read-only Table-I extraction pilot.

## Non-Blocking Warnings

- Four-frequency phase unwrapping was diagnostic only and too sparse for paper-level phase curves.
- The artifact did not include dense `Mk` scan coverage.
- The artifact did not include `kM=4`.
- The artifact did not include a Kirchhoff baseline.

## Must-Read Files For Next T7 At Archive Time

1. `status.md`
2. `docs/handoffs/T7_current.md`
3. `docs/handoffs/T0_current.md`
4. `docs/handoffs/T8_current.md`
5. `references/notes/t10f_fig5_fig6_tablei_extraction_plan.md`
6. `docs/phase5_m5_four_frequency_closeout.md`
7. `docs/phase5_fig4_exact_angular_closeout.md`
8. `project.md`

## Frozen Decisions

- Fourier convention remains `exp(-i k t)`.
- Route B packaged polarization remains the production path.
- M5 complex ratios `F_plus_complex` and `F_cross_complex` are authoritative.
- M5 quantity is pointwise wave-optics amplification, not radial horizon transmission or absorption.
- Invalid ratio policy remains masks/NaN; no filling, clipping, smoothing, flooring, regularization, or interpolation.
- Table-I extraction indexes source arrays as `[z_index, x_index]`.
- The four-frequency extraction is not paper-level Fig.5/Fig.6 reproduction.

## Forbidden Actions

- Do not run `schwgw run` for this artifact.
- Do not rerun or recompute solver fields.
- Do not recompute flat/no-lens baselines or pointwise amplification for this artifact.
- Do not interpolate Table-I points.
- Do not generate dense scans, `kM=4`, R60_K4, Kirchhoff baseline, Appendix D/E curves, strict `Psi4`, arbitrary incident-direction outputs, fixtures, or plots unless T0 opens a separate gated slice.
- Do not label this pilot as paper-level Fig.5/Fig.6 reproduction.

## Exact Next Task At Archive Time

T0 could close out the four-frequency Table-I extraction pilot or schedule a separate read-only plotting/reporting-planning slice.

Recommended T0 boundary:

```text
T0 may close out the four-frequency Table-I extraction pilot or schedule a separate read-only plotting/reporting-planning slice. Do not schedule dense Mk scan, kM=4, Kirchhoff baseline, or paper-level Fig.5/Fig.6 reproduction without a new gate.
```
