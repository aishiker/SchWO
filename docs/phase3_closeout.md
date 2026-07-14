# Phase 3 Closeout: Metric Reconstruction, Weyl, and Polarization

Date: 2026-07-05

## Scope and Status

Phase 3 is physically closed. Q014 is resolved by T7f independent validation
and must not be reopened by API hardening work.

Q015 remains a separate non-blocking radial diagnostic warning. It concerns a
low-`k` transition-regime Wronskian/flux diagnostic and is not a Q014
polarization-bridge failure.

Q016 high-`ell` Wigner-D overflow is resolved and revalidated. The angular
layer can reach the high-`ell` windows needed by the saved-result workflow.

## Convention Boundaries

Strict NP scalars are Weyl tensor tetrad contractions:

```text
Psi0_NP = -C(l,m,l,m)
Psi1_NP = -C(l,n,l,m)
Psi2_NP = -C(l,m,n,mbar)
Psi3_NP = -C(l,n,n,mbar)
Psi4_NP = -C(n,mbar,n,mbar)
```

Packaged polarization scalars are positive-frequency recovery variables. They
are not strict NP scalars in general and must not be transformed by strict
NP tetrad rules.

Electric tidal components define Route B production packaging:

```text
E_xx = C(e0,ex,e0,ex)
E_xy = C(e0,ex,e0,ey)

Psi4_pack = -E_xx + i E_xy
Psi0_pack = -E_xx - i E_xy
```

## Route B Production Invariant

Production finite-radius polarization follows:

```text
strict NP full quintuple
  -> incident-frame electric tidal projection / packaged scalars
  -> polarization extraction
```

Raw strict `Psi0_NP/Psi4_NP` must not be passed directly to packaged
polarization extraction.

## Forbidden Shortcuts

- No same-positive-`k`, same-`m` literal conjugation for Li-Hou-Zhao
  Eq. (35g)-(35h).
- No strict two-scalar shortcut for curved finite-radius production.
- No promotion of the flat type-N/helicity diagnostic to curved production.
- No plotting-side physics formulas.
- No validation-threshold relaxation.

## Validation Evidence

Route B is active in the production path. The flat diagnostic is genuine:
it uses the T5 flat master functions, T6 metric reconstruction, Weyl mode
components, strict-NP transform/package bridge, and polarization recovery
rather than the direct Cartesian oracle as its actual result.

T7f final adjacent-pair convergence passed:

```text
k=0.5: final lmax 24->28, max change 4.43e-8
k=0.2: final lmax 18->22, max change 8.61e-11
```

Near-axis final-pair convergence also passed.

## Open Issues

Q015 structured metadata remains diagnostic hardening unless completed
elsewhere. It must remain separate from Q014.

Transmission normalization Q005 remains future M5 work.
