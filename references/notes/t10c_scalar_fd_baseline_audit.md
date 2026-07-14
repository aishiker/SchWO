# T10c Scalar Finite-Difference Baseline Audit

Date: 2026-07-07

Role: internal method note for deciding whether an external scalar Helmholtz finite-difference MATLAB project can serve as a baseline/reference for the Schwarzschild GW wave-optics project.

External project audited:

`/Users/aishiker/Desktop/学习/通向时空之路/博士/血肉苦弱_机械飞升/Codex-test/Projects/helmholtz-fd-matlab`

Files read:

- Current project: `project.md`, `status.md`, `docs/numerics.md`, `docs/validation_plan.md`
- External notes: `notes/implementation_notes.md`, `notes/figure7_plan.md`, `notes/figure7_impl_notes.md`, `notes/figure7_debug_report.md`, `notes/figure7_theta_pi4_notes.md`, `notes/figure7_theta_pi4_debug.md`
- External MATLAB source: `src/*.m`

## Executive conclusion

The MATLAB project is useful as a **scalar Schwarzschild Helmholtz finite-difference and image-reconstruction reference**, especially for finite-radius lens-plane sampling and Fourier/Hankel image integrals.

It must **not** be treated as a spin-2 RW/Zerilli/Weyl validation oracle. Its physics is scalar, axisymmetric, effectively `m=0`, and it solves a 2D finite-difference boundary-value problem for `hatPhi = r Phi`, not tensor metric perturbations or packaged GW polarization scalars.

Recommendation: T8/T10 should build a future **scalar baseline fixture**, but only behind an explicit scalar/imaging label. It should not gate Q018, Route B polarization, RW/Zerilli radial solver correctness, or spin-2 convergence.

## 1. MATLAB scalar project: equation and unknown

The external code implements a scalar monochromatic field on Schwarzschild, assuming axisymmetry:

- Units: `G = c = M = 1` in the implemented examples.
- Time dependence: `Phi(t,r,theta) = Phi(r,theta) exp(-i omega t)`.
- Azimuthal dependence: `partial_phi Phi = 0`.
- Tortoise coordinate:

```text
x = r + 2M log(r/(2M) - 1)
```

- Numerical unknown:

```text
hatPhi = r Phi
```

The scalar equation represented in the notes is

```text
d_x^2 hatPhi
+ (1/r^2)(1 - 2M/r) (1/sin theta) d_theta(sin theta d_theta hatPhi)
+ [omega^2 - (2M/r^3)(1 - 2M/r)] hatPhi
= S(r-rS, theta-pi).
```

The source is a scalar point-source prescription at `theta = pi`, written in the notes as

```text
S = 1/[r(1 - 2M/r)] delta(r-rS) delta(cos theta + 1).
```

In implementation, this delta source is not inserted as a conventional finite-difference RHS distribution. Instead, three neighboring nodal values around the source are prescribed from the appendix formula used by the MATLAB project.

## 2. Boundary conditions and source treatment

Radial boundaries:

- Inner radial boundary near the horizon: pure ingoing Sommerfeld-type condition.
- Outer radial boundary: pure outgoing Sommerfeld-type condition.
- With `exp(-i omega t)`, the code applies ghost-cell phase relations of the form

```text
hatPhi_{-1,j} = exp(i M omega Delta) hatPhi_{0,j},
hatPhi_{N+1,j} = exp(i M omega Delta) hatPhi_{N,j}.
```

Convention risk: the sign of these phase factors is tied to the external paper/code convention for `exp(-i omega t)` and to the direction of the tortoise coordinate. These relations should not be copied into the spin-2 radial solver without a fresh convention derivation.

Axis boundaries:

- Regularity at `theta = 0, pi` is enforced as a Neumann/axis condition:

```text
partial_theta hatPhi = 0.
```

- Ghost relations:

```text
hatPhi_{i,-1} = hatPhi_{i,1},
hatPhi_{i,N+1} = hatPhi_{i,N-1}.
```

- The singular `cot(theta)` angular stencil is replaced at the axis by a doubled second-derivative form.

Source prescription:

- The code selects the source radial index nearest to `rS_target`.
- Three nodes adjacent to `(rS, theta=pi)` are fixed:

```text
hatPhi_{iS-1,N} = hatPhi_{iS+1,N}
  = A rS exp(i omega Delta)/(Delta sqrt(1 - 2M/rS)),

hatPhi_{iS,N-1}
  = A/Delta_theta * exp(i omega rS Delta_theta/sqrt(1 - 2M/rS)).
```

This is a scalar source regularization/implementation choice, not a GW incident-wave boundary condition.

## 3. Grid, discretization, and solve

Grid:

- Uniform in tortoise coordinate `x` and polar angle `theta`.
- `theta_j = j Delta_theta`, `j = 0..N`, `Delta_theta = pi/N`.
- `x_i = x_min + i Delta`, typically also with `N+1` radial points.
- The code uses `delta = Delta_theta / Delta` in the finite-difference coefficients.
- Radius is recovered by numerical inversion of `x(r)`.

