# Phase 6 V2.0 convention freeze

Date: 2026-08-10

## State and stop boundary

V2.0 is a zero-science convention phase.  It freezes the analytic map needed
to compare three future asymptotic routes, but it does not execute those
routes and does not accept an infinity waveform or flux.  Existing V2
implementation primitives and the 2026-08-08 selected witness remain
precursors only; in particular, the finite-radius metric roundtrip must not be
promoted to an infinity-waveform result.

Machine-readable authorities:

```text
configs/phase6_v2_0_convention_contract_20260810.json
  1251392e0799ebafad91d832a128a6ad93a4d9dacf1a07a4fa50f5af2b119517
configs/phase6_v2_0_selected_domain_20260810.json
  9703286b02544b1c28b45250dec9bad0475d0196d857517f5c2ec3ee03afa818
```

The prose equation map is `docs/equation_map.md`, section
“Phase 6 V2.0 asymptotic normalization boundary”.  The repaired V1 entry gate
is `docs/phase6_v1_to_v2_transition_gate_20260810.md`.

The contract also binds seven protected radial-backend files and the
authoritative D_union plan by exact SHA-256.  This is necessary because the
historical worktree is already dirty: future T6/T7 reviews must rehash those
bytes before and after their work instead of inferring provenance from a git
diff.

## Frozen assumptions

- vacuum Schwarzschild radiative modes with `ell>=2`;
- metric signature `-+++`, `G=c=M=1` for selected evidence while formulas
  retain `M` explicitly;
- positive frequency `omega>0` and Fourier factor `exp(-i omega t)`;
- identical unit-normalized Condon--Shortley scalar harmonics;
- Li's odd vector harmonic is `-X_A` in the Martel--Poisson convention;
- no empirical amplitude, phase, sign, tortoise-offset, or normalization fit.

## Master normalization

For each `(ell,m)` coefficient separately,

```text
Psi_ZM  = psi_Li_even,
Psi_RW  = psi_Li_odd,
Psi_RW  = (1/2) partial_t Psi_CPM,
Psi_CPM = (2 i / omega) psi_Li_odd.
```

The last equality follows from the preceding time-domain identity and the
frozen Fourier sign.  The conversion is applied separately to incoming,
total outgoing, free outgoing, scattered outgoing, and horizon amplitudes;
it does not rename variables inside the radial backend.

## Absolute phase and mode definitions

The black hole is at the coordinate origin.  A `+z` incident plane wave uses
the right-handed Cartesian basis, `theta` is measured from `+z`, and `phi=0`
is the `+x` half-plane.  Its positive-frequency field is
`(A_plus,A_cross) exp[-i omega(t-z)]` and has zero phase at `t=z=0`.  The
frozen unit columns are `(1,0)` and `(0,1)`.  The exact `A_L/A_R`,
`A_lm^(plus/minus)`, and `c_lm^(plus/minus)` formulas are frozen in the
machine contract and `src/schwgw/waves/incident.py`.

```text
r_star = r+2M log(r/(2M)-1),   C_r_star=0,
u=t-r_star,                    v=t+r_star,
S_l=-A_out_raw/[(-1)^ell A_in_raw].
```

The production Jost factors include their recorded finite `1/r` series.
Their incoming, outgoing, and horizon leading coefficients are exactly one;
no later complex rescaling is permitted.  Bare exponentials are not silently
substituted.  The free reference has
`S_l=1`.  For parity `p`, the physical incident-plane-wave normalization is
`N_lm^p=c_lm^p/A_in_raw`; therefore

```text
A_in_physical            = c_lm^p,
A_out_total_physical     = c_lm^p A_out_raw/A_in_raw,
A_out_free_physical      = -(-1)^ell c_lm^p,
A_out_scattered_physical = (-1)^ell c_lm^p(1-S_l),
T_horizon_physical       = c_lm^p T_horizon_raw/A_in_raw.
```

Only `A_out_scattered_physical exp(+i omega r_star)` may contribute to a
per-mode future-null-infinity waveform.  After the Fourier factor is restored,
it has retarded dependence `exp(-i omega u)`.  The transmitted horizon mode
has advanced dependence `exp(-i omega v)`.  Neither the incoming mode nor a
total plane-wave partial-wave sum is placed at null infinity.

