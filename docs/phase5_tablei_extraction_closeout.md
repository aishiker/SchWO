# Phase 5 Fig.5/Fig.6 Table-I Extraction Closeout

Date: 2026-07-08

Decision label:

```text
CLOSED / ACCEPTED FOR FIG.5/FIG.6 TABLE-I FOUR-FREQUENCY READ-ONLY EXTRACTION ONLY
```

This closeout freezes the accepted scope, artifacts, provenance, verification evidence, limitations, and remaining gates for the Fig.5/Fig.6 Table-I four-frequency extraction pilot. It does not authorize solver runs, dense `Mk` scans, `kM=4`, R60_K4, Kirchhoff baselines, Appendix D/E curves, strict `Psi4`, arbitrary incident direction, fixtures, plotting, or paper-level Fig.5/Fig.6 reproduction.

## Accepted Scope

- Artifact class: read-only Table-I extraction from the accepted M5 four-frequency pointwise wave-optics amplification archive.
- Frequencies: `kM=[0.5,1.0,1.5,2.0]`.
- Points: the eight Table-I points at `z/M=30`, `y/M=0`.
- Extraction policy: exact grid-index extraction only from accepted M5 archive arrays.
- Source archive:
  - `runs/phase5/m5_four_frequency_amplification_artifacts/`
- Output archive:
  - `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/`
- Authoritative values:
  - `F_plus_complex`
  - `F_cross_complex`
- Derived summaries:
  - `abs_F_plus`
  - `abs_F_cross`
  - `arg_F_plus_principal`
  - `arg_F_cross_principal`
  - `arg_F_plus_unwrapped`
  - `arg_F_cross_unwrapped`
- Four-frequency unwrapping is diagnostic only. It is too sparse for paper-level phase curves.

The accepted quantity is pointwise wave-optics amplification,

```text
F_plus_complex  = h_plus_lensed  / h_plus_unlensed
F_cross_complex = h_cross_lensed / h_cross_unlensed
```

It is not radial horizon transmission, radial absorption, `A_in/A_out`, or a phase-shift observable.

## Accepted Artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| NPZ | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz` | `69b2e449ba24bdc17fb6f85f0450d38daae6ce16f551381f19b13717c836ad2d` |
| JSON sidecar | `runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json` | `8a64c50ae96f75dc9a9ed4db2191098fe6d92418e4877b8752f87c7ca434f3f8` |

The output directory must contain only these two files for this closeout scope.

## Accepted Source Archive

The extraction is accepted only against these four M5 amplification source NPZ files:

| `kM` | Source amplification NPZ | SHA-256 | Source M4 SHA-256 | `lmax` | Q018 warning count / codes |
|---:|---|---|---|---:|---|
| 0.5 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k0p5_dx0p5_amplification.npz` | `b0193570c0b0933318fe29493c57640bad7b88cce2a8fcfa47e6a978d5368e99` | `e477100337cebb7f351b2fffa423264b76b25264c1ffb46b13e8cd04da2c98e7` | 84 | `0 / []` |
| 1.0 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k1p0_dx0p5_amplification.npz` | `26393c18347983a15d51f9cb5a5594493d580e1cea7a78744953c08564cfb1af` | `1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9` | 108 | `0 / []` |
| 1.5 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k1p5_dx0p5_amplification.npz` | `12268ad66069ad004ed4626d7a0d30da0e89838911cab81d3db442c5e5d27abb` | `1c52852f4820aa09c2f53e456bea6674d0818aaf0d61dbffe223998a793e7c32` | 156 | `0 / []` |
| 2.0 | `runs/phase5/m5_four_frequency_amplification_artifacts/t8s_li_fig3_xz_k2p0_dx0p5_amplification.npz` | `f225d8cf5bb09d10a4d00034410bcad04af6d4a20ad79c1b8823ded889cdb276` | `a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762` | 180 | `56 / ["evanescent_tail_suppressed"]` |

The `kM=2.0` source inherits the accepted same-domain Q018 `evanescent_tail_suppressed` handling from the M4/M5 closeouts. This closeout does not extend Q018 coverage to larger domains, `kM=4`, or R60_K4.

## Table-I Points

Coordinates use `y=0`, `phi=0`, `r=sqrt(x^2+z^2)`, and `theta=atan2(abs(x),z)`. Source arrays are indexed as `[z_index, x_index]`.

| point_id | group | x/M | z/M | x_index | z_index | paper theta deg | paper xi/xi0 |
|---|---|---:|---:|---:|---:|---:|---:|
| `near_axis_x0_z30` | near-axis | 0 | 30 | 60 | 120 | 0.00000 | 0.0000 |
| `near_axis_x1_z30` | near-axis | 1 | 30 | 62 | 120 | 1.90915 | 0.0913 |
| `near_axis_x2_z30` | near-axis | 2 | 30 | 64 | 120 | 3.81407 | 0.1828 |
| `near_axis_x3_z30` | near-axis | 3 | 30 | 66 | 120 | 5.71059 | 0.2745 |
| `far_axis_x10_z30` | far-axis | 10 | 30 | 80 | 120 | 18.4349 | 0.9372 |
| `far_axis_x15_z30` | far-axis | 15 | 30 | 90 | 120 | 26.5651 | 1.4479 |
| `far_axis_x20_z30` | far-axis | 20 | 30 | 100 | 120 | 33.6901 | 2.0015 |
| `far_axis_x25_z30` | far-axis | 25 | 30 | 110 | 120 | 39.8056 | 2.6038 |

All selected `z_indices` equal `120`. The selected `x_indices` are:

```text
[60,62,64,66,80,90,100,110]
```

## Schema And Phase Policy

The accepted NPZ stores ratio-like arrays with shape `(frequency, point)`, where frequency order is:

```text
[0.5, 1.0, 1.5, 2.0]
```

The complex arrays are authoritative. Magnitudes and phases are derived from the complex arrays only.

Principal phases use:

```text
angle(F) in (-pi, pi]
```

Unwrapped phases are diagnostic and use increasing `kM`, independently per point and component, restarting across invalid or masked gaps.

## Verification Evidence

T7ba independently verified:

- The output directory contains exactly the NPZ and JSON sidecar listed above.
- The accepted artifact SHA-256 values match the hashes in this closeout.
- The sidecar source SHA-256 values match the accepted M5 source files.
- For all four frequencies and eight points, extracted `F_plus_complex` and `F_cross_complex` exactly equal source NPZ values at `[z_index, x_index]`.
- `x_indices`, `z_indices`, point coordinates, `r/theta/phi`, paper `theta_deg`, and paper `xi_over_xi0` match the T10f Table-I plan.
- `valid_ratio_plus_mask`, `valid_ratio_cross_mask`, `valid_ratio_norm_mask`, and `source_valid_mask` match the source arrays at selected points and are all true for the accepted entries.
- `abs_*` arrays match complex magnitudes.
- Principal phases match `np.angle(...)`.
- Unwrapped diagnostic phases match independent per-point unwrapping over the four valid frequency values.
- The NPZ-embedded `metadata_json` exactly matches the JSON sidecar.
- Static checks found no solver, radial, scattering, polarization, pointwise-amplification, or flat-baseline recomputation calls in the Table-I extraction helper.

T7ba command evidence:

```text
find runs/phase5/fig5_fig6_tablei_four_frequency_readonly -maxdepth 1 -type f -print | sort
```

listed exactly:

```text
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz
runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

