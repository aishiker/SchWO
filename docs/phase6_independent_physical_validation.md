# Phase 6 — Independent Physical Validation

Date opened: 2026-08-06

Status: **ACTIVE; acceptance is per observable and per parameter domain.**
There is no Phase-6 project-wide GREEN state.

## 1. Scientific objective

Phase 6 separates three questions which must never be collapsed into one
verdict:

1. verification of the RW/Zerilli equations and numerical boundary-value
   problem;
2. physical validation of explicitly defined observables;
3. Li–Hou–Zhao figure reproduction as a secondary regression suite.

No full paper figure is recomputed in this phase unless a later, separate
authorization identifies a validation need that cannot be met by selected
modes or probes. Raster similarity is never a primary acceptance gate.

## 2. Claim policy

Every accepted result is certified for one named observable and an explicit
parameter domain. The certificate schema is
`schwgw_phase6_observable_validity_v1` and must contain separate:

- numerical uncertainty: `lmax`, `r_in`, `r_out`, Jost order, ODE tolerance,
  arithmetic precision, axis limit and backend difference;
- convention/observable spread: observer, tetrad, polarization basis, phase
  origin and total-versus-scattered definition.

The code rejects a certificate whose observable is `global`, `project` or
`SchWO`. A GREEN certificate requires durable evidence identities.

At finite radius the primary quantity is the observer-qualified electric
tidal tensor `E_ij`. The derived `h_plus/h_cross` is named
`monochromatic_equivalent_tidal_strain` and remains qualified by RW gauge,
worldline, tetrad and polarization basis until Gate V4 closes.

## 3. Gate ledger

### V0 — Claim/provenance cleanup

Current state: **PASS for the Phase-6 claim/provenance implementation slice.**

The current repaired verification root is
`runs/phase6/v1_v0_verification_v2_20260810_py314`.  Its four machine-readable
checks PASS; the formal full suite records `1533 passed / 120 skipped / 0
failed`.  The final post-release exact-runtime run records `1535 passed, 119
skipped, 1 xfailed, 104 subtests`.  This V0 PASS does not promote any V1--V5
physical observable.

Acceptance requirements:

- no active metadata describes the direct metric-curvature route as a full-NP
  pseudoinverse;
- injected/unknown solvers fail closed instead of inheriting a physical claim;
- active callers of old lower-NP completion and pseudoinverse code use the
  explicit `schwgw.scattering.legacy` diagnostic namespace (former public
  modules remain compatibility surfaces for historical evidence readers);
- legacy channels and adapters have `physical_claim=false`;
- finite-radius metadata records gauge, observer worldline/congruence, tetrad,
  polarization basis, phase origin, axis prescription, radial boundary data
  and backend;
- Fig.4 is described as converged in `lmax` by approximately 160 for the
  selected probes, with independent high-ell backend validation still open.

### V1 — Radial S-matrix and flux conservation

Current state: **PARTIAL by explicit domain; implementation failures repaired.**

The generic turning-aware baseline passes all `17,818/17,818` frozen `D_union`
keys, and production exact-eight radial states cover `16,048/16,048` modes.
Independent direct RW/Zerilli versus SchWO passes on the selected 30-key
domain, while independent 60/80-dps ladders pass on a selected 24-key domain.
These selected independent domains do not constitute full-domain arithmetic,
backend, boundary-ladder, or convention closure, so the full-domain release
certificate remains PARTIAL rather than GREEN.

Required domain:

```text
kM = 0.01, 0.05, 0.1, 0.5, 1, 2, 4, 8
ell = 2 ... actual production lmax
sectors = odd, even
```

The sampling must be dense near `ell ~= k r_eval` and across every
Q018/turning/evanescent transition used by the completed Fig.5/6 production.
Each accepted mode must carry

```text
|R|^2 + |T_H|^2 - 1
Wronskian and flux residuals
r_in_eps ladder
r_out ladder
Jost-order ladder
ODE tolerance ladder
double/arbitrary-precision difference
BHPT MST difference
BHPT direct-integration difference
```

Odd and even sectors require algorithmically independent evidence. An even
value obtained only from the parity relation is not an independent even
radial solve.

### V1Q — Generic conditioning backend

Current state: **PARTIAL over exact `D_union` and `D_prod`; independent
full-domain backend comparison remains open.**

