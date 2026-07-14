# Q012 high-ell radial methods note

Date: 2026-07-05

Scope:
- Blocker: high-`ell` RW/Zerilli radial solver and Wronskian diagnostics become unstable in tunneling/high-barrier regimes.
- Target users: T4 radial solver, T7 validation, T0 coordination.
- Boundary: this note does not change `docs/physics_spec.md` frozen conventions and does not modify `src/` or `tests/`.

## Project-specific diagnosis

The Q012 failure mode is not primarily an outer 2x2 matching algebra error. In the failed outward unit-horizon shooting runs, `A_in` and `A_out` became exponentially large while the algebraic boundary residual stayed small. This is the standard forbidden-region conditioning problem: a unit horizon-ingoing solution is propagated through a large RW/Zerilli barrier action, so the finite-flux component becomes a cancellation-sensitive difference of nearly parallel large complex quantities.

With the project Fourier convention `exp(-i k t)`,

```text
exp(-i k r_star) = ingoing from infinity / into the horizon
exp(+i k r_star) = outgoing toward infinity
W = psi^* dpsi/dr_star - psi dpsi^*/dr_star
```

For a unit `exp(-i k r_star)` wave, `W = -2 i k`. Thus the old `k=0.5` unit-horizon check correctly started near `W=-i`; the drift happened after barrier amplification. In high-barrier unit-incoming-at-infinity normalization, the horizon flux can be exponentially small, so raw double-precision Wronskian samples may be dominated by cancellation even when the boundary value problem is well solved.

## Literature roles

### Li, Hou, Zhao 2025

File: `references/papers/li_hou_zhao_2025_spin_wave_optics.pdf`

Problem solved:
- Defines the project's primary finite-radius partial-wave framework, RW/Zerilli equations, boundary conditions, incident coefficients, reconstruction, Weyl scalars, and polarization extraction.
- Explicitly argues that asymptotic radial expansions fail for high-`ell` modes when `kr` is not much larger than `ell`, motivating finite-radius radial functions.

Direct relevance to Q012:
- Direct for boundary convention and for why finite-radius radial solutions must be retained.
- It does not prescribe a robust high-barrier numerical radial algorithm. The paper itself lists future work on solving high-`ell` perturbation equations.

Use in this project:
- Keep Eq. (11)-(13) as the authoritative outer/horizon boundary convention.
- Do not replace finite-radius partial-wave assembly with asymptotic scattering amplitudes.

### Mano, Suzuki, Takasugi 1996

File: `references/papers/mano_suzuki_takasugi_1996_rw_mst.pdf`

Problem solved:
- Gives analytic solutions of the Regge-Wheeler equation using hypergeometric-function series near the horizon and Coulomb-wave series near infinity.
- Introduces the same renormalized angular momentum for both series, fixed by continued-fraction convergence, and relates the two bases in their common convergence domain.
- Provides analytic expressions for incoming/outgoing amplitudes at infinity for a horizon-ingoing solution.

Direct relevance to Q012:
- Strong as a reference method and possible future oracle for RW homogeneous solutions.
- It directly addresses the two-basis/horizon-infinity structure that Q012 exposed.

Use in this project:
- Treat as a high-accuracy reference backend candidate, not as the minimum v0.1 fix.
- Useful future checks: compare `A_in`, `A_out`, phase factor, and selected `psi(r)` against an MST implementation for low-to-moderate `kM`.

Risk:
- Implementing MST requires continued fractions, renormalized angular momentum `nu`, Coulomb functions, careful normalization, and likely higher precision arithmetic. This is too large for a blocker fix unless a reliable library/backend is adopted.

### Sasaki and Tagoshi 2003

File: `references/papers/sasaki_tagoshi_2003_analytic_bhpt.pdf`

Problem solved:
- Reviews black-hole perturbation analytic methods.
- Explains that RW/Sasaki-Nakamura type equations have standard wave-equation asymptotics, while MST uses a horizon-convergent hypergeometric series and an infinity-convergent Coulomb-wave series matched exactly in an overlap.

Direct relevance to Q012:
- Strong for method selection and for understanding why horizon/infinity basis matching is the natural structure.
- Indirect for implementation because most of the review is PN/MST-oriented rather than a finite-radius numerical solver recipe.

Use in this project:
- Supports keeping RW/Zerilli as the working radial equation for Schwarzschild.
- Supports classifying MST as a standard BHPT method, but not as a small local patch.

### Dolan 2008

File: `references/papers/dolan_2008_gravitational_plane_wave_scattering.pdf`

Problem solved:
- Computes gravitational plane-wave scattering/absorption using partial waves and phase shifts.
- For Kerr, uses a Sasaki-Nakamura transformation to avoid Teukolsky far-field peeling and reads off ingoing/outgoing coefficients at a large radius.
- Documents that large-`l` phase-shift errors are strongly amplified in partial-wave cross sections, especially near the axis.

