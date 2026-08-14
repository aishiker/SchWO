# Li–Hou–Zhao Figures 3–8 computation and rendering closeout

Date: 2026-08-01
Project root: `/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`
Source paper: `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`

## Executive status

All six requested numerical datasets and publication-resolution renderings have
been produced.  `calculation_complete` and `paper_equivalence` are intentionally
reported separately: a completed numerical run is not treated as evidence that
the plotted observable is identical to the one used by Li, Hou, and Zhao.

| Figure | Numerical product | Rendering | Calculation status | Paper-equivalence status |
|---|---|---|---|---|
| 3 | Four \(241\times241\) \(x\)-\(z\) fields at \(kM=0.5,1,1.5,2\) | 600 dpi PDF/PNG, bilinear display plus nearest-neighbour audit | complete | **not fully accepted**: parameters and qualitative morphology agree, but the packaged positive-frequency polarization projection used by the repository has the same unresolved convention boundary described below |
| 4 | Four 1025-point angular solutions plus exact/asymptotic comparison | 600 dpi PDF/PNG | complete | **not accepted**: the radial/Weyl solve is valid, but the conversion to the paper's \(h_+,h_\times\) observable is not yet convention-equivalent |
| 5 | Full \(40\times8\) Table-I near-axis frequency grid | 600 dpi PDF/PNG | complete | **not accepted**: \(F_\times\) is qualitatively close, while \(F_+\) disagrees materially with the published panel |
| 6 | Full \(40\times8\) Table-I far-axis frequency grid | 600 dpi PDF/PNG | complete | **not accepted** for the same polarization-projection reason as Fig. 5 |
| 7 | Four \(241\times241\) apparent-polarization fields | 600 dpi PDF/PNG, bilinear display plus nearest-neighbour audit | complete | **not accepted as a paper reproduction**: the internal diagnostic is self-consistent, but the morphology and longitudinal-mode strength differ visibly from the published panel; it is not evidence for extra propagating degrees of freedom |
| 8 | Four-frequency angular cross section, 1440 angles, matched through ℓ=502 | 600 dpi PDF/PNG | complete | closest current reproduction, but not author-data equivalent: the high-ℓ portion is a controlled Coulomb/MST tail rather than unavailable author raw data |

## Frozen artifacts

### Figure 3

- Data directory: `runs/phase5/fig3_four_frequency_dx0p25_production/`
- NPZ SHA-256 values for \(kM=0.5,1,1.5,2\):
  `b93582cf10a20f8340b105f6c82f1faed9398c93dd83c6a003270a3417d21873`,
  `0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132`,
  `1f146a6c67192976538820b68e94118a3a6e636ba71ecebb045cbca123e5e7f2`,
  `b560f9ae072495590e59ae7c49d54ee0353e395a0bd9d60b4cf5b717d11c34fc`.
- Each field has \(57{,}884\) valid and 197 masked grid cells.
- Final PDF:
  `runs/phase5/paper_figures/fig3_stable_recomputation_20260801/fig3_stable_bilinear.pdf`
  (SHA-256 `5dafa8bdac8a93fd26a97930d758a48de2bf2a45885888c5d3a64f076b1759f6`).
- Raster size: \(4260\times2190\) pixels at 600 dpi.

### Figure 4

- Exact angular inputs:
  `runs/phase5/fig4_angular_n1025_production/`.
- NPZ SHA-256 values for \(kM=0.5,1,1.5,2\):
  `35606b4455a116584c2d54597792003483b9793a2979f43ca9569acd3d7374a4`,
  `e8d5942ea2d9c07140b86b9ec91346178f9afc2b26bd46d17bfb6a170de513b7`,
  `902594f4f706f0a3ee3bea0bd0bb9590a5acff4996a9f335cbead66df42a477d`,
  `53db438f5e222777aa46002d5d24f51baf9f43890ffd1ea510c05ad249001980`.
- Combined exact/asymptotic data:
  `runs/phase5/fig4_exact_asymptotic_comparison_20260801/fig4_exact_asymptotic_q2_comparison.npz`
  (SHA-256 `a175305e2a23cb4e73742715554cfe15473fc3e38982a21040199aaef5ce3410`).
- Final PDF:
  `runs/phase5/fig4_exact_asymptotic_comparison_20260801/fig4_exact_asymptotic_q2_comparison.pdf`
  (SHA-256 `168222c8666966d6a45736dd9b762e6941801f54f75db520d2703888e183f2b7`).