## Angular, strain, curvature, and flux conventions

The spin harmonics are frozen as

```text
{}_sY_lm=(-1)^s sqrt((2l+1)/(4pi))
          conjugate[D^l_{m,-s}(phi,theta,0)].
```

With `sigma_l=(l-1)l(l+1)(l+2)`, the Martel--Poisson angular identities and
the infinity/horizon plus/cross signs are those written exactly in the
machine contract and equation map.  Plus/cross refer to the outward
right-handed asymptotic `(e_theta,e_phi)` dyad.  They are not finite-radius
observer-frame outputs.  The normalized null tetrad is

```text
l=(e_0+e_r)/sqrt(2),       n=(e_0-e_r)/sqrt(2),
m=(e_theta+i e_phi)/sqrt(2),   mbar=conjugate(m),
l dot n=-1,                m dot mbar=+1.
```

No residual boost or spin rotation is allowed.  With
`Psi4=-C(n,mbar,n,mbar)` and the frozen strict-NP/Riemann convention,

```text
Psi4=-omega^2(h_plus-i h_cross).
```

The asymptotic Kinnersley tetrad has
`l_K=sqrt(2)l`, `n_K=n/sqrt(2)`, and therefore `Psi4_K=Psi4/2`.  Route B must
either contract curvature directly into the frozen symmetric tetrad or apply
the exact factor two to a raw Kinnersley scalar and record that conversion.

For complex peak amplitudes representing a physical real field, the explicit
time-average factor is `1/2`, so both infinity and horizon angle-integrated
fluxes carry `omega^2/(128 pi)` times the Martel--Poisson mode norm.  Raw
radial Wronskian flux is compared only after the same master normalization
and incident-mode normalization have been applied.

The existing finite-`areal_scale` Martel--Poisson strain helper is only an
algebraic precursor.  V2 infinity results must store the explicit coefficients
`H_plus/H_cross=lim_(r->infinity) r h_plus/cross`; a finite-radius helper call
cannot be relabeled as an infinity limit.

## Selected V2.0 domain

The radial inventory is the independently reviewed external 30-key domain,
not the full V1 domain.  It consists of 15 exact `(kM,ell)` odd/even pairs and
is lifted to `m=-2,+2`, giving 60 explicitly qualified mode channels per
incident unit column.  The two unit columns give 120 route-mode-column records
per future route before boundary/diagnostic ladders.  Observation angles are
deferred.  This sparse kernel inventory is not a complete angular partial-wave
sum and cannot produce a scientific `2x2` transfer matrix in V2.0.  Comparison
and certification remain per mode and per input column.  No summed total
incident plane wave is constructed at null infinity.

Published boundary identifiers are `future_null_infinity` and
`future_event_horizon`; the precursor API's `event_horizon` spelling is an
explicit alias for the latter, not a separate boundary.

The three future routes are:

1. repaired SchWO Li masters through the frozen Martel--Poisson map;
2. RW metric reconstruction followed by direct large-radius curvature/Psi4;
3. external independent odd-RW/even-Zerilli amplitudes through the same
   analytic Martel--Poisson map.

Routes 1 and 2 share the same SchWO radial/master input, so route 2 is an
observable-route cross-check rather than a radial-algorithm-independent solve.
Routes 1 and 3 have independent radial algorithms but share the analytic MP,
angular, Fourier, incident-normalization, Jost-phase, and flux conventions.
Routes 2 and 3 differ algorithmically but share those comparison conventions.
Every pair must carry its exact shared-source ledger; no pair is called fully
independent without that qualification.

Every future result must carry distinct numerical and convention uncertainty
budgets.  Missing components remain `NOT_ASSESSED` or `PARTIAL`, never zero,
and neither budget may be hidden in a combined scalar.  V2.0 creates no
scientific result to accept.

## V2.0 completion criterion

V2.0 stops when this contract, the equation map, selected domain, and the T6
and T7 executable prompts receive independent read-only review.  The next
step, if separately authorized, is bounded V2.1 implementation/evidence.  It
must use fresh artifacts and must not modify the radial backend or rerun Li
figures.
