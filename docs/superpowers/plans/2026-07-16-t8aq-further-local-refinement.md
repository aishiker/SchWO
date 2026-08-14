# T8aq Further-Local Frequency Refinement Implementation Plan

Date: 2026-07-16

## Goal

Generate a point-only, resumable artifact for exactly 24 further-local
frequencies, then record all data required for independent T7cb reconstruction
of 816 phase records and 768 hierarchical magnitude records.

This is executable only after T7ca accepts T4ab and T0 dispatches it. It is
not a full grid, uniform scan, or recursive refinement.

## Frozen Inputs

```text
frequencies = [
  0.325,0.375,0.825,0.875,0.925,0.975,
  1.525,1.575,1.625,1.675,1.7125,1.7375,
  2.7625,2.7875,2.825,2.875,2.925,2.975,
  3.7625,3.7875,3.825,3.875,3.925,3.975,
]
points = exact eight TABLEI_POINTS
M = 1
A_plus = 0.9+1.1j
A_cross = 0.4+0.6j
incident_direction = +z
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
convergence_tolerance = 1e-4
adapter = q018_tablei_further_local_transition
```

Use exact tokens, lmax windows, five sequences, and 24-row literal parent map
from the design. No lmax extension is authorized. A final-pair failure stops
YELLOW before aggregation.

Immutable sources are the exact accepted T8aj triplet, T8ao/T7bx roots,
T4aa/T7by gate, T8ap package, archived T7bz evidence, and future T4ab/T7ca
gate roots/snapshots supplied by T0 after exact GREEN. Paths and hashes form
one identity; never repair or substitute an input.

## Frozen File Map

The implementation commit paths are exactly:

```text
src/schwgw/io/tablei_further_local_refinement.py
src/schwgw/io/__init__.py
scripts/phase5_run_further_local_refinement.py
tests/unit/test_tablei_further_local_refinement.py
tests/regression/test_further_local_refinement_script.py
```

Additional writes are limited to:

```text
runs/phase5/fig5_fig6_further_local_refinement/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-16_pre_t8aq_further_local_refinement.md
```

## Task 1 — Start Gate And TDD RED

- [ ] Require exact T7ca decision
      `ACCEPT GREEN / FURTHER LOCAL RADIAL GATE ACCEPTED` and fresh T0
      dispatch. Verify all T4ab gate hashes, snapshots, adapter/code blobs,
      and 24 PASS checkpoints.
- [ ] Freshly verify all T8aj/T8ao/T8ap/T7bz inputs, contracts, cardinalities,
      units, dtypes, ordering, masks, and no-active-temp state.
- [ ] Test all 24 tokens, lmax windows, eight-point order, schema, adapter,
      literal parent map, source/gate hashes, and `53/52` cardinality.
- [ ] Prove the absent module/runner yields the expected TDD RED before
      implementation. Diagnose unrelated failures first.

## Task 2 — Contracts, Schema And Atomic Transactions

- [ ] Implement focused `tablei_further_local_refinement.py`; do not modify
      or migrate accepted T8ap modules/artifacts.
- [ ] Build a canonical generation contract over frequencies/tokens, lmax,
      points, physics/numerics, amplitudes, adapter, source/gate hashes,
      selected code/Git identity, convergence, cache, resume, and fail-closed
      rules.
- [ ] Build a separate metadata contract for exact schema
      `phase5_t8aq_further_local_refinement_v1_units_dtype_ordering`, units,
      dtypes, ordering, no-production/no-interpolation flags, generation hash,
      source/gate hashes, and array fingerprints.
- [ ] Put all required metadata on every embedded object, sidecar, ledger,
      aggregate, audit, and manifest surface; nothing may be inferred.
- [ ] Use sibling-temporary atomic NPZ/JSON writes and atomic ledger
      replacement. Complete means pair, hashes, contracts, adapter, lmax,
      source/gate identity, and ledger all agree.
- [ ] Quarantine partial/mismatched pairs and exclude quarantine from active
      cardinality.

## Task 3 — Fake Compute, Cache, And Pre-Run Commit

- [ ] Exercise behavior through injected fake compute only; do not write a
      real transaction in this task.
- [ ] Use a frequency-local cache keyed by sector, ell, k, background,
      boundary/tolerances, and adapter; retain complete certified radius
      domains and preserve disjoint local solutions.
- [ ] Process points in decreasing radius and reuse only when the certified
      interval contains the requested point.
- [ ] Compute Route-B lensed plus/cross and flat/no-lens denominators; save
      independent complex ratios, masks, and histories at all frozen lmax.
- [ ] Require finite values, true masks, and final adjacent complex-pair
      relative delta `<=1e-4` for every point/component.
- [ ] Complete all five paths and fake-compute tests, run focused tests and
      Ruff, then create one scoped commit containing exactly the five paths
      before the first real frequency. Bind its commit and blobs into the
      generation contract.