- Raster size: \(6900\times3360\) pixels at 600 dpi.

### Figures 5 and 6

- Merged data:
  `runs/phase5/fig5_fig6_uniform40_direct_production/tablei_uniform40_merged.npz`
  (SHA-256 `76b0a3d3d3ffd44def8466e18ddcba4fe097d899e12980f988cc0e038cfef6a9`).
- The frequency axis is the complete uniform set \(kM=0.1,0.2,\ldots,4.0\);
  all eight Table-I observation points are present.  `F_plus_complex` and
  `F_cross_complex` both have shape `(40, 8)` and all stored numerical values
  are finite.
- Fig. 5 PDF:
  `runs/phase5/fig5_fig6_uniform40_direct_production/rendered_raw_20260801/fig5_near_axis_uniform40.pdf`
  (SHA-256 `efafbb781c11ec5245999889b4d6a8ad7e06d0793844af75ae189ca025742ff4`).
- Fig. 6 PDF:
  `runs/phase5/fig5_fig6_uniform40_direct_production/rendered_raw_20260801/fig6_far_axis_uniform40.pdf`
  (SHA-256 `d6ea1d280ffc4c7f87730542f1f19e47594bce2a7d827c48ac708a77504c2e7b`).
- Both rasters are \(7020\times3090\) pixels at 600 dpi.

### Figure 7

- Data directory:
  `runs/phase5/fig7_apparent_four_frequency_dx0p25_production/`.
- NPZ SHA-256 values for \(kM=0.5,1,1.5,2\):
  `6282791889fbad37efc19a683c1c85419443e35236d02489f4ea294fbff505ba`,
  `1e8930d6138d80f35379b4d69310aece1e1be95bd5ce7bed11bf8417d3bbf339`,
  `335631b5070b20da407d79d1f4bcc7ea1b669f72efd20a0609f01dea4c1a66e1`,
  `4c6de50707d6bd7941bdd62dd1f5edd38ea0f03027f1f570dfa1b446dfca02c5`.
- Each field has \(57{,}884\) valid and 197 masked grid cells.
- Final PDF:
  `runs/phase5/fig7_apparent_four_frequency_dx0p25_production/rendered_paper_v2_20260801/fig7_apparent_four_frequency.pdf`
  (SHA-256 `565a9d2df95e79f96adbf58d7f1a8e1d2bedc17e6858423064db7f983de7c3cc`).
- Raster size: \(4260\times4980\) pixels at 600 dpi.

### Figure 8

- Matched data:
  `runs/phase5/fig8_matched_production_20260801/fig8_matched_l500_n1440.npz`
  (SHA-256 `1a61bc7949a612dc126cfbd1cf28e6704501854c1138949be58806a20080e66f`).
- Stored shapes include four frequencies, 1440 angular samples, and partial
  waves ℓ=2,…,502.  Direct numerical modes through ℓ=180 are joined to a
  solver-free Coulomb/MST tail; the maximum overlap phase residual across the
  four frequencies is approximately \(0.030\)--\(0.067\) rad.
- Final PDF:
  `runs/phase5/fig8_matched_production_20260801/rendered/fig8_asymptotic_four_frequency.pdf`
  (SHA-256 `bbbb2bdf1d7aef91be669866e902b656bee2849828ffde05e1ef711be665daa5`).
- Raster size: \(6840\times1830\) pixels at 600 dpi.  The displayed window is
  \(0.1\leq\theta/\pi\leq1\); the data file retains the full generated angular
  grid.

## Unresolved physical convention for Figures 3–6

The repository's production route first forms an electric-tidal matrix from a
strict positive-frequency Newman–Penrose quintuple and then packages it as

\[
h_+^{\rm RB}=\frac{2E_{xx}}{k^2},\qquad
h_\times^{\rm RB}=\frac{2E_{xy}}{k^2}.
\]

The paper's Eq. (42), however, is stated for real-time fields,

\[
\ddot h_+=\operatorname{Re}(\Psi_4+\Psi_0),\qquad
\ddot h_\times=-\left(\operatorname{Im}\Psi_4-\operatorname{Im}\Psi_0\right).
\]

Turning this statement into an arbitrary complex, positive-frequency plotting
amplitude requires a complete reality/negative-frequency convention.  That
bridge is not specified by the paper and is not recoverable from a single
positive-frequency NP quintuple alone.  Under the most direct complex lift,