Representative external parameters:

- Figure-5-like field solve: `x in [-2, 23]`, `N = 1000`, so a `1001 x 1001` grid.
- Image runs use `x_max = 25` because `r_obs = 20` corresponds to `x_obs = 24.394449...`.
- Common values: `M = 1`, `M omega = 12`, `rS_target = 6`, `source_amplitude = 1`.

Discretization:

- The code assembles a complex sparse linear system directly:

```text
A phi = b.
```

- Flattening convention in MATLAB:

```text
idx = i + (j-1) nx.
```

- Interior angular stencils use the standard finite-difference representation of

```text
(1/sin theta) partial_theta(sin theta partial_theta hatPhi).
```

- Axis stencils use the regularized axis formula.

Solve diagnostic:

- `solve_field.m` records a relative linear-system residual:

```text
norm(A*phi_vec - b) / max(norm(b), 1).
```

This is a useful numerical diagnostic for the scalar finite-difference solve, but it is not a radial Wronskian/flux diagnostic and does not validate RW/Zerilli mode normalization.

## 4. Observer extraction and image reconstruction

Observer extraction:

- At fixed `r_obs`, the code computes `x_obs = x(r_obs)`.
- For each `theta`, it interpolates the solved `hatPhi(x,theta)` in `x` using `pchip`.
- Physical scalar field:

```text
Phi_obs(theta) = hatPhi(x_obs, theta) / r_obs.
```

- A smoothed background and fluctuation field are also computed:

```text
Phi_fluct = Phi_obs - Phi_background.
```

This background subtraction is a diagnostic/visual decomposition, not a rigorously frozen physical separation.

Image integral:

The code implements the scalar lens-plane integral corresponding to the external paper's formula (17):

```text
Phi_I(X_I) proportional to
int_{|X| <= d} d^2X Phi(X)
exp[-i (omega/f) X_I · X].
```

With image angular coordinates `theta_x = X_I/f`, `theta_y = Y_I/f`, the phase is

```text
exp[-i omega (theta_x X + theta_y Y)].
```

The absolute normalization is not frozen in the MATLAB notes/code; current outputs should be used for shapes, peak locations, relative morphology, and implementation checks, not absolute flux calibration.

Lens-plane mapping:

For an observation direction angle `theta0`, the lens plane samples the observer sphere through

```text
cos theta =
  (X/r) sin theta0
  + sqrt(1 - (X/r)^2 - (Y/r)^2) cos theta0.
```

The aperture is a disk `|X| <= d`, with typical `d = 0.5 r_obs = 10` for `r_obs = 20`.

On-axis `theta0 = 0`:

- The mapping reduces to `theta = asin(rho/r_obs)`.
- The 2D Fourier integral is reduced to a Hankel/Bessel integral:

```text
Phi_I(theta_I) proportional to
2 pi int_0^d rho d rho Phi(rho) J0(omega rho theta_I).
```

Off-axis examples:

- For `theta0 = pi/4`, `pi/2`, `3pi/4`, `pi`, the code uses a 2D Cartesian lens-plane grid and matrix multiplication for the Fourier kernel.
- It records horizontal-slice peaks, side peak positions, and brightness ratios.

## 5. Diagnostics already present in the MATLAB project

Scalar solve diagnostics:

- Sparse linear residual.
- Visual inspection of `Re Phi`, `Im Phi`, `|Phi|` on the physical half-plane.
- Source and boundary behavior through plots.

Image diagnostics:

- On-axis predicted scalar glory-ring angle:

```text
theta_g = 3 sqrt(3) M / r_obs.
```

- For `M=1`, `r_obs=20`, this gives

```text
theta_g = 0.259807621135...
```

- The theta0=0 debug note reports a measured peak around

```text
theta_peak = 0.318656182988...
theta_peak/theta_g = 1.226508...
```

Interpretation: the strongest ring selected by the current scalar image diagnostic is probably not a clean realization of the analytic glory formula alone. The total field contains direct/background structure and the peak finder can select an outer or mixed-feature peak.

Off-axis theta0=pi/4 diagnostics:

- Current notes find qualitatively plausible double-image morphology.
- The center intensity is barely changed by the implemented background subtraction.
- Reported horizontal slice peaks are approximately at `theta_x = -0.2933` and `theta_x = 0.3533`, with brightness ratios around `3.16` to `3.26` depending on total vs fluctuation field.
- The notes judge total `Phi_obs` slightly closer visually than `Phi_fluct`, but this remains qualitative.

Missing diagnostics before adopting as a fixture:

- No project-local frozen output file.
- No current-project metadata schema.
- No systematic grid-refinement convergence record in the audited notes.
- No absolute normalization convention.
- No explicit CI-friendly reduced-size fixture.

## 6. What can migrate as a scalar baseline/reference

Directly useful as scalar/imaging reference:

- A scalar Schwarzschild finite-difference baseline independent of the current partial-wave implementation.
- The observer-sphere to lens-plane sampling map.
- The on-axis Hankel integral with `J0`.
- The off-axis 2D aperture Fourier integral.
- The use of fixed saved scalar fields as read-only inputs for image reconstruction.
- Diagnostic peak-finding around `theta_g = 3 sqrt(3) M/r_obs`, with the caveat that total-field peaks need not equal the analytic glory prediction.
- Metadata fields worth preserving in future T8/T10 scalar fixtures:
  - `M`, `omega`, `rS`, `r_obs`, `x_min`, `x_max`, `N`
  - aperture radius `d`
  - lens grid resolution
  - image angular range/resolution
  - source prescription
  - boundary-condition phase convention
  - residual norm
  - chosen total/background/fluctuation field
  - peak locations and brightness ratios

Recommended future scalar fixture:

- Yes, T8/T10 should build a scalar baseline fixture if image reconstruction becomes part of accepted project outputs.
- The fixture should be explicitly named scalar, e.g. `scalar_fd_image_baseline`.
- It should use a reduced but reproducible grid suitable for local testing, plus a larger optional artifact if needed.
- It should compare saved numeric diagnostics, not generated figures.
- It should not depend on MATLAB in routine tests unless MATLAB/Octave availability is explicitly managed.

## 7. What must not migrate to the spin-2 RW/Zerilli/Weyl pipeline

Do not migrate:

- The scalar PDE as a substitute for RW/Zerilli master equations.
- The `m=0` axisymmetric setup as a proxy for incident plane GW `m = +/-2` spin-weighted structure.
- The scalar unknown `hatPhi = r Phi` as a proxy for metric perturbations, Weyl scalars, or packaged polarization.
- The scalar source-at-`theta=pi` prescription as a proxy for incident plane-wave GW coefficients.
- The finite-difference radial boundary ghost phases as direct replacements for T4 radial mode boundary conditions.
- The scalar image intensity as validation of `h_plus`, `h_cross`, `Psi0_pack`, `Psi4_pack`, or Route B electric-tidal projection.
- The scalar `theta_g` peak as a spin-2 convergence criterion.
- The background-subtracted scalar fluctuation as a production definition of a lensed GW signal.
- Plot-level gamma, percentile clipping, mirroring, or sign-flipped display axes as physical diagnostics.

In particular, this scalar FD project cannot validate:

- Q018 high-ell RW/Zerilli tail handling.
- Q014 strict-NP to packaged-polarization bridge.
- T6 Route B polarization extraction.
- Spin-2 parity phase shifts or helicity mixing.
- RW-gauge metric reconstruction.
- Finite-radius spin-2 partial-wave convergence.

## 8. Convention and implementation risks

Fourier convention:

- The scalar code assumes `exp(-i omega t)`.
- Boundary phase signs must be rederived before reuse.

Radial coordinate convention:

- The scalar FD solve is on a finite uniform `x` grid.
- The current project's main production path is a mode-by-mode radial ODE/partial-wave sum. The numerical error modes are different.

Normalization:

- The image integral is used up to an unspecified proportionality constant.
- Absolute image intensity should not be compared to M5 amplification denominators.

Field decomposition:

- `Phi_obs` vs `Phi_fluct` is diagnostic.
- The audited notes show background subtraction does not reliably isolate a clean glory component.

Angular convention:

- The scalar lens-plane mapping is geometric and can be reused after rechecking orientation/sign.
- Display-layer sign flips in plot scripts should not be adopted as mathematical conventions.

## 9. Recommendation to T8/T10

Build a scalar baseline fixture only if it is explicitly scoped:

1. Purpose: scalar image reconstruction and scalar finite-difference cross-check.
2. Non-purpose: spin-2 solver validation.
3. Input: saved scalar observer field or saved lens-plane field, not live figure generation.
4. Output: metadata plus numerical diagnostics such as peak positions, residuals, and intensity ratios.
5. Acceptance: compare scalar diagnostics against frozen scalar references with tolerances.
6. Separation: store under a scalar-specific path and make validation text state that it does not certify RW/Zerilli/Weyl physics.

Minimum recommended fixture contents:

- A small scalar FD or precomputed scalar observation fixture.
- One on-axis image reconstruction test using the Hankel `J0` integral.
- One off-axis image reconstruction test using the 2D Fourier aperture integral.
- Metadata proving the field is scalar and listing all boundary/source conventions.
- A warning in validation docs that scalar fixture failures are image-layer/scalar-baseline failures, not spin-2 radial or polarization failures.

## 10. Open issues

- The external scalar paper/source PDF is not yet integrated into the current project's `references/papers/` for this T10c audit.
- The external MATLAB project has useful notes but not a frozen current-project artifact.
- A reduced CI-friendly fixture size and tolerance policy remain to be designed.
- The scalar total-field/background-subtraction ambiguity should be resolved before using peak locations as hard acceptance criteria.
