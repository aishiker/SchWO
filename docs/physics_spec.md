# Physics specification

版本：v0.1-frozen

更新时间：2026-07-09

## 1. 固定 convention

本文件是项目的物理约定源文件。代码、测试和文档不得在其他位置重新定义与本文件冲突的 convention。

| 项 | 约定 |
|---|---|
| 单位 | `G = c = 1`，内部默认 `M = 1` |
| signature | `(-,+,+,+)` |
| Fourier convention | `h(t,r,theta,phi) = (1/2π) ∫ h_tilde(k,r,theta,phi) exp(-i k t) dk` |
| Schwarzschild coordinates | `x^mu = (t,r,theta,phi)` |
| Cartesian coordinates | `xhat^mu = (t,x,y,z)` |
| tortoise coordinate | `r_star = r + 2M log(r/(2M)-1)` |
| master equation | `d^2 psi/dr_star^2 + [k^2 - V_l(r)] psi = 0` |
| first-stage gauge | Regge–Wheeler gauge |
| default incident direction | `+z` |
| observable polarizations | `h_plus`, `h_cross` from Weyl scalars and geodesic deviation |

### 1.1 Fourier and radial phase

With the `exp(-i k t)` time dependence:

```text
partial_t -> -i k
partial_t^2 -> -k^2
```

For positive `k`, the radial factors have the following interpretation:

```text
exp(-i k r_star) with exp(-i k t) = ingoing from spatial infinity
exp(+i k r_star) with exp(-i k t) = outgoing toward spatial infinity
```

Real time-domain perturbations require the usual reality condition
`h_tilde(-k) = h_tilde(k)^*`. Numerical modules may work with `k > 0`
complex amplitudes, but metadata must record that the physical real field
is recovered from the above Fourier convention.

### 1.2 Angular convention

Scalar spherical harmonics use the Condon-Shortley phase and unit-sphere
normalization:

```text
Y_lm(theta,phi)
  = (-1)^m sqrt((2l+1)/(4pi) * (l-m)!/(l+m)!)
    P_l^m(cos theta) exp(i m phi)

int Y_lm(theta,phi)^* Y_l'm'(theta,phi) sin(theta) dtheta dphi
  = delta_ll' delta_mm'

Y_l,-m = (-1)^m Y_lm^*
```

Spin-weighted spherical harmonics are defined through Wigner-D functions.
The project Wigner-D convention is

```text
D^l_{m m'}(alpha,beta,gamma)
  = exp(-i m alpha) d^l_{m m'}(beta) exp(-i m' gamma)
```

and the spin-weighted harmonics are

```text
_sY_lm(theta,phi)
  = (-1)^s sqrt((2l+1)/(4pi)) [D^l_{m,-s}(phi,theta,0)]^*
```

This fixes `_0Y_lm = Y_lm`. Any external library must be wrapped so that
this scalar limit, conjugation relation, and orthonormality convention hold.

The target paper's tensor-harmonic projection formulas include radius
factors in the tensor-basis normalization constants. The angular module
must expose unit-sphere scalar and spin-weighted harmonics; tensor-basis
projection code must separately preserve the paper's `epsilon^(a)` factors.

## 2. Schwarzschild background

Metric:

```text
ds^2 = -f(r) dt^2 + f(r)^(-1) dr^2 + r^2(dtheta^2 + sin^2(theta)dphi^2)
f(r) = 1 - 2M/r
```

Tortoise coordinate:

```text
r_star = r + 2M log(r/(2M) - 1)
dr_star/dr = 1/f(r)
```

## 3. Perturbation decomposition

Frequency-domain metric perturbation:

```text
h_mu_nu(t,r) = (1/2π) ∫ h_tilde_mu_nu(k,r) exp(-i k t) dk
h_tilde_mu_nu(k,r) = sum_{a,l,m} h_tilde^{(a)}_{lm}(k,r) [T^{(a)}_{lm}(theta,phi)]_{mu_nu}
```

Tensor harmonic labels:

```text
a ∈ {tt, Rt, L0, T0, Et, E1, Bt, B1, E2, B2}
```

Parity split:

```text
even: {tt, Rt, L0, T0, Et, E1, E2}
odd:  {Bt, B1, B2}
```

Radiative modes: `l >= 2`.

RW-gauge radiative modes retain, for `l >= 2`,

```text
odd:  Bt, B1
even: tt, Rt, L0, T0
```

and set

```text
odd gauge-fixed:  B2 = 0
even gauge-fixed: Et = E1 = E2 = 0
```

Lower multipoles `l = 0,1` are not part of the first-stage radiative
scattering solver.

## 4. Master variables

First-stage project uses the target-paper normalization for the RW-gauge
radial master variables.

Odd sector:

```text
psi_tilde^(-)_{lm} = - f(r)/r * h_tilde^{(B1)}_{lm}(r)
```

Even sector:

```text
psi_tilde^(+)_{lm} = 1/Lambda * [ h_tilde^{(T0)}_{lm}/r + f(r)/(i k) h_tilde^{(Rt)}_{lm} ]
Lambda = lambda + 3M/r
lambda = (l-1)(l+2)/2
```

These variables are not the same as all Moncrief or Martel-Poisson
gauge-invariant master functions. In particular, foundational references
may differ by normalization, time derivatives, tracefree tensor-basis
choices, or source-term conventions. Code must implement the target-paper
normalization above unless `docs/physics_spec.md` is explicitly revised.

## 5. RW/Zerilli equations

Master equation:

```text
[d^2/dr_star^2 + k^2 - V_l^(±)(r)] psi_tilde^(±)_{lm}(k,r) = 0
```

Odd Regge–Wheeler potential:

```text
V_l^(-)(r) = f(r)/r^2 * [l(l+1) - 6M/r]
```

Even Zerilli potential:

```text
V_l^(+)(r) = f(r)/r^2 * 1/Lambda^2 * [
  2 lambda^2(lambda+1)
  + 6 lambda^2(M/r)
  + 18 lambda(M/r)^2
  + 18(M/r)^3
]
```

## 6. Boundary conditions

At spatial infinity:

```text
psi_tilde^(±)_{lm}(k,r -> infinity)
  -> c^(±)_{lm}(k) [ exp(-i k r_star) - (-1)^l exp(2i delta_l^(±)) exp(+i k r_star) ]
```

At horizon:

```text
psi_tilde^(±)_{lm}(k,r -> 2M) -> a^(±)_{lm}(k) exp(-i k r_star)
```

Interpretation:

- `c_lm` is fixed by incident plane GW.
- `delta_l` and `a_lm` are determined numerically.
- Solver may integrate a unit ingoing horizon solution, match at outer radius, then rescale to target `c_lm`.

## 7. Incident plane GW

Default incident wave propagates along `+z`:

```text
h_tilde^(0)_mu_nu(k,r) = A_tilde_mu_nu(k) exp(i k r cos(theta))
```

TT amplitudes:

```text
A_xx = -A_yy = A_plus
A_xy =  A_yx = A_cross
```

Circular basis:

```text
A_L = (A_plus + i A_cross)/sqrt(2)
A_R = (A_plus - i A_cross)/sqrt(2)

A_plus  = (A_L + A_R)/sqrt(2)
A_cross = -i (A_L - A_R)/sqrt(2)
```

Partial-wave amplitudes:

```text
sigma_l = (l-1) l (l+1) (l+2)
A_lm^(±) = i^l sqrt(2π(2l+1)/sigma_l) * (A_L delta_{m,-2} ± A_R delta_{m,2})
```

Incident coefficients:

```text
c_lm^(-) = -[i^(l+1)/2] A_lm^(-)
c_lm^(+) =  [i^(l+1)/k] A_lm^(+)
```

Implementation note: verify the exact parser and exponent binding in code; tests must catch `-i^(l+1)/2` vs `-(i^(l+1))/2` mistakes.

The `+z` incident direction enforces the selection rule:

```text
A_lm^(±) = 0 for m != -2, +2
```

This selection rule is not valid for a generic incident direction without
Wigner-D rotation of the incident state.

## 8. Metric reconstruction

The target paper gives RW-gauge reconstruction operators `J_hat_l^(a)(k,r)` such that:

```text
h_tilde^{(a)}_{lm}(k,r) = J_hat_l^(a)(k,r) psi_tilde^(±)_{lm}
```

Implementation rule:

- Store reconstruction operators in one module.
- Operators must accept `psi` and `dpsi_dr` or a radial state object.
- No reconstruction formula may be duplicated inside `weyl.py` or plotting code.

## 9. Weyl scalars and polarization extraction

This section separates strict Newman-Penrose scalars from the project's
positive-frequency polarization packaging. They are related in flat checks,
but they are not the same object and must not share transformation rules.

### 9.1 Strict Newman-Penrose scalars

Strict NP scalars are Weyl tensor tetrad contractions:

```text
Psi0_NP = -C(l,m,l,m)
Psi1_NP = -C(l,n,l,m)
Psi2_NP = -C(l,m,n,mbar)
Psi3_NP = -C(l,n,n,mbar)
Psi4_NP = -C(n,mbar,n,mbar)
```

`weyl_mode_components(...)`, `assemble_weyl_scalars(...)`, and any future
`transform_strict_np_weyl_to_incident_tetrad(...)` API are strict-NP APIs.
They must not silently return packaged polarization quantities.

Compute Schwarzschild partial-wave strict NP scalars first in the
Kinnersley tetrad:

```text
l^mu = (f^(-1), 1, 0, 0)
n^mu = (1/2) (1, -f, 0, 0)
m^mu = (1/(sqrt(2) r)) (0, 0, 1, i csc(theta))
```

Then transform strict NP scalars, and only strict NP scalars, to the
incident-direction Cartesian tetrad:

```text
lhat^muhat = (1/sqrt(2)) (1, 0, 0,  1)
nhat^muhat = (1/sqrt(2)) (1, 0, 0, -1)
mhat^muhat = (1/sqrt(2)) (0, 1, i,  0)
```

The first null leg of this second tetrad is aligned with the incident
`+z` null direction at future infinity. This is a convention for extracting
the two reported polarizations from the scattered finite-radius field; it
does not imply that the scattered wavefront has a unique local propagation
direction everywhere.

Frequency-domain Weyl scalars are assembled as:

```text
Psi_tilde_n(k,r,theta,phi) = sum_{l,m} Psi_tilde_{n,lm}(k,r,theta,phi)
```

with spin-weighted spherical harmonics `_sY_lm`.

Li-Hou-Zhao Eq. (39)-(40) belongs to this strict-NP transformation layer.
With the project Wigner-D convention, its active/passive sense, index order,
and `(theta,phi)` signs must be validated against direct tensor contraction.
It is not a valid transform for packaged polarization scalars.

Li-Hou-Zhao Eq. (35g)-(35h) contain a complex-conjugation star:

```text
Z1 = (2/f) Z3^*
Z0 = (2/f)^2 Z4^*
```

In the project `k>0` stored-amplitude convention this star must not be
implemented as same-positive-`k`, same-`m` conjugation. The literal
same-mode interpretation is antilinear in `A_plus/A_cross`. Its consistent
meaning is tied to the full real field, the `-k` Fourier partner, the `-m`
angular partner, and spin-weighted harmonic conjugation,

```text
[_sY_lm(theta,phi)]^* = (-1)^(s+m) _{-s}Y_{l,-m}(theta,phi).
```

Until the explicit `(-k,-m)` bridge is derived, strict lower scalars
`Psi0_NP/Psi1_NP` must be validated by direct tensor-contraction tests
rather than by local same-mode conjugation.

For a flat `+z` TT wave with `exp(i k z) exp(-i k t)` and the incident
tetrad above:

```text
h_xx =  H_plus  exp(i k z)
h_yy = -H_plus  exp(i k z)
h_xy =  H_cross exp(i k z)

Psi0_NP = Psi1_NP = Psi2_NP = Psi3_NP = 0
Psi4_NP = -k^2 (H_plus - i H_cross) exp(i k z)
```

Thus a one-sided strict NP `+z` wave cannot be passed directly to the
project polarization extraction formulas below.

### 9.2 Project packaged polarization scalars

For stored positive-frequency amplitudes, the project uses a separate pair
of packaged tidal scalars, `Psi0_pack/Psi4_pack`, for linear recovery of
`h_plus_tilde/h_cross_tilde`. These are not strict NP scalars in general.

For the same flat `+z` TT wave:

```text
R_txtx = (k^2/2) H_plus  exp(i k z)
R_txty = (k^2/2) H_cross exp(i k z)

Psi4_pack = -R_txtx + i R_txty
          = -(k^2/2)(H_plus - i H_cross) exp(i k z)

Psi0_pack = -R_txtx - i R_txty
          = -(k^2/2)(H_plus + i H_cross) exp(i k z)
```

The polarization definitions use these packaged scalars:

```text
hddot_plus  = Re(Psi4_pack) + Re(Psi0_pack)
hddot_cross = -(Im(Psi4_pack) - Im(Psi0_pack))
```

Equivalently, for stored positive-frequency complex amplitudes:

```text
hddot_plus_tilde  = Psi4_pack + Psi0_pack
hddot_cross_tilde = i (Psi4_pack - Psi0_pack)
```

For a monochromatic factor `exp(-i k t)`, time derivatives satisfy:

```text
hddot = -k^2 h

h_plus_tilde  = -(Psi4_pack + Psi0_pack)/k^2
h_cross_tilde = -i(Psi4_pack - Psi0_pack)/k^2
```

`polarization_from_weyl(...)` currently implements this packaged-scalar
contract despite its generic name. Future code should rename it to
`polarization_from_packaged_weyl(...)` or keep the old name only as a
documented compatibility alias.

The hardened observable API represents these boundaries explicitly:

```text
StrictNPScalars                  strict NP full quintuple in a named frame
ElectricTidalComponents          Route B incident-frame E_xx/E_xy
PackagedPolarizationScalars      Psi0_pack/Psi4_pack recovery variables
polarization_from_packaged_scalars(k, packaged_scalars)
```

The compatibility function `polarization_from_weyl(k, psi0_hat, psi4_hat)`
continues to exist only for packaged scalar inputs. It must not be called
with raw strict NP `Psi0_NP/Psi4_NP`.

These signs and the strict-NP/package separation must be covered by
no-lens, monochromatic derivative, and direct tensor-contraction tests.

### 9.3 Curved finite-radius production bridge

For curved finite-radius production, `compute_polarization(...)` must define
project packaged scalars from the electric part of the linearized
Weyl/Riemann tensor in the incident observer frame. It must not feed
one-sided strict NP `Psi0_NP/Psi4_NP` directly to `polarization_from_weyl(...)`.

Use the incident tetrad to define the observer-frame orthonormal legs:

```text
e0 = (lhat + nhat) / sqrt(2)
ez = (lhat - nhat) / sqrt(2)
ex = (mhat + mbarhat) / sqrt(2)
ey = (mhat - mbarhat) / (i sqrt(2))
```

The production finite-radius tidal projections are:

```text
E_xx = C(e0, ex, e0, ex)
E_xy = C(e0, ex, e0, ey)
```

where `C` denotes the linearized Weyl tensor in vacuum, equivalently the
linearized Riemann tensor for the perturbative tidal block used by
geodesic deviation. The project packaged scalars are then:

```text
Psi4_pack = -E_xx + i E_xy
Psi0_pack = -E_xx - i E_xy
```

and the production polarizations are:

```text
h_plus_tilde  = 2 E_xx / k^2
h_cross_tilde = 2 E_xy / k^2
```

Implementation rule for v0.1:

- The preferred production path is direct metric/Riemann/Weyl tidal
  projection from the reconstructed RW-gauge metric contributions.
