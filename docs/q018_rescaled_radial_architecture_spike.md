# Q018 Rescaled Radial Architecture Spike

Date: 2026-07-06

Thread: T4n radial ODE and matching

## 1. Problem Statement

The accepted `kM=2` production artifacts cover only the existing
`[-30,30]^2` x-z domain.  The current Q018 high-`ell`
`evanescent_tail_suppressed` branch starts at `ell=153`; its certified
`valid_until_r` range is about `42.47M` through `53.33M`, so it does not
cover R60.  T4m correctly added `BoundaryConfig.required_eval_radius` so a
request for `r=60M` fails closed instead of returning an uncertified
zero-tail solution.

This spike asks whether a stronger radial architecture can compute reliable
unit-incoming-at-infinity RW/Zerilli fields `psi(60)` and `dpsi/dr(60)` for
`k=2`, `r_out=300`, `ell=153..180`, odd/even.

## 2. Why T4m Is Correct But Insufficient

T4m is correct because the existing suppression certificate is domain-limited:
it records where the local WKB tail action from `r` to the outer turning point
is at least 55, and it refuses to extrapolate beyond that radius.  This
prevents R60 production from silently using a solution that is only certified
near the accepted `[-30,30]^2` radius.

It is insufficient because it is a guard, not a solver.  It does not return
nonzero finite-radius master fields at `r=60`, and it does not provide a
spin-2 observable-level tail bound.  R60_K2 therefore remains gated.

## 3. Candidate Method Assessment

| Method | Assessment | Main risk | Minimal next step |
|---|---|---|---|
| A. High-precision bidirectional matching oracle | Not executable in the current local Python environments: `mpmath`, `gmpy2`, and `sympy` are unavailable in both `/opt/homebrew/bin/python3` and the bundled Codex Python. No global install was performed. | Without arbitrary precision, the horizon/outer bases cross an `S~700` dynamic range and double precision overflows or loses rank. | Add a project-local optional high-precision dependency or an isolated script environment, then implement an oracle for one mode before running all 8 modes. |
| B. Logarithmic / Riccati / scaled-amplitude propagation | Scientifically plausible but not production-ready in this slice. A useful design is to propagate logarithmic derivatives and signed log-amplitudes for independent bases, match at `r=60` or a nearby conditioning point, then reconstruct normalized `psi` and `dpsi/dr` only after solving the scaled 2x2 system. | Complex phase, zeros/poles of Riccati variables, branch tracking, and normalization recovery must be handled explicitly. A partial implementation risks producing finite but convention-incompatible fields. | Write RED tests for one `ell=153` odd mode requiring finite `psi(60)`, finite `dpsi/dr(60)`, `A_in≈1`, and stable results under precision/tolerance changes. |
| C. Observable-level conservative bound | Current evidence says no-go for GREEN. Local WKB actions at `r=60` are too small for the first suppressed modes once even modest spin-2 polynomial prefactors are allowed. | A radial-only `p=0` bound would ignore metric reconstruction, tensor harmonics, and electric-tidal/Weyl derivatives. | Keep as a diagnostic/no-go unless a derivation includes reconstruction and observable prefactors and sums over suppressed modes. |

## 4. Selected Mode Diagnostics

Production guard probe:

```text
M=1, k=2, r_out=300, required_eval_radius=60,
r_in_eps=1e-6, rtol=1e-10, atol=1e-12
```

| ell | sector | current production outcome | solver/code | R60 covered | valid_until_r | runtime |
|---:|---|---|---|---|---:|---:|
| 153 | odd | structured failure | `evanescent_tail_required_radius_uncovered` | false | `42.472089374733` | `0.480s` |
| 153 | even | structured failure | `evanescent_tail_required_radius_uncovered` | false | `42.472089355132` | `0.479s` |
| 156 | odd | structured failure | `evanescent_tail_required_radius_uncovered` | false | `43.654269085025` | `0.458s` |
| 156 | even | structured failure | `evanescent_tail_required_radius_uncovered` | false | `43.654269066874` | `0.468s` |
| 168 | odd | structured failure | `evanescent_tail_required_radius_uncovered` | false | `48.464158978522` | `0.449s` |
| 168 | even | structured failure | `evanescent_tail_required_radius_uncovered` | false | `48.464158964916` | `0.456s` |
| 180 | odd | structured failure | `evanescent_tail_required_radius_uncovered` | false | `53.333518655706` | `0.436s` |
| 180 | even | structured failure | `evanescent_tail_required_radius_uncovered` | false | `53.333518645326` | `0.455s` |

