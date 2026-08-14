# T4ac–T8ar Literal Failed-Child Refinement Design

Date: 2026-07-18
Status: frozen T0 bounded-repair candidate; no execution authorization until
the same independent read-only reviewer returns exact package-review GREEN.

## 1. Gate Result And Bounded Objective

Frozen T7cb returned exactly:

```text
ACCEPT YELLOW / FURTHER LOCAL FREQUENCY REFINEMENT REQUIRED
```

The T8aq package is structurally valid. T7cb and a fresh T0 direct-load audit
independently reconstructed the same immutable evidence:

- 53 active files and 52 non-self manifest records;
- 24 complete NPZ/JSON transaction pairs;
- 816 phase records, of which 814 pass and 2 fail strict `< pi/2`;
- 768 literal-parent hierarchy records, of which 615 pass and 153 fail
  `child_relative_step <= parent_relative_step + 2e-15`;
- 80 sequence summaries and 181 strict interior extrema;
- maximum phase step `2.009547281330329`;
- maximum hierarchy excess `0.3055122866114057`.

The two phase failures are both plus polarization at
`near_axis_x2_z30`:

```text
[3.7625,3.775]   step = 1.8395305160664122
[3.775,3.7875]  step = 2.009547281330329
```

The 153 hierarchy failures occupy exactly 41 unique literal child intervals.
Both failed phase intervals are already members of that 41-interval set.
This repair advances exactly one separately frozen local hierarchy level by
sampling the midpoint of each of those 41 failed intervals once. It adds no
passing interval and performs no automatic or recursive selection.

## 2. Selected Repair And Rejected Alternatives

### 2.1 Selected: all 41 unique failed-child midpoints

This is the smallest batch that advances every observed T7cb hierarchy
failure interval one literal level while also addressing both phase failures.
Repeated failures across point or component share one frequency. Selection is
based only on complete T7cb failure membership, never on a new threshold.

### 2.2 Rejected: only the two phase intervals

This would knowingly leave 39 other hierarchy-failed child intervals
unexamined and therefore cannot test the full frozen hierarchy gate.

### 2.3 Rejected: largest failure per sequence or component

Ranking would introduce an unreviewed selection rule and omit valid failure
membership. No ranking, weighting, or budget threshold is introduced.

### 2.4 Rejected: uniform `0.0125` or `0.00625` grid

The selected frequencies happen to contain contiguous local patches where all
children failed, but the batch is the literal failed-child set only. It does
not fill passing intervals and is not a uniform or full grid.

### 2.5 Rejected: automatic recursive bisection

There is no runtime midpoint discovery. Any failure after T7cd stops at T0.
Another level would require a new design, immutable identity, and independent
package review.

## 3. Immutable Starting Evidence

The repair binds the following accepted identities:

```text
T8aq implementation commit  c34268b6977d9e4e228f0bcc29b628390bd1b1bb
T8aq implementation parent  c3a6479703f6c2d64aa2903edc7cf2db3d1ed112
generation contract          a43ab0769a73768723505b2bee0715646e215624cc5b5efd880d97bcfff778f1
metadata contract            ff4210c449dfedb5b37228f76e9d91d71488935c7c5064c40b1ddefb961e8d96
ledger                       7b63e0689a01e32e27397007a3e458c800e2802bdd72c3f582a6e8a6bec4ae72
aggregate NPZ                27c263e8cb4b3270fe3103a9d79617a345a383a636da0ab3af4f954432fdf50b
aggregate JSON               df30e1f3cb3d17f87bc8f62470a87d5bca2e6819543fe9430b5c48a1d9552a8e
sampling audit               a5f5e9d91d1b932fbec307244d35ebee688cfecaf2b11a54672b7eb2d33a2395
manifest                     f84d6a1fb2cee35d2a00e81756110d2b75b99edca2946e79e2f70362f7350f3c
T7cb handoff                 57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01
pre-T7cb T7ca archive        f7b46bf1e04bb5fdbe75ad522ec9673ca9df30d317fa0356cdd29295d80a91ef
```

