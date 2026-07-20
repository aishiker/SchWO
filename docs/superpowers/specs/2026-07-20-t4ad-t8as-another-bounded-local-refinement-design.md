# T4ad–T8as Another Bounded Local Refinement Design

Date: 2026-07-20
Status: T0 bounded-repair candidate; frozen only after an exact seven-file
local commit. It authorizes no execution until an independent read-only
reviewer returns exact package-review GREEN for that same identity.

## 1. Gate Result And Bounded Objective

Frozen T7cd returned exactly:

```text
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL REFINEMENT REQUIRED
```

The T8ar package is structurally valid. T7cd and a fresh T0 audit independently
reconstructed the same immutable evidence:

- 87 active files and 86 non-self manifest records;
- 41 complete NPZ/JSON transaction pairs;
- 1,472 phase records, with 5 failures of strict `< pi/2`;
- 1,312 literal-parent hierarchy records, with 253 failures of
  `child_relative_step <= parent_relative_step + 2e-15`;
- 80 summaries and 343 strict interior extrema;
- maximum phase step `3.1261517446459153`;
- maximum raw hierarchy excess `0.6461744059845573`.

The 253 hierarchy failures occupy exactly 55 unique literal child intervals.
All five phase-failed intervals are members of that exact 55-interval set.
This repair freezes one midpoint from each failed child once, adds no passing
interval, and performs no runtime, automatic, or recursive selection.

## 2. Selection And Rejected Alternatives

### 2.1 Selected: all 55 unique T7cd failed-child midpoints

This is the smallest batch that advances every observed T7cd hierarchy failure
one separately reviewed literal level. Repeated point/component failures share
one frequency. The five phase failures require no extra interval.

### 2.2 Rejected: phase-only refinement

Sampling only five phase-failed intervals would leave 50 hierarchy-failed
intervals unexamined and cannot test the frozen hierarchy gate.

### 2.3 Rejected: ranked or budgeted subset

Ranking by excess, point, component, sequence, or magnitude would introduce a
new scientific selection threshold and omit observed failure membership.

### 2.4 Rejected: uniform grids and recursive bisection

The exact set contains local contiguous patches because adjacent children
failed, but it does not fill passing intervals and is not a uniform scan. No
runtime midpoint discovery is allowed. Any T7cf failure stops at T0 and would
require a new candidate identity and independent review.

## 3. Immutable Starting Evidence

```text
reviewed candidate commit       f3a64522642abfaa2e0f3933125df06ae76895e4
reviewed candidate parent       fa22f20f775c1b15ae533c03047d156687e5f3bf
T4ac implementation commit      6e86d8b419d8c09af38e226400f7439f7cdfed79
T8ar implementation commit      366a517c71b56026bb0f3ca37c14cc75243985b2
T8ar implementation parent      6e86d8b419d8c09af38e226400f7439f7cdfed79
T8ar generation contract        b9ed45769f1bf61925ac5b59e6ab14b5e31a1aecc858bec076adf0e7e398da56
T8ar metadata contract          949041c7bd7b5ee41409e0a9b19ad73515aeb73674a5f3cd6e7782b4c4385d97
T8ar ledger                     0ba6a6ae8ecd44552af2524e556d99b00977efe4e141ea17a78113cde67d2e4c
T8ar aggregate NPZ              a3ba554efb94d6620c8b267077d0e57f843ad599e40586213f2a2ef8e1fdaf42
T8ar aggregate JSON             1c8f02d8d930f1f51439c15d5f0dad975f4a21567fbdc1dff830f95c84c8f8d2
T8ar sampling audit             1d9a701eb714ebd38fec2a37d7066f2aae188d25e80447e0abbecc717062bb70
T8ar manifest                   1b3003bf59a3989f54ef125484cffaada7913fabab0ab010464c94bd12f5b6e3
T7cd handoff                    99b669d8f7b1000dd9f002c27d1234a286d00690ad82c84f1ebc159ec33bb3fc
pre-T7cd T7cc archive           acfd4e53a8fc63a2e33eb7c5051508e5a1f918e6dcbe3768b1256452a5ff7298
pre-T7cc T7cb archive           57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01
```

