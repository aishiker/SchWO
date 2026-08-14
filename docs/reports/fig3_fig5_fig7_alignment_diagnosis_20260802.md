# Li–Hou–Zhao Fig. 3/5/7 alignment and Fig. 5 discrepancy diagnosis

Date: 2026-08-02  
Project root: `/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`  
Paper: `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`

## Outcome

- Fig. 3 now uses the same `viridis` colormap family as the paper and the
  existing Fig. 7 renderer.
- Fig. 3 and Fig. 7 now share one image-plane overlay definition: the black
  event-horizon disk has radius (2M), while the gray critical/light-ring
  disk has screen radius
  
  \[
  b_c=3\sqrt{3}M\simeq5.196M.
  \]
  
  The latter is the Schwarzschild critical impact parameter on the image
  plane, not the Schwarzschild-coordinate photon-sphere radius (r=3M).
- No solver or scientific dataset was rerun or modified for these display-only
  changes.  Fresh publication and nearest-neighbour audit renderings were made
  from the frozen NPZ files.
- Fig. 5 is **not** paper-equivalent.  The panel-by-panel audit identifies one
  definitive Kirchhoff-sign inconsistency, one definitive observable-interface
  mismatch, and one remaining high-frequency/off-axis physics mismatch.  The
  latter cannot be uniquely resolved without the authors' plotting convention
  or raw values.

## Fig. 3 and Fig. 7 display alignment

The shared constants live in `src/schwgw/viz/paper_geometry.py`.  Both
renderers consume those constants, so the two figures cannot silently drift
apart again.  Metadata records the colormap and the distinction between
(b_c=3\sqrt3M) and (r=3M).

Fresh outputs:

- Fig. 3:
  `runs/phase5/paper_figures/fig3_paper_aligned_20260802/`
- Fig. 7:
  `runs/phase5/fig7_apparent_four_frequency_dx0p25_production/rendered_paper_v3_20260802/`

The bilinear files are publication-display versions.  The corresponding
nearest-neighbour files are numerical-audit versions and do not alter the
underlying samples.

## Fig. 5 inputs and rendering surfaces checked

The current Fig. 5 uses the complete direct dataset
`runs/phase5/fig5_fig6_uniform40_direct_production/tablei_uniform40_merged.npz`:

- 40 exact frequency samples, (kM=0.1,0.2,\ldots,4.0);
- the first four exact Table-I points, ((x,z)=(0,30),(1,30),(2,30),(3,30));
- the paper's incident amplitudes
  (A_+=0.9+1.1i), (A_\times=0.4+0.6i);
- direct complex samples, principal `numpy.angle`, no smoothing, resampling,
  interpolation, or phase unwrapping.

The merged coordinates and frequency order agree exactly with the frozen
per-frequency products.  Therefore the visible discrepancy is not a merge,
coordinate, interpolation, or plotting-branch error.

## 1. Kirchhoff dashed curve: definitive sign inconsistency

The paper prints Eq. (47) as

\[
F_K=e^{+\pi\gamma/2}(-\gamma)^{-i\gamma}
\Gamma(1+i\gamma)\,{}_1F_1(-i\gamma,1;-i\gamma\eta^2),
\qquad \gamma=-2Mk.
\]

The repository evaluates this printed expression literally.  On the symmetry
axis, where (eta=0), it implies

\[
|F_K|^2=\frac{4\pi Mk}{e^{4\pi Mk}-1},
\]

which exponentially approaches zero.  That is exactly the dashed curve in
the current Fig. 5, but it is incompatible with the paper's plotted dashed
curve.

Replacing only the real exponential by (e^{-\pi\gamma/2}) gives

\[
|F_K|^2=\frac{4\pi Mk}{1-e^{-4\pi Mk}},
\]

and hence (|F_K|=7.0898) at (kM=4), matching the scale and growth of the
published first dashed panel.  Numerical probes are:

| (kM) | printed (e^{+\pi\gamma/2}) | figure-consistent (e^{-\pi\gamma/2}) |
|---:|---:|---:|
| 0.1 | 0.7071 | 1.3254 |
| 0.5 | 0.1084 | 2.5090 |
| 1.0 | 0.00662 | 3.5449 |
| 2.0 | (1.748\times10^{-5}) | 5.0133 |
| 3.0 | (3.999\times10^{-8}) | 6.1400 |
| 4.0 | (8.622\times10^{-11}) | 7.0898 |

This establishes an internal inconsistency between the printed Eq. (47) sign
convention and the plotted Fig. 5 curve.  It does **not** establish which line
in the authors' unavailable plotting code carried the typo.  The repository's
scientific Eq. (47) implementation was therefore not silently changed.

## 2. Red/blue triangles: the paper's Fig. 5 values overlap

A pixel-level audit of the original page raster found:

| region | red marker pixels | blue marker pixels |
|---|---:|---:|
| Fig. 5 amplitude axes | 4579 | 0 |
| Fig. 5 phase axes | 4731 | 0 |
| Fig. 5 legend | 34 | 32 |
| Fig. 6 amplitude axes | 3985 | 248 |
| Fig. 6 phase axes | 4487 | 32 |

Thus blue is present in the paper legend and elsewhere on the same raster, but
not in any of the eight Fig. 5 plot interiors.  The consistent explanation is
that the two marker centers are identical or closer than one raster pixel and
the red series was drawn last.  The PDF raster alone cannot distinguish exact
equality from sub-pixel equality.

