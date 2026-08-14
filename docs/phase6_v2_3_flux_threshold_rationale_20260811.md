# Phase 6 V2.3 flux-threshold rationale

## Decision boundary

V2.2 is already sufficient for bounded V2.3 entry.  Its accepted
`CLAIM_STATUS: PARTIAL` is the permitted absolute-phase limitation, not a flux
blocker.  V2.3 is phase invariant and does not attempt to repair or promote
absolute phase.

V2.3 nevertheless requires its own acceptance contract before execution.  The
contract is frozen from immutable V1, V2.1, V2.2 and external-direct evidence;
no V2.3 output exists or was used to choose a bound.  This is a selected
120-record mode-flux gate, not a full-domain V2 claim, an angular waveform
claim, a Li-figure gate or a global GREEN decision.

## Physical current and energy flux

For the frozen `exp(-i omega t)` convention, use

\[
 J=\frac{\Psi^*\partial_{r_*}\Psi-\Psi\partial_{r_*}\Psi^*}{2i}.
\]

At infinity and at the future horizon,

\[
 J_{\rm in}=-\omega |A_{\rm in}|^2,\qquad
 J_{\rm out}=+\omega |A_{\rm out,total}|^2,\qquad
 J_{\rm H}=-\omega |T_{\rm H}|^2.
\]

The Martel--Poisson mode flux for a complex peak amplitude representing a real
field is

\[
 F=\frac{\sigma_\ell\omega^2}{128\pi}|\Psi_{\rm MP}|^2,
 \qquad \sigma_\ell=\frac{(\ell+2)!}{(\ell-2)!}.
\]

Equivalently, a signed current maps to positive energy flux with

\[
 F=\frac{\sigma_\ell\omega}{128\pi}|J|.
\]

Every incoming, total-outgoing and horizon coefficient carries the same
physical `c_lm/A_in_raw` normalization and the parity-specific MP bridge.  In
the odd sector this includes `Psi_CPM=(2i/omega) Psi_RW`.  These common factors
cancel in incident-normalized flux fractions but remain explicit in every
record so that a missing factor of two, `omega`, `omega^2` or `sigma_l` fails
closed.

The only balance equation accepted by V2.3 is

\[
 F_{\mathscr I^-}=F_{\mathscr I^+,\,\mathrm{total}}+F_{\mathcal H^+}.
\]

The free and scattered fields interfere.  Their separately squared fluxes may
be stored as diagnostics, but scattered-only outgoing flux is never a positive
term in this balance equation.

## Frozen bounds

The internal SchWO balance residual retains the already frozen V1 value
`1e-8`.  The independent direct RW/Zerilli balance retains its already frozen
unitarity value `1e-15`.

The waveform/current and Route-A/Route-B map bounds are `2.1e-11`.  This is the
upward-rounded quadratic image `2 epsilon + epsilon^2` of the pre-frozen V2.2
relative-amplitude route-map allowance `epsilon=1e-11`.  It is an algebraic
map budget, not a new radial tolerance.

For SchWO versus external total-outgoing flux fractions, V1 already freezes
`|S_s-S_e| <= 2e-6`.  With unit incident flux and `|S| <= 1` up to the separately
budgeted radial residual,

\[
 \bigl||S_s|^2-|S_e|^2\bigr|\leq 2\epsilon+\epsilon^2.
\]

The rounded V2.3 bound is therefore `4.1e-6`.

For the horizon fraction, V1 freezes
`|log|T_s|-log|T_e|| <= 2e-6`.  Squaring the amplitude gives a worst-case ratio
`exp(2 epsilon)`; the upward-rounded symmetric-relative flux bound is again
`4.1e-6`.

The immutable inputs were inspected before V2.3 execution only to establish
conditioning and arithmetic requirements.  The smallest selected horizon
fraction is about `9.37e-1498`; hence binary64 would silently underflow and is
forbidden for the mandatory horizon comparison.  Arbitrary-precision decimal
arithmetic must retain all 120 records.  This observed value is not an
acceptance threshold and supplies no permission to drop a high-ell item.

## Acceptance and nonclaims

- All 120 records, both parities, both `m` values and both incident columns are
  mandatory.
- Positive physical fluxes, signed-current orientation, normalization factors,
  finite values and `radial_solve_count=0` are exact predicates.
- Numerical and convention uncertainty budgets remain separate.
- Absolute phase remains `PARTIAL`; flux closure may still advance under the
  frozen review-gate liveness protocol.
- Passing V2.3 means only selected-domain infinity/horizon/radial flux closure
  is ready for V2.4.  Full-domain V2 remains `NOT_ASSESSED`, and no global GREEN
  is permitted.
