# Phase 6 V1 production finite-radius radial-state gate

## Purpose and claim boundary

This gate closes the explicit `40M` boundary left by the generic conditioning
scan: it requests the radial master-field state at all eight finite radii used
by the completed Fig.5/6 production schedule.  It does **not** rerun or render
either paper figure, and Li-figure similarity is not an acceptance input.

The output is sector-resolved Regge--Wheeler/Zerilli radial state evidence.  It
is not an observer-qualified tidal response, detector response, reconstructed
metric, polarization observable, or infinity waveform.  Observer, tetrad,
polarization-basis, and absolute-phase convention axes therefore remain
`NOT_ASSESSED` or `PARTIAL`; none is represented by a false zero uncertainty.
No global `GREEN` or global `PASS` is permitted.

## Frozen production inventory

The loader accepts only the following immutable contracts and exact bytes.

| Input | Cardinality | SHA-256 |
| --- | ---: | --- |
| `D_prod.jsonl` | 16,048 keys | `54f13ea2473fb0a04ca5e16277edae31335c03b11753973d83a934cce2f0872b` |
| `domain_contract.json` | 40 production frequencies | `7ed99b905c3a1301d96101f357ab1fd9f4bc6e9a4922cb242d28e7cf06bb3bcf` |
| domain `manifest.json` | — | `f11d127e0bcfafa8f2fe24b2d3cec3e0cedc60f644d4285e6d52e53d8358d2d2` |
| `shard_inventory.jsonl` | 86 union shards | `b652ceb41d0dfa3c25f10d246e98bc707721faf4d83b049b3410dc4ca0b4efff` |
| `execution_contract.json` | — | `25ad4b4e723edbd44651edaa63df415141de504b85288b12c2a6a973fcb420ab` |
| execution `manifest.json` | — | `1de9d445d888cbb5ddbf426cc062d2fb5128cad111437ce7d147df6e004aed48` |
| Table-I coordinate NPZ | 8 sites | `76b0a3d3d3ffd44def8466e18ddcba4fe097d899e12980f988cc0e038cfef6a9` |

The number of production shards is **80**, not 86.  The 86-shard inventory is
the partition of `D_union`; its six `kM=0.01,0.05,8` sector shards are audit
extensions and are excluded here.  Filtering the immutable inventory to
`production_key_count>0` gives exactly `40 frequencies x 2 sectors = 80`
shards whose ordered union is byte-for-byte `D_prod`.

The exact Cartesian sites and independently rederived radii are:

| point | `x/M` | `y/M` | `z/M` | `r/M` |
| --- | ---: | ---: | ---: | --- |
| near-axis 0 | 0 | 0 | 30 | `30.0` |
| near-axis 1 | 1 | 0 | 30 | `30.0166620396072687634498509711014787920017888861306464075391` |
| near-axis 2 | 2 | 0 | 30 | `30.0665927567458165417578611261987112104121165748193474015466` |
| near-axis 3 | 3 | 0 | 30 | `30.1496268633626708106577947382787285608350704100791318717185` |
| far-axis 10 | 10 | 0 | 30 | `31.6227766016837933199889354443271853371955513932521682685750` |
| far-axis 15 | 15 | 0 | 30 | `33.5410196624968454461376050309691435316092753941728858640635` |
| far-axis 20 | 20 | 0 | 30 | `36.0555127546398929311922126747049594625129657384524621271045` |
| far-axis 25 | 25 | 0 | 30 | `39.0512483795332719706486136787955070678415256832428165008862` |

The radii are recomputed at 60-decimal working precision from the source
Cartesian arrays, then checked against the execution contract and the stored
float64 `point_r` array.  They are not copied from a rendered figure.

## One-call generic backend rule

Every supported production key receives exactly one
`ConditionedRadialRequest`:

- `required_radius` is the minimum site radius, `30M`;
- `evaluation_radii` are the remaining seven increasing radii;
- `r_in-2M = 10^-6 M`, `rtol=10^-10`, `atol=10^-12`;
- `jost_1_over_r`, order 160, exact column-scaled `2x2` solve;
- `r_out` is selected by the already frozen generic conditioning policy.

The generic selector uses turning-proxy, potential, asymptotic-margin,
segment-count, scaled-Jost-condition, and relative-determinant gates over
`r_out/M=(300,600,1200,2400,4800,9600,19200)`.  A key with no supported node
makes zero radial calls and fails closed.  There is no retry and no
paper-specific radius/frequency envelope.  Because the shared selector's
generic reference state is `40M`, this gate also recomputes the outer-segment
count from the actual `30M` start and reapplies the same 4,096-segment cap
before calling the solver.

The new production module imports neither the legacy oracle isolation package
nor `radial_solver.py`.  Runtime provenance rejects legacy, NP/Newman--Penrose,
and pseudoinverse flags or method text.  Historical “Q018” coverage is proved
by scanning the strict superset `D_prod`: every mode used by the old Q018 path
is included without consulting or reproducing a paper-specific classifier.

## Per-mode evidence and uncertainty budgets

A successful mode payload retains:

- all eight complex `psi` and `dpsi/dr` values;
- log-amplitude and phase for both components at every radius, including
  durable `LOG_SCALED_UNDERFLOW` states;
