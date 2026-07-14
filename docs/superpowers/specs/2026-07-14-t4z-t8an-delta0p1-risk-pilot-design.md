# T4z–T8an Bounded Delta(kM)=0.1 Risk Pilot Design

Date: 2026-07-14

Status: user-approved design direction; long background execution is allowed,
but the scientific and artifact scope remains bounded.

## 1. Decision

The next Phase-5 slice is a two-gate, nine-frequency risk-directed pilot for
the candidate production spacing `Delta(kM)=0.1`.

The pilot does not complete the 40-frequency production grid. It computes only
new frequencies inside the five review-grid intervals that produced the
largest accepted phase-slope or magnitude-step diagnostics:

```text
kM_pilot = [0.4, 0.8, 0.9, 1.6, 1.7, 2.8, 2.9, 3.8, 3.9]
```

The chain is:

```text
T4z radial/Q018 classification and exact-envelope adapter
  -> T7bv independent radial-gate review
  -> T8an nine-frequency point-only pilot
  -> T7bw independent pilot review
  -> T0 interpretation only
```

No downstream stage starts unless the immediately preceding gate returns its
frozen exact GREEN decision with all required artifacts and fresh checks.

## 2. Why This Pilot

### 2.1 Enabling evidence

T7bu accepted the review-grid diagnostics with the narrow decision:

```text
ACCEPT GREEN / FIG5-FIG6 REVIEW GRID SUPPORTS DELTA KM 0.1 PRODUCTION PILOT
```

The four conservative projected phase steps are below `pi/2`, but the accepted
diagnostics retain a material far-axis `F_cross` magnitude limitation:

```text
max absolute step = 1.7643213800514306
max relative step = 0.8039700767407513
point              = far_axis_x15_z30
coarse interval    = [0.75, 1.0]
```

The accepted 18-frequency run took `7099.062265498002 s` including
checkpointed work. Its per-frequency runtimes range from seconds at low `kM`
to about `1158 s` at `kM=4`. The nine-frequency pilot is therefore expected to
be hours-scale but materially smaller than a full 40-frequency completion.

### 2.2 Critical radial constraint

The current reviewed adapter
`q018_tablei_review_grid_transition` is fail-closed and permits only:

```text
kM in {2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0}
```

It must not be reused or silently broadened for `2.8`, `2.9`, `3.8`, or
`3.9`. A new measured radial/Q018 classification and independent review are
therefore mandatory before the pilot solver stage.

## 3. Alternatives Considered

### A. Selected: nine risk-directed frequencies

Advantages:

- tests the intervals with the strongest accepted warning signals;
- exercises both low/mid-frequency ordinary radial paths and new high-frequency
  Q018 transition envelopes;
- produces actual `0.1`-spaced samples without pretending to complete the
  production grid;
- limits rework if the new data reveal `0.05` spacing is needed locally.

Cost: two independent T7 reviews and a new narrow T4 adapter gate.

### B. Compute every missing point of the 40-frequency grid

Rejected for this slice. Only 11 of the accepted review frequencies lie on the
exact `0.1, 0.2, ..., 4.0` grid, so completing the grid would require 29 new
frequencies, not 22. That is full production rather than a bounded pilot and
would broaden the radial adapter before the risk-directed evidence exists.

### C. Low-frequency-only pilot without a T4 gate

Rejected because it would avoid the highest phase-slope intervals and would
not test the new high-frequency Q018 envelope that dominates scientific and
runtime risk.

## 4. Frozen Physical And Numerical Inputs

The pilot preserves:

- Schwarzschild `M=1`, `G=c=1`;
- Fourier factor `exp(-ikt)`;
- incident direction `+z`;
- `A_plus=0.9+1.1j`, `A_cross=0.4+0.6j`;
- Route-B packaged polarization bridge;
- pointwise amplification
  `F_plus=h_plus_lensed/h_plus_unlensed` and
  `F_cross=h_cross_lensed/h_cross_unlensed`;
- flat/no-lens packaged polarization denominators;
- `r_out=300`, `r_in_eps=1e-6`, `rtol=1e-10`, `atol=1e-12`;
- convergence tolerance `1e-4` for the complex final adjacent `lmax` pair;
- the eight Table-I points at `z/M=30` and
  `x/M=[0,1,2,3,10,15,20,25]`;