## Task 4 — Resume And 24-Frequency Execution

- [ ] Test exact resume, mismatch quarantine, `.tmp` rejection, unexpected
      active-file rejection, certified-domain cache, final-pair failure,
      missing T7ca GREEN, and extension rejection.
- [ ] Run frequencies in frozen order; after each frequency independently
      reload and validate NPZ/JSON/ledger before continuing.
- [ ] Reuse only complete matching transactions. Never recompute a valid one.
- [ ] If an implementation path changes after real execution begins, stop,
      freeze a new exact five-path commit/contract, quarantine all old-contract
      transactions, and restart contract validation. Never mix identities.
- [ ] Do not stop a healthy process for elapsed time. Capacity/system recovery
      requires process/checkpoint/artifact/test/scope safety first.

## Task 5 — Aggregate And Diagnostic Audit

- [ ] Require 24 active transaction pairs and no extra active file. Aggregate
      only the new rows in frozen order with shape `(24,8)`.
- [ ] Retain the accepted 22/21 per-frequency/aggregate array structures,
      actual NumPy dtypes, exact units coverage, and explicit ordering.
- [ ] Direct-load immutable T8aj/T8ao/T8ap rows plus the new rows to build only
      the five exact sequences in design Section 6.
- [ ] Use the literal 24-row parent map; never infer parents by float
      adjacency.
- [ ] Record exactly 816 phase, 768 grandchild/parent magnitude, and 80
      summary records, plus parent identity, spacing, total variation,
      cancellation, largest-step attribution, and all strict extrema.
- [ ] Emit no scientific acceptance decision or new threshold from T8aq.
- [ ] Write exactly 53 active files and 52 non-self manifest records:

```text
frequencies/kM_<token>.npz
frequencies/kM_<token>.npz.json
checkpoint_ledger.json
further_local_values.npz
further_local_values.npz.json
further_local_sampling_audit.json
manifest.md
```

## Task 6 — Runner, Tests And Standalone Audit

- [ ] Add a thin CLI accepting output, accepted source, gate, evidence, and
      resume paths; it delegates to the focused module and exits nonzero on
      contract failure.
- [ ] Use fake compute for unit/regression tests; no real solver in tests.
- [ ] Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_further_local_refinement.py \
  tests/regression/test_further_local_refinement_script.py
.venv/bin/python -m ruff check \
  src/schwgw/io/tablei_further_local_refinement.py \
  src/schwgw/io/__init__.py \
  scripts/phase5_run_further_local_refinement.py \
  tests/unit/test_tablei_further_local_refinement.py \
  tests/regression/test_further_local_refinement_script.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

- [ ] Run a standalone no-helper artifact audit for source/gate hashes,
      `53/52`, 24 pairs, exact keys/order/shape/dtype/units, masks, finiteness,
      lmax/final-pair data, canonical fingerprints, aggregate identity,
      ledger/manifest, contracts, `816/768/80`, temp/quarantine exclusion.
- [ ] Require the implementation commit to contain exactly the five paths and
      no radial/source/config/viz/fixture/Kirchhoff/unrelated diff.
- [ ] Archive/update T8 handoff and `status.md` separately, preserving
      unrelated worktree files.

## Decision, Dispatch And Stop Rules

Record exactly one:

```text
GREEN / FURTHER LOCAL FREQUENCY EVIDENCE GENERATED
YELLOW / FURTHER LOCAL FREQUENCY EVIDENCE PARTIAL
RED / FURTHER LOCAL FREQUENCY EVIDENCE BLOCKED
```

Only exact GREEN with all 24 transactions, complete contracts, tests, and
scope may dispatch frozen T7cb to existing T7. Report commit, contracts,
source/gate/output hashes, per-frequency runtimes/counts, final-pair maxima,
audit/tests, decision, and dispatch state to T0.

Stop on source/gate/code mismatch, missing/extra transaction, unsafe cache,
nonfinite value, false mask, final-pair failure, schema/units/dtype/ordering
mismatch, ledger/aggregate/manifest ambiguity, test/Ruff/scope failure, or
forbidden output. Do not lower lmax, extend it, relax `1e-4`, omit records,
interpolate/smooth/fill, alter hierarchy rules, broaden the adapter, start a
next midpoint, or push GitHub.

A `12 h` notice is soft and never stops a healthy process. Genuine
capacity/system recovery reuses only verified complete state and never
bypasses scientific/test/scope failure.

## Definition Of Done

- 24 atomic pairs and exact 53/52 package are complete;
- contracts, units, dtypes, ordering, hashes, and provenance are explicit;
- aggregate equals direct stacking and audit contains exactly 816 phase, 768
  hierarchy, and 80 summary records;
- focused tests, Ruff, full pytest, standalone audit, scope, and isolation pass;
- one exact decision and downstream state are recorded.
