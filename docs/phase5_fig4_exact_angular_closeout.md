# Phase 5 Fig.4 Exact-Angular Closeout

Date: 2026-07-08

Decision label: **CLOSED / ACCEPTED FOR FIG.4 EXACT-ANGULAR ALL-FREQUENCY READ-ONLY SCOPE ONLY**

This document closes out the currently accepted Fig.4 exact finite-radius angular artifacts. It freezes the accepted scope, source artifacts, plot artifact, provenance, validation evidence, limitations, diagnostic caveats, and remaining gates. It does not authorize new solver runs, fixtures, Fig.5/Fig.6 scans, `kM=4`, R60_K4, larger domains, arbitrary incident directions, Kirchhoff baselines, Appendix D/E asymptotic curves, or strict `Psi4` outputs.

## Accepted Scope

- Artifact class: Fig.4 exact finite-radius angular curves.
- Frequencies: `kM=[0.5,1.0,1.5,2.0]`.
- Observer radius: `r=60M`.
- Angular grid: `theta_count=65`, `phi_count=64`.
- Extraction policy: fixed `phi=0` only. No `phi` averaging is accepted.
- Fields: production `h_plus` and `h_cross`.
- Plotted quantities: `|h_plus|` and `|h_cross|`.
- Incident direction: default `+z`.
- Polarization convention: Route B packaged-polarization production path, using incident-frame electric tidal projection.
- Output interpretation: exact finite-radius packaged-polarization amplitudes, not asymptotic scattering amplitudes.

## Accepted Source Artifacts

