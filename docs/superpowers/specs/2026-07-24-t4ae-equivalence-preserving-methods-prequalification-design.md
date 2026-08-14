# T4ae Equivalence-Preserving Methods Prequalification Design

Date: 2026-07-24

Status: T0 bounded-repair candidate. This document freezes only a
pre-result methods/error-budget contract after an exact five-file local
commit and an independent package-review GREEN on that identity. It does not
freeze a new scientific frequency package, authorize a new frequency, or
claim a new scattering theory.

## 1. Trigger And Stop Boundary

T7cf returned exactly:

```text
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL REFINEMENT REQUIRED
```

The T8as artifact/provenance gate passed. Independent T7cf and T0
reconstructions agree on:

- exactly 55 ordered NPZ/JSON pairs, 115 active files, and 114 non-self
  manifest records;
- exactly 2,352 phase records, 1,760 literal-parent hierarchy records,
  80 summaries, and 1,085 strict extrema;
- 4 strict phase failures, maximum phase step
  `2.9549498637676037`;
- 719 hierarchy failures, split `372` plus and `347` cross, maximum raw
  excess `0.272823912893758`;
- exactly 87 unique failed-child intervals. The four phase-failed intervals
  are a subset, with zero extra phase-only interval.

The exact 87 diagnostic midpoints are not authorized run inputs. No T4 radial
gate, T8 frequency generation, T7 scientific review, automatic/recursive
selection, or new scientific package may start under this contract.

The only objective here is to establish, before any later numerical-design
freeze, that a proposed implementation architecture is scientifically
equivalent to the accepted legacy path and materially faster on predeclared
existing evidence.

## 2. Immutable Starting Identity

```text
legacy implementation commit   8fb8608c187280dc39fd56a78b976e6cf75a6ada
legacy implementation parent   6b613b475054cecd8ff420c7eb7e1781375c0412
frozen repair candidate         9a12fef8e09a46b4ed738723f4127896e64bf4c1
candidate parent                366a517c71b56026bb0f3ca37c14cc75243985b2
T8as generation contract        ccaf4f6aca14045c13f72bcdd1f61fd0c6928642bf7b0306211f68adadb5705d
T8as metadata contract          0f07ff5e105e0a2fe8d9245ef88ceb13e97dd1cea78342fbab2e4f89ed21e05c
T8as ledger                     4b8efee67914958086bccd504526a30793ba5f64f67e79b34e87d10f8bbfa516
T8as aggregate NPZ              1d78eed93ecc7ec13668ff5c769ea679f892ab2fed4e1c6f76ff470731385052
T8as aggregate sidecar          cb009a35b7b1ec76f7598fa70aeaa6c40ce66138cbaa4dea60f8a79a469640ab
T8as sampling audit             edec751d29291a86caf38b75352b265475654d5c8aa592051457ba8b8ab41d18
T8as manifest                   7470396704e913907afed6411bb43a4e433a2a294b48cc8385dffce75ce8dfd3
T7cf handoff                    ef05071fc62ca333e2cfefa89a35a9ef41958c095f616ce458565d053592f1c0
pre-T7cf T7 archive             4b801e46d7f23f0c224ab87912b85fcac0f72de721e15a9d544818b7bd990d1c
```

The seven files at candidate commit `9a12fef8...`, both older seven-file
candidates, T4ad roots/snapshots, all T8as source/gate hashes, and the exact
five-path `8fb8608...` implementation remain immutable historical evidence.
The methods work may create a new implementation identity but must never
rewrite or reinterpret those objects.

## 3. Unchanged Scientific Contract

The methods gate changes no physics or acceptance criterion:

- `G=c=M=1`, metric signature `(-,+,+,+)`;
- Fourier convention `exp(-i k t)`;
- Schwarzschild tortoise coordinate and radial ingoing/outgoing phase
  conventions;
- odd/even sectors, current RW/Zerilli master-variable normalization,
  incident `+z` state, angular conventions, tetrad, reconstruction, and
  observable packaging;
- `r_in_eps=1e-6`, `r_out=300`, `rtol=1e-10`, `atol=1e-12`;
- final adjacent-lmax criterion exactly `<=1e-4`;
- phase criterion strictly `<pi/2`;
- hierarchy criterion exactly
  `child_step <= immutable_failed_child_parent_step + 2e-15`;
- all frequencies, modes, points, independent validation, units, dtypes, and
  ordering required by a later frozen scientific package.

The equivalence tolerances below are an implementation-comparison error
budget. They do not replace or relax any scientific threshold.

## 4. Predeclared Legacy/New Benchmark Matrix

The cold legacy baseline must be generated before any code edit from exact
commit `8fb8608...`, with a clean implementation scope and full source/config
hashes. The optimized run must use the same machine, interpreter, NumPy/SciPy
versions, BLAS-thread settings, physical inputs, ordering, and output
contract.

