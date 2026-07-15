# T0 Current Handoff

Date: 2026-07-15

Thread: T0, project coordination and gate scheduling.

## Current Status

The bounded `Delta(kM)=0.1` risk-pilot chain is closed:

```text
T4z GREEN -> T7bv ACCEPT GREEN -> T8an GREEN -> T7bw REJECT RED
```

T0 exact closeout state:

```text
CLOSE RED / DELTA0P1 RISK-PILOT GATE CLOSED
```

The RED is an artifact-contract failure, not a failure of radial convergence,
finiteness, checkpoint integrity, or phase-step safety. No downstream task is
authorized.

## Completed Work

- T4z measured and independently validated the exact nine-frequency radial/Q018
  envelope; T7bv accepted it.
- T8an generated nine atomic point-only transactions and the aggregate/audit
  package under final contract hash
  `92d650a89431d64d204125b9ff17929099e016ea774fc0914c4db1ad130b07d9`.
- T8an fixed a runner-only point-local cache-domain bug in `47c3d63`; it did
  not change the radial solver, adapter, physics, thresholds, lmax, or boundary
  policy.
- T7bw independently reconstructed the five local sequences and reviewed all
  active transactions, ledger, aggregate, provenance, tests, and scope.
- The old-contract T8an transactions remain quarantined and are excluded from
  all active cardinality and acceptance claims.

## T0 Independent Verification

- T7bw exact decision is:

```text
REJECT RED / DELTA0P1 RISK PILOT INVALID
```

- Commits `c068868^..47c3d63` touch exactly the frozen five T8an
  implementation/test paths.
- Active root hashes match T8an/T7bw:
  - ledger `79d4c0f596650dcfb4d63c7e40758ea4afa82d2fe0e0cd3de5aa088bbbfd5ccd`;
  - aggregate NPZ `2e0a9fee1b6729466affd4c5f7f6e86c96e696e20882c9f4ad52ae3792d82957`;
  - aggregate JSON `2a9aa472e64747047cb28de90912eecf138b28884d87e8b8219e78d99482772f`;
  - sampling audit `461d040a180dfa8e5a743967285e67f8b682f8f67607f1c0c7a5c8ab2399d7bd`;
  - manifest `120ccd8f11e681bc6d2b3054bd7522ef331a282421f7661dd7888c993b052212`.
- Direct inspection confirms `units` is absent from all nine active
  per-frequency JSON sidecars, aggregate JSON, checkpoint ledger, sampling
  audit, manifest, and both inspected NPZ embedded metadata surfaces.
- Frozen design Section 8.3 and T7bw check 3 require explicit units metadata;
  inferable conventions do not satisfy that artifact contract.
- All 224 adjacent unwrapped phase steps are finite and below `pi/2`; the
  maximum is `1.4363184904108022 rad`.
- The frozen magnitude-dominance criterion fails for 38 exact records. Full
  membership and all 51 strict interior extrema are in
  `docs/handoffs/T7_current.md`.
- T7bw fresh checks passed: focused `11 passed`, Ruff clean, full
  `615 passed, 117 skipped, 1 xfailed, 81 subtests passed`; forbidden-output
  query empty.

## Incomplete Work And Blockers

1. The active T8an artifact package lacks explicit units metadata and is
   invalid under the frozen contract.
2. Even after a metadata-only repair and independent re-review, the scientific
   magnitude result requires targeted evidence rather than immediate full-grid
   production.
3. No metadata repair, artifact regeneration, T7 re-review, targeted
   `Delta(kM)=0.05` computation, or full-grid stage is currently authorized.

## Conditional Scientific Evidence

Only after a separately authorized metadata repair and independent GREEN
re-review may a future T0 design consider midpoint evidence at:

```text
kM=[0.35,0.45,0.85,0.95,1.55,1.65,2.85,2.95,3.85,3.95]
```

Existing failures already occur on `[1.7,1.75]`, `[2.75,2.8]`, and
`[3.75,3.8]`; any future design must state how those edge failures and new
midpoints will be interpreted. This list is evidence, not execution
authorization.

## Required Reading For The Next T0 Thread

1. `project.md`
2. `status.md`
3. `docs/handoffs/T7_current.md`
4. `docs/handoffs/T8_current.md`
5. `docs/superpowers/specs/2026-07-14-t4z-t8an-delta0p1-risk-pilot-design.md`
6. `docs/prompts/phase5_t7bw_delta0p1_risk_pilot_review.md`
7. `runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md`
8. The active ledger, nine frequency pairs, aggregate sidecar, and sampling
   audit in that run directory.

## Frozen Decisions

- The exact T7bw RED must not be relabeled YELLOW merely because intended units
  are inferable.
- T8an numerical arrays, ordering, masks, branches, lmax windows, thresholds,
  and physics are not authorized to change during any future metadata repair.
- The 38 magnitude-dominance failures are scientific evidence and must not be
  hidden by interpolation, smoothing, threshold relaxation, point omission,
  or frequency omission.
- Quarantined old-contract transactions are provenance only and must never be
  treated as active outputs.

## Forbidden Actions

- Do not start the full 40/79-frequency grid.
- Do not run the conditional `0.05` midpoint list.
- Do not repair or regenerate T8an artifacts without a separately reviewed
  bounded plan.
- Do not create plots, fixtures, Kirchhoff outputs, or paper-style artifacts.
- Do not modify the radial solver/adapter, physical conventions, thresholds,
  lmax, boundary policy, or accepted T8aj/T4z sources.
- Do not push this RED closeout to GitHub under the completed monitor; that
  monitor explicitly forbids GitHub action.

## Superseded Or Consumed Prompts

The T4z, T7bv, T8an, and T7bw prompts in the frozen chain have been consumed.
They must not be reused to authorize repair, re-review, `0.05`, or full-grid
work.

## Exact Next Task

Stop automatic execution. The next permissible T0 action is to present a
separately bounded metadata-contract repair and independent re-review proposal
to the user. Only after that gate is accepted may T0 design any targeted
`0.05` scientific evidence stage.

Allowed coordination changes for that proposal are documentation only.
Implementation, artifacts, tests, and downstream computations remain frozen
until explicit authorization.

## Definition Of Done For This Closeout

- T7bw exact RED independently verified.
- Missing units confirmed on active metadata surfaces.
- Five-sequence phase and magnitude results recorded without reinterpretation.
- No downstream task dispatched.
- Status and T0 handoff updated.
- Risk-pilot monitor deleted.