- A full-tensor reconstruction from all five strict NP scalars may be used
  only as a tensor-consistency diagnostic or as a future implementation
  after the full positive-frequency strict-NP tensor bridge is separately
  frozen and tested. It is not the current `compute_polarization(...)`
  production bridge.
- No direct two-scalar formula
  `strict Psi0_NP/Psi4_NP -> Psi0_pack/Psi4_pack` is allowed for curved
  finite-radius production.
- The flat type-N completion and helicity-channel packaged bridge are
  limited to `M=0` flat diagnostics and future far-zone/asymptotic helicity
  checks. They are not finite-radius curved production formulas.
- Li-Hou-Zhao Eq. (35g)-(35h) may be used for strict-NP formula audits only
  after resolving the full `(-k,-m)` reality bridge. It must not be used as
  same-positive-`k`, same-`m` conjugation in the production packaged API.

This convention follows the interpretation of Li-Hou-Zhao Eq. (41)-(42) as
a geodesic-deviation/tidal measurement in the chosen incident-aligned frame.
It also avoids imposing a local type-N/helicity interpretation on the
finite-radius scattered field, where the propagation direction is not unique.

## 10. Observable quantities

### 10.1 Wave field

For a fixed `k`, output complex amplitudes:

```text
h_plus(k,r,theta,phi)
h_cross(k,r,theta,phi)
```

Plotting may show:

- real part at a chosen phase;
- absolute value;
- phase;
- normalized intensity.

The plotted convention must be stored in result metadata.

### 10.2 Diffraction pattern

At fixed radius `r_obs`, compute angular distribution:

```text
|h_plus(theta,phi)|, |h_cross(theta,phi)|, or combined amplitude
```

### 10.3 Pointwise wave-optics amplification factor

The M5 finite-radius user-facing quantity is the pointwise wave-optics
amplification factor.  It may be informally called a lensing amplification
factor, but it must not be confused with radial horizon transmission,
absorption, `A_in/A_out`, or phase-shift diagnostics from RW/Zerilli radial
matching.

The production component ratios are complex amplitude ratios:

```text
F_plus_complex(k, r, theta, phi)
  = h_plus_lensed(k, r, theta, phi)
    / h_plus_unlensed(k, r, theta, phi)

F_cross_complex(k, r, theta, phi)
  = h_cross_lensed(k, r, theta, phi)
    / h_cross_unlensed(k, r, theta, phi)
```

If public shorthand names `F_plus` and `F_cross` are used, they mean these
complex ratios.  Absolute-value or intensity summaries must be named
explicitly:

```text
amplification_plus  = abs(F_plus_complex)
amplification_cross = abs(F_cross_complex)
intensity_plus_ratio  = abs(F_plus_complex)^2
intensity_cross_ratio = abs(F_cross_complex)^2
```

A combined scalar summary for plots is:

```text
H_norm = sqrt(abs(h_plus)^2 + abs(h_cross)^2)
F_pol_norm = H_norm_lensed / H_norm_unlensed
I_pol_ratio = H_norm_lensed^2 / H_norm_unlensed^2
```

The unlensed denominator is the flat/no-lens production-compatible
polarization field generated with the same Fourier convention `exp(-i k t)`,
same `k`, same `A_plus/A_cross`, same observer coordinates and coordinate
conversion, same incident tetrad/polarization convention, and the same Route B
packaged-polarization bridge.  For the current `+z` plane wave,

```text
h_plus_unlensed  = A_plus  exp(i k z)
h_cross_unlensed = A_cross exp(i k z)
z = r cos(theta)
```

The production baseline path is `compute_flat_no_lens_polarization(...)` or a
future API with the same contract.  It must not use a tiny-`M` Schwarzschild
solve, a Schwarzschild horizon boundary condition, radial RW/Zerilli matching,
or radial phase-shift/transmission data.

Denominator-zero handling is independent for plus, cross, and combined norm.
With

