# Phase 6 external BHPT direct-integration slice (V1)

## Scope and acceptance meaning

This slice is an external-source calibration of the frozen 30-key set in
`runs/phase6/v1_execution_contract_v4_20260806/D_external_direct_calibration.jsonl`
(SHA-256 `d572c88259ef4b42b490af263d012a8de880458902dcf5a4d303c9f587cd466b`).
It is not whole-domain acceptance, does not use paper-figure agreement, and
cannot produce a global GREEN state.

The 30 keys contain 15 odd and 15 even modes at the following frozen points:

- `kM=0.5`: `ell=2`;
- `kM=1`: `ell=20,39,40,41`;
- `kM=2`: `ell=60,79,80,81,153`;
- `kM=4`: `ell=120,159,160,161,360`.

Each multipole occurs once in each parity sector.

## Independent external calculation contract

The Wolfram producer calls the upstream
`BlackHolePerturbationToolkit/ReggeWheeler` package at commit
`2e01209271fb3d0d92705d5c27bd9e00a6140981`. The checkout must be clean, and
the runner verifies these source hashes before attempting science:

- `Kernel/ReggeWheelerRadial.m`:
  `2af593f527b39d2b7ece71f99e50ecb6b84399342251985004d6d2e2c3fed41f`;
- `Kernel/NumericalIntegration.m`:
  `6619df2ceaa83d373152ff20740a884c8a8bd401e50c0c91a20c1d21cc879ae0`;
- `LICENSE`:
  `b8baa31999241b81142016a24cdf8ea98f21d628d995592ba52def4ac9bca24b`.

For every key, one external `ReggeWheelerRadial` API call requests two
independently integrated boundary solutions with
`Method -> {"NumericalIntegration", "Domain" -> ...}`:

- odd parity uses the Regge--Wheeler potential;
- even parity uses the Zerilli potential directly;
- both sectors solve `In` and `Up` boundary conditions;
- even modes are not obtained from a Chandrasekhar/Starobinsky parity ratio;
- no SchWO radial solver, MST result, pseudoinverse, or internal fallback is
  permitted.

Thus the complete request represents 30 external API calls and 60 external
boundary solutions. `In` is decomposed against `Conjugate[Up]` and `Up` at
three overlap radii. The selected scattering convention is

\[
T=1/A_{\rm inc},\qquad
R=A_{\rm ref}/A_{\rm inc},\qquad
S_\ell=-A_{\rm ref}/[(-1)^\ell A_{\rm inc}],
\]

with time dependence `exp(-i*k*t)` and
`r_star=r+2*log(r/2-1)` for `M=1`. No phase or normalization fit is allowed.
Working precision is 800 decimal digits, with precision and accuracy goals of
200 digits. Per-mode output keeps numerical and convention uncertainty
budgets separate; matching-radius spread, flux residual, asymptotic-series
truncation, and cross-backend differences are not silently collapsed into one
error number.

## V1 formal terminal result (2026-08-08)

Formal evidence root:

`runs/phase6/radial_validation/v1_external_bhpt_direct_selected_v2_20260808_py314`

The source and frozen 30-key request validated, but no executable
`WolframKernel` was available. `/usr/local/bin/wolframscript` version 1.6.0 was
visible only as a wrapper and was not treated as a scientific kernel. The
terminal state is therefore:

- overall selected calibration: `NOT_ASSESSED / BLOCKED_BY_RUNTIME`;
- science executed: false;
- external records produced: 0;
- each of the 30 modes: `NOT_ASSESSED` with an explicit numerical budget and
  an explicit convention budget;
- internal fallback used: false;
- paper figures run: 0.

The terminal root is immutable (`0555` directory, `0444` regular files) and
was reloaded through the evidence validator. File hashes are:

- `request.json`:
  `aa27b79bd0c445750eb833e42d291c5f5c6c3771bc11b79e94dfce277250ee09`;
- `evidence.json`:
  `70a43c0ccf159cd232a58e7dd5be1a020b989885102ecaf89cdda1d0d7434858`;
- `manifest.json`:
  `4e2e604c97aff752348d0f668989ee01392602321617757b714c7ef1b0e79ca2`.

The earlier immutable root ending in
`v1_external_bhpt_direct_selected_v1_20260808_py314` is retained as a
superseded blocked predecessor. V2 is authoritative because its request also
binds the Python runner and validation-module hashes and its validator checks
the complete uncertainty, matching-radius, runtime, and call-count schemas.

This durable blocker must not be reinterpreted as a failed physical benchmark
or as an internally substituted result. A future attempt requires a genuinely
executable Wolfram kernel and a fresh evidence root; this root is never reused
or overwritten.
