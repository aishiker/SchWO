# T4ab–T8aq Further-Local Frequency Refinement Design

Date: 2026-07-16

Status: bounded T0 repair candidate for independent read-only review. It is
not executable until the same immutable seven-file package receives exactly
`REVIEW GREEN / T0 REPAIR PACKAGE APPROVED` under `project.md`.

## 1. Decision And Objective

T7bz accepted the T8ap artifact contract but returned:

```text
ACCEPT YELLOW / FURTHER LOCAL FREQUENCY REFINEMENT REQUIRED
```

The failure evidence is finite and localized:

- one of 432 observed phase steps fails strict `< pi/2`;
- 97 of 416 hierarchical magnitude records fail;
- those 97 failures occupy exactly 24 distinct child intervals;
- the phase failure interval `3.75 -> 3.775` is one of those 24 intervals.

The next repair is therefore one bounded mixed-resolution batch containing
exactly the 24 unique diagnostic midpoints of the failed child intervals:

```text
kM_new = [
  0.325, 0.375,
  0.825, 0.875, 0.925, 0.975,
  1.525, 1.575, 1.625, 1.675, 1.7125, 1.7375,
  2.7625, 2.7875, 2.825, 2.875, 2.925, 2.975,
  3.7625, 3.7875, 3.825, 3.875, 3.925, 3.975,
]
```

This is a targeted mixture of `0.025` and `0.0125` child spacing. It is not a
uniform `0.025` or `0.0125` scan and it is not an automatic recursive loop.

The gated chain is:

```text
T4ab 24-frequency radial/Q018 classification and exact adapter
  -> T7ca independent radial-gate review
  -> T0 exact-GREEN-only dispatch decision
  -> T8aq 24-frequency point-only further-local evidence
  -> T7cb independent scientific/artifact review
  -> T0 interpretation only
```

No downstream task starts unless the immediately preceding gate satisfies its
exact frozen decision, artifact, test, provenance, scope, and handoff
contract.

## 2. Accepted Starting State And Immutable Evidence

### 2.1 T8ap artifact validity

The accepted producer identity is:

```text
implementation commit = 575c275fcb4ab9263786e7e5ee7f3425f20b7ce6
generation contract    = 74cb3aafa63e12609d7f6b7f1efef10b539ebec1f1a91f2990356d9e56a51c94
metadata contract      = 5bf94f5bd0ac5ad8678fe9e561012c53ff4e9c1cff14bd401f3feadba6fd2865
schema                  = phase5_t8ap_targeted_adaptive_refinement_v1_units_dtype_ordering
```

Its active package is immutable at:

```text
runs/phase5/fig5_fig6_targeted_adaptive_refinement/
```

with exact root hashes:

```text
ec6328ad5b9acfdd341a00877a7aaf355d49a0d39db1569f3e488b34b9980f17  adaptive_refinement_values.npz
9d9c821ab8c7f5af1ceb5136451e859a41bccd5456fe3beee834b876ffdc38cc  adaptive_refinement_values.npz.json
4606960110b658b74894c1b82a604c333481290ca0c451f3013574906eea5d67  adaptive_sampling_audit.json
2dfcaa7802ed8c7e3b3225429bb8b312d651441f378719331d023a5adb1e1caf  checkpoint_ledger.json
b728b1f5b4d45e622d5bebc32e710ac2be786556ab1ee7b7d9f26ca545223e5c  manifest.md
```

The 31 active files, 30 manifest records, all 26 per-frequency hashes, units,
dtypes, ordering, masks, finite values, and no-extension state are accepted
inputs. The new chain reads them by exact path and hash and never modifies,
repairs, migrates, or substitutes them.

### 2.2 T7bz failure evidence

The exact T7bz handoff bytes used to derive this candidate are:

```text
8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e  docs/handoffs/T7_current.md
```

T4ab must verify that hash before computation. Before T7ca updates the current
T7 handoff, T7ca must archive those exact bytes at:

```text
docs/handoffs/archive/T7_2026-07-16_pre_t7ca_further_local_radial_review.md
```