The current calculation is qualitatively different: for the four near-axis
points, the maximum complex (|F_+-F_\times|) is respectively
(8.26,4.83,3.77,5.45).  Hiding the blue markers by drawing red on top would
therefore conceal a real scientific mismatch and is not an acceptable repair.

## 3. Polarization observable: definitive interface mismatch

The current production route stores

\[
F_+=h_+^{\rm lens}/h_+^{\rm flat},\qquad
F_\times=h_\times^{\rm lens}/h_\times^{\rm flat},
\]

where (h_+,h_\times) are Route-B incident-frame electric-tidal packaged
positive-frequency scalars.  The paper's Eq. (42), however, defines real-time
polarizations through real and imaginary parts of (Psi_4) and (Psi_0).
Turning that statement into two arbitrary complex positive-frequency
amplitudes requires a negative-frequency/reality convention that the paper
does not specify.

Under the direct complex lift of Eq. (42), the current Route-B values satisfy

\[
h_+^{\rm RB}=\tfrac12h_+^{\rm S}-\Psi_2/k^2,
\qquad
h_\times^{\rm RB}=\tfrac12h_\times^{\rm S}.
\]

Consequently the current (F_+) and (F_\times) need not overlap even if the
radial/Weyl solve is converged.  This observable bridge is the primary reason
the current blue and red triangles separate while the paper's Fig. 5 markers
overlap.  The exact convention used by the authors cannot be reconstructed
uniquely from the PDF alone.

## 4. Panel-by-panel amplitude comparison

Values digitized from the published red series were compared to the current
direct (F_+) and (F_\times).  The digitization is approximate, but the trend
is much larger than its uncertainty.

| point | (kM) | paper red | current (F_+) | current (F_\times) | (F_\times) relative difference |
|---|---:|---:|---:|---:|---:|
| (x=0,z=30) | 1.0 | 3.436 | 1.853 | 3.656 | +6.4% |
|  | 2.0 | 4.942 | 2.598 | 5.122 | +3.6% |
|  | 3.0 | 6.062 | 3.186 | 6.279 | +3.6% |
|  | 3.5 | 6.564 | 3.448 | 6.795 | +3.5% |
| (x=1,z=30) | 1.0 | 3.320 | 1.779 | 3.511 | +5.8% |
|  | 2.0 | 4.054 | 2.184 | 4.321 | +6.6% |
|  | 3.0 | 3.803 | 2.106 | 4.157 | +9.3% |
|  | 3.5 | 3.398 | 1.921 | 3.756 | +10.6% |
| (x=2,z=30) | 1.0 | 2.857 | 1.570 | 3.094 | +8.3% |
|  | 2.0 | 1.969 | 1.183 | 2.234 | +13.4% |
|  | 3.0 | 0.502 | 0.226 | 0.671 | +33.6% |
|  | 3.5 | 1.660 | 0.407 | 2.210 | +33.1% |
| (x=3,z=30) | 1.0 | 2.201 | 1.262 | 2.449 | +11.3% |
|  | 2.0 | 0.541 | 0.275 | 0.700 | +29.5% |
|  | 3.0 | 2.432 | 0.594 | 4.162 | +71.1% |
|  | 3.5 | 2.085 | 0.307 | 5.042 | +141.8% |

The current (F_\times) is fairly close on axis and at (x=1), while the
error grows strongly with offset and frequency.  The current (F_+) is not
the paper series in any panel.

The phase panels show the same qualitative split: the paper's red/blue centers
remain coincident to raster resolution, whereas the current two complex ratios
carry visibly different principal phases.  This is not caused by phase
unwrapping because neither rendering unwraps the phase.

## 5. Remaining high-frequency/off-axis mismatch

The stored runs pass their adjacent-(\ell_{\max}) convergence checks, contain
only finite values, and use the requested points and tolerances.  The growing
off-axis discrepancy is therefore not evidence of a simple plotting or
convergence failure.

The discrepancy becomes largest in the same frequency range where the bounded
high-(\ell) radial transition oracle is used (116 uses at (kM=3), 532 at
(kM=4)).  However, its frozen validation residuals are approximately
(10^{-15}) and its sensitivity probes approximately (10^{-7}).  This is a
correlation, not proof that the oracle causes the mismatch.  The remaining
scientific boundary should be recorded as an unresolved combination of the
paper's polarization/total-field convention and the high-frequency off-axis
reconstruction, pending author code/data or a convention-complete derivation.

## Ruled-out explanations

- wrong incident amplitudes;
- wrong Table-I coordinates or (eta);
- missing frequency samples or merge-order error;
- display interpolation, smoothing, normalization, or clipping;
- phase unwrapping;
- an obvious final-(\ell_{\max}) convergence failure;
- a global renderer omission of blue markers.

## Scientific disposition

1. Keep the printed Eq. (47) implementation and a separately named
   figure-consistent comparison if a repair is later authorized; do not
   overwrite one convention with the other.
2. Do not manufacture agreement by plotting (F_\times) twice or by changing
   marker order.
3. Treat Fig. 5 as calculation-complete but paper-equivalence unresolved until
   the complex positive-frequency observable bridge is derived or author data
   are obtained.

