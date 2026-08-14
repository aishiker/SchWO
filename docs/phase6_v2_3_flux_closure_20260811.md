# Phase 6 V2.3 selected-domain flux closure

## Bounded summary precision-provenance repair

The current V2.3 authority is the immutable control-plane repair root

```text
runs/phase6/asymptotic_waveform/v2_3_flux_closure_v2_20260811T050013_py314
```

The V2 repair places all summary-extrema parsing, comparison and serialization
inside an explicit `mp.workdps(100)` context.  A regression beginning at
ambient `mp.dps=15` proves that the corrected summary and report are
byte-identical to those constructed from ambient `mp.dps=100`, that every
stored summary extremum equals the exact 100-dps extremum of the canonical
record strings, and that ambient precision is restored on exit.

The corrected minimum external horizon fraction is
`9.373615409990476292528436114160436756813021669668934587236550056169801667903105000000000000000000000e-1498`.
The corrected maximum SchWO and external balance residuals are respectively
`2.456693814984740735626905876280748921163992416622833176415819278372141073001165780195065440402033493e-10`
and
`1.507593570579673192937307132619084520714038294582231000000000000000000005723877939848698251816805805e-29`.

The V2 `records.jsonl` is byte-identical to the predecessor V1 records, with
the same SHA-256
`ba8617224c89c7122e27d0399dafc510d126dd2b4cfd0ca2d8f741ae2a454d39`.
No formula, threshold, input, record, predicate, uncertainty vocabulary,
scientific result or claim ceiling changed.  The immutable V1 root remains
preserved as superseded evidence and is forbidden as current V2.3 authority.

## Scope

V2.3 evaluates exactly the accepted 120 selected-domain
`(radial key, m, incident column)` records.  It consumes immutable V2.1,
V2.2-v3, selected SchWO V1 and external direct RW/Zerilli evidence.  It does
not call a radial solver, select an observation angle, perform an angular sum,
or run a Li figure.

All mandatory complex coefficients, currents, fluxes, fractions and residuals
are evaluated inside `mp.workdps(100)`.  Original external `wp60` decimal
strings are parsed only after entering that context.  The surrounding ambient
precision is restored on exit.  No mandatory quantity is converted to
binary64.

## Normalization and balance

For every record, the Li incident coefficient is normalized by

\[
N_{\ell m}^{p}=c_{\ell m}^{p}/A_{\rm in,raw}.
\]

The even-sector Martel--Poisson bridge is one.  The odd-sector bridge is
\(\Psi_{\rm CPM}=(2i/\omega)\Psi_{\rm RW}\) under
\(\exp(-i\omega t)\).  The explicit real-field-peak time-average is `1/2`.
The signed currents and positive energy flux are

\[
J_{\rm in}=-\omega|A_{\rm in,MP}|^2,\quad
J_{\rm out}=+\omega|A_{\rm out,total,MP}|^2,\quad
J_{\mathcal H}=-\omega|T_{\mathcal H,MP}|^2,
\]

\[
F=\frac{\sigma_\ell\omega|J|}{128\pi}
 =\frac{\sigma_\ell\omega^2|\Psi_{\rm MP}|^2}{128\pi},\qquad
\sigma_\ell=\frac{(\ell+2)!}{(\ell-2)!}.
\]

Route A and Route B each reconstruct the total outgoing coefficient as the
frozen free coefficient plus its accepted scattered coefficient.  Only this
total enters

\[
F_{\mathscr I^-}=F_{\mathscr I^+,\mathrm{total}}+F_{\mathcal H^+}.
\]

Free and scattered squares are retained solely as nonadditive interference
diagnostics.  A scattered-only square never enters a balance predicate.

The external direct files store the unit-incident scattering coefficients as
`A_in=1`, `A_out=reflection_ratio`, and `T_horizon=transmission`.  Their
matching-basis `incidence` and `reflection` values are retained separately as
source provenance.  This distinction is required for the external unit-flux
identity.

## Frozen predicates and claim ceiling

Every record applies all six numeric bounds from
`configs/phase6_v2_3_flux_threshold_contract_20260811.json`, including both
radial balances, the waveform/current map, the Route-A/Route-B total-outgoing
map, and the SchWO/external outgoing and horizon comparisons.  All 120 records
are mandatory; there is no signal floor.  The smallest external horizon flux
fraction remains approximately `9.373615409990476e-1498` and is positive.

The accepted result is limited to selected-domain flux closure.  Absolute
phase remains `PARTIAL`; full-domain V2, angles and angular sums, finite-radius
observer responses, Li figures and global GREEN are not assessed.
