# Schwarzschild perturbations review notes

Source PDF:
`references/papers/Gravitational perturbations of the Schwarzschild spacetime.pdf`

Role:
- Cross-check for tensor harmonics, RW gauge, and gauge-invariant master
  variables.
- Not the primary normalization source for this project.

## Harmonic conventions

The review formulates perturbations using scalar, vector, and tensor
spherical harmonics on the unit two-sphere. It emphasizes that tensor
harmonic definitions can differ from Regge-Wheeler by tracefree choices and
overall signs.

Project consequence:
- The angular module must own the scalar and spin-weighted harmonic
  convention.
- Tensor-basis conversion formulas must be documented separately from scalar
  harmonic normalization.

The review relates tensor spherical harmonics to spin-weighted harmonics
with a complex dyad on the unit sphere. This is useful for checking spin
weights and parity, but it is not a replacement for the target paper's
finite-radius Weyl-scalar formula.

## RW gauge cross-check

For even parity, the review shows that one can choose RW gauge with the
vector/tensor gauge components set to zero, so the surviving even variables
are the scalar metric functions. For odd parity, RW gauge sets the odd
rank-two angular component to zero, leaving the odd vector components.

This agrees qualitatively with the target-paper RW-gauge radiative content:

```text
odd:  Bt, B1
even: tt, Rt, L0, T0
```

for `l >= 2`.

## Master-variable caveat

The review uses Zerilli-Moncrief and Cunningham-Price-Moncrief
gauge-invariant master functions. These are valuable for conceptual checks
and asymptotic radiation formulas, but the project does not implement their
normalization directly in Phase 0.

Project convention:
- `psi_even` and `psi_odd` are the target-paper RW-gauge master variables
  defined in `docs/physics_spec.md` Sec. 4.
- If a later module uses Moncrief or Martel-Poisson variables for validation,
  the conversion factor must be written explicitly before code is changed.

## Useful checks

- Radiative perturbations start at `l >= 2`.
- Even and odd tensor harmonics are orthogonal.
- Gauge-invariant statements should not be confused with RW-gauge metric
  reconstruction formulas.
- Different references may use `mu = (l-1)(l+2)` where this project uses
  `lambda = mu/2`.