- no interpolation, smoothing, fill, mask alteration, or Kirchhoff
  normalization.

Accepted T8aj source triplet:

```text
a54f07a472316c03e55dc2b49d134f0419dd780cf99bd427e9e0ac337b91fccb  NPZ
2145686bc0e72363870eb28bd29d6e2e558102a9c0d61e7e057b9d63b4beb537  JSON
86d77a92a54fcaba31934bc0a57d0b491aed44e2d5becb3e7dcc704bd4ede3bf  manifest
```

These files are immutable reference endpoints. The pilot must not overwrite,
append to, or regenerate them.

## 5. Exact Frequency And lmax Contract

The five targeted coarse intervals and new frequencies are:

| Accepted diagnostic | Coarse interval | New `0.1` points |
|---|---:|---:|
| far `F_plus` phase slope | `[0.3,0.5]` | `0.4` |
| far `F_cross` magnitude step | `[0.75,1.0]` | `0.8,0.9` |
| far `F_cross` phase slope | `[1.5,1.75]` | `1.6,1.7` |
| near `F_cross` phase slope | `[2.75,3.0]` | `2.8,2.9` |
| near `F_plus` phase slope | `[3.75,4.0]` | `3.8,3.9` |

Use the existing seed rule without changing thresholds:

```text
L_seed(kM) = ceil_to_multiple_of_12(max(84, 90*kM))
lmax_values = sorted unique [L_seed-72, L_seed-48, L_seed-24, L_seed]
lmax >= 24
```

The resulting frozen initial windows are:

| `kM` | `lmax_values` | final pair |
|---:|---|---|
| `0.4` | `[24,36,60,84]` | `[60,84]` |
| `0.8` | `[24,36,60,84]` | `[60,84]` |
| `0.9` | `[24,36,60,84]` | `[60,84]` |
| `1.6` | `[72,96,120,144]` | `[120,144]` |
| `1.7` | `[84,108,132,156]` | `[132,156]` |
| `2.8` | `[180,204,228,252]` | `[228,252]` |
| `2.9` | `[192,216,240,264]` | `[240,264]` |
| `3.8` | `[276,300,324,348]` | `[324,348]` |
| `3.9` | `[288,312,336,360]` | `[336,360]` |

One extension by `+24` or `+48` is permitted only when the new modes are
already inside the T7bv-accepted radial/Q018 envelope. Otherwise the run stops
YELLOW and returns to T0/T4.

## 6. Stage 1: T4z Radial/Q018 Gate

### 6.1 Objective

Classify every requested odd/even radial mode for the nine frequencies, eight
Table-I radii, and frozen `lmax` windows. The classification must distinguish:

- default covered;
- structured default fail-closed uncovered;
- structured default solver failure eligible for the experimental oracle;
- unstructured or nonfinite failure.

For every recoverable structured transition record, validate the existing
direct Riccati/log-amplitude oracle independently and record residual,
normalization, boundary, conditioning, and sensitivity evidence.

### 6.2 Adapter boundary

If and only if the measured evidence passes, T4z may add one new exact adapter:

```text
q018_tablei_delta0p1_risk_pilot_transition
```

Its envelope is the exact Cartesian contract:

- Schwarzschild `M=1`;
- only the nine frozen frequencies;
- only the eight exact Table-I radii;
- only odd/even sectors;
- only measured `(kM, ell, point_id)` transition records;
- exact boundary tolerances frozen in Section 4;
- default-covered modes remain on the ordinary production path;
- every out-of-envelope call fails closed with structured metadata.

No general interpolation of transition segments in `kM`, radius, or `ell` is
allowed.

### 6.3 T4z artifacts