The earlier T8aj/T8ao/T8ap sources, T4ab gate, classification snapshot
`52889944b58ec8aae442afb7c743679fcbbd9d3dd21819cc61cf1364b683eb43`,
and final-adapter snapshot
`ba6e63d87c7cc2cad4a64300a775bc07059d7a21760dbd431e411f6508febcb3`
remain immutable inputs. T4ac and T8ar must bind live file hashes and fail
closed on any drift.

The original seven-file package at commit
`76b57c90d6e54594ca480e1dcf629af685d9098f` remains frozen and must retain its
recorded SHA-256 values. The T8aq coordination correction at commit
`fa22f20f775c1b15ae533c03047d156687e5f3bf` is coordination-only and changes
no scientific evidence.

## 4. Physical And Numerical Conventions

All conventions are unchanged:

- Schwarzschild background, `G=c=M=1`;
- both odd and even sectors;
- every integer `ell=2..ell_max` required by the unchanged seed rule;
- the exact eight Table-I point IDs and their existing order;
- the same incident direction, polarization convention, boundary conditions,
  `r_out`, `r_in_eps`, solver tolerances, Q018 policy, and fail-closed rules;
- point-only complex amplification evidence, never interpolation or filling;
- final-pair convergence threshold exactly `1e-4`;
- phase criterion strictly `< pi/2`;
- hierarchy tolerance exactly `+2e-15`.

No lmax extension, threshold relaxation, sector merging, new point, smoothing,
interpolation, fill, observable production, plotting, fixture, Kirchhoff, or
paper-style output is allowed.

## 5. Exact Frequencies, Tokens, lmax Windows, And Cardinality

The unchanged seed rule is:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
lmax_values = sorted unique [max(24,L_seed-72), L_seed-48,
                             L_seed-24, L_seed]
classification_rows = (ell_max - 1) * 2 sectors * 8 points
```

| `kM` | token | `lmax_values` | classification rows |
|---:|---|---|---:|
| `0.3125` | `0p3125` | `[24,36,60,84]` | 1328 |
| `0.3375` | `0p3375` | `[24,36,60,84]` | 1328 |
| `0.3625` | `0p3625` | `[24,36,60,84]` | 1328 |
| `0.3875` | `0p3875` | `[24,36,60,84]` | 1328 |
| `0.8625` | `0p8625` | `[24,36,60,84]` | 1328 |
| `0.9125` | `0p9125` | `[24,36,60,84]` | 1328 |
| `0.9375` | `0p9375` | `[24,48,72,96]` | 1520 |
| `0.9625` | `0p9625` | `[24,48,72,96]` | 1520 |
| `0.9875` | `0p9875` | `[24,48,72,96]` | 1520 |
| `1.5125` | `1p5125` | `[72,96,120,144]` | 2288 |
| `1.5375` | `1p5375` | `[72,96,120,144]` | 2288 |
| `1.5625` | `1p5625` | `[72,96,120,144]` | 2288 |
| `1.5875` | `1p5875` | `[72,96,120,144]` | 2288 |
| `1.6125` | `1p6125` | `[84,108,132,156]` | 2480 |
| `1.6375` | `1p6375` | `[84,108,132,156]` | 2480 |
| `1.6625` | `1p6625` | `[84,108,132,156]` | 2480 |
| `1.6875` | `1p6875` | `[84,108,132,156]` | 2480 |
| `1.70625` | `1p70625` | `[84,108,132,156]` | 2480 |
| `1.71875` | `1p71875` | `[84,108,132,156]` | 2480 |
| `2.78125` | `2p78125` | `[180,204,228,252]` | 4016 |
| `2.79375` | `2p79375` | `[180,204,228,252]` | 4016 |
| `2.8125` | `2p8125` | `[192,216,240,264]` | 4208 |
| `2.8375` | `2p8375` | `[192,216,240,264]` | 4208 |
| `2.8625` | `2p8625` | `[192,216,240,264]` | 4208 |
| `2.8875` | `2p8875` | `[192,216,240,264]` | 4208 |
| `2.9125` | `2p9125` | `[192,216,240,264]` | 4208 |
| `2.9375` | `2p9375` | `[204,228,252,276]` | 4400 |
| `2.9625` | `2p9625` | `[204,228,252,276]` | 4400 |
| `2.9875` | `2p9875` | `[204,228,252,276]` | 4400 |
| `3.75625` | `3p75625` | `[276,300,324,348]` | 5552 |
| `3.76875` | `3p76875` | `[276,300,324,348]` | 5552 |
| `3.78125` | `3p78125` | `[276,300,324,348]` | 5552 |
| `3.79375` | `3p79375` | `[276,300,324,348]` | 5552 |
| `3.8125` | `3p8125` | `[276,300,324,348]` | 5552 |
| `3.8375` | `3p8375` | `[276,300,324,348]` | 5552 |
| `3.8625` | `3p8625` | `[276,300,324,348]` | 5552 |
| `3.8875` | `3p8875` | `[288,312,336,360]` | 5744 |
| `3.9125` | `3p9125` | `[288,312,336,360]` | 5744 |
| `3.9375` | `3p9375` | `[288,312,336,360]` | 5744 |
| `3.9625` | `3p9625` | `[288,312,336,360]` | 5744 |
| `3.9875` | `3p9875` | `[288,312,336,360]` | 5744 |

Exact radial-classification cardinality:

```text
41 frequencies
146,416 classification records
41 atomic frequency checkpoints
```

Transition cardinality is measured, never predicted. The maximum lmax remains
360, so this package introduces no lmax extension.

## 6. Five Literal Sequences And 41-Row Parent Map

T7cd reconstructs only these sequences from immutable prior rows plus the new
T8ar rows:

```text
[0.3,0.3125,0.325,0.3375,0.35,0.3625,0.375,0.3875,0.4,0.45,0.5]