- unit-incoming `A_in`, `A_out`, `S=-A_out/(-1)^ell`, and horizon transmission;
- reflection, horizon-transmission, balance, and flux residual;
- raw generic backend and outer-selection diagnostics;
- exact request, site, policy, key, source, and provenance identities.

Flux may be a local numerical `PASS` when its residual is at most `10^-6`.
The eight-radius state and radial S-matrix remain `PARTIAL` because this gate
has only one float64 configuration per mode.  The `r_in`, `r_out`, Jost-order,
ODE-tolerance, independent-backend, and observer/convention differences remain
finite unassessed sentinels.  A failed solve, unsupported outer node, malformed
state inventory, prohibited provenance, or excessive flux residual makes the
mode `FAIL`; any mode `FAIL` makes its shard and the full campaign `FAIL`.

Thus a clean full campaign is still `PARTIAL`, never `PASS` or `GREEN`.

## Immutable shard publication and strict resume

Each invocation selects one frozen `kM;sector` shard.  The output root must be
a fresh absolute direct path.  Canonical JSON is written to an O_EXCL staging
file, fsynced, hardlinked exclusively to its final name, changed to mode 0444,
and reloaded.  The terminal root is mode 0555.  Existing files and roots are
never replaced.

Each mode has an immutable payload and terminal.  The shard result embeds:

- `scientific_evidence=true`, `science_executed=true`,
  `kernel_unit_test_only=false`, `contract_only=false` for formal runs;
- `acceptance` and `overall_state` restricted to `PARTIAL` or `FAIL`;
- implementation-source SHA-256s;
- every raw terminal identity;
- separate numerical/convention budgets and every failure reason.

Injected tests carry the inverse non-scientific flags and are rejected by the
campaign validator.  Resume accepts only a direct immutable predecessor with
the exact scientific context.  The general Phase-6 rule requires an exact
all-`PASS` predecessor for reuse.  Because this single-configuration V1 gate
intentionally emits only `PARTIAL` or `FAIL`, such predecessors are blocked
without recomputation; a fresh root is required for a deliberate rerun.

Before sealing, the runner rehashes every implementation source and reloads
all frozen inputs.  Temporal source/input drift fails the root closed.

## Full 80-shard campaign proof

The campaign publisher performs no numerical solve.  It accepts exactly 80
unique immutable formal roots and independently verifies:

- the exact canonical 80-shard ID set;
- ordered union equality with all 16,048 `D_prod` keys;
- 16,048 terminals and payload identities;
- up to 128,384 (`16,048 x 8`) radial-state records, with missing records
  explicitly counted and forcing `FAIL`;
- identical implementation-source hashes and identities across all shards;
- root/file modes, hardlink counts, manifests, raw terminal ledgers, budgets,
  statuses, and failure reasons.

The campaign result embeds all 16,048 raw terminal identities and all 80 shard
result identities.  Any hidden mode failure, fake root, missing shard, missing
state, source mismatch, or identity/permission mismatch is rejected or forces
campaign `FAIL`.  The release qualification remains radial-state-only and
forbids global green.

### Superseded representative root

The sealed representative root
`runs/phase6/radial_validation/v1_production_finite_radius_k0p5_odd_v1_20260808_py314`
is retained as consumed diagnostic evidence but is campaign-incompatible: its
runner omitted `payload_identity` from the shard-level failure ledger while the
campaign validator required that identity.  It must not be used as a resume
source or as one of the 80 campaign roots.  The fresh replacement root is
`runs/phase6/radial_validation/v1_production_finite_radius_k0p5_odd_v2_20260808_py314`.

## Invocation after explicit numerical approval

One shard:

```bash
/opt/homebrew/bin/python3.14 \
  scripts/phase6_run_production_finite_radius_shard.py \
  --output-root /absolute/fresh/shard/root \
  --shard-id 'kM=2;sector=odd'
```

After all 80 formal roots exist, repeat `--shard-root` exactly 80 times:

```bash
/opt/homebrew/bin/python3.14 \
  scripts/phase6_publish_production_finite_radius_campaign.py \
  --output-root /absolute/fresh/campaign/root \
  --shard-root /absolute/shard/root/one \
  --shard-root /absolute/shard/root/two
```

There is intentionally no all-shards numerical entry point.  This
implementation task does not execute a production shard, publish a formal
evidence root, run the campaign publisher, or rerun a paper figure.

## Execution-size estimate (not an acceptance result)

The exact upper plan is 16,048 solver calls: one for every `D_prod` key.  A
mode rejected by generic outer preflight makes zero calls, so the realized
count can only be smaller.  As of this implementation review, 71 already
sealed generic-conditioning shards contained 8,559 supported baselines among
11,965 keys (about 71.5%).  That is an observational sizing sample, not a
promise about the remaining production shards; a rough extrapolation is about
11,500 realized calls.

Those existing baseline diagnostics have mean/median runtime about
`0.546/0.539 s` per supported call and a 90th percentile about `0.706 s`.
The present gate starts at `30M` instead of `40M`, retains eight checkpoints,
and publishes more metadata, so a conservative planning range is roughly
2--3 serial compute hours plus immutable-file overhead.  Safe shard-level
parallelism can reduce wall time, but the estimate must be revised from actual
early-shard timing before scheduling all 80 roots.