T4ac classification/oracle/preflight/manifest roots, classification snapshot
`e675b751fd4beae2446597034b99f847e0cc3528551bfc30f8efd3460ad944fe`,
final-adapter snapshot
`8188b306fea0190654f752190f0ab6e96ef6970b16fea704b9cdb99ca96c7ccc`,
and all earlier T8aj/T8ao/T8ap/T8aq sources remain immutable inputs. The
original seven-file package at commit
`76b57c90d6e54594ca480e1dcf629af685d9098f` and all recorded SHA-256 values
must remain unchanged.

## 4. Unchanged Physical And Numerical Conventions

- Schwarzschild background and `G=c=M=1`;
- both odd/even sectors and every integer `ell=2..ell_max`;
- exact eight Table-I point IDs and ordering;
- unchanged incident direction, polarization, boundary conditions, `r_out`,
  `r_in_eps`, solver tolerances, Q018 policy, and fail-closed rules;
- point-only complex amplification evidence with no interpolation or filling;
- final-pair convergence threshold exactly `1e-4`;
- phase criterion strictly `< pi/2`;
- hierarchy tolerance exactly `+2e-15`.

No lmax extension, threshold relaxation, smoothing, sector merging, new point,
uniform/full grid, production, plot, fixture, Kirchhoff, or paper-style output
is allowed.

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
| `0.86875` | `0p86875` | `[24,36,60,84]` | 1328 |
| `0.94375` | `0p94375` | `[24,48,72,96]` | 1520 |
| `0.95625` | `0p95625` | `[24,48,72,96]` | 1520 |
| `0.96875` | `0p96875` | `[24,48,72,96]` | 1520 |
| `1.54375` | `1p54375` | `[72,96,120,144]` | 2288 |
| `1.56875` | `1p56875` | `[72,96,120,144]` | 2288 |
| `1.58125` | `1p58125` | `[72,96,120,144]` | 2288 |
| `1.59375` | `1p59375` | `[72,96,120,144]` | 2288 |
| `1.63125` | `1p63125` | `[84,108,132,156]` | 2480 |
| `1.65625` | `1p65625` | `[84,108,132,156]` | 2480 |
| `1.69375` | `1p69375` | `[84,108,132,156]` | 2480 |
| `1.703125` | `1p703125` | `[84,108,132,156]` | 2480 |
| `1.715625` | `1p715625` | `[84,108,132,156]` | 2480 |
| `2.778125` | `2p778125` | `[180,204,228,252]` | 4016 |
| `2.784375` | `2p784375` | `[180,204,228,252]` | 4016 |
| `2.80625` | `2p80625` | `[192,216,240,264]` | 4208 |
| `2.81875` | `2p81875` | `[192,216,240,264]` | 4208 |
| `2.83125` | `2p83125` | `[192,216,240,264]` | 4208 |
| `2.84375` | `2p84375` | `[192,216,240,264]` | 4208 |
| `2.85625` | `2p85625` | `[192,216,240,264]` | 4208 |
| `2.86875` | `2p86875` | `[192,216,240,264]` | 4208 |
| `2.88125` | `2p88125` | `[192,216,240,264]` | 4208 |
| `2.89375` | `2p89375` | `[192,216,240,264]` | 4208 |
| `2.90625` | `2p90625` | `[192,216,240,264]` | 4208 |
| `2.91875` | `2p91875` | `[192,216,240,264]` | 4208 |
| `2.93125` | `2p93125` | `[192,216,240,264]` | 4208 |
| `2.94375` | `2p94375` | `[204,228,252,276]` | 4400 |
| `2.95625` | `2p95625` | `[204,228,252,276]` | 4400 |
| `2.96875` | `2p96875` | `[204,228,252,276]` | 4400 |
| `2.98125` | `2p98125` | `[204,228,252,276]` | 4400 |
| `2.99375` | `2p99375` | `[204,228,252,276]` | 4400 |
| `3.753125` | `3p753125` | `[276,300,324,348]` | 5552 |
| `3.759375` | `3p759375` | `[276,300,324,348]` | 5552 |
| `3.765625` | `3p765625` | `[276,300,324,348]` | 5552 |
| `3.771875` | `3p771875` | `[276,300,324,348]` | 5552 |
| `3.778125` | `3p778125` | `[276,300,324,348]` | 5552 |
| `3.784375` | `3p784375` | `[276,300,324,348]` | 5552 |
| `3.790625` | `3p790625` | `[276,300,324,348]` | 5552 |
| `3.796875` | `3p796875` | `[276,300,324,348]` | 5552 |
| `3.80625` | `3p80625` | `[276,300,324,348]` | 5552 |
| `3.81875` | `3p81875` | `[276,300,324,348]` | 5552 |
| `3.83125` | `3p83125` | `[276,300,324,348]` | 5552 |
| `3.84375` | `3p84375` | `[276,300,324,348]` | 5552 |
| `3.85625` | `3p85625` | `[276,300,324,348]` | 5552 |
| `3.86875` | `3p86875` | `[288,312,336,360]` | 5744 |
| `3.88125` | `3p88125` | `[288,312,336,360]` | 5744 |
| `3.89375` | `3p89375` | `[288,312,336,360]` | 5744 |
| `3.90625` | `3p90625` | `[288,312,336,360]` | 5744 |
| `3.91875` | `3p91875` | `[288,312,336,360]` | 5744 |
| `3.93125` | `3p93125` | `[288,312,336,360]` | 5744 |
| `3.94375` | `3p94375` | `[288,312,336,360]` | 5744 |
| `3.95625` | `3p95625` | `[288,312,336,360]` | 5744 |
| `3.96875` | `3p96875` | `[288,312,336,360]` | 5744 |
| `3.98125` | `3p98125` | `[288,312,336,360]` | 5744 |
| `3.99375` | `3p99375` | `[288,312,336,360]` | 5744 |