[0.75,0.8,0.825,0.85,0.8625,0.875,0.9,0.9125,0.925,0.9375,
 0.95,0.9625,0.975,0.9875,1.0]

[1.5,1.5125,1.525,1.5375,1.55,1.5625,1.575,1.5875,1.6,
 1.6125,1.625,1.6375,1.65,1.6625,1.675,1.6875,1.7,
 1.70625,1.7125,1.71875,1.725,1.7375,1.75]

[2.75,2.7625,2.775,2.78125,2.7875,2.79375,2.8,2.8125,2.825,
 2.8375,2.85,2.8625,2.875,2.8875,2.9,2.9125,2.925,2.9375,
 2.95,2.9625,2.975,2.9875,3.0]

[3.75,3.75625,3.7625,3.76875,3.775,3.78125,3.7875,3.79375,
 3.8,3.8125,3.825,3.8375,3.85,3.8625,3.875,3.8875,3.9,
 3.9125,3.925,3.9375,3.95,3.9625,3.975,3.9875,4.0]
```

The sequences contain 92 adjacent intervals:

```text
92 * 8 points * 2 components = 1,472 phase records
41 * 2 children * 8 points * 2 components = 1,312 hierarchy records
5 * 8 points * 2 components = 80 summaries
```

The parent map is literal and must never be inferred from floating adjacency:

| midpoint | exact failed child parent | new child 1 | new child 2 | parent width |
|---:|---|---|---|---:|
| `0.3125` | `[0.3,0.325]` | `[0.3,0.3125]` | `[0.3125,0.325]` | `0.025` |
| `0.3375` | `[0.325,0.35]` | `[0.325,0.3375]` | `[0.3375,0.35]` | `0.025` |
| `0.3625` | `[0.35,0.375]` | `[0.35,0.3625]` | `[0.3625,0.375]` | `0.025` |
| `0.3875` | `[0.375,0.4]` | `[0.375,0.3875]` | `[0.3875,0.4]` | `0.025` |
| `0.8625` | `[0.85,0.875]` | `[0.85,0.8625]` | `[0.8625,0.875]` | `0.025` |
| `0.9125` | `[0.9,0.925]` | `[0.9,0.9125]` | `[0.9125,0.925]` | `0.025` |
| `0.9375` | `[0.925,0.95]` | `[0.925,0.9375]` | `[0.9375,0.95]` | `0.025` |
| `0.9625` | `[0.95,0.975]` | `[0.95,0.9625]` | `[0.9625,0.975]` | `0.025` |
| `0.9875` | `[0.975,1.0]` | `[0.975,0.9875]` | `[0.9875,1.0]` | `0.025` |
| `1.5125` | `[1.5,1.525]` | `[1.5,1.5125]` | `[1.5125,1.525]` | `0.025` |
| `1.5375` | `[1.525,1.55]` | `[1.525,1.5375]` | `[1.5375,1.55]` | `0.025` |
| `1.5625` | `[1.55,1.575]` | `[1.55,1.5625]` | `[1.5625,1.575]` | `0.025` |
| `1.5875` | `[1.575,1.6]` | `[1.575,1.5875]` | `[1.5875,1.6]` | `0.025` |
| `1.6125` | `[1.6,1.625]` | `[1.6,1.6125]` | `[1.6125,1.625]` | `0.025` |
| `1.6375` | `[1.625,1.65]` | `[1.625,1.6375]` | `[1.6375,1.65]` | `0.025` |
| `1.6625` | `[1.65,1.675]` | `[1.65,1.6625]` | `[1.6625,1.675]` | `0.025` |
| `1.6875` | `[1.675,1.7]` | `[1.675,1.6875]` | `[1.6875,1.7]` | `0.025` |
| `1.70625` | `[1.7,1.7125]` | `[1.7,1.70625]` | `[1.70625,1.7125]` | `0.0125` |
| `1.71875` | `[1.7125,1.725]` | `[1.7125,1.71875]` | `[1.71875,1.725]` | `0.0125` |
| `2.78125` | `[2.775,2.7875]` | `[2.775,2.78125]` | `[2.78125,2.7875]` | `0.0125` |
| `2.79375` | `[2.7875,2.8]` | `[2.7875,2.79375]` | `[2.79375,2.8]` | `0.0125` |
| `2.8125` | `[2.8,2.825]` | `[2.8,2.8125]` | `[2.8125,2.825]` | `0.025` |
| `2.8375` | `[2.825,2.85]` | `[2.825,2.8375]` | `[2.8375,2.85]` | `0.025` |
| `2.8625` | `[2.85,2.875]` | `[2.85,2.8625]` | `[2.8625,2.875]` | `0.025` |
| `2.8875` | `[2.875,2.9]` | `[2.875,2.8875]` | `[2.8875,2.9]` | `0.025` |
| `2.9125` | `[2.9,2.925]` | `[2.9,2.9125]` | `[2.9125,2.925]` | `0.025` |
| `2.9375` | `[2.925,2.95]` | `[2.925,2.9375]` | `[2.9375,2.95]` | `0.025` |
| `2.9625` | `[2.95,2.975]` | `[2.95,2.9625]` | `[2.9625,2.975]` | `0.025` |
| `2.9875` | `[2.975,3.0]` | `[2.975,2.9875]` | `[2.9875,3.0]` | `0.025` |
| `3.75625` | `[3.75,3.7625]` | `[3.75,3.75625]` | `[3.75625,3.7625]` | `0.0125` |
| `3.76875` | `[3.7625,3.775]` | `[3.7625,3.76875]` | `[3.76875,3.775]` | `0.0125` |
| `3.78125` | `[3.775,3.7875]` | `[3.775,3.78125]` | `[3.78125,3.7875]` | `0.0125` |
| `3.79375` | `[3.7875,3.8]` | `[3.7875,3.79375]` | `[3.79375,3.8]` | `0.0125` |
| `3.8125` | `[3.8,3.825]` | `[3.8,3.8125]` | `[3.8125,3.825]` | `0.025` |
| `3.8375` | `[3.825,3.85]` | `[3.825,3.8375]` | `[3.8375,3.85]` | `0.025` |
| `3.8625` | `[3.85,3.875]` | `[3.85,3.8625]` | `[3.8625,3.875]` | `0.025` |
| `3.8875` | `[3.875,3.9]` | `[3.875,3.8875]` | `[3.8875,3.9]` | `0.025` |
| `3.9125` | `[3.9,3.925]` | `[3.9,3.9125]` | `[3.9125,3.925]` | `0.025` |
| `3.9375` | `[3.925,3.95]` | `[3.925,3.9375]` | `[3.9375,3.95]` | `0.025` |
| `3.9625` | `[3.95,3.975]` | `[3.95,3.9625]` | `[3.9625,3.975]` | `0.025` |
| `3.9875` | `[3.975,4.0]` | `[3.975,3.9875]` | `[3.9875,4.0]` | `0.025` |

Every new child is compared only with its exact immutable T7cb failed-child
parent step for the same point and component. No comparison crosses a parent,
point, component, or sequence.

## 7. T4ac Literal Failed-Child Radial Gate

T4ac classifies all 146,416 mode/sector/point records and computes a direct
oracle only for measured structured transitions. It must create exactly 41
atomic checkpoints plus classification, oracle-validation, resume-preflight,
and manifest roots under:

```text
runs/phase5/fig5_fig6_literal_failed_child_radial_gate/
```

Before classification it records a classification snapshot binding the
parent-commit radial implementation and every immutable input. After adding a
literal sector-aware envelope and opt-in adapter, it records a final-adapter
snapshot binding the exact implementation commit and all five blobs. The two
snapshots must bridge without changing classification membership.

The exact implementation commit changes only:

```text
scripts/phase5_literal_failed_child_radial_gate.py
src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