\[
h_+^{\rm S}=-(\Psi_4+\Psi_0)/k^2,\qquad
h_\times^{\rm S}=-i(\Psi_4-\Psi_0)/k^2,
\]

the current Route-B values obey

\[
h_+^{\rm RB}=\tfrac12 h_+^{\rm S}-\Psi_2/k^2,\qquad
h_\times^{\rm RB}=\tfrac12 h_\times^{\rm S}.
\]

This explains why a numerically converged radial/Weyl calculation can still
disagree with the paper's plotted \(F_+\).  It is a definition/projection
boundary, not evidence that the radial solver failed.

Direct panel comparison also exposes two additional non-cosmetic failures:

- In Fig. 4 the repository's exact curves approach zero near
  \(\theta/\pi=1\), whereas the published exact curves retain nonzero
  plateaus of roughly 1.6 and 0.7.  The asymptotic repository curves retain
  similar plateaus, so the exact total/scattered-field surface is not yet
  closed against the paper.
- In Figs. 5 and 6 the repository Kirchhoff magnitudes rapidly approach zero
  over much of the frequency interval, while the published dashed curves
  remain comparable to the exact scattering points.  Therefore the current
  Kirchhoff normalization/observable is also not paper-equivalent; the
  polarization projection alone does not explain the full discrepancy.

Two tempting adjustments were explicitly rejected:

1. Adding an extra incident wave to the computed angular field double-counts
   it, because the outer boundary condition already includes incident plus
   reflected content.
2. Replacing the mismatch by an empirical \(F_+\leftarrow F_\times\) mapping
   would fit the appearance without a derivation and is therefore not a valid
   reproduction.

A literal Eq. (35)-style conjugation probe at \(kM=0.5\), \(\theta=0\), and
\(\ell_{\max}=84\) produced
\(|h_+|=1.7796990158\) and \(|h_\times|=1.7855037266\); it did not recover the
published plus/cross split.  The experimental change was reverted and is not
present in the stored products.

## Verification performed

- Direct NPZ reload and shape checks for every frozen dataset.
- Mask-aware validation of the Fig. 3 and Fig. 7 fields; non-finite values are
  confined to the intentional 197-cell black-hole mask.
- Direct finite-value checks for all Fig. 4, Fig. 5/6, and Fig. 8 arrays.
- SHA-256 rehash of every final PDF and every core numerical product listed
  above.
- Raster-dimension checks with `sips`.
- Focused physics/unit suite:
  `140 passed, 1 skipped, 1 xfailed` under exact Python 3.14.
- Full project suite:
  `1101 passed, 117 skipped, 1 xfailed, 104 subtests passed` under exact
  Python 3.14; the 137 warnings are the existing intentional/fail-closed
  SciPy radial-path diagnostics.
- No active figure-generation process, optimized lock, partial, quarantine, or
  temporary publication file remained at closeout.

## Canonical entry points

- Fig. 3 and the paper-figure wrapper:
  `scripts/phase5_generate_li_hou_zhao_figures.py`.
- Fig. 4 renderer: `src/schwgw/viz/fig4_comparison.py`.
- Fig. 5/6 merge, preflight, and rendering:
  `scripts/phase5_merge_tablei_uniform.py`,
  `scripts/phase5_preflight_tablei_uniform.py`, and
  `scripts/phase5_render_tablei_uniform.py`.
- Fig. 7 production and rendering:
  `scripts/phase5_generate_fig7_apparent_frequency.py`,
  `scripts/phase5_generate_fig7_apparent_wavefields.py`, and
  `src/schwgw/viz/fig7_apparent.py`.
- Fig. 8 production, matching, and rendering:
  `scripts/produce_fig8_asymptotic.py`,
  `scripts/build_fig8_matched.py`, and
  `src/schwgw/viz/fig8_asymptotic.py`.

## Closeout interpretation

The requested compute-and-render work for Figures 3–8 is complete and durable.
The scientific claim is narrower: Figure 8 is the closest current matched
reproduction, while Figure 7 is only an internally defined diagnostic.
Figures 3–7 must not be advertised as strict pixel-level reproductions of the
paper until the positive-frequency polarization bridge, total/scattered-field
surface, Kirchhoff normalization, and apparent-mode projection are closed
against low-cost paper-facing numerical probes or the authors' original
plotting convention is obtained.
