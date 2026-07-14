# Q018 Note: Scalar Finite-Radius Partial-Wave Cutoff

Source:
- Zhao Li and Wen Zhao, "Rigorous calculation of scalar scattering in Schwarzschild background: the convergence of partial-wave series and Poisson spot", arXiv:2508.17253.
- Local extracted memory: `arxiv-reading/2508.17253.memory.md`.
- Public links: https://arxiv.org/abs/2508.17253 and https://ar5iv.labs.arxiv.org/html/2508.17253.

## What the paper establishes for scalar waves

The paper studies finite-radius scalar partial-wave scattering in weak-field
and Schwarzschild backgrounds.  Its central numerical lesson for this project
is:

```text
finite-radius scalar PWS naturally truncates around ell_max ~ k r
```

The reason is not just empirical.  The exact finite-radius spherical-Bessel
plane-wave expansion is convergent, while the asymptotic radial expansion is
valid only for `k r >> ell`.  Therefore applying an asymptotic expansion to
`ell ~ k r` modes creates artificial divergence.  In the finite-radius
calculation, modes with `ell` much larger than `k r` have turning points
outside the observer radius and are suppressed by the centrifugal barrier.

For Schwarzschild scalar scattering the paper uses the spin-0 RW potential:

```text
V_ell = f(r) [ell(ell+1)/r^2 + 2M/r^3].
```

At large `ell`, the leading term is the centrifugal barrier.

## Relevance to the gravitational-wave solver

The current project uses RW/Zerilli spin-2 master equations.  Their large-ell
potentials share the same leading centrifugal scaling:

```text
V_RW, V_Zerilli ~ f(r) ell(ell+1)/r^2
```

so the scalar result is a strong prior that the finite-radius gravitational
partial-wave sum should not require solving modes far beyond the largest
observer `k r` scale, provided the omitted tail is bounded and recorded.

The result is not a complete proof for this project because the gravitational
observable includes:

- parity odd/even master variables;
- metric reconstruction operators;
- tensor/spin-weighted angular factors;
- Weyl/tidal packaged scalar extraction;
- possible spin-dependent prefactors near the cutoff band.

Therefore the scalar rule can guide Q018, but T4/T7 must validate the
spin-2-specific cutoff or tail bound before accepting it.

## Q018 application

For the current T8k failure:

```text
kM = 2
x,z in [-30M,30M]
rmax = sqrt(30^2 + 30^2) M ~= 42.43M
k rmax ~= 84.85
failure: sector=odd, ell=153, r_out=300M
barrier action S ~= 706.303
exp(-S) ~= 1.8e-307
```

This is far beyond the scalar finite-radius support scale for the saved grid.
It is also near the dynamic-range limit of double precision.  The most likely
correct direction is not to force a direct radial solve for `ell=153`, but to
define a structured high-ell evanescent-tail policy:

1. determine an effective observer scale, e.g. `k r_max` for the saved grid;
2. bracket a conservative cutoff band above that scale;
3. bound the omitted contribution to `h_plus/h_cross`;
4. record requested `lmax`, effective radial `ell` range, tail bound, and
   trigger criteria in result metadata;
5. require T7 independent review.

This must not be implemented as a silent `lmax` reduction.

## Implementation caution

The paper itself says the full gravitational-wave extension, including gauge,
polarization distortions, and helicity issues, remains future work.  Therefore
T4k should use this note as a physical/numerical guide, not as a direct
replacement for gravitational-wave validation.