and verify the same SHA-256. Later tasks use that archive as the immutable
T7bz evidence path. They must not rely on a subsequently overwritten
`docs/handoffs/T7_current.md`.

The unique midpoint set and failure multiplicities reconstructed from the 97
literal T7bz rows are:

| midpoint | failing rows selecting it |
|---:|---:|
| `0.325` | 2 |
| `0.375` | 1 |
| `0.825` | 2 |
| `0.875` | 3 |
| `0.925` | 2 |
| `0.975` | 4 |
| `1.525` | 2 |
| `1.575` | 4 |
| `1.625` | 1 |
| `1.675` | 3 |
| `1.7125` | 1 |
| `1.7375` | 2 |
| `2.7625` | 4 |
| `2.7875` | 4 |
| `2.825` | 4 |
| `2.875` | 8 |
| `2.925` | 4 |
| `2.975` | 6 |
| `3.7625` | 6 |
| `3.7875` | 7 |
| `3.825` | 6 |
| `3.875` | 7 |
| `3.925` | 7 |
| `3.975` | 7 |

The multiplicities sum to 97. They are provenance for selection only; no
weighting or new acceptance threshold is introduced.

### 2.3 Earlier accepted anchors

The accepted T8aj triplet remains immutable:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  runs/phase5/fig5_fig6_dense_review_grid/manifest.md
```

The accepted T8ao/T7bx roots remain immutable:

```text
8729ad80043a1837793264b101a776a08e92191c7856cf792ed34683b743859e  checkpoint_ledger.json
69cf9812ddd51d6486f854b77b76d202c281d719041cc07e8e87c1af9bd973f7  risk_pilot_values.npz
b812a4325b9afca91ee360b68dc3e959115f2d992fba21b60cf70a7ad3ce3566  risk_pilot_values.npz.json
7e1e8646bfa51b09cd96ee301e8847fdc830128d7eca7ac770031bc7b13ce42b  risk_pilot_sampling_audit.json
27301b9f300563a5feb654b48d9ef11ca8eb1e10f9c065c805534adfb27bfd78  manifest.md
```

The accepted T4aa/T7by gate roots and snapshots remain immutable:

```text
aa3af55cd8454d610ebcd31fd8bbda5d37522a9a4e2279c8622decf3459a1b83  classification_manifest.json
002889f81ebce0574b948912217bf1231add3411253855db71adf2769b441d02  oracle_validation.json
a39bacfea6f2728129fde71b791c6f4f18eba05b34e9fa7dcf49b8b64d9824d4  resume_preflight.json
a796e4c34af8a80f800ec1f9ebc04089e4b3af9d79a190bc5a733b7c9f4c85d8  manifest.md
f20ae61c736034138d0dadded4512c8f1e7afa95124e5dd16624930f1e404c40  classification snapshot
71f5b8ecb9f43cfb0f4f70529767b1a8bbcfa4b7ca470ac633ff8aa4b6d50478  final adapter snapshot
```

These exact-frequency adapters remain historical inputs and may not be
interpolated, broadened, or reused for any of the 24 new frequencies.

## 3. Alternatives Considered

### 3.1 Selected: all 24 unique failed-child midpoints

This batch covers every T7bz hierarchy failure interval once and includes the
only observed phase-failure interval. Duplicate midpoint recommendations are
deduplicated by exact decimal identity, not by tolerance clustering.

Advantages:

- no known failed child interval is left unresolved by construction;
- the radial gate is paid once for the complete bounded repair;
- the scientific test advances exactly one local hierarchy level;
- the set remains point-only and limited to 24 frequencies and eight points;
- any new failure returns YELLOW instead of triggering recursion.

### 3.2 Rejected: only `3.7625`

This would target the phase failure but knowingly leave 96 other hierarchy
failure rows across 23 intervals without new evidence.

### 3.3 Rejected: select only the largest failure in each sequence

The current criterion is record-wise. Dropping smaller failing records would
change the frozen scientific rule and could hide a local non-monotone feature.

### 3.4 Rejected: uniform `0.025` or `0.0125` grid

A uniform grid would compute many intervals that T7bz did not flag and would
turn a bounded repair into a production-scale scan. No such grid is
authorized.

### 3.5 Rejected: automatic recursive bisection

The code must not invent the next frequency after a gate failure. This
package contains one literal 24-row level only; any failed child returns to
T0 and the independent package-review loop.

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

Frequencies use the canonical decimal tokens listed below and corresponding
binary64 values. Adapter membership uses `rtol=0`, `atol=1e-15`; nearest-
frequency selection is forbidden.

## 5. Exact Frequency, Token, lmax, And Cardinality Contract

The unchanged seed rule is:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
lmax_values = sorted unique [max(24,L_seed-72), L_seed-48,
                             L_seed-24, L_seed]
```

