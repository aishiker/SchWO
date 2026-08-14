# Phase 6 V3.1-X external direct-route design

Date: 2026-08-13

Gate ID: `phase6_v3_1_x_external_direct_route_v1`

State at freeze: `NOT_ASSESSED / PACKAGE CANDIDATE`

This is a distinct gate created by Root T0 under the review-gate liveness
protocol after V3.1-U exhausted two bounded repairs and formal T7 returned
`ESCALATE / FAIL`. It is not V3.1-U repair cycle 3. It preserves every V3.0
science authority and replaces only the failed external MST route with one
predeclared BHPT `NumericalIntegration` route. No science is executed by this
design.

## Frozen scientific boundary

- Production V3.1 remains exact `496` Route-A modes and `9920` Route-A ladder
  nodes.
- Route U remains exact `318` modes and `954` precision nodes.
- Route B remains exact `102` AP modes and `458` AP intents/nodes.
- Route C remains the exact ordered `23` odd anchors derived from
  `V3A-MODE-BHPT-RW-001`.
- All 16 V3.1 thresholds and five certificate IDs are unchanged.
- The seven protected SchWO radial sources are byte-frozen.
- Failed V3.1/V3.1-U/sentinel science is evidence only. It may not be read as
  an accepted value, cache, checkpoint, initial condition, fit, or selected
  method result.
- The 14 prior MST successes may not define a favorable subset. All 23 keys
  use the same direct method and the same input-derived ladder.

## Exact Route-C key order

```text
00 (0.1,2,odd)   01 (0.1,3,odd)   02 (0.1,4,odd)   03 (0.1,8,odd)
04 (0.5,2,odd)   05 (0.5,3,odd)   06 (0.5,4,odd)   07 (0.5,10,odd)
08 (1,2,odd)     09 (1,3,odd)     10 (1,4,odd)     11 (1,5,odd)
12 (1,13,odd)
13 (2,2,odd)     14 (2,3,odd)     15 (2,4,odd)     16 (2,10,odd)
17 (2,18,odd)
18 (4,2,odd)     19 (4,3,odd)     20 (4,4,odd)     21 (4,20,odd)
22 (4,28,odd)
```

The compact canonical inventory SHA-256 is
`5e93fca57b6d4fb82762043fedea4631de92111164c8c4a991d76925e3867c76`.

## External numerical method

Each node starts one fresh Wolfram kernel and makes exactly one public call:

```text
ReggeWheelerRadial[
  2, ell, omega,
  Method -> {"NumericalIntegration", "Domain" -> domainRules},
  "BoundaryConditions" -> {"In", "Up"},
  "Potential" -> "ReggeWheeler",
  WorkingPrecision -> wp,
  PrecisionGoal -> pg,
  AccuracyGoal -> ag
]
```

The frequency is constructed from an exact rational map before `N`:

```text
0.1 -> 1/10; 0.5 -> 1/2; 1 -> 1; 2 -> 2; 4 -> 4
```

The WLS must assert that the numerical frequency carries at least
`wp+10` decimal digits. Machine-precision construction is a hard error.

The BHPT code independently integrates the horizon-normalized `In` solution
and infinity-normalized `Up` solution. At each of three overlap radii, with
dot denoting `d/dr_star`, it extracts

```text
D     = conj(U) Udot - U conj(Udot)
A_in  = (H Udot - U Hdot)/D
A_out = (conj(U) Hdot - H conj(Udot))/D
A_H   = 1
S     = (-1)^(ell+1) A_out/A_in
Gamma_flux = |A_H|^2/|A_in|^2
Gamma_S    = 1-|S|^2
```

The raw evidence retains `H,Hdot,U,Udot,D,A_in,A_out,A_H`, signed currents,
positive fluxes, flux balance and all three overlap projections. WLS emits
only a minimal independent amplitude/current basis as canonical decimal
strings. Python derives all redundant ratios, probabilities and logarithms
from those strings. Missing/nonfinite values, zero or ill-conditioned `D`,
boundary-series failure, source drift, process failure, or a missing node
fails closed.

## Frozen BHPT overlay

The base source is the immutable 25-file snapshot rooted at
`runs/phase6/external_sources/bhpt_reggewheeler_2e012092_v1_20260813/source`.
Its `Kernel/NumericalIntegration.m` SHA-256 is
`6619df2ceaa83d373152ff20740a884c8a8bd401e50c0c91a20c1d21cc879ae0`.