Direct relevance to Q012:
- Moderate. It is useful for phase-shift extraction and for warning that large-`l` phase errors can poison partial-wave sums.
- It is not the project's main finite-radius observable algorithm and should not define the solver normalization.

Use in this project:
- Use as a validation warning: large-`l` phase shifts must be checked by `r_out` and `lmax` sweeps.
- Do not switch to asymptotic cross-section formulas as the main output.

### Johnson 1973 log-derivative method

File: no open PDF stored. Official metadata: OSTI record `https://www.osti.gov/biblio/4376059`, DOI `10.1016/0021-9991(73)90049-1`.

Problem solved:
- Introduces propagating the logarithmic derivative/Riccati equation for scattering calculations, which controls amplitude growth by evolving derivative ratios rather than the wavefunction itself.

Direct relevance to Q012:
- Conceptually relevant to high-barrier numerical conditioning.
- Not BHPT-specific and not enough by itself for finite-radius `psi(r)` reconstruction.

Use in this project:
- Keep as a future optional stabilization idea only.
- If implemented later, it must include a robust way to reconstruct normalized `psi(r)` over the finite-radius grid and to handle poles where `psi=0`.

### Black Hole Perturbation Toolkit ReggeWheeler documentation

Source: `https://bhptoolkit.org/ReggeWheeler/`

Problem solved:
- Provides an existing BHPT tool that computes Regge-Wheeler homogeneous radial solutions with either semi-analytic MST or numerical integration.
- States that MST is the default for high precision and requires high-precision input; numerical integration is faster but not as effective beyond machine precision.

Direct relevance to Q012:
- Strong as an external-practice signal: production BHPT code treats MST and direct numerical integration as distinct backends.

Use in this project:
- Use as a possible external benchmark if Mathematica/BHPT Toolkit is available.
- Do not make it a dependency for the Python v0.1 solver.

## Method comparison for Q012

### Bidirectional / inward-outward matching

Assessment:
- Recommended in principle.
- The analytic MST construction is exactly a controlled horizon/infinity basis matching strategy.
- A numerical two-point BVP is a pragmatic version of bidirectional matching: enforce the horizon ingoing condition and the outer incoming/outgoing form simultaneously instead of transporting a badly scaled unit-horizon solution across the barrier.

Recommendation:
- Keep T4's high-barrier unit-incoming-at-infinity BVP route as the minimum robust algorithm.
- Treat simple one-radius matching of independently propagated bases as a secondary fallback only after conditioning diagnostics show a usable overlap region.

Failure mode:
- If the chosen match radius lies in a region where both bases are nearly linearly dependent or one component is exponentially suppressed, the matching matrix can be misleading even when local ODE residuals look small.

### Log-derivative / Riccati propagation

Assessment:
- Useful for avoiding amplitude blow-up and common in scattering calculations.
- Less suitable as the first project fix because this project needs the finite-radius radial function and derivative, not only phase shifts or an S-matrix.

Recommendation:
- Do not introduce now.
- Reconsider only if BVP collocation fails for larger `kM`, larger `ell`, or future coupled-channel extensions.

Convention/algorithm risks:
- Riccati variables have poles at zeros of `psi`.
- Reconstructing absolute normalization requires a separate amplitude integration or matching step.
- Complex phase and Wronskian sign must be tied back to the project `exp(-i k t)` convention.

### Jost solution / phase-shift extraction

Assessment:
- Good for asymptotic scattering amplitudes and absorption/transmission studies.
- Not sufficient for the current finite-radius observable pipeline, which needs `psi(r_obs)` and `dpsi/dr(r_obs)`.

Recommendation:
- Keep phase shifts as diagnostics and future transmission/cross-section outputs.
- Do not make Jost/phase-shift extraction the main Q012 solver.

Risks:
- High-`ell` phase errors are amplified in partial-wave sums.
- Long-range logarithmic phases must be handled through `r_star`; using `r` phases would break frozen convention.

### Coulomb-wave asymptotic matching

Assessment:
- Strong theoretical basis through MST/Leaver. It naturally incorporates the Schwarzschild logarithmic phase structure at infinity.
- Better as a high-precision backend or oracle than as a short blocker fix.

Recommendation:
- Do not alter current outer boundary to a new convention.
- Later, use Coulomb-wave/MST results to validate phase factors and `A_in/A_out`, while translating them back to the project `exp(± i k r_star)` normalization.

Risks:
- Published amplitudes may use `z=omega r`, `epsilon=2M omega`, `z^{±i epsilon}` or Teukolsky/Sasaki-Nakamura normalizations. These must be converted before comparing with project `A_in`, `A_out`.

### WKB high-ell treatment

Assessment:
- Useful for diagnostics, branch selection, and rough transmission estimates.
- Not accurate enough alone for finite-radius complex radial functions near turning points or for phase-sensitive partial-wave sums.

Recommendation:
- Keep WKB barrier action

```text
S = integral sqrt(max(V_l(r)-k^2, 0)) dr_star
```

as a solver-selection and diagnostic quantity.
- Do not replace numerical radial solutions with WKB fields in the main pipeline.

