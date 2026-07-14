# Phase 3 T6a formula audit

Date: 2026-07-03

Scope: T6 formula and interface freeze before implementing metric reconstruction, Weyl scalars, tetrad transformation, and polarization extraction.

Primary source:

- Li-Hou-Zhao 2025, Eqs. (28)-(42), checked against `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf` pages 4-6.
- Project conventions in `docs/physics_spec.md` v0.1-frozen are authoritative for Fourier sign, metric signature, angular conventions, and stored positive-frequency amplitudes.

## 1. Shared notation

Use Schwarzschild exterior coordinates `(t, r, theta, phi)`, signature `(-,+,+,+)`, and Fourier factor `exp(-i k t)`.

For each radiative mode:

```text
ell >= 2
lambda = (ell - 1)(ell + 2)/2
sigma_l = (ell - 1) ell (ell + 1) (ell + 2)
u = M/r
Lambda = lambda + 3M/r = lambda + 3u
f = 1 - 2M/r
R[psi] = r dpsi/dr
```

All radial derivatives in Li-Hou-Zhao Eqs. (29) and (35) are areal-radius derivatives `d/dr`, not tortoise derivatives. If a caller has `dpsi/dr_star`, convert by

```text
dpsi/dr = (dpsi/dr_star) / f
```

No T6 formula below requires an independent `d2psi/dr_star2`. If a later derivation produces one, eliminate it using

```text
d2psi/dr_star2 = (V_l^(sector)(r) - k^2) psi
```

before adding public API surface.

## 2. RW-gauge metric reconstruction operators

Formula:

```text
h_tilde_lm^(a)(k,r) = J_hat_l^(a)(k,r) psi_tilde_lm^(sector)(k,r)
```

Odd sector, using `psi = psi^(-)`:

```text
h^(B1) = -(r/f) psi
h^(Bt) = [f/(i k)] [psi + r dpsi/dr]
```

Even sector, using `psi = psi^(+)`:

```text
h^(T0) = r { [sigma_l/4 + 3 lambda u + 6 u^2]/Lambda * psi
             + f r dpsi/dr }

h^(Rt) = -i k { [lambda - 3 lambda u - 3 u^2]/(Lambda f) * psi
                + r dpsi/dr }

h^(L0) = -[r/f^2] [k^2 - V_l^(+)(r)/2] psi
         -[1/f] [u - lambda f/Lambda] dpsi/dr

h^(tt) = f^2 h^(L0)
```

Dependencies:

| component | sector | needs `psi` | needs `dpsi/dr` | needs `dpsi/dr_star` | needs second derivative |
|---|---|---:|---:|---:|---:|
| `B1` | odd | yes | no | no | no |
| `Bt` | odd | yes | yes | no, convertible | no |
| `T0` | even | yes | yes | no, convertible | no |
| `Rt` | even | yes | yes | no, convertible | no |
| `L0` | even | yes | yes | no, convertible | no |
| `tt` | even | yes | yes, through `L0` | no, convertible | no |

Interface freeze:

```text
src/schwgw/perturbations/reconstruction.py
  MetricModeComponents
  reconstruct_metric_mode(sector, ell, k, r, psi, dpsi_dr, background)
```

`MetricModeComponents` should carry `sector`, `ell`, `k`, `r`, and the nonzero RW-gauge components for that sector. Components outside the sector should be absent or `None`; do not fill them with physically meaningful zeros unless the dataclass explicitly documents that convention.

## 3. Weyl mode components in the Kinnersley tetrad

The frequency-domain Weyl scalar mode contribution is

```text
Psi_tilde_n(k,r,theta,phi) = sum_{ell,m} Psi_tilde_{n,lm}(k,r,theta,phi)
```

For each `(ell,m)`:

```text
Psi_4,lm = sqrt(sigma_l) [Z_4,lm^(-) + Z_4,lm^(+)] _{-2}Y_lm
Psi_3,lm = sqrt(2 ell(ell+1)) [Z_3,lm^(-) + Z_3,lm^(+)] _{-1}Y_lm
Psi_2,lm = [Z_2,lm^(-) + Z_2,lm^(+)] _0Y_lm
Psi_1,lm = sqrt(2 ell(ell+1)) [Z_1,lm^(-) + Z_1,lm^(+)] _{+1}Y_lm
Psi_0,lm = sqrt(sigma_l) [Z_0,lm^(-) + Z_0,lm^(+)] _{+2}Y_lm
```

This fixes the spin weights:

```text
Psi_4 -> s = -2
Psi_3 -> s = -1
Psi_2 -> s = 0
Psi_1 -> s = +1
Psi_0 -> s = +2
```

Radial source functions, with `R = r dpsi/dr`:

```text
16 r^3 Z_4^(-)
  = (2/k) [r^2 V_l^(-) + 2 i k r (1 - 3u) - 2 (k r)^2] psi^(-)
    + (4/k) f (1 - 3u + i k r) R[psi^(-)]

16 r^3 Z_4^(+)
  = [r^2 V_l^(+) + (2 i k r/Lambda)(lambda - 3 lambda u - 3u^2)
     - 2 (k r)^2] psi^(+)
    + 2 f { (lambda - 3 lambda u - 3u^2)/Lambda + i k r } R[psi^(+)]

8 r^3 Z_3^(-)
  = (2/k) [f u + i k r (lambda + u)] psi^(-)
    + (2/k) f (lambda + u) R[psi^(-)]

8 r^3 Z_3^(+)
  = [-3 f u + i k r Lambda] psi^(+)
    + f Lambda R[psi^(+)]

16 r^3 Z_2^(-)
  = (4/k) sigma_l psi^(-)

16 r^3 Z_2^(+)
  = [4 ell(ell+1) lambda^2 + 10 sigma_l u
     + 24(ell^2 + ell + 1)u^2 - 48u^3] psi^(+) / Lambda
    - 8 f u R[psi^(+)]
```

Target-paper literal relations:

```text
Z_1^(sector) = (2/f) [Z_3^(sector)]^*
Z_0^(sector) = (2/f)^2 [Z_4^(sector)]^*
```

Risk note: the star in Eq. (35g)-(35h) is a high-risk convention point for this project because the code stores positive-frequency complex amplitudes. A literal complex conjugate makes these pieces antilinear in the input amplitude. T6c must test no-lens polarization recovery and complex-amplitude linearity before this convention is treated as physically validated. Do not silently replace the star by a non-conjugated expression; if tests show a conflict, stop and update `docs/physics_spec.md` before implementation proceeds further.

Interface freeze:

```text
src/schwgw/scattering/weyl.py
  WeylModeComponents
  weyl_mode_components(sector, ell, m, k, r, theta, phi, metric_mode, background)
  assemble_weyl_scalars(...)
  transform_weyl_to_incident_tetrad(...)
```

Implementation rule: `weyl.py` may compute the `Z_n` functions from the same `psi` and `dpsi/dr` data used by reconstruction, but it must not duplicate the metric reconstruction operators as a second source of truth. If `metric_mode` is accepted for API traceability, it should be treated as the output of `reconstruct_metric_mode`.

## 4. Tetrads and transformation

Kinnersley tetrad in Schwarzschild coordinates:

```text
l^mu = (f^(-1), 1, 0, 0)
n^mu = (1/2)(1, -f, 0, 0)
m^mu = (1/(sqrt(2) r))(0, 0, 1, i csc(theta))
```

With signature `(-,+,+,+)`, check:

```text
l.n = -1
m.m_conj = +1
all other tetrad inner products vanish
```

Incident-aligned Cartesian tetrad:

```text
lhat^muhat = (1/sqrt(2))(1, 0, 0,  1)
nhat^muhat = (1/sqrt(2))(1, 0, 0, -1)
mhat^muhat = (1/sqrt(2))(0, 1, i,  0)
```

Weyl transformation source formula:

```text
Psi_hat_{2-m} = sum_s Lambda_{2 m s} Psi_{2-s}
```