Exact radial contract:

```text
55 frequencies
239,120 classification records
55 atomic frequency checkpoints
maximum lmax = 360
```

Transition cardinality is measured, never predicted.

## 6. Five Literal Sequences And 55-Row Parent Map

T7cf uses only the following literal sequences:

```text
[0.3,0.3125,0.325,0.3375,0.35,0.3625,0.375,0.3875,0.4,0.45,0.5]

[0.75,0.8,0.825,0.85,0.8625,0.86875,0.875,0.9,0.9125,0.925,
 0.9375,0.94375,0.95,0.95625,0.9625,0.96875,0.975,0.9875,1.0]

[1.5,1.5125,1.525,1.5375,1.54375,1.55,1.5625,1.56875,1.575,
 1.58125,1.5875,1.59375,1.6,1.6125,1.625,1.63125,1.6375,1.65,
 1.65625,1.6625,1.675,1.6875,1.69375,1.7,1.703125,1.70625,
 1.7125,1.715625,1.71875,1.725,1.7375,1.75]

[2.75,2.7625,2.775,2.778125,2.78125,2.784375,2.7875,2.79375,2.8,
 2.80625,2.8125,2.81875,2.825,2.83125,2.8375,2.84375,2.85,
 2.85625,2.8625,2.86875,2.875,2.88125,2.8875,2.89375,2.9,
 2.90625,2.9125,2.91875,2.925,2.93125,2.9375,2.94375,2.95,
 2.95625,2.9625,2.96875,2.975,2.98125,2.9875,2.99375,3.0]

[3.75,3.753125,3.75625,3.759375,3.7625,3.765625,3.76875,3.771875,
 3.775,3.778125,3.78125,3.784375,3.7875,3.790625,3.79375,
 3.796875,3.8,3.80625,3.8125,3.81875,3.825,3.83125,3.8375,
 3.84375,3.85,3.85625,3.8625,3.86875,3.875,3.88125,3.8875,
 3.89375,3.9,3.90625,3.9125,3.91875,3.925,3.93125,3.9375,
 3.94375,3.95,3.95625,3.9625,3.96875,3.975,3.98125,3.9875,
 3.99375,4.0]
```

The exact cardinalities are:

```text
147 adjacent intervals * 8 points * 2 components = 2,352 phase records
55 parents * 2 children * 8 points * 2 components = 1,760 hierarchy records
5 sequences * 8 points * 2 components = 80 summaries
55 NPZ + 55 JSON + 5 roots = 115 active files
114 non-self manifest records
```

The parent map is literal and must not be inferred from floating adjacency:

| midpoint | exact T7cd failed child parent | new child 1 | new child 2 |
|---:|---|---|---|
| `0.86875` | `[0.8625,0.875]` | `[0.8625,0.86875]` | `[0.86875,0.875]` |
| `0.94375` | `[0.9375,0.95]` | `[0.9375,0.94375]` | `[0.94375,0.95]` |
| `0.95625` | `[0.95,0.9625]` | `[0.95,0.95625]` | `[0.95625,0.9625]` |
| `0.96875` | `[0.9625,0.975]` | `[0.9625,0.96875]` | `[0.96875,0.975]` |
| `1.54375` | `[1.5375,1.55]` | `[1.5375,1.54375]` | `[1.54375,1.55]` |
| `1.56875` | `[1.5625,1.575]` | `[1.5625,1.56875]` | `[1.56875,1.575]` |
| `1.58125` | `[1.575,1.5875]` | `[1.575,1.58125]` | `[1.58125,1.5875]` |
| `1.59375` | `[1.5875,1.6]` | `[1.5875,1.59375]` | `[1.59375,1.6]` |
| `1.63125` | `[1.625,1.6375]` | `[1.625,1.63125]` | `[1.63125,1.6375]` |
| `1.65625` | `[1.65,1.6625]` | `[1.65,1.65625]` | `[1.65625,1.6625]` |
| `1.69375` | `[1.6875,1.7]` | `[1.6875,1.69375]` | `[1.69375,1.7]` |
| `1.703125` | `[1.7,1.70625]` | `[1.7,1.703125]` | `[1.703125,1.70625]` |
| `1.715625` | `[1.7125,1.71875]` | `[1.7125,1.715625]` | `[1.715625,1.71875]` |
| `2.778125` | `[2.775,2.78125]` | `[2.775,2.778125]` | `[2.778125,2.78125]` |
| `2.784375` | `[2.78125,2.7875]` | `[2.78125,2.784375]` | `[2.784375,2.7875]` |
| `2.80625` | `[2.8,2.8125]` | `[2.8,2.80625]` | `[2.80625,2.8125]` |
| `2.81875` | `[2.8125,2.825]` | `[2.8125,2.81875]` | `[2.81875,2.825]` |
| `2.83125` | `[2.825,2.8375]` | `[2.825,2.83125]` | `[2.83125,2.8375]` |
| `2.84375` | `[2.8375,2.85]` | `[2.8375,2.84375]` | `[2.84375,2.85]` |
| `2.85625` | `[2.85,2.8625]` | `[2.85,2.85625]` | `[2.85625,2.8625]` |
| `2.86875` | `[2.8625,2.875]` | `[2.8625,2.86875]` | `[2.86875,2.875]` |
| `2.88125` | `[2.875,2.8875]` | `[2.875,2.88125]` | `[2.88125,2.8875]` |
| `2.89375` | `[2.8875,2.9]` | `[2.8875,2.89375]` | `[2.89375,2.9]` |
| `2.90625` | `[2.9,2.9125]` | `[2.9,2.90625]` | `[2.90625,2.9125]` |
| `2.91875` | `[2.9125,2.925]` | `[2.9125,2.91875]` | `[2.91875,2.925]` |
| `2.93125` | `[2.925,2.9375]` | `[2.925,2.93125]` | `[2.93125,2.9375]` |
| `2.94375` | `[2.9375,2.95]` | `[2.9375,2.94375]` | `[2.94375,2.95]` |
| `2.95625` | `[2.95,2.9625]` | `[2.95,2.95625]` | `[2.95625,2.9625]` |
| `2.96875` | `[2.9625,2.975]` | `[2.9625,2.96875]` | `[2.96875,2.975]` |
| `2.98125` | `[2.975,2.9875]` | `[2.975,2.98125]` | `[2.98125,2.9875]` |
| `2.99375` | `[2.9875,3.0]` | `[2.9875,2.99375]` | `[2.99375,3.0]` |
| `3.753125` | `[3.75,3.75625]` | `[3.75,3.753125]` | `[3.753125,3.75625]` |
| `3.759375` | `[3.75625,3.7625]` | `[3.75625,3.759375]` | `[3.759375,3.7625]` |
| `3.765625` | `[3.7625,3.76875]` | `[3.7625,3.765625]` | `[3.765625,3.76875]` |
| `3.771875` | `[3.76875,3.775]` | `[3.76875,3.771875]` | `[3.771875,3.775]` |
| `3.778125` | `[3.775,3.78125]` | `[3.775,3.778125]` | `[3.778125,3.78125]` |
| `3.784375` | `[3.78125,3.7875]` | `[3.78125,3.784375]` | `[3.784375,3.7875]` |
| `3.790625` | `[3.7875,3.79375]` | `[3.7875,3.790625]` | `[3.790625,3.79375]` |
| `3.796875` | `[3.79375,3.8]` | `[3.79375,3.796875]` | `[3.796875,3.8]` |
| `3.80625` | `[3.8,3.8125]` | `[3.8,3.80625]` | `[3.80625,3.8125]` |
| `3.81875` | `[3.8125,3.825]` | `[3.8125,3.81875]` | `[3.81875,3.825]` |
| `3.83125` | `[3.825,3.8375]` | `[3.825,3.83125]` | `[3.83125,3.8375]` |
| `3.84375` | `[3.8375,3.85]` | `[3.8375,3.84375]` | `[3.84375,3.85]` |
| `3.85625` | `[3.85,3.8625]` | `[3.85,3.85625]` | `[3.85625,3.8625]` |
| `3.86875` | `[3.8625,3.875]` | `[3.8625,3.86875]` | `[3.86875,3.875]` |
| `3.88125` | `[3.875,3.8875]` | `[3.875,3.88125]` | `[3.88125,3.8875]` |
| `3.89375` | `[3.8875,3.9]` | `[3.8875,3.89375]` | `[3.89375,3.9]` |
| `3.90625` | `[3.9,3.9125]` | `[3.9,3.90625]` | `[3.90625,3.9125]` |
| `3.91875` | `[3.9125,3.925]` | `[3.9125,3.91875]` | `[3.91875,3.925]` |
| `3.93125` | `[3.925,3.9375]` | `[3.925,3.93125]` | `[3.93125,3.9375]` |
| `3.94375` | `[3.9375,3.95]` | `[3.9375,3.94375]` | `[3.94375,3.95]` |
| `3.95625` | `[3.95,3.9625]` | `[3.95,3.95625]` | `[3.95625,3.9625]` |
| `3.96875` | `[3.9625,3.975]` | `[3.9625,3.96875]` | `[3.96875,3.975]` |
| `3.98125` | `[3.975,3.9875]` | `[3.975,3.98125]` | `[3.98125,3.9875]` |
| `3.99375` | `[3.9875,4.0]` | `[3.9875,3.99375]` | `[3.99375,4.0]` |