Every node receives a fresh copied snapshot. Exactly the first odd-sector
occurrence of each of the following literals is replaced; the even-sector
occurrences and all other bytes remain unchanged:

```text
rin=2+10^-5
rout =100*Abs[\[Omega]]^-1;
```

The six allowed transformed variants are:

| Variant | Replacement `rin` | Replacement `rout` | SHA-256 |
|---|---|---|---|
| `rin8_m1` | `rin=2+10^-8` | `rout =Max[300,8 Sqrt[l(l+1)]/Abs[\[Omega]]];` | `ec110e7612a14fce135be77a649324a98498da04b18785502e969ec437622380` |
| `rin10_m1` | `rin=2+10^-10` | `rout =Max[300,8 Sqrt[l(l+1)]/Abs[\[Omega]]];` | `a8601cd1b377bf4741035a03bec98590ebffbec0004a63af498a260f1d05c5fc` |
| `rin12_m1` | `rin=2+10^-12` | `rout =Max[300,8 Sqrt[l(l+1)]/Abs[\[Omega]]];` | `574f64024363e59b2fea678f33ed3b373e73374b33efb318fe781aa5b6607958` |
| `rin10_m2` | `rin=2+10^-10` | `rout =2 Max[300,8 Sqrt[l(l+1)]/Abs[\[Omega]]];` | `42369d4584fc079224d5ae9bd6e7565aafeb0a52d0d2a0f06c1666d54dbee008` |
| `rin10_m4` | `rin=2+10^-10` | `rout =4 Max[300,8 Sqrt[l(l+1)]/Abs[\[Omega]]];` | `b5c7b2e496daac3f7d1edf48843b41e7633800329d528065c0f87a94db641bbf` |
| `rin10_m8` | `rin=2+10^-10` | `rout =8 Max[300,8 Sqrt[l(l+1)]/Abs[\[Omega]]];` | `8bdf36d3bba5dc2ffa6e4949dffcd15d42a90acba9c0f9cf431fa8c30e71ffd5` |

The producer must prove one old occurrence and one new occurrence at the odd
sites, unchanged even literals, the exact whole-file hash, complete copied
snapshot identity and loaded-source start/end identity. No runtime-selected
patch, per-key method, environment fallback or additional changed byte exists.

## Seven-node ladder per key

Let

```text
B(k,ell) = Max[300,8*Sqrt[ell*(ell+1)]/k].
```

The selected node is `wp/pg/ag=120/60/60`, `r_in-2=1e-10`, outer multiplier
`1`. The only adjacent precision node is `90/45/45`, so the replacement never
uses lower working precision or goals than the failed MST contract. Three
overlap fractions are always `0.80,0.88,0.96`, with `0.88`
selected. The exact unique node order is:

```text
P0  90/45/45, rin=1e-10, m=1
P1 120/60/60, rin=1e-10, m=1   [selected]
I0 120/60/60, rin=1e-8,  m=1
I2 120/60/60, rin=1e-12, m=1
O2 120/60/60, rin=1e-10, m=2
O4 120/60/60, rin=1e-10, m=4
O8 120/60/60, rin=1e-10, m=8
```

For each node, the `In` integration reaches `0.96*r_out` and the `Up`
integration reaches `0.80*r_out`. The three overlap values are evaluated from
the same independently integrated pair. This gives exact official Route-C
cardinality `23*7=161` public calls, `322` boundary solutions and `483`
overlap records.

The predeclared sentinel runs selected node `P1` for all 23 keys and the six
nonselected nodes for fixed input-geometry extrema ordinals 3 and 22. After
deduplication it contains exactly `35` public calls, `70` boundary solutions
and `105` overlap records. Sentinel values are never reusable in the official
candidate.

## Acceptance and budgets

Every mandatory node must complete. Numerical budgets and convention budgets
are separate fields on every accepted record. Numerical checks include the
precision, inner, outer and overlap axes, determinant conditioning, direct
signed-current balance and direct `Gamma_flux` versus `Gamma_S`. Convention
checks bind Fourier sign, tortoise additive constant, RW normalization,
`In/Up` unit transmission, current orientation and V3-F02 conversion.

The package does not alter any V3.0 threshold. The future official whole-gate
result must evaluate the unchanged 16 V3.1 thresholds exactly as frozen in
`configs/phase6_v3_0_thresholds.json`; the direct route supplies the Route-C
records needed by the existing applicable comparisons.