where `s,m in {-2,-1,0,1,2}` and

```text
Lambda_{ell m s}
  = (-1)^(s+m) 2^(-s/2)
    sqrt((ell+m)!(ell-m)! / ((ell+s)!(ell-s)!))
    D^ell_{m s}(phi, theta, 0)
```

with `ell=2` for Weyl scalars. The project Wigner-D convention remains the one in `docs/physics_spec.md`:

```text
D^ell_{m m'}(alpha,beta,gamma)
  = exp(-i m alpha) d^ell_{m m'}(beta) exp(-i m' gamma)
```

Active/passive audit item: Eq. (39)-(40) must be tested with identity/axis cases before generic use. Do not infer the direction of rotation from a third-party function name.

Interface freeze:

```text
src/schwgw/scattering/tetrads.py
  kinnersley_tetrad(background, r, theta)
  incident_cartesian_tetrad()
  tetrad_inner_products(...)
```

`scattering/tetrads.py` is preferred over the older singular `tetrad.py` spelling for this T6 slice because the API exposes multiple tetrads.

## 5. Polarization extraction

Paper real-time acceleration convention:

```text
hddot_plus  = Re(Psi_hat_4) + Re(Psi_hat_0)
hddot_cross = -(Im(Psi_hat_4) - Im(Psi_hat_0))
```

Project positive-frequency complex-amplitude convention with `exp(-i k t)`:

```text
hddot_plus_tilde  = Psi_hat_4_tilde + Psi_hat_0_tilde
hddot_cross_tilde = i (Psi_hat_4_tilde - Psi_hat_0_tilde)

h_plus_tilde  = -hddot_plus_tilde/k^2
h_cross_tilde = -hddot_cross_tilde/k^2
              = -i(Psi_hat_4_tilde - Psi_hat_0_tilde)/k^2
```

Interface freeze:

```text
src/schwgw/scattering/observables.py
  PolarizationResult
  polarization_from_weyl(k, psi0_hat, psi4_hat)
```

`k` must be positive. The result should retain both `hddot_plus/cross` and `h_plus/cross` so the Fourier sign test can inspect the intermediate acceleration convention directly.

## 6. Existing API support

T4 radial API:

```text
RadialSolution.psi_at(r)
RadialSolution.dpsi_dr_at(r)
RadialSolution.dpsi_drstar_at(r)
```

This is sufficient for T6 formulas. No minimum T6 formula requires a new T4 `d2psi` public method.

Important scaling rule: `solve_radial_mode` currently returns a unit-horizon solution with matched `A_in`. T6 assembly must rescale it to the incident coefficient by

```text
scale_lm^(sector) = c_lm^(sector) / radial_solution.A_in
psi_scaled = scale_lm^(sector) psi_unit
dpsi_dr_scaled = scale_lm^(sector) dpsi_dr_unit
```

T5 incident coefficients can be used directly as the target incoming coefficient for this rescaling:

```text
c_lm^(-) = -[i^(ell+1)/2] A_lm^(-)
c_lm^(+) =  [i^(ell+1)/k] A_lm^(+)
```

T3 spin-weighted harmonics are compatible with the T6 assembly because they implement `_sY_lm` for `s = -2,-1,0,+1,+2` under the frozen Wigner-D convention and pass scalar-limit/orthonormality tests according to `status.md`.

## 7. Stop-condition review

No immediate stop condition was triggered.

- `docs/physics_spec.md` v0.1-frozen does not need to be modified for T6b to begin.
- Eq. (28)-(42) are now present in this audit note at an implementation-guiding level.
- Existing T2-T5 APIs can support T6 through a small scaling adapter; no source API blocker was found.
- Plotting, transmission factors, generic incident direction, and numeric regression fixtures are not required for this slice.

Open risks to carry into T6c/T7:

- Eq. (35g)-(35h) complex conjugation versus positive-frequency complex-amplitude linearity.
- Eq. (39)-(40) active/passive Wigner-D convention and the `2^(-s/2)` factor.
- No-lens polarization recovery remains the decisive end-to-end sign test.