The exact existing T8as frequency cases are:

| `kM` | role | immutable legacy NPZ SHA-256 |
|---:|---|---|
| `0.86875` | low-frequency / max-lmax 84 | `58768a1c4be7b351dd5c44351b98ecd61b80b96f74ebebd5f4f3d156d2ad42c5` |
| `1.58125` | transition / max-lmax 144 | `4edbfcd8d6024876f6efdebd29e47736d36f1385ed29a8ad3ff6adf0e6704b9e` |
| `2.91875` | mid-high / max-lmax 264 | `d6b81923284142dfe5faf13e8932b4e5c12aed1cd253c459ab10641ab0949b8b` |
| `3.759375` | phase-failure neighborhood / max-lmax 348 | `22a82e643a9b348b82999f2f065f25e9e47b017582da964d1b33d2ec3473b386` |
| `3.89375` | high-frequency / max-lmax 360 | `770340a9dcfbd17abb5de160f6289de473c184c1de75297fb45a8e23626b35d3` |

The downstream image regression is the full accepted `241x241` complex
field artifact:

```text
runs/phase5/fig3_four_frequency_dx0p25_production/
  t8ah_li_fig3_xz_k1p0_dx0p25.npz
SHA-256 0de560ce7a2696074e708506240c69e43eb4d40520447ec378208b37f64c0132
```

It is a read-only golden artifact. The methods gate may reproduce its exact
configuration in an isolated benchmark directory, but may not overwrite it,
create a publication plot, or promote a new production artifact.

## 5. Predeclared Equivalence Error Budget

All comparisons are direct, array-level, and performed before any rendering.

### 5.1 Exact equality

The following must be exact:

- array names, shapes, dtypes, units, axes, masks, point/frequency/lmax order,
  history/final-row relation, convention metadata, and finite/nonfinite
  pattern;
- mode/channel ordering and deterministic parallel reduction ordering;
- cache identity payload and rejection reason;
- checkpoint/transaction membership and canonical manifest ordering.

### 5.2 Floating comparison

For legacy versus optimized radial and observable complex arrays:

```text
absolute difference <= 5e-12
normalized relative difference <= 5e-10
```

For magnitudes above `1e-10`, principal phase difference after the frozen
phase convention must be `<=5e-9 rad`. Below that guard the complex-value
comparison remains mandatory; phase is not used to hide near-zero values.
Magnitude absolute/relative differences use the same `5e-12/5e-10` budget.

Final-pair deltas must individually remain `<=1e-4`, and the legacy/new delta
difference must be `<=1e-10`. Boundary/Wronskian/effective residuals must
still satisfy their existing hard gates and may not worsen beyond
`max(legacy*1.05, legacy+5e-13)`.

For the full image regression:

```text
valid_mask and coordinates       exact
h_plus/h_cross complex arrays    abs<=5e-12 and normalized rel<=5e-10
real/imag/abs pixel NRMSE         <=1e-11
normalized pixel L-infinity      <=5e-10
guarded phase difference         <=5e-9 rad
```

No resampling, smoothing, colormap, clipping, lower resolution, or
image-only normalization is permitted.

## 6. Required Performance Evidence

Each legacy and optimized benchmark record must include:

- wall time, user CPU, system CPU, and peak RSS;
- ODE/oracle solve count, cache hit/miss/rejection count, and stage timings;
- Python, NumPy, SciPy, platform/CPU, BLAS library, and controlled thread
  environment;
- exact implementation commit/blobs, physics hash, solver hash, config hash,
  source/gate hashes, cache identity, and artifact hashes.

Methods GREEN requires all equivalence gates plus:

```text
total ODE/oracle solve count <= 0.70 * legacy
aggregate wall time          <= 0.85 * legacy
aggregate CPU time           <= 0.85 * legacy
each case wall time          <= 1.05 * legacy
peak RSS                     <= 1.25 * legacy
```

If platform noise makes any timing condition fail, the result is YELLOW, not
an invitation to lower scientific work. Raw timing records must be retained.

## 7. Allowed Optimization Architecture

T4ae must profile before changing code. Within the exact scope, it may:

1. Reuse one ordinary radial solve across all certified evaluation radii and
   lmax/observable consumers through dense/vectorized evaluation.
2. Consume independently generated T4ad oracle values as an immutable,
   content-addressed read-only cache only after exact full-identity
   validation. A radius-specific oracle record remains a distinct certified
   state; records from different radii may not be conflated.
3. Use a fixed-size executor with at most two workers. Results must be
   stably sorted by the frozen scientific key, and BLAS/OpenMP threads must be
   fixed to one inside workers.