Because the frozen AP precision thresholds name the `80/120/180` Route-B
ladder rather than this external ladder, V3.1-X separately freezes the
following route-admission criteria before implementation. They reuse equal or
stricter observable budgets already frozen for V3.1 and do not replace,
weaken, reinterpret, or increment the count of the 16 thresholds:

```text
external adjacent precision:  symmetric relative complex-S <= 5e-7
external adjacent precision:  absolute log-Gamma change <= 1e-4
external adjacent r_in:       symmetric relative complex-S <= 1e-6
external adjacent r_in:       absolute log-Gamma change <= 2e-4
external adjacent r_out:      symmetric relative complex-S <= 2e-6
external adjacent r_out:      absolute log-Gamma change <= 3e-4
three-overlap spread:         symmetric relative complex-S <= 2e-6
three-overlap spread:         absolute log-Gamma change <= 2e-4
per-node signed-current balance absolute value <= 1e-8
```

Every applicable criterion must pass on every key. `log Gamma` criteria apply
only when both compared values are finite and positive; absence/nonpositivity
is a node failure, not an exemption. Convention mismatch cannot be absorbed
into a numerical budget or phase fit.

## Process, provenance and publication

T0 sentinel and official dispatches are distinct canonical O_EXCL `0444`
files, each binding one exact fresh UTC root and exact reviewed source hashes.
The sentinel dispatch is single-use and cannot authorize official science.
The official dispatch cannot exist before a formal T7 sentinel
`ADVANCE_DECISION: ADVANCE`.

One outer Python producer is launched per dispatch. It runs Wolfram children
strictly sequentially, exactly one child and one public API call per node, and
records exact argv/environment/start/end/wait/reap/process-group-empty
receipts. The only permitted kernel is
`/Volumes/JohnnyTforGR/Applications/Wolfram.app/Contents/MacOS/WolframKernel`
with frozen SHA-256
`70ad9d850224b4723a04c581e769579cc3df4b4392ae2ed1886780e6b9be046c`.

Every record is canonical, ordered, unique, O_EXCL/no-follow, fsynced,
`0444/nlink1`; terminal directories are `0555`. Any node or validation error
publishes immutable `failure.json` plus a non-self-referential manifest and
makes that attempt nonresumable/nonretryable. Source and protected identities
must match at start and end. No network access or source substitution is
permitted.

## Resource gate

Existing immutable direct-integration evidence at 40/60 digits gives only a
lower-precision feasibility/timing reference (the count-scaled figures were
about 74 minutes centrally and 7.7 hours under its observed maximum). It does
not bound the frozen 90/120-digit schedule or multiplier-8 geometry and must
not be presented as the V3.1-X runtime estimate. The 35-call sentinel must
report fixed geometry-class timings. Before official dispatch, the controller
must derive a conservative projection from the maximum sentinel class time,
inflate by exact domain-length ratio and a fixed safety factor of at least 2,
and require projected wall time `<=36 h`. Projected storage must remain below
one quarter of measured free workspace space. Resource failure blocks official
dispatch but may not select keys or methods.

## Exact implementation scope

Only these six new paths may be created or changed during implementation:

```text
scripts/phase6_v3_1_x_bhpt_direct.wls
src/schwgw/validation/phase6_v3_external_direct.py
src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py
scripts/phase6_v3_1_x_external_direct.py
tests/unit/test_phase6_v3_external_direct.py
tests/regression/test_phase6_v3_external_direct_publication.py
```

Implementation review is zero-science. No dispatch or real root is created
until formal T7 accepts the exact implementation. The 35-call sentinel then
requires its own one-use T0 dispatch and formal T7 terminal review. Only a
sentinel `ADVANCE` permits a different official dispatch. Official science
recomputes Route A/U/B/C from zero and requires a final formal T7 scientific
review.

## Nonclaims

- V3.1 and V3.1-U remain `FAIL`; V3.1-X science is `NOT_ASSESSED` at freeze.
- This is an odd-only external anchor, not independent even-sector evidence.
- The overlay route is not a pristine-upstream claim.
- Package or implementation GREEN means only bounded readiness.
- No V3.2, Li-figure equivalence, finite-radius observer claim, full-domain V3
  certification or global GREEN follows from this design.