The exact initial windows are:

| `kM` | token | `lmax_values` | classification rows |
|---:|---|---|---:|
| `0.325` | `0p325` | `[24,36,60,84]` | 1328 |
| `0.375` | `0p375` | `[24,36,60,84]` | 1328 |
| `0.825` | `0p825` | `[24,36,60,84]` | 1328 |
| `0.875` | `0p875` | `[24,36,60,84]` | 1328 |
| `0.925` | `0p925` | `[24,36,60,84]` | 1328 |
| `0.975` | `0p975` | `[24,48,72,96]` | 1520 |
| `1.525` | `1p525` | `[72,96,120,144]` | 2288 |
| `1.575` | `1p575` | `[72,96,120,144]` | 2288 |
| `1.625` | `1p625` | `[84,108,132,156]` | 2480 |
| `1.675` | `1p675` | `[84,108,132,156]` | 2480 |
| `1.7125` | `1p7125` | `[84,108,132,156]` | 2480 |
| `1.7375` | `1p7375` | `[96,120,144,168]` | 2672 |
| `2.7625` | `2p7625` | `[180,204,228,252]` | 4016 |
| `2.7875` | `2p7875` | `[180,204,228,252]` | 4016 |
| `2.825` | `2p825` | `[192,216,240,264]` | 4208 |
| `2.875` | `2p875` | `[192,216,240,264]` | 4208 |
| `2.925` | `2p925` | `[192,216,240,264]` | 4208 |
| `2.975` | `2p975` | `[204,228,252,276]` | 4400 |
| `3.7625` | `3p7625` | `[276,300,324,348]` | 5552 |
| `3.7875` | `3p7875` | `[276,300,324,348]` | 5552 |
| `3.825` | `3p825` | `[276,300,324,348]` | 5552 |
| `3.875` | `3p875` | `[288,312,336,360]` | 5744 |
| `3.925` | `3p925` | `[288,312,336,360]` | 5744 |
| `3.975` | `3p975` | `[288,312,336,360]` | 5744 |

For every frequency, both sectors, every integer `ell=2..ell_max`, and all
eight points are classified. The exact total is:

```text
81,792 default-classification records
24 atomic frequency checkpoints
```

Transition cardinality is measured, never assumed. No lmax extension is
authorized. An initial final-pair failure at T8aq is YELLOW and stops before
aggregation.

## 6. Exact Sequences And Literal Parent Mapping

T7cb reconstructs these five sequences from immutable T8aj, T8ao, T8ap, and
new T8aq rows:

```text
[0.3,0.325,0.35,0.375,0.4,0.45,0.5]
[0.75,0.8,0.825,0.85,0.875,0.9,0.925,0.95,0.975,1.0]
[1.5,1.525,1.55,1.575,1.6,1.625,1.65,1.675,1.7,
 1.7125,1.725,1.7375,1.75]
[2.75,2.7625,2.775,2.7875,2.8,2.825,2.85,2.875,2.9,
 2.925,2.95,2.975,3.0]
[3.75,3.7625,3.775,3.7875,3.8,3.825,3.85,3.875,3.9,
 3.925,3.95,3.975,4.0]
```

There are 51 adjacent intervals and exactly:

```text
51 * 8 points * 2 components = 816 phase-step records
```

Every new midpoint bisects one literal T7bz-failed child interval. Each
midpoint creates two grandchildren, yielding exactly:

```text
24 * 2 children * 8 points * 2 components = 768 hierarchy records
```

The parent mapping is literal and must not be inferred from floating-point
adjacency:

| midpoint | exact T7bz parent child | grandchild 1 | grandchild 2 | parent width |
|---:|---|---|---|---:|
| `0.325` | `[0.3,0.35]` | `[0.3,0.325]` | `[0.325,0.35]` | `0.05` |
| `0.375` | `[0.35,0.4]` | `[0.35,0.375]` | `[0.375,0.4]` | `0.05` |
| `0.825` | `[0.8,0.85]` | `[0.8,0.825]` | `[0.825,0.85]` | `0.05` |
| `0.875` | `[0.85,0.9]` | `[0.85,0.875]` | `[0.875,0.9]` | `0.05` |
| `0.925` | `[0.9,0.95]` | `[0.9,0.925]` | `[0.925,0.95]` | `0.05` |
| `0.975` | `[0.95,1.0]` | `[0.95,0.975]` | `[0.975,1.0]` | `0.05` |
| `1.525` | `[1.5,1.55]` | `[1.5,1.525]` | `[1.525,1.55]` | `0.05` |
| `1.575` | `[1.55,1.6]` | `[1.55,1.575]` | `[1.575,1.6]` | `0.05` |
| `1.625` | `[1.6,1.65]` | `[1.6,1.625]` | `[1.625,1.65]` | `0.05` |
| `1.675` | `[1.65,1.7]` | `[1.65,1.675]` | `[1.675,1.7]` | `0.05` |
| `1.7125` | `[1.7,1.725]` | `[1.7,1.7125]` | `[1.7125,1.725]` | `0.025` |
| `1.7375` | `[1.725,1.75]` | `[1.725,1.7375]` | `[1.7375,1.75]` | `0.025` |
| `2.7625` | `[2.75,2.775]` | `[2.75,2.7625]` | `[2.7625,2.775]` | `0.025` |
| `2.7875` | `[2.775,2.8]` | `[2.775,2.7875]` | `[2.7875,2.8]` | `0.025` |
| `2.825` | `[2.8,2.85]` | `[2.8,2.825]` | `[2.825,2.85]` | `0.05` |
| `2.875` | `[2.85,2.9]` | `[2.85,2.875]` | `[2.875,2.9]` | `0.05` |
| `2.925` | `[2.9,2.95]` | `[2.9,2.925]` | `[2.925,2.95]` | `0.05` |
| `2.975` | `[2.95,3.0]` | `[2.95,2.975]` | `[2.975,3.0]` | `0.05` |
| `3.7625` | `[3.75,3.775]` | `[3.75,3.7625]` | `[3.7625,3.775]` | `0.025` |
| `3.7875` | `[3.775,3.8]` | `[3.775,3.7875]` | `[3.7875,3.8]` | `0.025` |
| `3.825` | `[3.8,3.85]` | `[3.8,3.825]` | `[3.825,3.85]` | `0.05` |
| `3.875` | `[3.85,3.9]` | `[3.85,3.875]` | `[3.875,3.9]` | `0.05` |
| `3.925` | `[3.9,3.95]` | `[3.9,3.925]` | `[3.925,3.95]` | `0.05` |
| `3.975` | `[3.95,4.0]` | `[3.95,3.975]` | `[3.975,4.0]` | `0.05` |

Each grandchild magnitude step is compared only with the exact parent-child
step saved in immutable source artifacts. Comparisons never cross sequence,
point, component, or parent interval.

## 7. Stage 1 — T4ab Radial/Q018 Gate

T4ab classifies all 81,792 default records and independently validates every
recoverable transition key `(kM, sector, ell, point_id)` with the existing
direct Riccati/log-amplitude oracle. It preserves the T4aa requirements for
finite fields, residuals, normalization, boundary consistency, tolerance
sensitivity, explicit requested/actual precision, deterministic anchors,
sector-aware literal membership, atomic checkpoints, and no odd/even
inference.