The adapter label is
`q018_tablei_literal_failed_child_transition`. Default-covered modes make no
oracle call. Every wrong frequency, point, ell, sector, boundary, radius,
tolerance, or implementation identity fails closed.

Exact producer decision:

```text
GREEN / LITERAL FAILED-CHILD RADIAL GATE READY
YELLOW / LITERAL FAILED-CHILD RADIAL EVIDENCE INCOMPLETE
RED / LITERAL FAILED-CHILD RADIAL GATE INVALID
```

Only exact GREEN returns to T0/T7cc. T4ac never starts T7cc or T8ar itself.

## 8. T7cc Independent Radial Review

T7cc is read-only. It independently verifies exact 146,416 classification
cardinality, 41 sector-aware transition sets, direct oracle and anchors, 41
checkpoints, both snapshots and hash bridge, literal envelope expansion,
five-path commit scope, focused/Ruff/full tests, and empty forbidden outputs.
It archives the pre-review T7cb handoff byte-for-byte and requires SHA-256
`57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01`.

Exact reviewer decision:

```text
ACCEPT GREEN / LITERAL FAILED-CHILD RADIAL GATE ACCEPTED
ACCEPT YELLOW / LITERAL FAILED-CHILD RADIAL EVIDENCE INCOMPLETE
REJECT RED / LITERAL FAILED-CHILD RADIAL GATE INVALID
```