Every new child is compared only to its exact immutable T7cd failed-child
parent step for the same sequence, point, and component.

## 7. Gated Chain

Only the existing tasks may be used:

```text
T4 = 019f5fa6-1288-7c01-8a87-4c4370cf5517
T7 = 019f5ed1-b421-7ec2-9bac-8d134855a1ed
T8 = 019f5ece-f578-7b91-8f61-df882c656591
```

```text
matching package-review GREEN -> T0 fresh verify -> T4ad
T4ad exact GREEN -> T7ce
T7ce exact ACCEPT GREEN -> T0 fresh verify -> T8as
T8as exact GREEN -> T0 fresh verify -> T7cf
T7cf -> T0 only
```

Normal dispatch uses `gpt-5.6-sol/high`. Confirmed capacity/system interruption
may resume the same task with `gpt-5.6-terra/high` only after exact safe
checkpoint/transaction and implementation identity verification. Model changes
never bypass scientific, numerical, nonfinite, test, scope, or provenance
failure.

## 8. T4ad Radial Gate

T4ad changes exactly five implementation/test paths in one pre-compute commit:

```text
scripts/phase5_another_bounded_local_radial_gate.py
src/schwgw/numerics/q018_tablei_another_bounded_local_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

The opt-in adapter label is `q018_tablei_another_bounded_local_transition`.
T4ad freezes pre-adapter classification and final-adapter snapshots, measures
transition membership, direct-oracles every measured transition, validates
anchors/sensitivity, and writes exactly 55 complete/PASS checkpoints plus
classification/oracle/preflight/manifest roots under
`runs/phase5/fig5_fig6_another_bounded_local_radial_gate/`.

Exact decisions:

```text
GREEN / ANOTHER BOUNDED LOCAL RADIAL GATE READY
YELLOW / ANOTHER BOUNDED LOCAL RADIAL EVIDENCE INCOMPLETE
RED / ANOTHER BOUNDED LOCAL RADIAL GATE INVALID
```

## 9. T7ce Independent Radial Review

T7ce is read-only apart from its three review records. It archives the exact
pre-review T7cd handoff and requires SHA-256
`99b669d8f7b1000dd9f002c27d1234a286d00690ad82c84f1ebc159ec33bb3fc`.
It independently verifies the 253-to-55 derivation, five phase-failure
inclusion, 239,120 classification keys, 55 checkpoint groups, both snapshots,
direct oracle, literal envelope, strict adapter behavior, exact commit scope,
tests, provenance, and forbidden-output isolation.

Exact decisions:

```text
ACCEPT GREEN / ANOTHER BOUNDED LOCAL RADIAL GATE ACCEPTED
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL RADIAL EVIDENCE INCOMPLETE
REJECT RED / ANOTHER BOUNDED LOCAL RADIAL GATE INVALID
```

## 10. T8as Point-Only Evidence

After T0 fresh verification, T8as creates one exact five-path implementation
commit:

```text
scripts/phase5_run_another_bounded_local_refinement.py
src/schwgw/io/__init__.py
src/schwgw/io/tablei_another_bounded_local_refinement.py
tests/unit/test_tablei_another_bounded_local_refinement.py
tests/regression/test_another_bounded_local_refinement_script.py
```

It then creates exactly 55 atomic NPZ/JSON pairs plus ledger, aggregate NPZ,
aggregate JSON, diagnostic audit, and manifest under
`runs/phase5/fig5_fig6_another_bounded_local_refinement/`. The schema is
`phase5_t8as_another_bounded_local_refinement_v1_units_dtype_ordering`.
Resume may reuse only complete transactions with exact matching scientific,
implementation, source, gate, and contract identity and must never recompute a
complete matching frequency.

The audit records exactly 2,352 phase, 1,760 hierarchy, and 80 summary records,
but sets `diagnostic_only=true` and `acceptance_decision_emitted=false`. T8as
emits no scientific judgment or next midpoint.

Exact decisions:

```text
GREEN / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE GENERATED
YELLOW / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE INCOMPLETE
RED / ANOTHER BOUNDED LOCAL FREQUENCY ARTIFACT INVALID
```

## 11. T7cf Independent Scientific Review

T7cf directly loads all 55 pairs and immutable predecessor rows without using
T8as loader/aggregation/sampling/acceptance helpers. Artifact, contract,
source, test, scope, or provenance failure is RED.

For every one of the 2,352 records:

```text
phase = np.unwrap(np.angle(F), axis=frequency)
abs(diff(phase)) < pi/2
```

For every one of the 1,760 hierarchy records, with nonnegative magnitudes
`a=|F(k_i)|` and `b=|F(k_j)|`:

```text
relative_step(a,b) = abs(a-b) / max(1,a,b)
new_child_step <= exact_T7cd_failed_child_parent_step + 2e-15
```

T7cf reports every failure, all 80 summaries, total variation, cancellation,
largest steps, strict extrema, and diagnostic-only midpoints. It invents no
threshold and authorizes nothing.

Exact decisions:

```text
ACCEPT GREEN / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL REFINEMENT REQUIRED
REJECT RED / ANOTHER BOUNDED LOCAL FREQUENCY ARTIFACT INVALID
```

## 12. Authorized Writes And Stop Rules

- T0: this seven-file candidate package, status/T0 handoff/archive, monitor
  update, and exact gated messages after matching package-review GREEN.
- T4ad: exact five implementation paths, its radial-gate artifacts, one gate
  note, status/T4 handoff, and one byte-identical archive.
- T7ce/T7cf: status/T7 handoff and one byte-identical archive per review.
- T8as: exact five implementation paths, point-only artifacts, status/T8
  handoff, and one byte-identical archive.

Any YELLOW, RED, incomplete state, hash drift, nonfinite value, test failure,
scope drift, provenance ambiguity, missing task, or messaging failure stops at
T0. No stage authorizes threshold relaxation, lmax extension,
automatic/recursive midpoint, uniform/full grid, production, plot, fixture,
Kirchhoff, paper-style output, task creation/replacement, or GitHub action.

## 13. Definition Of Done

- candidate has an exact seven-file commit/blob/SHA identity and matching
  independent package-review GREEN;
- T4ad/T7ce establish the exact 55-frequency radial gate without lmax
  extension or forbidden output;
- T8as produces exactly 55 pairs and the 115/114 package;
- T7cf independently reconstructs exactly 2,352 phase, 1,760 hierarchy, and 80
  summary records and returns one exact decision only to T0;
- every stage preserves immutable sources, tests, provenance, scope, and all
  non-claims.