Write only under:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/
```

Required records:

```text
classification_manifest.json
oracle_validation.json
resume_preflight.json
checkpoint/kM_<token>.json       # one atomic checkpoint per frequency
manifest.md
```

Checkpoint files are written to a temporary sibling and atomically renamed.
A resume may reuse a checkpoint only when its input contract and all selected
source hashes match exactly.

### 6.4 T4z decision

```text
GREEN / DELTA0P1 RISK-PILOT RADIAL GATE READY
YELLOW / DELTA0P1 RISK-PILOT RADIAL GATE PARTIAL
RED / DELTA0P1 RISK-PILOT RADIAL GATE BLOCKED
```

Only exact GREEN may dispatch T7bv.

## 7. Stage 2: T7bv Independent Radial Review

T7bv independently checks:

1. exact frequency/point/mode/tolerance scope;
2. default-path classification cardinality;
3. every transition record against direct-oracle evidence;
4. adapter exactness and out-of-envelope rejection;
5. default-covered modes never call the adapter;
6. checkpoint provenance and source hashes;
7. focused radial/Q018 tests, Ruff, and full pytest;
8. no Table-I observable pilot artifact exists yet.

Decision:

```text
ACCEPT GREEN / DELTA0P1 RISK-PILOT RADIAL GATE ACCEPTED
ACCEPT YELLOW / DELTA0P1 RISK-PILOT RADIAL EVIDENCE INCOMPLETE
REJECT RED / DELTA0P1 RISK-PILOT RADIAL GATE INVALID
```

Only exact GREEN may dispatch T8an.

## 8. Stage 3: T8an Point-Only Pilot

### 8.1 Computation

Compute the nine frozen frequencies at exactly the eight Table-I points. Use
the T7bv-accepted adapter name, source hashes, and mode envelope. Do not compute
a full x-z grid and do not modify the accepted review-grid artifact.

Each frequency is an independent resumable transaction:

1. validate frozen inputs and code/config hashes;
2. compute all requested `lmax` partial sums;
3. require finite valid plus/cross values at all eight points;
4. check the complex final adjacent pair at tolerance `1e-4`;
5. write a per-frequency NPZ and JSON sidecar atomically;
6. append a hash-only completion record to the checkpoint ledger;
7. begin the next frequency only after the previous record passes.

On resume, a complete frequency is skipped only when its NPZ, sidecar, source
hashes, configuration, adapter identity, and ledger hash all agree. Partial or
mismatched outputs are quarantined and never treated as completed data.

### 8.2 T8an artifacts

Write only under:

```text
runs/phase5/fig5_fig6_delta0p1_risk_pilot/
```

Required layout:

```text
frequencies/kM_<token>.npz
frequencies/kM_<token>.npz.json
checkpoint_ledger.json
risk_pilot_values.npz
risk_pilot_values.npz.json
risk_pilot_sampling_audit.json
manifest.md
```

The aggregate file contains only the nine new frequencies. The sampling audit
may combine them with the immutable accepted T8aj endpoints by hash-verified
read-only reference; it must not create a disguised 40-frequency production
artifact.

### 8.3 Metadata

Record at minimum:

- exact frequency/point ordering and units;
- complex plus/cross values, magnitudes, principal and locally unwrapped
  phases, and separate masks;
- per-frequency `lmax` windows, final pairs, deltas, runtimes, radial cache
  statistics, warnings, and adapter-use counts;
- T4z/T7bv gate artifact hashes;
- selected source/config/code hashes and Git commit/dirty state;
- checkpoint/resume provenance;
- `point_only=true`, `risk_directed_pilot=true`,
  `not_40_frequency_production=true`, `no_kirchhoff=true`,
  `no_interpolation=true`, `no_smoothing=true`, `no_fill=true`,
  `not_fixture=true`, and `not_paper_style=true`.

### 8.4 T8an decision

```text
GREEN / DELTA0P1 NINE-FREQUENCY RISK PILOT GENERATED
YELLOW / DELTA0P1 NINE-FREQUENCY RISK PILOT PARTIAL
RED / DELTA0P1 NINE-FREQUENCY RISK PILOT BLOCKED
```

Only exact GREEN may dispatch T7bw.

## 9. Stage 4: T7bw Pilot Review And Sampling Criteria

T7bw loads the accepted T8aj NPZ and nine pilot frequency files directly,
without calling T8an aggregation or metric helpers. It independently rebuilds
each of the five targeted local frequency sequences.

### 9.1 Phase criterion

For every point and polarization component, every actual adjacent unwrapped
phase step in the targeted sequences must be finite and strictly below
`pi/2`. Adjacent spacings are at most `0.1`; intervals whose accepted endpoint
lies on a quarter step include a conservative `0.05` edge segment.

This replaces the earlier projected slope proxy with observed `0.1` steps. It
is still a sampling diagnostic, not a band-limit theorem.

### 9.2 Magnitude criterion

Use the already frozen scale-normalized step definition:

```text
relative_step(a,b) = |a-b| / max(1, |a|, |b|)
```

Within each targeted coarse interval, require every observed magnitude step at
spacing at most `0.1` to be no larger than that same point/component's accepted
coarse endpoint step, up to absolute comparison tolerance `2e-15`.

This dominance rule is non-arbitrary: refinement must not reveal a larger
local jump than the coarse interval it was selected to resolve. It does not
claim magnitude convergence. T7bw must also report local total variation,
largest step attribution, and any new interior extremum without converting
them into an unstated threshold.

### 9.3 Pilot review decision

```text
ACCEPT GREEN / DELTA0P1 RISK PILOT SUPPORTS FULL GRID DESIGN
ACCEPT YELLOW / DELTA0P1 RISK PILOT REQUIRES TARGETED 0P05 EVIDENCE
REJECT RED / DELTA0P1 RISK PILOT INVALID
```

GREEN requires all radial, source, checkpoint, artifact, finiteness, mask,
convergence, phase, magnitude-dominance, test, and scope checks. It permits
only T0 to design a later full-grid completion; it does not start that work.

YELLOW must name exact intervals, points, components, and proposed `0.05`
frequencies. RED identifies invalid computation, provenance, or scope.

## 10. Runtime, Background Execution, And Recovery

The user explicitly permits a long background task. Runtime is therefore a
soft planning budget rather than a scientific acceptance threshold:

- expected T8an solver time: roughly `1–3 h` from accepted per-frequency data;
- soft T4z alert: `4 h`;
- soft T8an alert: `4 h`;
- no healthy process is killed solely for crossing a soft budget;
- storage target: `<100 MB` for both gates and the pilot combined.

A monitor may observe process liveness, checkpoint growth, artifacts, tests,
and exact decisions. It may recover the same task with `gpt-5.6-terra/high`
only after an explicit model-capacity/system interruption and only when the
scientific/test/scope state remains healthy. It must reuse safe checkpoints
and avoid recomputation.

Scientific, numerical, test, provenance, scope, or nonfinite failures never
qualify for a model switch. They stop the chain and return to T0.

## 11. Authorized Change Boundaries

T4z may change only the radial adapter implementation/tests and its own
gate docs/artifacts/handoff/status named by the implementation plan.

T8an may change only a focused resumable Table-I pilot runner, its CLI/export,
its tests, its own artifacts/handoff/status, and no unrelated solver formula.
It may consume the T7bv-accepted T4z adapter but may not broaden it.

T7bv and T7bw are review-only. They may update only `status.md`, their T7
handoff, and a T7 archive.

All stages preserve unrelated T1/T2/T3/T5/T6 worktree changes. No stage pushes
GitHub; only T0 may perform a milestone sync after an independently accepted
major node.

## 12. Explicit Non-Goals

- No full 40- or 79-frequency production.
- No frequency interpolation or transition-envelope interpolation.
- No full x-z field grid.
- No Kirchhoff regeneration, normalization, correction, or masking.
- No fixture or benchmark promotion.
- No paper-style Fig.5/Fig.6 rendering.
- No `Delta(kM)=0.05` computation in this chain.
- No threshold, convention, Route-B, Q018, or `lmax` relaxation.
- No automatic continuation after T7bw.

## 13. Definition Of Done

- T4z exact radial gate is complete with per-frequency checkpoints.
- T7bv independently accepts the exact adapter envelope.
- T8an produces exactly nine new point-only frequencies with resumable,
  hash-verified provenance and final-pair convergence.
- T7bw independently reconstructs all targeted local sequences and applies
  the frozen observed-phase and magnitude-dominance criteria.
- T0 records and interprets the exact review decision.
- No full production, `0.05` escalation, fixture, or paper-style stage starts.