Only exact ACCEPT GREEN returns to T0 for fresh verification. T7cc never
starts T8ar.

## 9. T8ar Point-Only Evidence

After T0 fresh-verifies T7cc exact ACCEPT GREEN, T8ar creates exactly 41
atomic NPZ/JSON pairs, then one ledger, aggregate NPZ, aggregate JSON,
diagnostic-only audit, and manifest under:

```text
runs/phase5/fig5_fig6_literal_failed_child_refinement/
```

Exact active/manifest cardinality:

```text
41 NPZ + 41 JSON + 5 roots = 87 active files
86 non-self manifest records
```

Before the first real frequency, T8ar completes fake-compute tests, Ruff, and
creates one implementation commit changing exactly:

```text
scripts/phase5_run_literal_failed_child_refinement.py
src/schwgw/io/__init__.py
src/schwgw/io/tablei_literal_failed_child_refinement.py
tests/unit/test_tablei_literal_failed_child_refinement.py
tests/regression/test_literal_failed_child_refinement_script.py
```

Each transaction binds the exact implementation commit, generation contract,
metadata contract, source/gate hashes, units, actual dtypes, ordering, lmax
history, complete masks, and final-pair convergence. Resume may reuse only a
complete transaction with exact matching implementation and contract identity.
It may never recompute a complete matching frequency or reuse across identity.

The aggregate must equal direct stacking of all 41 pairs. The audit records
exactly 1,472 phase records, 1,312 hierarchy records, and 80 summaries, but
must set:

```text
diagnostic_only = true
acceptance_decision_emitted = false
```

T8ar emits no scientific acceptance decision and invents no threshold.
Exact producer decision:

```text
GREEN / LITERAL FAILED-CHILD FREQUENCY EVIDENCE GENERATED
YELLOW / LITERAL FAILED-CHILD FREQUENCY EVIDENCE INCOMPLETE
RED / LITERAL FAILED-CHILD FREQUENCY ARTIFACT INVALID
```

Only exact GREEN returns to T0 for fresh verification. T8ar never starts T7cd.

## 10. T7cd Independent Scientific Review

T7cd directly loads the 41 new transaction pairs and immutable prior rows. It
must not call T8ar loaders, aggregation, sampling, migration, or acceptance
helpers.

Artifact RED conditions include any cardinality, hash, contract, unit, dtype,
ordering, finiteness, mask, lmax, final-pair, aggregate, ledger, checkpoint,
source, test, scope, or provenance failure.

For all 1,472 adjacent records:

```text
phase = np.unwrap(np.angle(F), axis=frequency)
abs(diff(phase)) < pi/2
```

For magnitudes `a=|F(k_i)|`, `b=|F(k_j)|`:

```text
relative_step(a,b) = abs(a-b) / max(1,a,b)
new_child_relative_step <= exact_T7cb_failed_child_step + 2e-15
```

T7cd reports every failure, full attribution, total variation, cancellation,
largest steps, all strict extrema, and diagnostic-only next midpoints. It
invents no threshold and authorizes nothing.

Exact decisions:

```text
ACCEPT GREEN / LITERAL FAILED-CHILD FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL REFINEMENT REQUIRED
REJECT RED / LITERAL FAILED-CHILD FREQUENCY ARTIFACT INVALID
```

GREEN requires the full artifact gate and every phase and hierarchy record to
pass. YELLOW means valid artifact plus one or more scientific failures. RED is
reserved for invalid artifact/computation/test/provenance/scope. T7cd returns
only to T0 and starts nothing downstream.

## 11. Existing Tasks, Dispatch, And Recovery

Only the existing tasks may be used:

```text
T4 = 019f5fa6-1288-7c01-8a87-4c4370cf5517
T7 = 019f5ed1-b421-7ec2-9bac-8d134855a1ed
T8 = 019f5ece-f578-7b91-8f61-df882c656591
```

No task may be created or replaced. The chain is:

```text
same package reviewer exact GREEN -> T0 fresh verify -> T4ac
T4ac exact GREEN -> T7cc
T7cc exact ACCEPT GREEN -> T0 fresh verify -> T8ar
T8ar exact GREEN -> T0 fresh verify -> T7cd
T7cd -> T0 only
```

Normal dispatch uses `gpt-5.6-sol/high`. T4ac 30 h and T8ar 12 h are soft
notifications only. A confirmed capacity/system interruption may resume the
same task with `gpt-5.6-terra/high` only after process, checkpoints,
implementation identity, artifacts, tests, scope, status, and provenance are
verified safe. Scientific, numerical, nonfinite, test, scope, or provenance
failure cannot be bypassed by switching model.

## 12. Authorized Writes And Stop Rules

- T0: candidate documents, status/T0 handoff/archive, monitor update, and
  exact gated messages after matching package-review GREEN.
- T4ac: its exact five implementation paths, radial-gate artifacts, one gate
  note, status/T4 handoff, and one byte-identical archive.
- T7cc/T7cd: status/T7 handoff and one byte-identical archive per review.
- T8ar: its exact five implementation paths, point-only artifacts,
  status/T8 handoff, and one byte-identical archive.

Any YELLOW, RED, incomplete state, hash drift, nonfinite value, test failure,
scope drift, provenance ambiguity, missing task, or messaging failure stops at
T0. It authorizes no next midpoint, production, plot, fixture, Kirchhoff,
paper-style work, GitHub action, or threshold change.

## 13. Definition Of Done

- the candidate has immutable commit/blob/SHA identity and matching
  independent package-review GREEN;
- T4ac and T7cc establish the exact 41-frequency radial envelope without lmax
  extension or forbidden output;
- T8ar produces exactly 41 atomic pairs and 87/86 artifact cardinality;
- T7cd independently reconstructs exactly 1,472 phase, 1,312 hierarchy, and
  80 summary records and returns one exact decision to T0;
- every stage preserves tests, scope, provenance, stop rules, and non-claims.