Only after a complete passing gate may it add:

```text
q018_tablei_further_local_transition
```

The adapter is exact to the 24 frequencies, eight points, both sectors,
literal measured ell membership, and frozen boundary/tolerance fields.
Default-covered modes remain on the ordinary solver path. Every wrong
frequency, point, radius, ell, sector, `M`, boundary, or tolerance fails
closed. There is no frequency/radius/ell interpolation.

Artifacts are written only under:

```text
runs/phase5/fig5_fig6_further_local_radial_gate/
```

with exactly 24 atomic checkpoints plus:

```text
classification_manifest.json
oracle_validation.json
resume_preflight.json
manifest.md
```

As in T4aa, classification and final-adapter provenance are separate:

1. the classification snapshot binds the final gate script, pre-adapter
   `radial_solver.py`, direct oracle, Table-I source, frozen package and full
   input contract;
2. the final adapter snapshot binds the generated literal envelope, final
   `radial_solver.py`, exact implementation commit and all five blobs;
3. checkpoints compare only with the classification snapshot;
4. preflight and manifest bind both snapshots through an explicit hash bridge.

The implementation commit may contain exactly:

```text
scripts/phase5_further_local_radial_gate.py
src/schwgw/numerics/q018_further_local_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Exact decisions are:

```text
GREEN / FURTHER LOCAL RADIAL GATE READY
YELLOW / FURTHER LOCAL RADIAL GATE PARTIAL
RED / FURTHER LOCAL RADIAL GATE BLOCKED
```

Only exact GREEN may dispatch T7ca.

## 8. Stage 2 — T7ca Independent Radial Review

T7ca is review-only. It independently verifies exact scope, 81,792-row
cardinality, 24 checkpoints, raw transition/oracle/preflight key equality,
fresh default samples, deterministic producer and complementary reviewer
anchors, literal sector-aware envelope expansion, strict adapter behavior,
both provenance snapshots, tests, Ruff, full pytest, and absence of any T8aq
or forbidden output.

Exact decisions are:

```text
ACCEPT GREEN / FURTHER LOCAL RADIAL GATE ACCEPTED
ACCEPT YELLOW / FURTHER LOCAL RADIAL EVIDENCE INCOMPLETE
REJECT RED / FURTHER LOCAL RADIAL GATE INVALID
```

T7ca returns only to T0. Only T0 may dispatch T8aq after exact GREEN.

## 9. Stage 3 — T8aq Point-Only Further-Local Evidence

T8aq computes exactly the 24 new frequencies at the eight Table-I points. It
uses only the T7ca-accepted exact adapter and does not alter any accepted
T8aj/T8ao/T8ap/T4aa artifact.

The implementation commit may contain exactly:

```text
src/schwgw/io/tablei_further_local_refinement.py
src/schwgw/io/__init__.py
scripts/phase5_run_further_local_refinement.py
tests/unit/test_tablei_further_local_refinement.py
tests/regression/test_further_local_refinement_script.py
```

Before the first real frequency, T8aq completes fake-compute tests and Ruff,
then creates one exact five-path implementation commit. The generation
contract binds that commit and its five blobs. No transaction may cross an
implementation identity.

Every frequency is an independent atomic NPZ/JSON transaction with a hash-
bound ledger record. Resume reuses only a complete matching transaction. A
partial or mismatched pair is quarantined and excluded. Radial cache reuse is
frequency-local and requires the complete certified radius domain; disjoint
local solutions are preserved.

Write only under:

```text
runs/phase5/fig5_fig6_further_local_refinement/
```

The active layout is:

```text
frequencies/kM_<token>.npz
frequencies/kM_<token>.npz.json
checkpoint_ledger.json
further_local_values.npz
further_local_values.npz.json
further_local_sampling_audit.json
manifest.md
```

The exact cardinality is 53 active files and 52 non-self manifest records.
The aggregate contains only the 24 new frequencies with shape `(24,8)`.

The schema is exactly:

```text
phase5_t8aq_further_local_refinement_v1_units_dtype_ordering
```

Separate generation and metadata contracts explicitly bind frequencies,
tokens, lmax windows, physical/numerical inputs, accepted source and gate
hashes, implementation/code identity, convergence, cache/resume rules, schema,
units, dtypes, ordering, array fingerprints, and no-production flags on every
embedded metadata/sidecar/ledger/audit/manifest surface.

The per-frequency and aggregate array contracts retain the accepted 22/21
structures, actual NumPy dtypes, units, and axis ordering. No reviewer may be
required to infer a unit, dtype, axis, or source identity.

The audit records exactly 816 phase, 768 hierarchy, and 80 sequence-summary
records, plus all strict interior extrema. It is diagnostic-only and emits no
scientific acceptance decision.

Exact decisions are:

```text
GREEN / FURTHER LOCAL FREQUENCY EVIDENCE GENERATED
YELLOW / FURTHER LOCAL FREQUENCY EVIDENCE PARTIAL
RED / FURTHER LOCAL FREQUENCY EVIDENCE BLOCKED
```

Only exact GREEN may dispatch T7cb.

## 10. Stage 4 — T7cb Independent Scientific Review

T7cb directly loads the 24 new transaction pairs and immutable prior source
rows. It must not call T8aq loaders, aggregation, sampling, migration, or
acceptance helpers.

The artifact gate requires exact 53/52 cardinality, all hashes/contracts,
units/dtypes/ordering, aggregate identity, finite values, true masks, frozen
lmax windows, final-pair convergence, ledger/resume/quarantine isolation,
focused tests, Ruff, full pytest, exact implementation scope, and empty
forbidden outputs. Any invalid artifact, source mismatch, scope drift,
nonfinite value, or test/provenance failure is RED.

### 10.1 Observed phase criterion

For all 816 adjacent records:

```text
phase = np.unwrap(np.angle(F), axis=frequency)
abs(diff(phase)) < pi/2
```

All values must be finite. This remains observed local evidence, not a global
band-limit theorem.

### 10.2 Hierarchical magnitude criterion

For magnitudes `a=|F(k_i)|`, `b=|F(k_j)|`:

```text
relative_step(a,b) = abs(a-b) / max(1, a, b)
```

For all 768 grandchild records require:

```text
grandchild_relative_step <= exact_T7bz_parent_child_step + 2e-15
```

The parent values are direct immutable complex rows, not rounded report
numbers. No comparison crosses a point, component, or literal parent row.
T7cb reports full failure membership, total variation, cancellation, largest
steps, and all strict extrema; it invents no new threshold.

Exact decisions are:

```text
ACCEPT GREEN / FURTHER LOCAL FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / FURTHER LOCAL FREQUENCY REFINEMENT REQUIRED
REJECT RED / FURTHER LOCAL FREQUENCY ARTIFACT INVALID
```

GREEN requires the artifact gate plus all 816 phase and all 768 hierarchy
records to pass. It permits only T0 to interpret whether a later nonuniform
production completion is justified. It does not start one or claim global
convergence.

YELLOW means the artifact is valid but one or more scientific records fail.
It identifies exact intervals and diagnostic next midpoints but authorizes
nothing. RED is reserved for artifact/computation/test/provenance/scope
invalidity. T7cb never repairs or dispatches downstream work.

## 11. Existing Tasks And Automatic Coordination

Use only the existing Codex tasks:

```text
T4 = 019f5fa6-1288-7c01-8a87-4c4370cf5517
T7 = 019f5ed1-b421-7ec2-9bac-8d134855a1ed
T8 = 019f5ece-f578-7b91-8f61-df882c656591
```

Default dispatch is `5.6 Sol High` where the platform supports model
selection.

- A matching independent T0 package-review GREEN is equivalent only to the
  user's approval of this exact repair package.
- T0 dispatches frozen T4ab to existing T4.
- T4ab exact GREEN may dispatch frozen T7ca to existing T7.
- T7ca returns only to T0; only T0 may dispatch T8aq after fresh verification.
- T8aq exact GREEN may dispatch frozen T7cb to existing T7.
- T7cb returns only to T0 and starts nothing.
- Missing/archived tasks or messaging failure stop the chain; no replacement
  task is created.

## 12. Runtime, Recovery, And Monitoring

Elapsed time is a health signal, not a scientific threshold.

- T4ab has 24 checkpoints and may take roughly a day; `30 h` is a soft
  notification only.
- T8aq may take several hours; `12 h` is a soft notification only.
- Combined active storage target is `<250 MB`.
- Every computational frequency is atomically checkpointed.
- A monitor checks process liveness, checkpoint growth, hashes, tests,
  decisions, and gated dispatch without restarting a healthy process.

A clear model-capacity/system interruption may resume the same task with
`5.6 Terra High` only after process, checkpoint, artifact, contract, test, and
scope checks prove there is no scientific failure. Resume must reuse safe
state and never recompute a complete matching frequency. Scientific,
numerical, nonfinite, contract, provenance, test, or scope failure never
qualifies for model switching.

## 13. Authorized Change Boundaries

- T4ab: exact five gate implementation/test paths, its new run directory,
  one gate note, `status.md`, T4 handoff, and one T4 archive.
- T7ca/T7cb: review-only; `status.md`, T7 handoff, and one exact archive for
  each review.
- T8aq: exact five IO/runner/test paths, its new run directory, `status.md`,
  T8 handoff, and one T8 archive.
- T0: this seven-file candidate package, T0 status/handoff/archive,
  monitoring, exact gated dispatch, and major-node GitHub handling only if a
  later independent GREEN satisfies `project.md`.

All stages preserve unrelated T1/T2/T3/T5/T6 worktree changes. T4/T7/T8 do
not push GitHub.

## 14. Explicit Non-Goals

- No full, 40-, or 79-frequency production grid.
- No uniform `0.025` or `0.0125` scan.
- No automatic recursive midpoint.
- No lmax extension.
- No interpolation, smoothing, clipping, fill, or inferred adapter membership.
- No full x-z field grid.
- No plot, PDF, PNG, fixture, benchmark promotion, or paper-style rendering.
- No Kirchhoff regeneration, normalization, correction, or mask use.
- No physics convention, Route-B bridge, Q018 threshold, boundary value,
  convergence tolerance, lmax rule, or warning relaxation.
- No mutation of accepted T8aj, T8ao/T7bx, T4aa/T7by, T8ap/T7bz artifacts.
- No automatic continuation after T7cb.

## 15. Failure Rules

- Missing or changed immutable source hash: RED; never regenerate the source.
- Complete valid radial evidence with unresolved structured coverage: T4ab
  YELLOW.
- Unstructured/default-other error, nonfinite oracle value, residual or
  sensitivity failure, checkpoint ambiguity, scope drift, or failed tests:
  T4ab RED.
- Incomplete/nonconverged T8aq frequency: preserve completed transactions,
  do not aggregate, and stop YELLOW.
- Invalid schema/units/dtype/ordering, hash, ledger, cardinality, aggregate
  identity, or active temporary state: RED.
- Valid artifact with failed phase or hierarchy criterion: scientific YELLOW.
- Review tasks never fix producers.

## 16. Definition Of Done

- T4ab produces complete 24-frequency/81,792-record radial evidence, exact
  adapter, 24 checkpoints, fresh tests, and one exact decision.
- T7ca independently accepts or rejects the radial gate.
- T8aq produces exactly 24 new point-only transactions, a 53-file package,
  explicit units/dtype/ordering contracts, and no mutation of accepted inputs.
- T7cb independently reconstructs exactly 816 phase and 768 hierarchy records
  and gives one exact artifact/scientific decision.
- T0 records and interprets the result.
- No recursive refinement, production grid, plot, fixture, Kirchhoff,
  paper-style work, or later task starts automatically.
