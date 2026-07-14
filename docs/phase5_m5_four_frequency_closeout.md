# Phase 5 M5 Four-Frequency Closeout

Date: 2026-07-06

Status: the M5 four-frequency pointwise wave-optics amplification archive is
closed after T8s generated the archived artifacts and T7ae independently
accepted them. This closeout freezes the accepted scope, provenance,
verification result, limitations, and remaining gates. It does not start
`kM=4`, R60_K2/R60_K4, arbitrary incident direction, larger-domain work,
scalar/Kirchhoff baselines, or radial horizon-transmission observables.

## Accepted Scope

This closeout accepts the M5 finite-radius pointwise wave-optics amplification
archive for:

- Production quantity: pointwise wave-optics amplification
  `h_lensed / h_unlensed`, not radial horizon transmission or absorption.
- Frequencies: `kM=[0.5,1.0,1.5,2.0]`.
- Observer plane: `x/M,z/M in [-30,30]`.
- Sampling: `dx=dz=0.5M`, shape `(121,121)`.
- Incident direction: default `+z`.
- Source wave-field artifacts:
  `runs/phase4/m4_production_first_pass/`.
- M5 archive directory:
  `runs/phase5/m5_four_frequency_amplification_artifacts/`.

This closeout relies on the already accepted M4-production first-pass saved
results and does not validate any new wave-field solve.

## Artifact Manifest

The accepted M5 archive contains:

- Four amplification NPZ files.
- Sixteen PNG plots.
- Sixteen JSON sidecars.
- One `manifest.md`.

The authoritative generated file list, file sizes, and SHA-256 checksums are
recorded in:

```text
runs/phase5/m5_four_frequency_amplification_artifacts/manifest.md
```

The four amplification NPZ checksums accepted by T7ae are:

| `kM` | Amplification NPZ | SHA-256 |
|---:|---|---|
| 0.5 | `t8s_li_fig3_xz_k0p5_dx0p5_amplification.npz` | `b0193570c0b0933318fe29493c57640bad7b88cce2a8fcfa47e6a978d5368e99` |
| 1.0 | `t8s_li_fig3_xz_k1p0_dx0p5_amplification.npz` | `26393c18347983a15d51f9cb5a5594493d580e1cea7a78744953c08564cfb1af` |
| 1.5 | `t8s_li_fig3_xz_k1p5_dx0p5_amplification.npz` | `12268ad66069ad004ed4626d7a0d30da0e89838911cab81d3db442c5e5d27abb` |
| 2.0 | `t8s_li_fig3_xz_k2p0_dx0p5_amplification.npz` | `f225d8cf5bb09d10a4d00034410bcad04af6d4a20ad79c1b8823ded889cdb276` |

The archive manifest checksum observed by T7ae is:

```text
2d3db0ad4443dbedb6cb329a0b65f542bdac0c43d1d8eb978464c4ec95d912db
```

## Provenance

The source M4 artifacts are the accepted M4-production first-pass saved
results:

| `kM` | Source path | SHA-256 |
|---:|---|---|
| 0.5 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k0p5_dx0p5.npz` | `e477100337cebb7f351b2fffa423264b76b25264c1ffb46b13e8cd04da2c98e7` |
| 1.0 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz` | `1923663926ce09eae26bdc10eb94ac4092b9d3af2358f52164356312bef7a8e9` |
| 1.5 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p5_dx0p5.npz` | `1c52852f4820aa09c2f53e456bea6674d0818aaf0d61dbffe223998a793e7c32` |
| 2.0 | `runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz` | `a06c2e8d7f26773c790214630d3eab5f6cd09c5013ac12151ec0992b09160762` |

T8s embedded source provenance in the generated artifacts:

- Every generated amplification NPZ metadata records the source M4 path,
  source SHA-256, source byte size, source case id, output case id,
  normalization metadata, baseline API, grid metadata, `k`, and `lmax`.
- Every plot sidecar records the source M4 path/SHA/size and the generated
  amplification NPZ path/SHA/size.

This source-SHA metadata hardening closes the non-blocking provenance gap
identified in T7ad for the first single-frequency M5 artifact.

## Physics And Conventions

The accepted M5 quantity is the Q005 production pointwise amplification:

```text
F_plus_complex  = h_plus_lensed  / h_plus_unlensed
F_cross_complex = h_cross_lensed / h_cross_unlensed
```

These are complex amplitude ratios. Plot-oriented summaries such as
`amplification_plus`, `amplification_cross`, `F_pol_norm`, and `I_pol_ratio`
do not replace the complex component ratios.

The unlensed denominator uses the flat/no-lens production-compatible baseline
with the same `exp(-i k t)` Fourier convention, same positive `k`, same
`A_plus/A_cross`, same observer coordinates, default `+z` incident direction,
and the same Route B incident-frame electric-tidal packaged-polarization
bridge as the lensed production field.

Denominator masks are independent:

- `valid_ratio_plus_mask` for `F_plus_complex` and plus-derived summaries.
- `valid_ratio_cross_mask` for `F_cross_complex` and cross-derived summaries.
- `valid_ratio_norm_mask` for `F_pol_norm` and `I_pol_ratio`.

Invalid ratios remain NaN/masked. They are not zero-filled, one-filled,
clipped, floored, or regularized to force finite values.

No Q005, Q014, Fourier, tetrad, Route B, RW/Zerilli, radial threshold, or
`lmax` convention was changed by T8s, T7ae, or this closeout.

## Verification Summary

T7ae independently checked:

- All four M4 source checksums.
- Archive layout: four amplification NPZ files, sixteen PNG plots, sixteen
  JSON sidecars, and one manifest.
- Generated checksums against the T8s manifest.
- `AmplificationGridResult` schema for all four NPZ files.
- Shape `(121,121)`, `grid.kind="xz_plane"`, and x/z ranges `[-30,30]`.
- Source path, source case, source SHA-256, and source byte size metadata.
- Pointwise amplification normalization metadata and baseline API metadata.
- Independent plus/cross/norm masks and NaN invalid policy.
- Complex ratio phases, confirming `F_plus_complex/F_cross_complex` were not
  replaced by magnitudes.
- Plot sidecars for all four frequencies and all four required quantities.
- Read-only visualization boundary.

Verification commands recorded by T7ae included:

```bash
shasum -a 256 runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k0p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p0_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k1p5_dx0p5.npz runs/phase4/m4_production_first_pass/t8o_li_fig3_xz_k2p0_dx0p5.npz
find runs/phase5/m5_four_frequency_amplification_artifacts -maxdepth 1 -type f -print | sort
find runs/phase5/m5_four_frequency_amplification_artifacts -mindepth 2 -print
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q tests/unit/test_transmission.py tests/unit/test_io_results.py tests/unit/test_viz_results.py tests/regression/test_io_cli.py tests/regression/test_plot_cli.py
PYTHONPATH=src /opt/homebrew/bin/python3 -m pytest -q
rg -n "schwgw\\.(scattering|perturbations|angular|numerics|backgrounds)|compute_polarization|run_solver_grid|solve_radial|compute_pointwise_amplification|flat_no_lens_baseline_at_point" src/schwgw/viz || true
```

Results:

- Source checksums matched.
- Archive layout matched the T8s/T7ae record.
- No nested extra files were present.
- Targeted tests passed: `72 passed`.
- Full pytest passed: `215 passed, 1 skipped, 1 xfailed, 75 subtests passed`.
- `src/schwgw/viz` had no forbidden solver/scattering/radial/baseline imports
  or calls.

No `schwgw run` was used for M5 artifact generation. The M5 archive was
derived from saved M4-production wave-field results.

## Q018 And Radial Limitation

The `kM=2.0` M4 source carries accepted same-domain Q018
`evanescent_tail_suppressed` metadata:

- Warning count: `56`.
- Warning code: `evanescent_tail_suppressed`.
- Accepted M4 domain: `x/M,z/M in [-30,30]`.
- Production-grid maximum radius:
  `sqrt(30^2 + 30^2) = 42.42640687119285 M`.
- The accepted M4 closeout records minimum `valid_until_r` as
  `42.472089355131786`, covering this domain.

This closeout inherits that same-domain acceptance only. It must not be used
as evidence for larger observer domains. Any larger-domain M5 artifact must
re-check Q018 `valid_until_r` coverage and the spin-2 finite-radius
applicability assumptions.

## Explicit Non-Scope

This closeout does not validate:

- `kM=4`.
- R60_K2 or R60_K4 regression fixtures.
- Arbitrary incident direction.
- Larger domains beyond `[-30,30]^2`.
- Scalar/Kirchhoff/eikonal baselines.
- Radial horizon transmission or radial absorption.
- `A_in/A_out`, phase shifts, Wronskians, horizon flux, or asymptotic
  scattering observables as M5 production outputs.
- Pixel-for-pixel reproduction of a reference-paper figure.

Those items remain open gates or future diagnostic observables. They must not
be inferred from the accepted four-frequency M5 archive.

## Closeout Decision

The M5 four-frequency pointwise wave-optics amplification archive is accepted
and closed for the specified scope:

```text
kM=[0.5,1.0,1.5,2.0]
x/M,z/M in [-30,30]
dx=dz=0.5M
shape=(121,121)
default +z incident direction
source M4 archive: runs/phase4/m4_production_first_pass/
M5 archive: runs/phase5/m5_four_frequency_amplification_artifacts/
```

## Next-Decision Menu

T0 should choose the next scientific slice explicitly. Options include:

- `kM=4` stress.
- R60_K2/R60_K4 regression fixtures.
- Arbitrary incident direction / Wigner-D rotation integration.
- Scalar/Kirchhoff baseline comparisons.
- Larger-domain Q018 re-check.
- M5 closeout-to-paper plotting/reporting.

Do not open `kM=4`, R60_K2/R60_K4, arbitrary incident direction, larger-domain
work, scalar/Kirchhoff baselines, or radial horizon-transmission diagnostics
by implication from this closeout.
