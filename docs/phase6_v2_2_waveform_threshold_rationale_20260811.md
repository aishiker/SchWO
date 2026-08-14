# Phase 6 V2.2 waveform-threshold rationale

## Decision

V2.2 must not learn its acceptance thresholds from its own three-route output.
The threshold contract is therefore frozen before V2.2 execution and uses only
the immutable V1 selected radial acceptance evidence, the immutable external
odd-RW/even-Zerilli evidence, the accepted V2.1 normalization records, and the
V2.0 convention/domain authorities.

This is a bounded selected-domain rule.  It is not a full-domain V2
certification, a Li-figure gate, or a global GREEN decision.

## Observable and conditioning scale

For one frozen sector/mode/incident-column record, define the scattered
Martel--Poisson coefficient

\[
 H_{\rm sc}=F_p c_{\ell m}^{p}(-1)^\ell(1-S_\ell),\qquad
 F_{\rm even}=1,\quad F_{\rm odd}=\frac{2i}{\omega}.
\]

The fixed physical scale

\[
 C_{\rm record}=|F_p c_{\ell m}^{p}|
\]

comes entirely from the frozen incident normalization.  It is never fitted to
a candidate route.  Consequently

\[
 \frac{|H_i-H_j|}{C_{\rm record}}=|S_i-S_j|
\]

for the SchWO/external comparison.  This exact propagation is why the existing
V1 selected `backend_complex_S=2e-6` bound can supply an upstream error budget
without being silently relabelled as a waveform threshold.

Plain relative error is ill-conditioned when a scattered coefficient nearly
vanishes.  V2.2 therefore uses both a fixed-scale comparator and a conventional
relative-magnitude comparator.  Relative magnitude and wrapped phase are
mandatory only after a separately frozen signal-conditioning check.  The
conditioning floor is `rho=|H|/C_record >= 0.1`; falling below it is a gate
failure, not a way to omit a difficult record.

Before any V2.2 route existed, the immutable inputs gave minimum normalized
signals `0.21573803340039804` (SchWO) and `0.21573804826069762` (external).
The factor-of-two margin means the `0.1` floor is not tuned to a borderline
record.  The observed maximum SchWO/external difference,
`1.7268260316599918e-8`, is recorded only as a diagnostic and is not used as an
acceptance threshold.

## Frozen comparator bounds

For Routes A/B, both routes share one SchWO radial input.  Their purpose is to
catch a normalization, metric/curvature, tetrad, or `Psi4` map error.  The
fixed-scale complex and phase-invariant bounds are `1e-12`, a conservative
analytic/double-precision route-map envelope that remains six orders of
magnitude below the selected external radial bound.  With the `0.1` signal
floor, the corresponding relative-magnitude and geometric wrapped-phase
bounds are `1e-11` and `1.01e-11 rad`.

For Routes A/C, the fixed-scale complex and phase-invariant bounds are `2e-6`,
the explicit image of the already frozen V1 selected radial bound.  The
relative-magnitude bound is `2e-5`.  From

\[
 |z-w|^2=(|z|-|w|)^2+4|z||w|\sin^2(\Delta\phi/2)
\]

and `min(|z|,|w|)/C_record >= 0.1`, the phase bound is
`2 asin(2e-6/(2*0.1))`; `2.01e-5 rad` rounds it upward.

For Routes B/C, the threshold reserves the independently required A/B map
budget by the triangle inequality: `2e-6 + 1e-12 = 2.001e-6`.  Its relative
and phase bounds are `2.001e-5` and `2.011e-5 rad`.

The phase-invariant comparator is

\[
 D_{\rm invariant}=\frac{\bigl||H_i|-|H_j|\bigr|}{C_{\rm record}},
\]

which remains meaningful without accepting a shared absolute phase as a
convention-independent observable.  V2.2 therefore caps `absolute_phase` at
`PARTIAL`.  That limitation is nonblocking when the frozen inventory,
magnitude, phase-invariant and no-fit relative-phase gates pass.

## Nonclaims and execution boundary

- Every route must contain the exact same 120 records; no channel may be
  dropped because it is inconvenient.
- No phase or complex-scale fit is allowed.
- No radial solve, finite-radius observer frame, angular sum, total plane-wave
  sum at null infinity, or Li-figure rerun is allowed.
- Numerical and convention uncertainty budgets remain separate.
- Passing V2.2 means only that the selected three-route waveform coefficients
  are ready for the bounded V2.3 flux gate.  It does not make full-domain V1 or
  V2 GREEN.
