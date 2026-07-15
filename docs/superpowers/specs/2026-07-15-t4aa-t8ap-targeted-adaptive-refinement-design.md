# T4aa–T8ap Targeted Adaptive Frequency Refinement Design

Date: 2026-07-15

Status: the user approved this written 13-frequency mixed-resolution design
and authorized execution. The bounded repair package must still obtain the
independent T0 subagent review required by `project.md` before dispatch.

## 1. Decision And Objective

The next Phase-5 slice is a bounded, point-only adaptive-frequency evidence
chain for the five previously selected Fig.5/Fig.6 Table-I intervals.

The new frequency set is exactly:

```text
kM_new = [
  0.35, 0.45,
  0.85, 0.95,
  1.55, 1.65, 1.725,
  2.775, 2.85, 2.95,
  3.775, 3.85, 3.95,
]
```

Ten values bisect all `0.1` subintervals for which T7bw found at least one
magnitude-dominance failure. Three values (`1.725`, `2.775`, and `3.775`)
bisect the already-failing `0.05` edge intervals. The result is a mixed local
spacing of `0.05` and targeted `0.025`; it is not a uniform production grid.

The chain is:

```text
T4aa 13-frequency radial/Q018 classification and exact adapter
  -> T7by independent radial-gate review
  -> T0 exact-GREEN-only dispatch decision
  -> T8ap 13-frequency point-only adaptive pilot
  -> T7bz independent scientific/artifact review
  -> T0 interpretation only
```

No downstream task starts unless the immediately preceding gate satisfies its
exact frozen decision, artifact, test, provenance, scope, and handoff contract.

## 2. Accepted Starting State

### 2.1 Artifact-contract decision

The previous repair chain closed with:

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT METADATA REPAIR GATE CLOSED
```

The accepted risk-pilot package has:

```text
generation_contract_hash = 92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9
metadata_contract_hash   = 1bd32a3e2988ef786c3777859f76f8d38a276cdacd12cdadba7f79e843ca0161
schema_version           = phase5_t8ao_delta0p1_risk_pilot_v2_units_ordering
```

Its five accepted root hashes are:

```text
8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e  checkpoint_ledger.json
69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7  risk_pilot_values.npz
b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566  risk_pilot_values.npz.json
7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b  risk_pilot_sampling_audit.json
27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78  manifest.md
```

Their exact active paths are:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/checkpoint_ledger.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz
runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_sampling_audit.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md
```

The active package, its 23-file cardinality, 22-record manifest, explicit
units/ordering, and all 219 non-metadata arrays are immutable inputs. The new
stage reads them by hash and never appends to, rewrites, migrates, or repairs
them.

### 2.2 Accepted endpoint sources

The accepted T8aj review-grid triplet remains immutable:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

The accepted T4z/T7bv radial-gate hashes remain provenance anchors:

```text
ee051831e1da7ebb250cab37d7da3a64d8a57298b445577f238d9cefae319d54  runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/classification_manifest.json
8f6d23da0894d0abfb42867bf911b9da95090ad5293bc76289daf4522e4067f9  runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/oracle_validation.json
59e99ade6993eab6d570f8a2ad18f0778595f7309fbb87fbf1edf32903b80968  runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/resume_preflight.json
```

These anchors establish history only. The T4z adapter is exact-frequency and
must not be interpolated or silently broadened to any of the 13 new values.

### 2.3 Scientific reason for refinement

The accepted scientific state is:

```text
YELLOW / TARGETED ADAPTIVE FREQUENCY REFINEMENT REQUIRED
```

Established facts:

- all 224 previous adjacent phase steps are finite and `< pi/2`;
- the largest previous phase step is `1.4363184904108022 rad`;
- magnitude dominance fails for exactly 38 point/component/interval records;
- the previous five sequences contain 51 strict interior magnitude extrema;
- the failures occupy exactly 13 distinct parent intervals: ten of width
  `0.1` and three of width `0.05`.

This stage measures those 13 parent intervals at the next local level. It does
not alter the frozen criterion or claim a band-limit theorem.

## 3. Alternatives Considered

### 3.1 Selected: one 13-frequency mixed-resolution batch

Compute all ten missing `0.05` midpoints and all three already-required
`0.025` edge midpoints behind one new radial gate.

Advantages:

