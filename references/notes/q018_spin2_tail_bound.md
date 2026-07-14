# Q018 spin-2 finite-radius tail bound support note

Date: 2026-07-06

Thread: T10b literature and formula support

Scope: decide whether a finite-radius WKB/high-ell tail bound can support the spin-2 RW/Zerilli R60_K2 case, or whether T4m should record a no-go / stronger-method requirement.

## Executive conclusion

T4m Route B is not supportable as a GREEN R60_K2 negligible-tail criterion for the current first suppressed modes `ell >= 153`.

The scalar paper gives a strong finite-radius prior: modes with `ell >> k r_obs` are behind a centrifugal barrier and the scalar partial-wave series naturally truncates around `ell_max ~ k r_obs`. This transfers to the leading radial potential of spin-2 RW/Zerilli equations, because both parity sectors have the same large-`ell` centrifugal term.

However, for R60_K2 the relevant first suppressed modes are not far enough into the forbidden tail at the target radius. Direct local-WKB checks with the project RW/Zerilli potentials give, at `k=2`, `r=60`:

| ell | sector | outer turning point | local action `S_tail(60)` | `exp(-S_tail)` |
|---:|---|---:|---:|---:|
| 153 | odd | `75.729210131606` | `15.334712751011` | `2.188864e-07` |
| 153 | even | `75.729210110560` | `15.334712718037` | `2.188865e-07` |
| 156 | odd | `77.229625055447` | `17.556073057696` | `2.374075e-08` |
| 156 | even | `77.229625035959` | `17.556073025582` | `2.374075e-08` |
| 168 | odd | `83.231131379602` | `27.338154584875` | `1.340264e-12` |
| 168 | even | `83.231131365073` | `27.338154556535` | `1.340264e-12` |
| 180 | odd | `89.232430317243` | `38.387892662728` | `2.129855e-17` |
| 180 | even | `89.232430306190` | `38.387892638092` | `2.129855e-17` |

The old Q018 local-tail threshold `S_tail >= 55` at the evaluation radius would first be reached only around `ell=197`, outside the current `lmax=180` run. Therefore a target-radius-aware version of the current policy would reject R60_K2 for all currently suppressed modes `ell=153..180`.

With any conservative spin-2 polynomial allowance, the first modes are not negligible. For example:

| ell | `exp(-S)` | `ell^2 exp(-S)` | `ell^4 exp(-S)` | `ell^6 exp(-S)` |
|---:|---:|---:|---:|---:|
| 153 | `2.189e-07` | `5.124e-03` | `1.199e+02` | `2.808e+06` |
| 156 | `2.374e-08` | `5.778e-04` | `1.406e+01` | `3.422e+05` |
| 168 | `1.340e-12` | `3.783e-08` | `1.068e-03` | `3.013e+01` |
| 180 | `2.130e-17` | `6.901e-13` | `2.236e-08` | `7.244e-04` |
| 197 | `5.284e-25` | `2.051e-20` | `7.958e-16` | `3.089e-11` |

This is enough to support a no-go for using the current zero-tail suppression at R60_K2. It does not prove that R60_K2 is physically impossible; it means T4m needs either target-radius-aware rejection, rescaled/log radial propagation to `r=60`, or a much stronger spin-2 observable-level tail derivation.

## Source list and priority

1. Li & Zhao, "Rigorous calculation of scalar scattering in Schwarzschild background: the convergence of partial-wave series and Poisson spot", arXiv:2508.17253.
   - Local PDF: `references/papers/li_zhao_2025_scalar_schwarzschild_convergence_poisson_spot.pdf`.
   - Local cache: `arxiv-reading/2508.17253.html`.
   - Local memory: `arxiv-reading/2508.17253.memory.md`.
   - Priority: high for finite-radius scalar cutoff intuition; not a direct spin-2 theorem.

2. Li, Hou, Zhao, "Gravitational Lensing of Gravitational Waves: Spin-wave Optics through Black Hole Scattering".
   - Local PDF: `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`.
   - Priority: highest for this project’s spin-2 RW/Zerilli equations, metric reconstruction, Weyl/tidal extraction, and finite-radius output.

3. `docs/physics_spec.md` and `docs/numerics.md`.
   - Priority: authoritative project conventions and current Q018 policy.

4. `references/notes/q018_scalar_partial_wave_cutoff.md` and `references/notes/q012_high_ell_radial_methods.md`.
   - Priority: local distilled notes for scalar cutoff and high-barrier radial numerics.

## Established claims

### Scalar finite-radius partial-wave result

Li & Zhao establish for scalar finite-radius partial-wave sums:

- The exact finite-radius spherical-Bessel plane-wave expansion is convergent at finite `r`.
- The usual asymptotic radial expansion is valid only for `kr >> ell`; applying it near `ell ~ kr` causes divergence.
- In finite-radius scalar Schwarzschild scattering, the natural empirical truncation is `ell_max ~ k r` for a plane-wave source.
- Physically, modes with outer turning point beyond the observer are suppressed by the centrifugal barrier and do not significantly reach the detector.
- For finite source and observer radii the expected scale is `ell_max ~ k min(r, r_s)`.

Important limitation: the paper explicitly treats full gravitational-wave scattering, including gauge transformations, polarization distortions, helicity, and spin-2 effects, as future work. Its Appendix B supports scalar behavior as a high-frequency/eikonal approximation to GW amplitudes, not as a finite-frequency spin-2 RW/Zerilli observable theorem.

### Spin-2 project equations

The project spin-2 radial equations are

```text
d^2 psi/dr_star^2 + [k^2 - V_l^(±)(r)] psi = 0.
```

The odd and even potentials have the same leading large-`ell` behavior:

```text
V_l^(±)(r) = f(r) ell(ell+1)/r^2 + lower-order spin/parity terms.
```

Thus the scalar centrifugal-turning-point mechanism transfers at the leading radial-potential level.

### Spin-2 observable complexity

The gravitational production observable is not the master radial function alone. Li-Hou-Zhao reconstructs metric components by operators `J_l^(a)(k,r)` and then computes Weyl/tidal polarizations. The reconstruction operators include `sigma_l=(l-1)l(l+1)(l+2)`, `lambda=(l-1)(l+2)/2`, angular/tensor-harmonic derivatives, and radial derivatives. These can introduce polynomial `ell` factors before the final electric-tidal projection.

Therefore a radial WKB factor `exp(-S_tail)` is not by itself a conservative bound on `h_plus/h_cross`.

## Assumptions used in this note

- Schwarzschild `M=1`, `k=2`, project RW/Zerilli potentials from `docs/physics_spec.md`.
- Observer target radius for R60_K2 is `R=60`.
- Outer turning point `r_t^+` is the largest solution of `V_l^(±)(r)=k^2`.
- Local forbidden-tail action is

```text
S_tail^(±)(ell; R) =
  integral_R^{r_t^+} sqrt(V_l^(±)(r) - k^2) dr_star
  = integral_R^{r_t^+} sqrt(V_l^(±)(r) - k^2) / f(r) dr
```

when `R < r_t^+`; if `R >= r_t^+`, this local evanescent-tail suppression is not available at that radius.

- No cancellation between parity sectors, `m=+2/-2`, angular harmonics, or plus/cross components is used as a bound.
- No scalar-field theorem is treated as a spin-2 observable theorem.

## What transfers from scalar to spin-2

1. The leading centrifugal barrier.

   Since both RW and Zerilli potentials share `f ell(ell+1)/r^2`, the location of high-`ell` outer turning points and the qualitative evanescent-tail behavior are scalar-like at leading order.

2. The finite-radius warning against asymptotic radial expansions.

   The scalar paper’s central warning applies directly to the project: do not replace finite-radius radial functions by asymptotic expansions near `ell ~ kr`.

3. The role of `ell ~ k r_obs` as an initial scale.

   It is reasonable to use `ell ~ k r_obs` as an initial support scale or tail-policy diagnostic. This matches `docs/numerics.md`: `lmax ~ k r_obs` is an initial estimate, not a sufficient convergence condition.

4. The need for target-radius-aware metadata.

   The scalar turning-point picture supports recording the evaluation radius, outer turning point, and local action rather than relying on a domain-independent high-barrier flag.

## What does not directly transfer

1. Parity odd/even potentials.

   RW and Zerilli potentials differ at lower order. They are nearly identical in the high-`ell` leading term, but a safe bound must compute both sectors and use the weaker bound.

2. Metric reconstruction factors.

   The project observable uses reconstructed metric components. Li-Hou-Zhao Eq. (29) includes explicit `ell`-dependent factors such as `sigma_l` and `lambda`; some operators behave with positive powers of `ell` before final normalization and derivatives are applied.

3. Tensor harmonics.

   Tensor and spin-weighted harmonics include angular derivatives and normalization factors. Pointwise sup-norms can grow with `ell`; a scalar Legendre-mode cutoff does not directly bound tensor-harmonic pointwise contributions.

4. Weyl/electric-tidal extraction.

   Route B production extracts `E_xx/E_xy` from the reconstructed metric/Riemann/Weyl tensor. Curvature involves derivatives and tetrad projections, which can add powers of `ell` and `k`.

5. Finite-radius polarization extraction.

   The final `h_plus/h_cross` are packaged electric-tidal observables, not scalar field values. A radial master tail bound must be propagated through reconstruction and tidal projection.

6. Possible cancellations.

   The partial-wave sum may be smaller because of oscillatory phases or parity/helicity cancellation, but a conservative criterion cannot assume those cancellations.

## Recommended conservative bound form

