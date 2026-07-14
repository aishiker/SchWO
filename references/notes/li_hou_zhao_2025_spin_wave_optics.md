# Li-Hou-Zhao 2025 spin-wave optics notes

Source PDF:
`references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`

Role:
- Primary implementation target for the first Schwarzschild GW wave-optics solver.
- Project conventions in `docs/physics_spec.md` v0.1 follow this paper unless a caveat is explicitly listed.

## Convention summary

The paper uses geometric units `G = c = 1`, Schwarzschild coordinates
`x^mu = (t,r,theta,phi)`, Cartesian coordinates
`xhat^mu = (t,x,y,z)`, and frequency-domain factors `exp(-i k t)`.

For positive `k`, the project therefore fixes:

```text
partial_t -> -i k
partial_t^2 -> -k^2
exp(-i k r_star) = ingoing radial factor
exp(+i k r_star) = outgoing radial factor
```

The Schwarzschild background and tortoise coordinate are taken from
Eqs. (1) and (13):

```text
f(r) = 1 - 2M/r
r_star = r + 2M log(r/(2M) - 1)
```

## Perturbation basis and RW gauge

The paper decomposes the metric perturbation into frequency modes and ten
tensor-harmonic components:

```text
{tt, Rt, L0, T0, Et, E1, Bt, B1, E2, B2}
```

Appendix A defines the tensor basis and normalization constants. The parity
split is:

```text
even: {tt, Rt, L0, T0, Et, E1, E2}
odd:  {Bt, B1, B2}
```

Appendix B gives the gauge transformation rules. For radiative `l >= 2`,
RW gauge leaves:

```text
odd:  Bt, B1
even: tt, Rt, L0, T0
```

and fixes:

```text
B2 = 0
Et = E1 = E2 = 0
```

The project ignores lower multipoles `l = 0,1` in the first-stage radiative
solver.

## Master variables and potentials

The project uses the paper's RW-gauge master-variable normalization:

```text
psi_tilde^(-)_{lm} = -f(r)/r * h_tilde^{(B1)}_{lm}

psi_tilde^(+)_{lm}
  = 1/Lambda * [ h_tilde^{(T0)}_{lm}/r
                 + f(r)/(i k) h_tilde^{(Rt)}_{lm} ]

Lambda = lambda + 3M/r
lambda = (l-1)(l+2)/2
```

These master variables satisfy:

```text
[d^2/dr_star^2 + k^2 - V_l^(±)(r)] psi_tilde^(±)_{lm} = 0
```

with the odd Regge-Wheeler and even Zerilli potentials listed in
`docs/physics_spec.md` Sec. 5. The paper's formula is algebraically the same
as the implemented `lambda = (l-1)(l+2)/2`, `Lambda = lambda + 3M/r` form.

## Incident plane wave

The default incident wave propagates along `+z`:

```text
h_tilde^(0)_mu_nu(k,r) = A_tilde_mu_nu(k) exp(i k r cos(theta))
A_xx = -A_yy = A_plus
A_xy = A_yx = A_cross
```

Circular amplitudes:

```text
A_L = (A_plus + i A_cross)/sqrt(2)
A_R = (A_plus - i A_cross)/sqrt(2)
```

The `+z` choice implies the `m = ±2` selection rule:

```text
sigma_l = (l-1) l (l+1) (l+2)

A_lm^(±)
  = i^l sqrt(2 pi (2l+1)/sigma_l)
    (A_L delta_{m,-2} ± A_R delta_{m,2})

c_lm^(-) = -[i^(l+1)/2] A_lm^(-)
c_lm^(+) =  [i^(l+1)/k] A_lm^(+)
```

The parentheses around powers of `i` are part of the convention and must be
tested directly.

## Metric reconstruction

The paper summarizes RW-gauge reconstruction operators in Eq. (29):

```text
h_tilde^{(a)}_{lm}(k,r) = J_hat_l^{(a)}(k,r) psi_tilde^(±)_{lm}
```

The operators act on the master function and its radial derivative. In the
project, reconstruction formulas belong only in the perturbation
reconstruction module and must not be duplicated in Weyl or plotting code.

## Weyl scalars and tetrads

Weyl scalars are first computed in the Schwarzschild Kinnersley tetrad:

```text
l^mu = (f^(-1), 1, 0, 0)
n^mu = (1/2) (1, -f, 0, 0)
m^mu = (1/(sqrt(2) r)) (0, 0, 1, i csc(theta))
```

The paper then transforms to a Cartesian tetrad aligned with the incident
`+z` null direction:

```text
lhat^muhat = (1/sqrt(2)) (1, 0, 0,  1)
nhat^muhat = (1/sqrt(2)) (1, 0, 0, -1)
mhat^muhat = (1/sqrt(2)) (0, 1, i,  0)
```

The transformation uses Wigner-D functions. The paper's notation is not a
complete standalone software convention for all Wigner-D phase choices, so
the project freezes the implementation convention in `docs/physics_spec.md`
Sec. 1.2 and requires wrapper tests for any library.

## Polarization extraction

The paper defines observable plus/cross accelerations through geodesic
deviation:

```text
hddot_plus  = Re(Psi_hat_4) + Re(Psi_hat_0)
hddot_cross = -(Im(Psi_hat_4) - Im(Psi_hat_0))
```

With the project Fourier factor `exp(-i k t)`, the stored complex amplitudes
are:

```text
h_plus_tilde  = -(Psi_hat_4_tilde + Psi_hat_0_tilde)/k^2
h_cross_tilde = -i(Psi_hat_4_tilde - Psi_hat_0_tilde)/k^2
```

This relation is a convention-sensitive sign trap and must be covered by
the no-lens flat-limit polarization test.

## Traps for implementation

- Do not replace the finite-radius partial-wave sum with asymptotic
  scattering amplitudes as the main algorithm.
- Do not mix the paper's tensor-basis normalization with unit-sphere scalar
  harmonic normalization inside the angular API.
- Do not silently switch from the paper's `exp(-i k t)` convention.
- Do not import a Wigner-D or spin-weighted harmonic library without a
  wrapper test proving the scalar limit and conjugation convention.
- Do not treat the incident-aligned tetrad as a unique local propagation
  direction of the scattered finite-radius field.