| kM | Source path | Case id | SHA-256 | Size bytes | lmax | Final adjacent pair | Final selected relative change | Final near-axis relative change | Q018 oracle status |
|---:|---|---|---|---:|---:|---|---:|---:|---|
| 0.5 | `runs/phase5/fig4_exact_angular_k0p5/r60_k0p5_fig4_exact_angular_first_pass.npz` | `R60_K0P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `a0d06ba4d3073c4f18e086439f1dd88255569a8a08afedf1ae47622738ce6c97` | 4098094 | 84 | `[72,84]` | 0.0 | 0.0 | absent |
| 1.0 | `runs/phase5/fig4_exact_angular_k1p0/r60_k1p0_fig4_exact_angular_first_pass.npz` | `R60_K1P0_FIG4_EXACT_ANGULAR_FIRST_PASS` | `f76e975f0f70c3d83b10aa9320bce929d9f975d343f95945ee368a82055d7f09` | 4081714 | 108 | `[96,108]` | 4.7046640690111286e-11 | 7.8437173980455e-13 | absent |
| 1.5 | `runs/phase5/fig4_exact_angular_k1p5/r60_k1p5_fig4_exact_angular_first_pass.npz` | `R60_K1P5_FIG4_EXACT_ANGULAR_FIRST_PASS` | `76074eb9de412b4e7b94d27a78ffa1aa0541f17a1f0585dff94de5dc6c7c0931` | 4147238 | 156 | `[132,156]` | 2.0362176912290822e-11 | 3.3497787698762443e-13 | absent |
| 2.0 | `runs/phase5/q018_r60_k2_angular_production_first_pass/r60_k2_q018_angular_production_first_pass.npz` | `R60_K2_Q018_ANGULAR_PRODUCTION_FIRST_PASS` | `065b2d3dacd5ab8657d0aa8e95fe3ee8b149efd3dd7d1d8b7375ac5df6cfadb2` | 4524170 | 180 | `[156,180]` | 2.0272571360273772e-07 | 1.3676928945796113e-09 | `q018_riccati`, warning count 56, ell range `[153,180]`, code `q018_required_radius_oracle_used` |

All four sources are accepted only for the angular `r=60M` scope above. They share the same `theta` and `phi` grids, have no duplicate `phi=2pi` endpoint, and contain finite saved `h_plus/h_cross` fields.

## Accepted Plot Artifacts

| Artifact | Path | Size bytes | SHA-256 | Notes |
|---|---|---:|---|---|
| PNG | `runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png` | 270015 | `b1799a84da0c9fe7a0bf8f592392c906a2868fb7d372f7d206525efec89d8332` | `1620 x 1920` RGBA PNG, nonblank, two panels for `|h_plus|` and `|h_cross|` |
| JSON sidecar | `runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png.json` | 9542 | `52ca04a9a21eb736a55db4b21a85c12487f1a983a7791ab634504180cb7621fd` | `plot_type=fig4_all_frequency_exact_angular_curves`, `curve_extraction_policy=fixed_phi_cut` |

Sidecar summary:

- `source_kM_values=[0.5,1.0,1.5,2.0]`.
- `source_lmax_values=[84,108,156,180]`.
- `field_names=["h_plus","h_cross"]`.
- `plotted_quantities=["abs_h_plus","abs_h_cross"]`.
- `phi_selected=0.0`, `phi_selected_index=0`.
- `theta_count=65`, `phi_count=64`.
- `no_phi_average=true`.
- `no_solver_rerun=true`.
- `no_field_recomputation=true`.
- `no_strict_psi4=true`.
- `no_asymptotic_comparison=true`.
- `no_kirchhoff_baseline=true`.
- `convergence_caveat=selected_17x8_final_pair_only_not_full_grid`.

## Provenance Summary

- T8x generated the `kM=2` R60 angular production NPZ; T7as accepted that source artifact.
- T8y generated the single-frequency fixed-`phi=0` `kM=2` read-only Fig.4 plot boundary; T7au accepted that plot boundary.
- T8z generated lower-frequency readiness configs and bounded smoke NPZs; T7av accepted lower-frequency readiness only.
- T8aa generated lower-frequency `kM=0.5,1.0,1.5` full angular source NPZs; T7aw accepted those source artifacts.
- T8ab generated the all-frequency fixed-`phi=0` read-only Fig.4 PNG/sidecar from the four accepted NPZs; T7ax accepted that all-frequency plot artifact.
- T7ay closes out the accepted Fig.4 exact-angular artifact set for the narrow scope stated here.

## Physics And Convention Summary

- The accepted plot uses project production `h_plus/h_cross`.
- It does not plot strict Newman-Penrose scalars.
- It does not expose strict `Psi4`.
- It does not use or validate an asymptotic scattering amplitude.
- It does not use a Kirchhoff baseline.
- It does not change Fourier convention, harmonic convention, tetrad convention, RW/Zerilli master-variable convention, Route B packaged-polarization convention, Q014 policy, Q015 policy, or Q018 policy.
- The accepted output is an exact finite-radius packaged-polarization artifact at `r=60M`, not an Appendix D/E asymptotic curve or pixel-for-pixel paper reproduction.

## Verification Summary

T7ax and T7ay checked the artifact boundary independently.

Fresh T7ay verification:

```text
shasum -a 256 <four source NPZs plus PNG plus sidecar>
```

matched the six SHA-256 values recorded above.

```text
find runs/phase5/fig4_all_frequency_exact_angular -maxdepth 2 -type f -print | sort
```

listed exactly:

```text
runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png
runs/phase5/fig4_all_frequency_exact_angular/fig4_all_frequency_exact_phi0_curves.png.json
```

```text
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial" src/schwgw/viz || true
```

returned no output, confirming the visualization package remains free of solver/scattering imports for this check.

```text
find runs configs tests/regression/fixtures -maxdepth 6 \( -iname '*R60*K4*' -o -iname '*k4*' -o -iname '*.h5' -o -iname '*.hdf5' \) -print
```

returned no output.

```text
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
```

returned:

```text
371 passed, 117 skipped, 1 xfailed, 75 subtests passed
```

T7ax also checked source SHAs, sidecar fields, nonblank PNG structure, fixed-`phi=0` policy, read-only visualization boundary, and full pytest. Plotting did not run `schwgw run` and did not generate new numerical data.

## Q018 And Radial Limitations

- The `kM=2` source uses the reviewed `q018_riccati` opt-in for the continuous `ell=153..180` band, odd/even sectors, at `r=60M`.
- The lower-frequency `kM=0.5,1.0,1.5` sources use no Q018 oracle.
- The `kM=1.5` source retains `max_match_condition_number=4.939017032749817e+144`; this remains an explicit diagnostic caveat, not hidden by plotting.
- The convergence caveat remains: source convergence was selected `17 x 8` final-pair convergence, not a full `65 x 64` grid convergence proof.
- This closeout does not validate radial horizon transmission, absorption, phase-shift diagnostics, or a scalar cutoff-only proof.

## Explicit Non-Scope

The accepted Fig.4 exact-angular artifact set must not be cited as evidence for:

- Fig.5/Fig.6 scans.
- Regression fixtures.
- R60_K4.
- `kM=4`.
- Larger-domain artifacts.
- Arbitrary incident direction.
- Kirchhoff baseline.
- Appendix D/E asymptotic curves.
- Strict `Psi4` outputs.
- Scalar baseline validation.
- Radial horizon transmission or absorption diagnostics.
- Pixel-for-pixel reference-paper reproduction.

## Next-Decision Menu For T0

T0 may choose one of the following as a separate gated slice:

- Fig.5/Fig.6 Table-I point-frequency extraction planning.
- Dense Fig.5/Fig.6 scan with an explicit `kM=4` gate.
- Kirchhoff/Appendix D/E baseline convention review.
- Arbitrary incident direction / Wigner-D rotation integration.
- Larger-domain or R60_K4 Q018 re-check.

Recommended next step: open a separate Fig.5/Fig.6 Table-I point-frequency extraction planning slice. This closeout does not write that implementation prompt.