```text
shasum -a 256 runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz runs/phase5/fig5_fig6_tablei_four_frequency_readonly/tablei_four_frequency_amplification_values.npz.json
```

matched the two accepted artifact hashes above.

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_tablei_extraction.py tests/regression/test_io_cli.py::test_cli_extract_tablei_four_frequency_writes_npz_and_sidecar
```

returned:

```text
5 passed in 0.34s
```

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

returned:

```text
376 passed, 117 skipped, 1 xfailed, 75 subtests passed in 97.17s
```

T7bb closeout verification re-ran the required file-existence, listing, and SHA checks and did not rerun full pytest because this slice modified only documentation.

## Sidecar Scope Flags

The accepted JSON sidecar records:

- `case_id=FIG5_FIG6_TABLEI_FOUR_FREQUENCY_READONLY`
- `quantity_kind=pointwise_wave_optics_amplification_tablei_four_frequency`
- `normalization_kind=pointwise_wave_optics_amplification`
- `baseline_api=compute_flat_no_lens_polarization`
- `incident_direction=+z`
- `fourier=exp(-i k t)`
- `polarization_bridge=Route B incident-frame electric tidal packaged scalars`
- `array_axis_order=ratio_arrays_indexed_as_z_then_x_before_extraction`

The required boundary flags are all true:

- `no_interpolation`
- `no_solver_rerun`
- `no_field_recomputation`
- `no_kirchhoff_baseline`
- `not_paper_level_dense_scan`
- `no_kM4`
- `no_dense_Mk_scan`
- `no_new_physics_convention`
- `no_plotting`

## Explicit Non-Scope

This closeout does not validate or authorize:

- dense `Mk` scan;
- `kM=4`;
- R60_K4;
- Kirchhoff baseline;
- Appendix D/E curves;
- strict `Psi4`;
- arbitrary incident direction;
- fixtures;
- plotting;
- paper-level Fig.5/Fig.6 reproduction;
- scalar/Kirchhoff/eikonal comparison as the production denominator;
- radial horizon transmission, absorption, `A_in/A_out`, Wronskian, or phase-shift observables as M5 outputs.

## Remaining Gates

The four-frequency Table-I extraction can be cited only as a sparse read-only extraction pilot from the accepted M5 archive. Future work requires separate T0 gates:

- read-only Table-I plotting/reporting-planning slice using the accepted Table-I data;
- dense `Mk` scan planning with an explicit `kM=4` gate;
- Kirchhoff convention freeze with T1/T10;
- no action / pause.

Recommended T0 next action:

```text
T0 may schedule a separate read-only Table-I plotting/reporting-planning slice, or pause. Do not schedule dense Mk scan, kM=4, Kirchhoff baseline, fixtures, or paper-level Fig.5/Fig.6 reproduction without a new gate.
```