Double-precision direct bidirectional baseline:

| mode | rtol/atol | outcome | runtime | warnings |
|---|---|---|---:|---:|
| `ell=153`, odd | `1e-8/1e-10` | step-size failure after overflow/invalid warnings | `0.230s` | 110 |
| `ell=153`, odd | `1e-10/1e-12` | step-size failure after overflow/invalid warnings | `0.414s` | 122 |
| `ell=153`, odd | `1e-12/1e-14` | step-size failure after overflow/invalid warnings | `0.739s` | 141 |

This baseline is not a usable oracle.  Tightening tolerance increases runtime
and warning count but does not produce finite fields.

Target-radius WKB diagnostic, recomputed from current project potentials:

| ell | sector | outer turning point | `S_tail(60)` | `exp(-S_tail)` | `ell^2 exp(-S)` | `ell^4 exp(-S)` |
|---:|---|---:|---:|---:|---:|---:|
| 153 | odd | `75.729210131606` | `15.334712751011` | `2.188864e-07` | `5.123913e-03` | `1.199457e+02` |
| 153 | even | `75.729210110560` | `15.334712718037` | `2.188865e-07` | `5.123913e-03` | `1.199457e+02` |
| 156 | odd | `77.229625055447` | `17.556073057696` | `2.374075e-08` | `5.777548e-04` | `1.406024e+01` |
| 156 | even | `77.229625035959` | `17.556073025582` | `2.374075e-08` | `5.777548e-04` | `1.406024e+01` |
| 168 | odd | `83.231131379603` | `27.338154584875` | `1.340264e-12` | `3.782761e-08` | `1.067646e-03` |
| 168 | even | `83.231131365073` | `27.338154556535` | `1.340264e-12` | `3.782761e-08` | `1.067646e-03` |
| 180 | odd | `89.232430317243` | `38.387892662728` | `2.129855e-17` | `6.900730e-13` | `2.235837e-08` |
| 180 | even | `89.232430306190` | `38.387892638092` | `2.129855e-17` | `6.900730e-13` | `2.235837e-08` |

These values are useful diagnostics, but not regression oracles for
`psi(60)` or `dpsi/dr(60)`.  The first suppressed modes are not negligible
under conservative spin-2 polynomial allowance.

## 5. Prototype Status

No production or test-only radial helper was added.  The only executable
prototype attempt was a direct call to the existing double-precision
bidirectional branch for `ell=153`, odd.  It failed with

```text
Radial basis integration failed: Required step size is less than spacing between numbers.
```

after overflow/invalid floating-point warnings.  Because high-precision ODE
support is not available locally and double precision fails before producing
finite values, this spike does not provide numerical `psi(60)` or
`dpsi/dr(60)` values.

## 6. Future GREEN Implementation Slice

R60_K2 cannot be promoted to GREEN from this spike alone.  A future GREEN
method slice is still scientifically plausible, but it must implement and
verify a real rescaled architecture.  Minimum acceptance should include:

- finite `psi(60)` and `dpsi/dr(60)` for `ell=[153,156,168,180]`, odd/even;
- unit incoming-at-infinity normalization with `A_in≈1`;
- clear recovery of `A_out`, phase factor, and radial interpolation values;
- Wronskian/flux diagnostics defined in the scaled normalization;
- sensitivity checks under precision/tolerance or mesh changes;
- no changes to Fourier/radial phase conventions;
- no `ell_max` truncation or threshold relaxation.

## 6.1 T4o Oracle Prerequisites

T4o adds prerequisites for the future GREEN implementation slice, not the
implementation itself.

Code boundary:

- `src/schwgw/numerics/experimental/q018_rescaled_oracle.py` defines
  `RescaledOracleRequest`, `RescaledOracleResult`, and
  `solve_q018_rescaled_oracle(...)`.
- `solve_q018_rescaled_oracle(...)` is explicitly experimental and raises
  `NotImplementedError`.
- The module is not imported by `schwgw.numerics` and is not wired into
  `solve_radial_mode(...)`.
- The existing production `required_eval_radius=60` path remains
  fail-closed with `evanescent_tail_required_radius_uncovered`.

Future oracle contract:

- output normalization is unit incoming-at-infinity, with `A_in ~= 1`;
- output must be valid at `required_radius`;
- `psi`, `dpsi_dr`, `A_in`, and `A_out` must be mutually consistent;
- diagnostics must record method, precision/tolerance, matching radius,
  finite checks, and a Wronskian or flux proxy;