```text
A_scale = max(abs(A_plus), abs(A_cross), tiny)
eps_component = max(1e-14 * A_scale,
                    1e-12 * max_valid(abs(h_component_unlensed)))
eps_norm = max(1e-14 * A_scale,
               1e-12 * max_valid(H_norm_unlensed))
```

ratios are valid only where the lensed grid point is valid, the denominator is
finite, and the denominator magnitude is greater than its epsilon.  Invalid
ratios are stored as NaN.  `F_plus_complex` and `F_cross_complex` may be NaN
independently; do not fill, clip, or floor zero denominators to force finite
values.  Result metadata must store the normalization kind, baseline API,
Fourier/Route B convention, denominator thresholds, mask field names, and an
explicit statement that radial horizon transmission is excluded from this
pointwise amplification factor.

### 10.4 Kirchhoff Eq. (47) comparison baseline

Li-Hou-Zhao Eq. (47) is frozen in this project only as a scalar Kirchhoff
comparison baseline for future Fig. 5/Fig. 6 diagnostics. It is not the
production denominator for pointwise wave-optics amplification.

With the project Fourier convention `exp(-i k t)`, Li-Hou-Zhao Eq. (46)
`h_tilde^{(0)}_{+,\times}=A_tilde_{+,\times} exp(i k r cos(theta))` matches
the project flat `+z` positive-frequency plane wave `exp(i k z)`. Therefore
the Eq. (47) baseline is used without an additional positive-`k` complex
conjugation or sign flip:

```text
F_K(k, r, theta; M)
  = exp(pi gamma / 2)
    * (-gamma)^(-i gamma)
    * Gamma(1 + i gamma)
    * 1F1(-i gamma, 1; -i gamma * eta^2),

gamma = -2 M k,
eta = xi / xi0 = (1/2) * sqrt(r / M) * tan(theta).
```

The power `(-gamma)^(-i gamma)` uses the principal real logarithm of
`-gamma=2Mk>0`. `Gamma(1+i gamma)` uses the principal complex Euler gamma
function. `1F1(a,b;z)` means Kummer's regular confluent hypergeometric
function `M(a,b,z)`. The stored phase is

```text
theta_F = Arg(F_K)
```

with the principal argument in `(-pi, pi]`; any unwrapped phase is a separate
display-only quantity.

`F_K` is polarization independent. It may be plotted as a dashed comparison
curve against `F_plus_complex` and/or `F_cross_complex`, but labels and
metadata must identify it as a Kirchhoff scalar comparison baseline. It must
not be used as a denominator, mask, normalization, correction, or production
spin-2 prediction. See `references/notes/kirchhoff_eq47_conventions.md`.

## 11. Known traps

1. `e^{-ikt}` vs `e^{+ikt}` flips signs in time derivatives and boundary matching.
2. `r_star` phase must be used at outer matching, not `r`.
3. `m=±2` rule holds only for incident direction aligned with `+z`.
4. Spin-weighted harmonic conventions differ across libraries.
5. RW gauge metric components are not observables; Weyl/polarization extraction is required.
6. Asymptotic scattering amplitudes are only validation/baseline tools, not the main finite-radius algorithm.
7. `lmax ~ k r` is empirical; convergence diagnostics are mandatory.
8. Generic static spherical black holes may not share Schwarzschild RW/Zerilli reconstruction.
9. Strict NP scalars and project packaged polarization scalars are different objects.
10. Li-Hou-Zhao Eq. (35g)-(35h) stars are not same-positive-`k`, same-`m` conjugation rules.
11. Li-Hou-Zhao Eq. (39)-(40) may transform strict NP scalars only, not packaged scalars.
12. Curved production polarization must use incident-frame electric tidal projection, not flat type-N or helicity packaging.
13. Pointwise wave-optics amplification `F=h_lensed/h_unlensed` is not radial horizon transmission or absorption.
14. Li-Hou-Zhao Eq. (47) is a Kirchhoff scalar comparison baseline only; it is not the pointwise-amplification denominator and not a production spin-2 observable.