4. Use atomic checkpoint/transaction writes and exact-identity resume.
   A complete matching work unit is reused; a partial or mismatched unit is
   rejected/quarantined. No complete matching work unit is recomputed.
5. Reuse accepted baseline/intermediate evidence only as a read-only oracle
   with recorded provenance. No result may cross an implementation,
   physics, solver, config, source, or gate identity boundary.

No tolerance, lmax, frequency, mode, point, physical model, or independent
check may be removed to obtain speed.

## 8. Generic Interface Boundary

The methods implementation must add typed contracts that separate:

- background geometry and potential provider;
- field spin, polarization, parity, and channel specification;
- scalar or coupled radial system;
- horizon/outer boundary and asymptotic basis;
- source/incident waveform;
- angular basis and mode coupling;
- frequency-domain and future time-domain driver;
- solver backend;
- observable/projector;
- artifact writer.

Typed convention metadata must explicitly carry units, metric signature,
Fourier sign, tortoise-coordinate definition, ingoing/outgoing
normalization, phase convention, and provenance hashes.

The current Schwarzschild legacy scalar-master/RWZ path is preserved as an
adapter and must reproduce existing behavior. Generic protocols must not
assume Schwarzschild separability, a one-component state, or uncoupled
channels, so later Regge-Wheeler/Zerilli, Teukolsky, or coupled-channel
backends can be added. This methods gate implements and validates no new
spin-2 theory and makes no gravitational-wave-scattering readiness claim.

## 9. Exact Implementation Scope

After an exact matching package-review GREEN, T4ae may make one clean
implementation commit changing exactly these paths:

```text
docs/architecture.md
docs/extension_interface.md
docs/numerics.md
docs/validation_plan.md
scripts/phase5_equivalence_preserving_methods_gate.py
src/schwgw/numerics/radial_cache.py
src/schwgw/scattering/contracts.py
src/schwgw/scattering/legacy_adapter.py
src/schwgw/scattering/partial_wave.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_scalar_adapter_equivalence.py
tests/regression/test_equivalence_preserving_methods_gate.py
tests/unit/test_radial_cache.py
tests/unit/test_scattering_contracts.py
```

Other allowed writes are only:

```text
runs/phase5/equivalence_preserving_methods_gate/**
docs/phase5_equivalence_preserving_methods_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-24_pre_t4ae_methods_gate.md
```

No existing frozen design/plan/prompt, accepted artifact, physics
specification, config, threshold, or historical handoff archive may change.

## 10. Layered Tests And Fault Injection

Required tests:

- legacy scalar/RWZ golden and direct equivalence;
- generic solver/backend protocol contracts, including a non-Schwarzschild
  mock that makes no physical claim;
- horizon/outer-asymptotic and normalization invariants;
- deterministic serial versus two-worker ordering;
- cache hit under exact identity and rejection after changing each identity
  component;
- truncated, corrupt, interrupted, and stale checkpoint fault injection;
- exact downstream artifact schema and full image-array regression;
- performance regression and stage-profile contract;
- current focused Q018 tests, exact-scope Ruff, and fresh full pytest.

T7ch must independently review scientific equivalence, provenance, benchmark
methods/results, tests, implementation scope, and non-claims before any later
scientific candidate is frozen.

## 11. Gated Sequence

Only existing tasks may be used:

```text
package review: T7 019f5ed1-b421-7ec2-9bac-8d134855a1ed
methods work:   T4 019f5fa6-1288-7c01-8a87-4c4370cf5517
```

```text
T0 freezes five-file prequalification package
-> T7cg exact package REVIEW GREEN
-> T0 fresh identity verification
-> T4ae with gpt-5.6-sol/ultra
-> T4ae exact methods GREEN
-> T7ch independent methods review with gpt-5.6-sol/high
-> T0 fresh verification
-> only then may T0 design and freeze a separate bounded scientific package
```

No T8 work and no new frequency are part of this sequence. Code design,
implementation, or modification requires `gpt-5.6-sol/ultra`. Only after
code, tests, exact implementation commit, source/config identity, benchmark
contract, and resume rules are frozen, and the remaining work is merely a
long benchmark run, may orchestration use `gpt-5.6-terra/medium`. Solver
tolerances never depend on agent reasoning.

## 12. Exact Decisions

T4ae:

```text
GREEN / EQUIVALENCE-PRESERVING METHODS GATE READY
YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE
RED / EQUIVALENCE-PRESERVING METHODS GATE INVALID
```

T7ch:

```text
ACCEPT GREEN / EQUIVALENCE-PRESERVING METHODS GATE ACCEPTED
ACCEPT YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE
REJECT RED / EQUIVALENCE-PRESERVING METHODS GATE INVALID
```

Any YELLOW/RED stops at T0. It does not authorize frequency refinement,
threshold changes, task creation/replacement, downstream work, or GitHub.