- no Fourier, radial phase, `ell_max`, residual-threshold, Route B, or
  Q005 convention changes are allowed.

Dependency decision:

- `pyproject.toml` now has optional group `oracle = ["mpmath"]`.
- This is only a project-local optional dependency declaration.  No global
  install was performed in T4o.

RED test boundary:

- `tests/physics/test_q018_rescaled_oracle.py` has a default-suite contract
  test proving the experimental API is documented, production still fails
  closed at R60 for `ell=153`, and the experimental function is not
  implemented.
- The same file has an opt-in `full_regression` RED test gated by
  `Q018_RUN_EXPERIMENTAL_ORACLE_TESTS=1`.  It requires future finite
  oracle values for `M=1,k=2,r=60,r_out=300,ell=153,sector=odd`, and
  currently fails with `NotImplementedError` by design.

This remains **YELLOW / prerequisites only**.  It does not authorize T8
R60_K2 production, R60_K4 production, `kM=4`, larger-domain artifacts, or
any bypass of the T4m guard.

## 6.2 T4p Experimental Oracle Prototype

T4p implements the first experimental oracle prototype inside
`src/schwgw/numerics/experimental/q018_rescaled_oracle.py`.  It remains
outside the production radial solver and is not exported by
`schwgw.numerics`.

Method:

- Propagate the horizon-ingoing logarithmic derivative
  `y=(d psi/dr_star)/psi` from `r_in=2M(1+r_in_eps)` to the requested radius.
- Use the Riccati equation
  `dy/dr = [V_l(r)-k^2-y^2]/f(r)`.
- At the requested radius, set a temporary state `psi=1` and
  `dpsi/dr=y/f`, then integrate that state outward to `r_out`.
- Match the outward-integrated temporary state to
  `A_in exp(-ikr_star)+A_out exp(+ikr_star)` at `r_out`.
- Rescale by `1/A_in` to recover unit incoming-at-infinity normalization at
  the requested radius.

This avoids the direct outer incoming/outgoing basis cancellation at
`r=60`, where the physical tail is small but the separately propagated outer
bases are large.  It also avoids modifying the production BVP or the
`evanescent_tail_required_radius_uncovered` guard.

Opt-in target result:

```text
M=1
k=2
r=60
r_out=300
ell=153
sector=odd
rtol=1e-10
atol=1e-12
```

| quantity | value |
|---|---:|
| `psi(60)` | `-2.4468035897057717e-07 + 5.348044242428217e-08 i` |
| `dpsi/dr(60)` | `-3.914493075323992e-07 + 8.55601252245548e-08 i` |
| `A_in` | `1 + 0 i` |
| `A_out` | `0.9088085469746445 - 0.41721340456154404 i` |
| `abs(A_out)` | `0.9999999999999996` |
| outer boundary residual | `1.5790813988009534e-16` |
| normalization residual | `5.001912885297727e-17` |
| log-derivative match residual | `1.4360870152372987e-16` |
| match condition number | `2.0134228187919474` |
| Riccati / outward steps | `1759 / 1202` |
| max temporary unit-state amplitude | `1.5849068752621084e7` |

The opt-in test also checks determinism and a shifted requested radius
(`r=60.1`) to reject hard-coded constants.

Limitations:

- This is a double-precision SciPy prototype, not a reviewed arbitrary
  precision oracle.
- It has only been accepted by the active test for the minimum odd-sector
  target mode `ell=153`.
- It does not yet certify all suppressed modes `ell=153..180`, both parity
  sectors, or production partial-wave sums at R60.
- It does not provide an observable-level spin-2 tail bound.
- It does not authorize R60_K2/R60_K4 artifacts, `kM=4`, larger-domain
  production, or bypassing `BoundaryConfig.required_eval_radius`.

## 7. No-Go For Current Production

Current production remains **YELLOW / gated**.  The available methods in this
slice do not compute reliable R60 radial fields and do not provide a
conservative spin-2 observable-level bound.  T8 must not run R60_K2
production from this spike.

Required future work is a rescaled/log-amplitude radial architecture, most
likely based on logarithmic derivative propagation plus scaled amplitude
bookkeeping, with explicit handling of phase, poles, matching, and
normalization recovery.

## 8. kM=4 Non-Validation

This spike does not validate `kM=4`.  All diagnostics here use `M=1`,
`k=2`, `r=60`, and `r_out=300`.  No conclusion follows for `kM=4`,
R60_K4, its `lmax`, or its turning-point structure.
