# Phase 5 Table-I Reporting Pilot Closeout

Date: 2026-07-08

Final status label:

```text
CLOSED GREEN / TABLE-I REPORTING PILOT CLOSED
```

Decision label:

```text
CLOSED / ACCEPTED FOR TABLE-I FOUR-FREQUENCY READ-ONLY PLOTTING/REPORTING ONLY
```

This closeout freezes the accepted scope, artifacts, provenance, verification evidence, limitations, and remaining gates for the Fig.5/Fig.6 Table-I four-frequency read-only plotting/reporting pilot. It does not authorize solver runs, field recomputation, dense `Mk` scans, `kM=4`, R60_K4, Kirchhoff baselines, Appendix D/E curves, strict `Psi4`, arbitrary incident direction, fixtures, or paper-level Fig.5/Fig.6 reproduction.

## Accepted Scope

- Artifact class: read-only reporting from the accepted Fig.5/Fig.6 Table-I four-frequency extraction artifact.
- Frequencies: `kM=[0.5,1.0,1.5,2.0]`.
- Points: the eight Table-I points at `z/M=30`, `y/M=0`.
- Data source: only the accepted extraction NPZ/JSON under `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/`.
- Output archive: `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/`.
- Reporting artifacts: CSV, Markdown, two pilot PNGs, and two PNG JSON sidecars.
- Plotted quantities: `abs_F_plus`, `abs_F_cross`, `arg_F_plus_unwrapped`, and `arg_F_cross_unwrapped`.

The authoritative numerical quantities remain the accepted extraction arrays:

```text
F_plus_complex
F_cross_complex
```

Magnitudes and phases are derived summaries only. Four-frequency unwrapped phases are diagnostic only.

## Accepted Reporting Artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| Near-axis PNG | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png` | `a134657d37d5a3efd4b72777fb357ae1d7eacdfe486715926032eae6e13b9d88` |
| Near-axis PNG sidecar | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png.json` | `1e5611893ff400ff7f2d9df74b57841e6979da61796e48f3256ed1b21bf31ef2` |
| Far-axis PNG | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png` | `0b5b5986a809354b739fb2c2c35fdb67a7acb26aa9c6ec2501248568e8bcf9ff` |
| Far-axis PNG sidecar | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png.json` | `e283e0ad3feab2395467482aaebb5992cec608bd3b0d731711293aa0fe2414c9` |
| CSV | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.csv` | `5ec531025bb2549da41e915617e7dfd4a1e5acdee5c5eb0a32dbc0dbf841ad2f` |
| Markdown | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.md` | `61c88f197f1426e0ca69d3763e8dc6d6d8a79193ee68604a0fc9ac9b67ac393a` |

These SHA-256 values were copied from a fresh T7bd run of:

```bash
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/*
```

## Source Extraction Artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| Accepted extraction NPZ | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz` | `69b2e449ba24bdc17fb6f85f0450d38daae6ce16f551381f19b13717c836ad2d` |
| Accepted extraction JSON sidecar | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json` | `8a64c50ae96f75dc9a9ed4db2191098fe6d92418e4877b8752f87c7ca434f3f8` |

Both PNG sidecars point to these exact source paths and hashes.

## Sidecar Scope Flags

Both PNG sidecars record:

- `plot_type=tablei_four_frequency_readonly_pilot`
- `source_extraction_case_id=FIG5_FIG6_TABLEI_FOUR_FREQUENCY_READONLY`
- `source_extraction_schema_version=phase5_t8ac_tablei_v1`
- `phase_policy.four_frequency_unwrap_is_diagnostic_only=true`
- invalid value policy: preserve masks and NaN values; do not fill, clip, smooth, regularize, or substitute component ratios.

The required boundary flags are all true:

- `no_solver_rerun`
- `no_field_recomputation`
- `no_interpolation`
- `no_kirchhoff_baseline`
- `not_paper_level_dense_scan`
- `no_kM4`
- `no_dense_Mk_scan`
- `no_new_physics_convention`
- `read_only_from_tablei_extraction`

## T7bc Verification Evidence

T7bc independently verified:

- The reporting directory contains exactly the six accepted reporting files.
- The CSV has 32 data rows, one per `(kM, point_id)`.
- Every CSV numeric field was checked against the accepted extraction arrays, including coordinates, indices, masks, complex plus/cross values, magnitudes, principal phases, and diagnostic unwrapped phases.
- Markdown splits near-axis and far-axis groups and states that the output is not a paper-level Fig.5/Fig.6 reproduction.
- PNG sidecars record plotted point IDs, plotted quantities, phase policy, mask policy, and the required no-solver/no-recompute/no-interpolation/no-Kirchhoff/no-`kM=4`/not-paper-level flags.
- PNGs are nonblank:
  - `fig5_near_axis_tablei_four_frequency_pilot.png`: size `(2100,1560)`, array shape `(1560,2100,4)`, pixel std `34.8049819438`, unique RGBA colors `4389`.
  - `fig6_far_axis_tablei_four_frequency_pilot.png`: size `(2100,1560)`, array shape `(1560,2100,4)`, pixel std `36.4157065074`, unique RGBA colors `2446`.
- Static checks found no solver, radial, scattering, polarization, pointwise-amplification, or flat-baseline recomputation calls in the plotting/reporting helper path.
- Focused tests passed:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_viz_results.py tests/regression/test_plot_cli.py
58 passed in 5.46s
```

- Full pytest passed under T7bc:

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
380 passed, 117 skipped, 1 xfailed, 75 subtests passed in 99.23s
```

T7bd re-ran the required listing/hash commands and a sidecar provenance/flag check. T7bd did not rerun full pytest because this closeout slice changed only documentation and the prompt forbids source/test changes.

## T7bd Fresh Checks

Listing:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig5_near_axis_tablei_four_frequency_pilot.png.json
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/fig6_far_axis_tablei_four_frequency_pilot.png.json
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.csv
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/reporting/tablei_four_frequency_values.md
```

Sidecar provenance/flag check:

```text
SIDECAR_CHECK ok
```

## Scope Limitation

The PNGs are sparse reporting pilots, not paper-level Fig.5/Fig.6 reproductions. Their apparent visual simplicity is expected because the accepted data contain only four frequency samples, no dense `Mk` scan to about `4`, no `kM=4`, and no Kirchhoff dashed comparison curves.

The reporting pilot must not be post-processed into apparent dense curves through interpolation or smoothing. It must not be cited as a paper-level comparison to Li-Hou-Zhao Fig.5/Fig.6.

## Explicit Non-Scope

This closeout does not validate or authorize:

- dense `Mk` scan;
- explicit `kM=4`;
- R60_K4;
- Kirchhoff Eq. (47) baseline or dashed comparison curves;
- Appendix D/E curves;
- strict `Psi4`;
- arbitrary incident direction;
- fixtures;
- solver reruns or field recomputation;
- new physics convention;
- paper-level Fig.5/Fig.6 plotting or reproduction.

## Remaining Gates

Future work requires separate T0 gates:

- dense `Mk` scan planning;
- explicit `kM=4` gate;
- Kirchhoff Eq. (47) convention freeze;
- production dense scan;
- paper-level Fig.5/Fig.6 plotting after accepted dense artifacts.

Recommended next action:

```text
T0 may proceed to T10g dense Fig.5/Fig.6 + Kirchhoff readiness planning. Do not schedule kM=4, dense scan production, Kirchhoff implementation, fixtures, or paper-level Fig.5/Fig.6 reproduction without the required planning/review gates.
```