The target architecture is:

```text
generic scaled radial backend
  + conditioning/error estimator
  + backend-selection policy
external experiment configuration
```

The core selector must not contain Table-I positions, Li frequencies, paper
figure names or review-grid labels. Existing paper-specific Q018 envelopes
remain frozen legacy evidence until the generic backend validates every
Q018 mode used by the completed Fig.5/6 transactions. `precision_dps` must
mean actual arithmetic precision or be renamed to
`requested_precision_dps` with an explicit backend precision record.

### V2 — Gauge-invariant asymptotic waveform and fluxes

Current state: **PARTIAL on the frozen selected witness domain.**  The
Martel--Poisson bridge and flux primitives are implemented, but the large-r
metric/Psi4 and external absolute-amplitude three-way closure remains open.

Implement Martel–Poisson normalization for the Zerilli–Moncrief even master
function and Cunningham–Price–Moncrief odd master function. Compare:

```text
A. gauge-invariant masters -> asymptotic h_plus/h_cross
B. metric/curvature -> Psi4 -> asymptotic h_plus/h_cross
C. external BHPT amplitudes -> asymptotic h_plus/h_cross
```

Required observables are waveform, energy flux at infinity, horizon flux and
their consistency with the radial S-matrix flux balance.

### V3 — Analytic and classical scattering benchmarks

Current state: **PARTIAL on the frozen selected benchmark domain.**

Acceptance suite:

- low-frequency spin-2 differential cross section;
- absorption tending to zero as `M omega -> 0`;
- high-frequency absorption tending to `27 pi M^2`;
- helicity-preserving/reversing amplitudes and parity relation;
- backward-glory peak position, width and frequency scaling;
- series-reduction-order and `lmax` convergence.

### V4 — Operational finite-radius response

Current state: **PARTIAL; existing finite-radius results remain
observer-qualified tidal responses.**

At minimum implement static Schwarzschild and radial free-fall worldlines,
Fermi–Walker transported tetrads, `E_ij` (and where needed `B_ij`), and a
detector-arm/geodesic-deviation response. A nontrivial pure-gauge perturbation
must leave the detector response invariant when metric, worldline and tetrad
are transformed consistently.

### V5 — Complex polarization transfer matrix and absolute phase

Current state: **PARTIAL on one frozen selected transfer domain.**

Two independent incident basis vectors must produce the full complex matrix

```text
[h_plus, h_cross]^T_out = F [A_plus, A_cross]^T_in.
```

Validate basis-rotation covariance and record singular values, `tr(F^dag F)`,
helicity mixing and matrix elements. Freeze the tortoise additive constant,
time/retarded-time origin, incident baseline and long-range phase subtraction
before interpreting any absolute phase residual.

### V6 — Release and uncertainty policy

Current state: **PASS for release-policy enforcement.**  The repaired release
contains only per-domain certificates, separate numerical/convention budgets,
`global_status=null`, no Li-primary gate, and no full-paper-figure rerun.

Release artifacts contain only per-observable/per-domain certificates. A
paper comparison may be linked as secondary evidence but cannot promote a
certificate.

## 4. Selected-domain populated V1 evidence (2026-08-08)

A bounded CPython 3.14 measurement run has now populated the V2--V5 evidence
schema without recomputing any paper figure.  This is selected-domain evidence,
not production-domain acceptance: all five certificates are `PARTIAL`, with
zero `PASS`, zero `FAIL`, and no project-wide state.

The immutable raw root is
`data/processed/phase6/v1_observable_measurements_selected_v1_20260808_py314/`.
Its `selected_measurements.json` SHA-256 is
`2c5ab799b821e2fb9abfd5c35a39ab3ceeb12aac9cb1bcea9f4d11cd1364d13c`;
the canonical submission SHA-256 is
`ee8e76413914d0af465b00b86c954c5a342a672f5f7de9d312de1474cbfd7146`.
The formal immutable bundle is
`runs/phase6/v1_observable_evidence_selected_v1_20260808_py314/`, with
`observable_evidence.json` SHA-256
`291745e684bd5354f4c42949126061117036efc3a3464c894c0d82275c312dad`.
It is bound to the authoritative zero-science observable contract v2 SHA-256
`3853df8fbc245b81552198d99201778e4020d82f618e3f80ac745768fc3d104b`.
Both roots are mode `0555`; their files are mode `0444` and were written with
no-overwrite semantics.

