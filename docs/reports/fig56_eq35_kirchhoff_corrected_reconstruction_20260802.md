# Fig. 5/6 corrected Kirchhoff and inferred-\(F\) reconstruction (2026-08-02)

## Status

This is a **reproduction diagnostic**, not a claim that the missing author
implementation has been uniquely recovered.  It keeps the original Table-I
geometry, the 40 direct frequencies \(kM=0.1,0.2,\ldots,4.0\), the accepted
per-frequency final \(l_{\max}\) pairs, the radial solver, and all boundary
tolerances.  There is no interpolation or smoothing of the scattering data.

The corrected hypothesis consists of two changes:

1. The Kirchhoff curve uses
   \[
   \exp(-\pi\gamma/2),\qquad \gamma=-2Mk,
   \]
   rather than the printed positive sign in the exponential.
2. The scattering calculation assembles all five strict Newman--Penrose
   scalars, applies the literal stars printed in Li--Hou--Zhao
   Eqs. (35g)--(35h), transforms to the incident tetrad, and forms the complex
   positive-frequency continuation of Eq. (42).  The plotted
   \(F_+\) and \(F_\times\) are the two pure-input diagonal response columns,
   divided by their corresponding Eq. (46) incident plane waves.

The second item is the form that best reproduces the published markers among
the tested candidates.  It remains an inference: a formally complete
real-field treatment of the stars in Eqs. (35g)--(35h) involves the
\((-k,-m)\) reality partners.  Treating the stars as same-
\((+k,m)\) conjugation is therefore a figure-reproduction hypothesis, not a
new physics result.

## Numerical production

- 40/40 direct frequencies completed transactionally.
- Eight Table-I observation points per frequency.
- Full two-row final-\(l_{\max}\) histories retained for both polarizations.
- Maximum adjacent-final-pair relative difference:
  \(4.4811981434466694\times10^{-10}\), below the frozen \(10^{-4}\) gate.
- Sum of per-frequency runtimes: 17,528.10 s (4.87 h); four-way independent
  frequency execution reduced the observed transaction span to 4,405.55 s
  (1.22 h).
- Merged data SHA-256:
  `b1dc8898ef8b29b55daddc54668a95b4d47fcbe752992dc23d9a43ab2968bd38`.

Primary merged data:

`runs/phase5/fig5_fig6_paper_inferred_eq35_literal_probe_20260802/tablei_uniform40_eq35_literal_merged.npz`

## Comparison with the published raster

The comparison script digitizes the published red markers from the frozen
1700-by-2200 page raster.  This is a raster-level diagnostic; it is not
source-data ground truth.  Its approximate vertical resolutions are 0.0386
for Fig. 5 magnitude, 0.0154 for Fig. 6 magnitude, and 0.0303 rad for phase.

Across 319 magnitude and 320 phase samples:

| candidate | magnitude MAE | magnitude RMSE | circular phase MAE | circular phase RMSE |
|---|---:|---:|---:|---:|
| old Route-B | 0.5281 | 0.7536 | 1.9779 rad | 2.0654 rad |
| corrected Eq. (35) diagonal response | **0.3713** | **0.4952** | **1.1405 rad** | **1.3665 rad** |

The median red/blue magnitude separation falls from 0.8624 to 0.0456.  The
maximum magnitude separation falls from 4.8575 to 0.3395.  This explains why
the revised Fig. 5 now reproduces the near-overlap of the published red and
blue markers.

Panel-wise corrected magnitude MAE, in Fig. 5 panel order followed by Fig. 6,
is

`[0.3176, 0.1733, 0.3095, 0.7349, 0.4841, 0.3694, 0.3375, 0.2408]`.

Panel-wise corrected circular phase MAE is

`[0.5601, 0.7979, 0.8287, 1.1274, 1.0289, 1.4440, 1.7050, 1.6317] rad`.

### What is now aligned

- The corrected Kirchhoff magnitude is oscillatory in Fig. 6 instead of
  spuriously decaying rapidly to zero.
- Its oscillation count and qualitative phase-wrap structure agree with the
  published Fig. 5/6 curves.
- Fig. 5 scattering-marker envelopes and red/blue overlap are substantially
  closer to the paper, especially the first three columns.

### What is not yet exactly aligned

- Fig. 5 column four retains a high-frequency peak/height mismatch.
- Fig. 6 scattering magnitudes remain more irregular than the published
  nearly unit-amplitude sequence.
- Fig. 6 scattering phases retain order-one circular errors, largest in the
  last three columns.
- The paper raster is consistent with essentially identical red/blue marker
  coordinates, while the corrected reconstruction still has a finite
  high-frequency separation.

Adding the off-diagonal response to represent simultaneous mixed
\((A_+,A_\times)\) incidence was tested from the stored response matrix without
new ODE solves.  It is decisively worse: for example, at \(kM=1\) it drives
the near-axis \(F_\times\) magnitude to about 7 where the paper is about 3.
That candidate is therefore rejected.

## Conclusion

The prefactor sign explains the previous Kirchhoff mismatch.  The literal
Eq. (35) diagonal-response hypothesis explains much, but not all, of the
scattering-marker mismatch.  The residual cannot honestly be removed without
either the authors' exact analytic-signal/reality bridge and \(F\)-assembly
code, or additional source data.  These figures should be labelled
**corrected inferred reconstruction**, not exact reproduction.