### MST / standard BHPT radial methods

Assessment:
- The most standard high-precision analytic method for homogeneous black-hole radial equations.
- Worth introducing only as an optional backend or external oracle, not as the immediate v0.1 implementation.

Recommendation:
- Defer in-project MST implementation.
- If T4/T7 later need a gold-standard radial oracle, use an existing validated backend first, e.g. BHPT Toolkit ReggeWheeler if available.

Risks:
- MST implementation is a substantial numerical-special-functions project.
- Conventions differ from Li-Hou-Zhao master variables and from this project's stored positive-frequency amplitudes.

## Recommended algorithm route for T4

1. Preserve the current public contract:

```text
A_in = coefficient of exp(-i k r_star) at infinity
A_out = coefficient of exp(+i k r_star) at infinity
scale = c_lm / A_in
```

2. Use low-barrier outward shooting only where the barrier action is small and raw Wronskian conservation is numerically resolved.

3. Use high-barrier unit-incoming-at-infinity BVP for tunneling cases:

```text
d psi/dr_star = p
d p/dr_star = -(k^2 - V_l) psi

horizon: p + i k psi = 0
infinity: psi = exp(-i k r_star) + A_out exp(+i k r_star)
          p   = -i k exp(-i k r_star) + i k A_out exp(+i k r_star)
```

4. Record diagnostics separately:
- `solver`
- `barrier_action`
- raw Wronskian samples, if resolved
- BVP collocation residual
- boundary residual
- `|A_in|`, `|A_out|`
- `max|psi|`
- `r_out`, `r_in_eps`, `rtol`, `atol`

5. Do not loosen the existing `<1e-7` high-ell diagnostic target. The diagnostic definition may switch from raw Wronskian to stabilized residual only when the physical horizon flux scale is below double-precision resolution.

## Not recommended now

- Replacing the finite-radius radial functions by asymptotic phase-shift formulas.
- Making WKB the production radial function.
- Implementing full MST inside the blocker fix.
- Adding Riccati/log-derivative propagation before there is a concrete failure of the BVP branch.
- Changing `docs/physics_spec.md` boundary convention to fit a different paper's phase notation.

## Convention risks

- Time convention: many references use different signs for `exp(± i omega t)`. Re-derive ingoing/outgoing signs before copying formulas.
- Radial phase: outer matching must use `r_star`, not `r`.
- Wronskian sign: with the project convention, unit ingoing has `W=-2ik`, unit outgoing has `W=+2ik`.
- Master variables: Li-Hou-Zhao `psi^(±)` are not generically the same as Moncrief or Martel-Poisson gauge-invariant variables.
- RW/Zerilli parity: odd/even phase shifts may differ by phase relations even when transmission probabilities agree.
- Teukolsky/Sasaki-Nakamura references often use different radial functions and asymptotic powers; compare only after transformation.
- Coulomb/MST asymptotics use `z^{± i epsilon}` factors that correspond to the Schwarzschild logarithmic `r_star` phase only after normalization conversion.

## Minimal implementation advice

For the current codebase, the minimal stable route is already the right class of solution:

- high-barrier branch: unit-incoming-at-infinity BVP in `r_star`;
- low-barrier branch: outward unit-horizon shooting;
- WKB barrier action: branch selector and diagnostic;
- public scaling: unchanged through `A_in`;
- diagnostics: stabilized residual for unresolved flux, raw Wronskian for resolved flux.

Small hardening items for T4, if more work is requested:

- store raw Wronskian residual and stabilized residual as separate fields instead of overloading one value;
- add `r_out` sensitivity checks for high-barrier phase factors;
- add a transition-zone test near the barrier-action threshold;
- optionally add an external MST/BHPT Toolkit comparison fixture for a few low/moderate modes.

## T7 validation recommendations

1. Keep active high-barrier tests:
- `ell=8, k=0.5, r_out=120`, odd/even;
- `ell=6, k=0.2, r_out=120`, odd/even;
- `ell=12, k=0.5`, odd/even finite and small boundary residual.

2. Add or retain assertions:
- `solver == "bvp_unit_infinity"` for high-barrier cases;
- `barrier_action > threshold`;
- `A_in = 1` within tolerance;
- `|A_out| <= 1 + tolerance` for tunneling reflection;
- boundary residual `<1e-8`;
- stabilized residual `<1e-7`;
- `max|psi|` finite and non-exploding.

3. For raw Wronskian:
- require raw Wronskian only when expected flux scale is above double-precision resolution;
- otherwise record raw samples but validate collocation plus boundary residual.

4. Rerun Phase 3 selected-probe and lmax convergence after Q012:
- historical lmax/near-axis failures may change after radial stabilization;
- Q013 flat no-lens O(1) mismatch remains independent and should not be blamed on Q012.

5. Future optional oracle:
- compare a small set of modes against an MST implementation or BHPT Toolkit, but only after translating all normalizations to the project `A_in/A_out` convention.