The bounded measurements are:

- V2: the explicit Li-to-Martel--Poisson bridge is exercised for
  `(kM,ell,m)=(0.5,2,2)`.  The finite-radius metric/master roundtrip maximum
  relative residual is `2.23e-15`, and the selected radial flux residual is
  `1.26e-9`.  The finite-radius total field is used only for the invariant
  roundtrip, never as an infinity waveform.  Large-radius metric/Psi4 and
  external BHPT absolute-amplitude routes remain `NOT_ASSESSED`.
- V3: 66 independently integrated odd/even conditioned-radial modes cover
  `kM=0.1,2,4` with selected finite `lmax`.  The low-frequency differential
  relative difference is about `4.29e2`, the exact-parity residual is about
  `2.05`, and the `q=0,1,2` comparison is unconverged (`q0/q2` about
  `7.63e14`, `q1/q2` about `4.87`).  Although the selected `kM=2` absorption
  differs from `27 pi M^2` by about `9.73e-3`, this does not override the open
  low-frequency, parity, glory, tail, precision, or backend checks.
- V4: the nontrivial radial pure-gauge oracle gives a maximum operational
  residual `4.07e-20` for static and E=1 radial-freefall observers.  Exact
  Schwarzschild connection checks give a maximum frame-transport residual
  `1.73e-18`; the maximum tetrad Gram residual is `2.22e-16`.  This covers one
  frozen gauge family and two point-observer frames only; finite-arm worldline
  integration and a general transported detector remain open.
- V5: a full complex `2x2` scattered-field transfer matrix is built from two
  independent unit polarization columns.  The selected basis-rotation
  covariance residual is `8.27e-25`, and the direct column/matrix residual is
  zero at stored float64 precision.  The absolute-phase ledger SHA-256 is
  `4ed45d8409ccad858c8141f2b363d0509c6e1be5b197ab136069d66dfb4b4902`.
  This is one selected asymptotic scattering angle; production unit-column
  solves and an independent transfer backend were not performed.

Each certificate carries separate eight-component numerical and six-component
convention budgets.  A measured component remains `PARTIAL` because no
a-priori threshold or independent backend is bound; unevaluated components
remain `NOT_ASSESSED`.  Li-figure agreement is absent from the acceptance
logic.

## 5. Repaired V1/V1Q release (2026-08-10)

The current release chain is rooted at
`configs/phase6_v1_repaired_release_map_20260810.json`,
`runs/phase6/v1_release_preparation_repaired_v2_20260810_py314`, and
`runs/phase6/v1_release_repaired_v2_20260810_py314`.  It contains 14
certificates: `PASS=2`, `PARTIAL=12`, `FAIL=0`, `NOT_ASSESSED=0`, with no
global status.  The only PASS certificates are V0 implementation verification
and V6 policy.

The full generic radial root is
`runs/phase6/radial_validation/v1_final_radial_baseline_v2_20260810_py314`:
`17,818/17,818` native algorithmic PASS and zero FAIL.  Its V1 and V1Q release
projections are each `PARTIAL 17818/17818`.  Production exact-eight state
coverage is `PARTIAL 16048/16048`.  The selected 30-key native direct
comparison is a scoped numerical PASS, but its release certificate stays
PARTIAL because the strict release layer does not invent separate evidence
roles from one composite source.  Exact identities and remaining budgets are
documented in `docs/phase6_v1_radial_repair_v2_20260810.md`.

## 6. Execution order and cost boundary

1. preserve the repaired V1/V1Q chain and do not rerun full paper figures;
2. extend arbitrary-precision and external comparison from selected witnesses
   toward explicit full-domain subsets only where the uncertainty budget needs
   it;
3. close V2 large-r metric/Psi4/external-amplitude agreement;
4. close the unresolved V3 low-frequency, parity, series and glory benchmarks;
5. extend V4 to a general worldline/tetrad-consistent detector response;
6. validate production unit columns and an independent V5 transfer backend;
7. issue new certificates only in fresh roots and only for the measured domain.

No existing Fig.5/6 transaction, merged dataset or render is overwritten.
Failed validation attempts use fresh roots and remain distinguishable from
accepted evidence.