- covers every known failed parent interval in one gate chain;
- avoids a guaranteed second T4/T7/T8/T7 cycle after a ten-frequency-only run;
- batches the expensive radial classification and direct-oracle validation;
- preserves a hard bound of 13 frequencies and eight points;
- leaves any newly discovered finer-scale failure as an explicit YELLOW
  rather than triggering unbounded recursion.

Cost: the radial gate may be longer than T4z and the high-frequency pilot
contains several hours-scale frequencies.

### 3.2 Rejected: ten `0.05` midpoints only

This would leave `[1.7,1.75]`, `[2.75,2.8]`, and `[3.75,3.8]` unresolved even
if every new `0.05` midpoint passed. It therefore guarantees another major
radial and artifact chain before T0 could interpret all known failures.

### 3.3 Rejected: uniform `0.025` coverage of all five intervals

Uniform `0.025` coverage would require 34 new frequencies rather than 13. It
would broaden the radial envelope and runtime before the targeted hierarchy
shows that such coverage is necessary. That is a production-scale decision,
not a bounded evidence slice.

### 3.4 Rejected: automatic recursive bisection

An open-ended adaptive loop would allow the code to invent frequencies and
continue after a scientific YELLOW without T0/user review. This conflicts with
the project's exact-scope, fail-closed gate model. The present chain has one
level only; any failed child interval returns to T0.

## 4. Frozen Physical And Numerical Inputs

The stage preserves:

- Schwarzschild `M=1`, internal `G=c=1`;
- Fourier factor `exp(-ikt)`;
- incident direction `+z`;
- `A_plus=0.9+1.1j`, `A_cross=0.4+0.6j`;
- Route-B packaged polarization bridge;
- `F_plus=h_plus_lensed/h_plus_unlensed` and
  `F_cross=h_cross_lensed/h_cross_unlensed`;
- flat/no-lens packaged polarization denominators;
- `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`;
- complex final-pair convergence tolerance `1e-4`;
- the eight exact Table-I points at `z/M=30` and
  `x/M=[0,1,2,3,10,15,20,25]`;
- separate plus/cross masks and no invalid-value fill;
- no interpolation, smoothing, clipping, inference, Kirchhoff normalization,
  or mask alteration.

Frequencies are identified by the canonical decimal tokens shown in Section
1 and corresponding binary64 values. Radial-envelope membership uses the
existing strict comparison convention `rtol=0`, `atol=1e-15`; no nearest-
frequency selection is allowed.

## 5. Exact Frequency And lmax Contract