If T4m implements a Route B helper, it should be an audit/failure-capable bound, not a blanket acceptance rule:

```text
S_tail = integral_R^{r_t^+} sqrt(V_l^(sector)(r)-k^2) dr_star
radial_tail_bound = exp(-S_tail)
observable_tail_bound =
  C_prefactor * (1+ell)^p * coefficient_scale(ell,k,sector,m) * radial_tail_bound
```

Minimum metadata:

- `required_eval_radius`
- `sector`
- `ell`
- `k`
- `potential_name`
- `outer_turning_point`
- `tail_action_at_required_radius`
- `radial_tail_bound_at_required_radius`
- `prefactor_power_p`
- `prefactor_constant_or_policy`
- `coefficient_scale_policy`
- `observable_tail_bound`
- `tail_bound_tolerance`
- `tail_bound_covers_required_radius`
- no-go reason when not covered

Minimum safety rule:

- Use the weaker of odd/even sector bounds.
- Do not use cancellation.
- Do not use `p=0` unless a separate derivation proves all reconstruction/tensor/Weyl factors are already included.
- Compare a sum over all suppressed modes, not only an individual mode, to the tolerance relevant for the final observable or convergence diagnostic.

For R60_K2, the first suppressed modes fail this conservative form for any plausible nonzero polynomial allowance. Even `p=2` gives `ell^2 exp(-S) ~ 5.1e-3` at `ell=153`, above the project `1e-4` convergence scale; `p=4` is completely non-negligible. Therefore this note recommends that Route B should report R60_K2 as uncovered unless T4m supplies a stronger spin-2 observable-level derivation.

## No-go recommendation for T4m

Recommended wording:

```text
The current evanescent-tail suppression policy is not certified for R60_K2.
At k=2 and r=60, the first suppressed spin-2 modes ell=153..180 have
target-radius local WKB actions below the existing S_tail>=55 criterion
(ell=153 has S_tail≈15.33).  Because the spin-2 observable includes
RW/Zerilli parity sectors, metric reconstruction, tensor harmonics, and
electric-tidal projection with possible polynomial ell prefactors, the scalar
ell_max~kr result is only a leading-potential prior and does not provide a
conservative bound on h_plus/h_cross.  R60_K2 remains gated until these modes
are solved with a rescaled/log radial method through r=60 or a reviewed
spin-2 observable-level tail bound is implemented.
```

This supports T4m Route A as a metadata hardening step:

- `required_eval_radius=None` keeps accepted `[-30,30]^2` behavior.
- `required_eval_radius=60` must not silently accept the old `valid_until_r≈42.47`.
- The correct outcome in the current method is a structured uncovered/no-go result.

It also supports T4m Route C if no target-radius-aware code change is made.

## Exact warning about kM=4

This note does not validate `kM=4`.

All numerical estimates here use `kM=2`, `M=1`, `r=60`, and the current Schwarzschild RW/Zerilli potentials. No conclusion follows for `kM=4`, its required `lmax`, its turning-point structure, its suppression threshold, or its R60/R larger-domain coverage.

## How T4 should use this note

- Do not use scalar `ell_max~kr` as a proof for spin-2 R60_K2.
- Implement target-radius-aware suppression metadata if modifying the solver.
- For `required_eval_radius=60`, reject the current `ell>=153` zero-tail suppression unless a stronger method is added.
- If implementing a WKB helper, compute local action at the requested radius and record the polynomial allowance explicitly.
- Prefer a structured no-go over a weak GREEN.
- Future method requirement: rescaled/log-amplitude propagation or another stable radial architecture that can return `psi(r)` and `dpsi/dr` through `r=60` for the first suppressed modes, or a rigorous spin-2 observable bound including reconstruction/tensor/Weyl factors.

## How T7 should use this note

- Verify that any T4m GREEN claim for R60_K2 includes target-radius local action at `r=60`, not only total barrier action or old `valid_until_r`.
- Check that warning metadata is JSON-safe and includes `required_eval_radius`, `outer_turning_point`, target action/bound, prefactor policy, and covered/uncovered status.
- Reject any review that treats scalar `ell_max~kr` as a spin-2 theorem.
- Reject any review that validates `kM=4` from this note.
- Accept YELLOW/no-go if T4m clearly prevents silent R60 acceptance and records the stronger-method requirement.

## Commands / calculations used

- `curl -L --fail https://arxiv.org/pdf/2508.17253` to store the scalar paper PDF locally.
- `pdftotext` on the scalar PDF and Li-Hou-Zhao PDF.
- Local Python/SciPy calculation using project `regge_wheeler_potential`, `zerilli_potential`, and `SchwarzschildBackground`:

```text
S_tail(R) = integral_R^{r_t^+} sqrt(V_l(r)-k^2) / f(r) dr
```

The calculation is diagnostic/literature support only. It does not modify `src/` or tests.
