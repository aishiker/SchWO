# Phase 6 V2.2 v2 three-route asymptotic waveform evidence

## Bounded observable

This implementation evaluates exactly the accepted 120 selected-domain
mode/channel/incident-column records.  It stores the future-null-infinity
scattered Martel--Poisson master coefficient

```text
H_sc = F_sector c_lm (-1)^ell (1-S_l),
F_even=1,  F_odd=2 i/omega,
C_record=abs(F_sector c_lm).
```

There is no observation angle, angular or `m` sum, finite-radius observer,
total-plane-wave sum, radial solve, or Li-figure operation.  `C_record` is
fixed by the accepted incident normalization and is never fitted.

## Route definitions

Route A reads the accepted V2.1 SchWO Li scattered coefficient and applies
the frozen ZM/CPM bridge.

Route C reads the immutable external `wp60` node `phase_factor` as `S_l`.
The source root records direct Regge--Wheeler for odd parity and independently
solved Zerilli for even parity (`parity_derived_even_used=false`).  It shares
the frozen analytic incident, Fourier, Jost-phase and MP conventions, but no
SchWO radial numerical result.

Route B is separately coded from the frozen RW-gauge reconstruction and
large-`r` curvature formulas.  Write the outgoing Li master coefficient as
`q exp(+i omega r_star)[1+O(1/r)]`.  After factoring out the common radial
exponential and tensor harmonic, the RW-gauge metric leading coefficients are

```text
odd:  Bt/r -> q,              B1/r -> -q,
even: T0/r^2 -> i omega q,    Rt/r -> omega^2 q,
      L0/r -> -omega^2 q,     tt/r -> -omega^2 q.
```

The direct Kinnersley `Z4` large-radius limit then gives

```text
odd:  r Z4_K -> -(omega/2) q
               = -(omega/2)(Bt/r) = +(omega/2)(B1/r),
even: r Z4_K -> -(omega^2/4) q
               = (tt/r)/4 = -(Rt/r)/4 = (L0/r)/4.
```

Both independent metric-component expressions are evaluated and their
complex consistency residual is stored.  The angular factor
`sqrt(sigma_l) {}_-2Y_lm` is deliberately left symbolic, so no angle is
introduced.  The frozen symmetric outgoing tetrad is related to the
Kinnersley limit by exactly

```text
Psi4_symmetric = 2 Psi4_K.
```

Using `Psi4_symmetric=-omega^2(h_plus-i h_cross)` and the frozen MP angular
coefficient, Route B recovers

```text
even: H_sc = -2 (r Z4_symmetric)/omega^2,
odd:  H_sc =  2 (r Z4_symmetric)/(i omega^2).
```

Thus Route B reaches ZM/CPM through RW metric and curvature intermediates; it
does not copy Route A's final coefficient and does not call the forbidden
finite-radius or legacy NP APIs.

## Frozen comparisons and claims

Every record evaluates all four contract comparators for A/B, A/C and B/C,
plus the mandatory `rho>=0.1` signal floor.  The exact threshold path,
SHA-256 and field are stored with every value and PASS/FAIL state.  No phase,
complex scale, unwrap offset, or per-mode adjustment is allowed.

Numerical and convention uncertainty budgets remain separate.  Absolute
phase is stored as `PARTIAL` exactly as frozen, even when all no-fit relative
phase, magnitude, phase-invariant and complex comparisons pass.  Full-domain
V2, flux closure, finite-radius response, angular waveforms and global GREEN
remain unassessed or forbidden; full-domain V1 independent certification
remains `PARTIAL`.