The unchanged seed rule is:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
lmax_values = sorted unique [L_seed-72, L_seed-48, L_seed-24, L_seed]
lmax >= 24
```

The exact initial windows are:

| `kM` | canonical token | `lmax_values` | final pair |
|---:|---|---|---|
| 0.35 | `0p35` | `[24,36,60,84]` | `[60,84]` |
| 0.45 | `0p45` | `[24,36,60,84]` | `[60,84]` |
| 0.85 | `0p85` | `[24,36,60,84]` | `[60,84]` |
| 0.95 | `0p95` | `[24,48,72,96]` | `[72,96]` |
| 1.55 | `1p55` | `[72,96,120,144]` | `[120,144]` |
| 1.65 | `1p65` | `[84,108,132,156]` | `[132,156]` |
| 1.725 | `1p725` | `[84,108,132,156]` | `[132,156]` |
| 2.775 | `2p775` | `[180,204,228,252]` | `[228,252]` |
| 2.85 | `2p85` | `[192,216,240,264]` | `[240,264]` |
| 2.95 | `2p95` | `[204,228,252,276]` | `[252,276]` |
| 3.775 | `3p775` | `[276,300,324,348]` | `[324,348]` |
| 3.85 | `3p85` | `[276,300,324,348]` | `[324,348]` |
| 3.95 | `3p95` | `[288,312,336,360]` | `[336,360]` |

No convergence extension is authorized in this slice. T4aa measures only the
initial windows above, so an added `+24` or `+48` mode would not have a frozen
T7by-accepted radial envelope. If the initial final pair fails `1e-4`, T8ap
stops YELLOW and returns to T0 without aggregation or adapter broadening.

## 6. Exact Reconstructed Sequences And Parent Mapping

T7bz reconstructs these sequences directly from three immutable sources:
T8aj endpoints, the accepted T8ao/T7bx nine-frequency package, and the new
T8ap 13-frequency package.

```text
[0.3, 0.35, 0.4, 0.45, 0.5]
[0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
[1.5, 1.55, 1.6, 1.65, 1.7, 1.725, 1.75]
[2.75, 2.775, 2.8, 2.85, 2.9, 2.95, 3.0]
[3.75, 3.775, 3.8, 3.85, 3.9, 3.95, 4.0]
```

There are 27 adjacent intervals and therefore exactly:

```text
27 intervals * 8 points * 2 components = 432 phase-step records
```

Thirteen failed parent intervals are bisected. Each produces two children, so
the hierarchical magnitude review contains exactly:

```text
26 child intervals * 8 points * 2 components = 416 child-dominance records
```

Each `0.05` child is compared only with its exact accepted `0.1` parent. Each
`0.025` child is compared only with its exact accepted `0.05` parent. The
already-passing unrefined interval `[0.75,0.8]` remains phase/sequence context
but is not counted as a new child-dominance record.

The parent mapping is frozen explicitly; no task infers it from floating-point
neighbours:

| midpoint | exact parent | child 1 | child 2 | parent width |
|---:|---|---|---|---:|
| `0.35` | `[0.3,0.4]` | `[0.3,0.35]` | `[0.35,0.4]` | `0.1` |
| `0.45` | `[0.4,0.5]` | `[0.4,0.45]` | `[0.45,0.5]` | `0.1` |
| `0.85` | `[0.8,0.9]` | `[0.8,0.85]` | `[0.85,0.9]` | `0.1` |
| `0.95` | `[0.9,1.0]` | `[0.9,0.95]` | `[0.95,1.0]` | `0.1` |
| `1.55` | `[1.5,1.6]` | `[1.5,1.55]` | `[1.55,1.6]` | `0.1` |
| `1.65` | `[1.6,1.7]` | `[1.6,1.65]` | `[1.65,1.7]` | `0.1` |
| `1.725` | `[1.7,1.75]` | `[1.7,1.725]` | `[1.725,1.75]` | `0.05` |
| `2.775` | `[2.75,2.8]` | `[2.75,2.775]` | `[2.775,2.8]` | `0.05` |
| `2.85` | `[2.8,2.9]` | `[2.8,2.85]` | `[2.85,2.9]` | `0.1` |
| `2.95` | `[2.9,3.0]` | `[2.9,2.95]` | `[2.95,3.0]` | `0.1` |
| `3.775` | `[3.75,3.8]` | `[3.75,3.775]` | `[3.775,3.8]` | `0.05` |
| `3.85` | `[3.8,3.9]` | `[3.8,3.85]` | `[3.85,3.9]` | `0.1` |
| `3.95` | `[3.9,4.0]` | `[3.9,3.95]` | `[3.95,4.0]` | `0.1` |

## 7. Stage 1 — T4aa Radial/Q018 Gate

### 7.1 Objective

Classify every requested odd/even mode for all 13 frequencies, eight exact
Table-I radii, and frozen lmax windows. Records distinguish:

- default covered;
- structured fail-closed uncovered;
- structured solver failure eligible for the experimental oracle;
- unstructured, nonfinite, or out-of-contract failure.

Every recoverable transition key `(kM, sector, ell, point_id)` is independently validated with the
existing direct Riccati/log-amplitude oracle. Required evidence includes
residuals, normalization, boundary consistency, conditioning, and tolerance
sensitivity. Requested precision and actual backend precision are recorded
separately.

The precision/tolerance anchor set is deterministic. For every nonempty
`(kM, sector)` transition group, select the lexicographically first and last
`(ell, point_id)` keys, then add the lexicographically first transition for
each of the eight point IDs not already represented. Run the deduplicated
union at requested `70/80/100` dps and the frozen loose/tight tolerance
perturbations. A frequency or sector with no transition records must explicitly
record `transition_count=0` and an empty anchor list; no oracle anchor is
invented and no odd/even symmetry is assumed.

### 7.2 Exact adapter

Only if the complete measured gate passes may T4aa add:

```text
q018_tablei_targeted_adaptive_transition
```

The adapter permits only:

- Schwarzschild `M=1`;
- the 13 exact frequencies and eight exact point radii;
- odd/even sectors;
- literal measured `(kM, sector, ell, point_id)` transition membership;
- the frozen boundary values and tolerances in Section 4.

Default-covered modes remain on the ordinary solver path. Any wrong frequency,
point, radius, ell, sector, `M`, `r_out`, `r_in_eps`, `rtol`, or `atol` fails
closed with structured metadata. There is no interpolation in frequency,
radius, ell, or transition segments.

The literal envelope is sector-aware. Its transition map is keyed by exact
`(kM, sector)` and stores only consecutive ell segments with exact point-ID
sets; a sector may not reuse another sector's membership.

### 7.3 Artifacts and checkpoints

Write only under:

```text
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/
```

Required records:

```text
classification_manifest.json
oracle_validation.json
resume_preflight.json
checkpoint/kM_<token>.json   # exactly 13 atomic checkpoints
manifest.md
```

Each checkpoint is written to a temporary sibling and atomically renamed. A
resume skips work only when the complete input contract, selected code hashes,
checkpoint decision, and output hash agree. Mismatched state is quarantined.

T4aa has two distinct provenance layers:

1. The **classification snapshot** binds the final gate script, the exact
   pre-adapter `radial_solver.py` blob used for default classification, the
   direct-oracle blob, Table-I source blob, design/plan/prompt blobs, and input
   contract. The thirteen checkpoints and raw classification/oracle artifacts
   bind only this snapshot and remain resumable after adapter integration.
2. The **final adapter snapshot** binds the generated literal envelope, final
   `radial_solver.py`, the complete five-path implementation commit, and all
   implementation/test blobs. `resume_preflight.json` and `manifest.md` bind
   both snapshots and the exact classification/oracle hashes.

A final-adapter blob must never be substituted for a classification-snapshot
blob when deciding checkpoint reuse. T7by independently verifies both
identities and their hash-bound bridge.

### 7.4 Implementation boundary and decisions

The T4aa implementation commit may change exactly:

```text
scripts/phase5_targeted_adaptive_radial_gate.py
src/schwgw/numerics/q018_targeted_adaptive_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

T4aa may additionally update only its run directory, `status.md`, T4 handoff,
and one T4 archive. The implementation plan may narrow this scope but may not
add another implementation/test path without returning to T0 and the user.

Exact decisions:

```text
GREEN / TARGETED ADAPTIVE RADIAL GATE READY
YELLOW / TARGETED ADAPTIVE RADIAL GATE PARTIAL
RED / TARGETED ADAPTIVE RADIAL GATE BLOCKED
```

Only exact GREEN may dispatch T7by.

## 8. Stage 2 — T7by Independent Radial Review

T7by is review-only and independently checks:

1. exact frequency, point, lmax, mode, boundary, and tolerance scope;
2. complete cardinality with no omissions or duplicates;
3. fresh classification samples across all frequencies/sectors/points and all
   structured classes;
4. every transition key and saved maximum against direct-oracle evidence;
5. exact generated-envelope expansion with no interpolation;
6. adapter direct-match behavior, default-path zero calls, and fail-closed
   rejection of every wrong contract field;
7. 13 atomic checkpoints, hashes, backend precision, provenance, and resume;
8. focused tests, Ruff, full pytest, and forbidden observable outputs;
9. no T8ap artifact or later-stage output exists yet.

Exact decisions:

```text
ACCEPT GREEN / TARGETED ADAPTIVE RADIAL GATE ACCEPTED
ACCEPT YELLOW / TARGETED ADAPTIVE RADIAL EVIDENCE INCOMPLETE
REJECT RED / TARGETED ADAPTIVE RADIAL GATE INVALID
```

T7by returns only to T0. Only T0 may dispatch T8ap after exact GREEN.

## 9. Stage 3 — T8ap Point-Only Adaptive Pilot

### 9.1 Computation and isolation

Compute exactly the 13 new frequencies at exactly the eight Table-I points.
Use the T7by-accepted adapter and envelope. The new implementation must live
in a focused adaptive-refinement IO/runner module; it may read the accepted
risk-pilot package but must not modify `tablei_risk_pilot.py` or any accepted
T8aj/T8ao/T4z artifact.

The T8ap implementation commit may change exactly:

```text
src/schwgw/io/tablei_adaptive_refinement.py
src/schwgw/io/__init__.py
scripts/phase5_run_targeted_adaptive_refinement.py
tests/unit/test_tablei_adaptive_refinement.py
tests/regression/test_targeted_adaptive_refinement_script.py
```

The implementation plan may narrow this scope but may not add another
implementation/test path without returning to T0 and the user.

Each frequency is an independent transaction:

1. validate all accepted source, gate, code, configuration, units, dtype, and
   ordering hashes;
2. compute all frozen lmax partial sums with no extension;
3. require finite plus/cross values and true masks at all eight points;
4. require the complex final adjacent pair to pass `1e-4`;
5. atomically write one NPZ and one JSON sidecar;
6. append one hash-only completion record to the atomic ledger;
7. start the next frequency only after the prior transaction validates.

On resume, a frequency is reused only when its NPZ, sidecar, contract, source
hashes, adapter identity, lmax window, and ledger record all match. Partial or
mismatched outputs are quarantined and never counted as active.

### 9.2 Artifact layout and cardinality

Write only under:

```text
runs/phase5/fig5_fig6_targeted_adaptive_refinement/
```

Required active layout:

```text
frequencies/kM_<token>.npz
frequencies/kM_<token>.npz.json
checkpoint_ledger.json
adaptive_refinement_values.npz
adaptive_refinement_values.npz.json
adaptive_sampling_audit.json
manifest.md
```

There are exactly 31 active files: 26 per-frequency files, four non-manifest
root files, and the manifest. The manifest has exactly 30 non-self records.
The aggregate contains only the 13 new frequencies with shape `(13,8)`; it is
not a disguised full grid.

### 9.3 Generation and metadata contracts

The new schema is exactly:

```text
phase5_t8ap_targeted_adaptive_refinement_v1_units_dtype_ordering
```

The generation contract binds:

- the 13 frequency tokens/values and exact lmax windows;
- the eight points and all Section-4 physical/numerical inputs;
- accepted T8aj and T8ao/T7bx source hashes;
- accepted T4aa/T7by gate hashes and adapter identity;
- selected scientific code hashes and Git state;
- convergence and fail-closed policies.

Before the first real frequency, T8ap must finish the five implementation/test
paths, pass fake-compute focused tests and Ruff, and create one scoped
implementation commit containing exactly those paths. The generation contract
binds that commit and its five blobs. If any implementation file changes after
real computation starts, the contract is invalid: all transactions from the
old contract are quarantined and none may be reused under the new commit.

The separate metadata contract binds:

- schema identifier and generation-contract hash;
- exact units, dtype, and ordering registries;
- all no-interpolation/non-production flags;
- source and gate hashes.

Units, dtype, ordering, generation/metadata hashes, and source provenance must
appear consistently in all 13 embedded metadata objects and sidecars, the
aggregate embedded metadata and sidecar, ledger, sampling audit, and manifest.
The artifact is invalid if a reviewer must infer any required unit, dtype, or
axis ordering.

### 9.4 Array contract

Per-frequency arrays use the accepted 22-array structure and dtypes:

- scalar/coordinate/magnitude/phase/delta arrays: `float64`;
- lmax values: `int64`;
- complex histories and final amplitudes: `complex128`;
- validity masks: `bool`;
- point identifiers/groups: exact NumPy Unicode dtypes `<U16` and `<U9`.

The aggregate uses the accepted 21-array structure with `(13,8)` field arrays,
`float64` frequency/coordinate/magnitude/phase/delta arrays, `complex128`
amplitudes, Boolean masks, and the same Unicode identifiers. Every metadata
dtype declaration must equal the actual loaded dtype exactly.

Units remain: `kM` dimensionless (`M k`), coordinates/radii in `M`, angles and
phases in radians, complex amplifications and deltas dimensionless, lmax
dimensionless integer, masks Boolean, runtimes seconds, and counters counts.

Ordering is exactly the Section-1 frequency order, the accepted eight-point
order, frequency-local lmax order, `[lmax,point]` history axes, `[point]`
per-frequency final axes, and `[frequency,point]` aggregate axes.

### 9.5 Sampling audit and decisions

The audit may combine values from the three immutable source packages only by
fresh hash-verified direct loading. It records all five Section-6 sequences,
432 phase records, 416 child-dominance records, parent mapping, local total
variation, largest-step attribution, and all strict interior extrema. It emits
no acceptance decision.

Exact T8ap decisions:

```text
GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE GENERATED
YELLOW / TARGETED ADAPTIVE FREQUENCY EVIDENCE PARTIAL
RED / TARGETED ADAPTIVE FREQUENCY EVIDENCE BLOCKED
```

GREEN means all 13 transactions and the artifact contract are complete and
valid. It does not prejudge the scientific magnitude result. Only exact GREEN
may dispatch T7bz.

## 10. Stage 4 — T7bz Independent Adaptive Review

T7bz must not call T8ap aggregation, metric, or acceptance helpers. It directly
loads the 13 per-frequency files and the two accepted source packages and
independently reconstructs all sequences and parent mappings.

### 10.1 Artifact and provenance gate

Before interpreting science, T7bz requires:

- exact 31/30 active/manifest cardinality and no active temporary file;
- all source, T4aa/T7by gate, transaction, ledger, aggregate, audit, and
  manifest hashes;
- exact generation/metadata contract reconstruction;
- units/dtype/ordering consistency and actual-array agreement;
- aggregate-to-transaction byte/value identity;
- finite values, true masks, final-pair convergence, warnings, cache and
  adapter accounting;
- checkpoint/resume/quarantine isolation;
- focused tests, Ruff, full pytest, and forbidden outputs.

An invalid artifact, scope drift, source mismatch, nonfinite accepted value,
test failure, or provenance ambiguity is RED and cannot be downgraded by good
sampling metrics.

### 10.2 Observed phase criterion

For every one of the 432 adjacent sequence records:

```text
phase = np.unwrap(np.angle(F), axis=frequency)
abs(diff(phase)) < pi/2
```

Every value must be finite. This is observed local sampling evidence, not a
global band-limit theorem.

### 10.3 Hierarchical magnitude criterion

For magnitudes `a=|F(k_i)|`, `b=|F(k_j)|`, use exactly:

```text
relative_step(a,b) = abs(a-b) / max(1, a, b)
```

For each of the 416 child records, require:

```text
child_relative_step <= exact_parent_relative_step + 2e-15
```

Parent values are loaded from the already accepted artifacts, not recomputed
from rounded report values. `0.05` children use their `0.1` parent; `0.025`
children use their `0.05` parent. No comparison may cross points, components,
or parent intervals.

T7bz also reports child total variation, parent endpoint step, cancellation
structure, largest child attribution, and all old/new strict extrema. No extra
numeric threshold is invented. Interior extrema do not disappear from the
record and GREEN is not called magnitude convergence; the hierarchical test
only determines whether the next local refinement level reveals a child jump
larger than its accepted parent.

### 10.4 Exact review decisions

```text
ACCEPT GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / FURTHER LOCAL FREQUENCY REFINEMENT REQUIRED
REJECT RED / TARGETED ADAPTIVE FREQUENCY ARTIFACT INVALID
```

GREEN requires the complete artifact/provenance gate, all 432 phase records,
and all 416 hierarchical magnitude records to pass. It permits only T0 to
design a later nonuniform production-grid completion; it does not start one or
claim global convergence.

YELLOW means the artifact is valid but one or more scientific child records
fail. It must name the exact parent/child interval, point, component, phase and
magnitude values, and the next candidate midpoint. It does not authorize that
midpoint.

RED means invalid computation, artifact, test, source, provenance, or scope.
T7bz never repairs T8ap or dispatches another task.

## 11. Existing Tasks And Automatic Coordination

Use only the existing Codex tasks:

```text
T4 = 019f5fa6-1288-7c01-8a87-4c4370cf5517
T7 = 019f5ed1-b421-7ec2-9bac-8d134855a1ed
T8 = 019f5ece-f578-7b91-8f61-df882c656591
```

Default dispatch model is `gpt-5.6-sol/high`.

- T0 dispatches frozen T4aa after the written design, plan, and prompts are
  approved and committed.
- T4aa exact GREEN may dispatch frozen T7by to the existing T7 task.
- T7by returns only to T0. Only T0 may dispatch T8ap after independently
  verifying T7by exact GREEN.
- T8ap exact GREEN may dispatch frozen T7bz to the existing T7 task.
- T7bz returns only to T0 and starts nothing.
- Missing/archived tasks or messaging failure stop the chain; no replacement
  task is silently created.

An exact final T7bz GREEN is a potential major-node trigger for T0's private
GitHub synchronization rule. A scientific YELLOW is recorded and returned to
the user without automatic continuation or milestone push unless another
independent major-node condition is separately established.

## 12. Runtime, Recovery, And Monitoring

The user permits long background execution. Runtime is a health-monitoring
signal, not a scientific threshold.

- T4aa may exceed the previous T4z runtime because it covers 13 frequencies;
  a `12 h` notification is soft and does not kill a healthy process.
- T8ap is expected to be hours-scale; a `6 h` notification is soft.
- Storage target for both gates and the active pilot is `<150 MB`.
- Both computational stages use per-frequency atomic checkpoints.
- A monitor checks process liveness, checkpoint growth, output hashes, tests,
  exact decisions, and dispatch state without restarting healthy work.

A clear model-capacity/system interruption may resume the same existing task
with `gpt-5.6-terra/high` only after process, checkpoint, artifact, contract,
test, and scope checks prove there is no scientific failure. Resume must reuse
safe state and avoid recomputation.

Scientific, numerical, nonfinite, contract, provenance, test, or scope failure
never qualifies for a model switch. It stops the chain and reports T0.

## 13. Authorized Change Boundaries

- T4aa: only the five exact gate implementation/test paths frozen by the
  implementation plan, its run directory, `status.md`, T4 handoff, and one T4
  archive.
- T7by/T7bz: review-only; only `status.md`, T7 handoff, and one exact archive
  per review.
- T8ap: only the new focused adaptive IO module/export, thin runner, two
  focused test modules, its run directory, `status.md`, T8 handoff, and one T8
  archive. It may consume but not modify the accepted radial adapter.
- T0: design/plan/prompts, T0 handoff/archive, status, monitoring, exact gated
  dispatch, and project-rule GitHub sync only after an independently accepted
  major node.

Every stage preserves unrelated T1/T2/T3/T5/T6 worktree changes. T4/T7/T8 do
not push GitHub.

## 14. Explicit Non-Goals

- No 40- or 79-frequency production grid.
- No uniform `0.025` scan.
- No automatically generated next midpoint.
- No frequency, radial-envelope, or artifact interpolation.
- No full x-z field grid.
- No plot, PDF, PNG, fixture, benchmark promotion, or paper-style rendering.
- No Kirchhoff regeneration, normalization, correction, or mask use.
- No physics convention, Route-B bridge, Q018 threshold, boundary value,
  convergence tolerance, lmax rule, or warning relaxation.
- No mutation of any accepted T8aj, T4z/T7bv, or T8ao/T7bx artifact.
- No automatic continuation after T7bz.

## 15. Failure Rules

- Missing or changed accepted source hash: stop RED; never regenerate source.
- A complete, valid gate package with structured unresolved or incomplete
  radial coverage is T4aa YELLOW.
- A default-other/unstructured error, nonfinite oracle value, residual or
  sensitivity failure, source/provenance mismatch, test failure, scope drift,
  or invalid checkpoint/artifact is T4aa RED.
- Incomplete or nonconverged T8ap frequency: preserve checkpoints, do not
  aggregate it, and stop YELLOW.
- Invalid units/dtype/ordering, hash, ledger, cardinality, aggregate identity,
  or active temporary state: RED.
- Valid artifact with failed phase or hierarchical magnitude criterion:
  scientific YELLOW.
- A review task never fixes the producer.

## 16. Definition Of Done

- T4aa produces a complete 13-frequency radial classification, validated exact
  adapter envelope, atomic checkpoints, fresh tests, and one exact decision.
- T7by independently accepts or rejects the radial gate.
- T8ap produces exactly 13 new point-only frequency transactions, a 31-file
  active package with explicit units/dtype/ordering contracts, and no mutation
  of accepted sources.
- T7bz independently reconstructs 432 phase and 416 hierarchical magnitude
  records and gives one exact artifact/scientific decision.
- T0 records and interprets the decision.
- No full grid, recursive refinement, plot, fixture, Kirchhoff, paper-style
  work, or later task starts automatically.
