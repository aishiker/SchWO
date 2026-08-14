# T8ap Targeted Adaptive Frequency Refinement Implementation Plan

Date: 2026-07-15

## Goal

Generate a point-only, resumable artifact for exactly thirteen targeted
adaptive frequencies, then record all data needed for an independent T7bz
reconstruction of 432 phase-step records and 416 hierarchical magnitude
records.

This plan is executable only after T7by independently accepts the T4aa radial
gate and T0 explicitly dispatches T8ap. It is not a full or uniform grid.

## Frozen Inputs

```text
frequencies = [
  0.35, 0.45, 0.85, 0.95, 1.55, 1.65, 1.725,
  2.775, 2.85, 2.95, 3.775, 3.85, 3.95,
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
adapter = q018_tablei_targeted_adaptive_transition
```

Use the exact per-frequency lmax windows in the frozen design. No lmax
extension is authorized because T4aa measures only those initial windows. If
an initial final pair fails, stop YELLOW without aggregation.

Immutable input anchors include the accepted T8aj triplet, all five accepted
T8ao root files and their v1/v2 contracts, and the future exact T4aa/T7by gate
hashes. Never repair or rewrite an accepted source.

Exact immutable source/history paths are:

```text
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz
runs/phase5/fig5_fig6_dense_review_grid/tablei_dense_review_values.npz.json
runs/phase5/fig5_fig6_dense_review_grid/manifest.md
runs/phase5/fig5_fig6_delta0p1_risk_pilot/checkpoint_ledger.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz
runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_values.npz.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot/risk_pilot_sampling_audit.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot/manifest.md
runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/classification_manifest.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/oracle_validation.json
runs/phase5/fig5_fig6_delta0p1_risk_pilot_radial_gate/resume_preflight.json
```

The future T4aa classification/oracle/preflight/manifest paths and hashes are
supplied by T0 only after T7by exact GREEN at exactly:

```text
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/classification_manifest.json
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/oracle_validation.json
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/resume_preflight.json
runs/phase5/fig5_fig6_targeted_adaptive_radial_gate/manifest.md
```

The generation contract binds exact paths and hashes; same-named substitutes
are invalid.

## Frozen File Map

Implementation commit paths are exactly:

```text
src/schwgw/io/tablei_adaptive_refinement.py
src/schwgw/io/__init__.py
scripts/phase5_run_targeted_adaptive_refinement.py
tests/unit/test_tablei_adaptive_refinement.py
tests/regression/test_targeted_adaptive_refinement_script.py
```

Additional writes are limited to:

```text
runs/phase5/fig5_fig6_targeted_adaptive_refinement/
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-15_pre_t8ap_targeted_adaptive_refinement.md
```

## Task 1 — Start-Gate Preflight And TDD RED

- [ ] Require exact T7by decision
      `ACCEPT GREEN / TARGETED ADAPTIVE RADIAL GATE ACCEPTED` and fresh T0
      dispatch. Hash all T4aa gate files and selected adapter/code blobs.
- [ ] Freshly verify the accepted T8aj and T8ao/T7bx source hashes, source
      cardinalities, v1 generation contract, v2 metadata contract, units,
      dtype, ordering, and no-active-temp state. Stop on any mismatch.
- [ ] Add import/frozen-constant tests for all thirteen tokens, exact lmax
      windows, eight-point order, schema, adapter, parent mapping, source/gate
      hashes, and output cardinality `31/30`.
- [ ] Add failing tests for the absent module/runner and prove the expected TDD
      RED before implementation.

## Task 2 — Contracts, Schema And Atomic Transactions

- [ ] Implement a focused module `tablei_adaptive_refinement.py`; do not modify
      or call a migration path in `tablei_risk_pilot.py`.
- [ ] Build a canonical generation contract covering frequencies/tokens,
      lmax windows, points, physical/numerical inputs, amplitudes, adapter,
      source and gate hashes, selected code hashes, Git state, convergence,
      cache, resume, and fail-closed policies.
- [ ] Build a separate metadata contract for the exact schema
      `phase5_t8ap_targeted_adaptive_refinement_v1_units_dtype_ordering`,
      units, dtype and ordering registries, non-production/no-interpolation
      flags, generation hash, source/gate hashes, and array fingerprints.
- [ ] Make all required metadata explicit in every embedded metadata object,
      sidecar, ledger, aggregate, sampling audit, and manifest. Reviewers must
      not infer units, dtype, axis order, source identity, or schema.
- [ ] Implement sibling-temporary atomic NPZ/JSON writes and atomic ledger
      replacement. A transaction is complete only after NPZ, sidecar, contract,
      hashes, adapter, lmax, source/gate identity, and ledger entry all agree.
- [ ] Quarantine partial/mismatched pairs. Never count quarantine as active.

## Task 3 — Implement Cache And Transaction With Fake Compute Only

- [ ] Do not invoke the real solver or write a real-frequency transaction in
      this task. Exercise all behavior through injected fake compute functions.
- [ ] Use a frequency-local cache keyed by sector, ell, k, background,
      boundary/tolerances and adapter. Retain the exact certified radius domain
      of each solution.
- [ ] Process points in decreasing radius and reuse a solution only when its
      certified interval contains the requested point. Preserve disjoint local
      solutions; never repeat the T8an pre-`47c3d63` cache-domain bug.
- [ ] Load exact Table-I geometry and compute Route-B lensed plus/cross fields
      and flat/no-lens denominators. Form independent complex ratios and masks.
- [ ] For every frozen lmax, save histories at all eight points. Require finite
      values, true plus/cross masks, and the final adjacent complex pair to pass
      `abs(a-b)/max(1,abs(a),abs(b)) <= 1e-4` for every point/component.
- [ ] Record runtime, solve/reuse/adapter counts, warnings, convergence deltas,
      the explicit no-extension decision, code/source/gate hashes, and exact
      non-claims.
- [ ] Implement writing one atomic NPZ/JSON pair and one hash-only ledger entry
      only after the complete fake frequency validates.
- [ ] Complete all five implementation/test paths and fake-compute tests, run
      focused tests and Ruff, and create one scoped implementation commit
      containing exactly the frozen five paths **before** the first real
      frequency. Freeze the generation contract from that commit and its five
      blobs. No real transaction may predate this identity.

## Task 4 — Resume And Thirteen-Frequency Execution

- [ ] Test exact resume reuse, source/gate/code/contract mismatch quarantine,
      `.tmp` rejection, unexpected active file rejection, domain-aware cache,
      final-pair failure, missing T7by GREEN, and attempted extension rejection.
- [ ] Run frequencies in the frozen order. After every frequency, independently
      reload and validate its pair and ledger record before proceeding.
- [ ] On resume, reuse only complete, hash-matching transactions; do not rerun
      a valid completed frequency.
- [ ] If any of the five implementation files changes after real execution
      starts, stop, commit the new five-path implementation identity, quarantine
      every old-contract transaction/ledger, and restart contract validation.
      No transaction crosses an implementation-commit boundary.
- [ ] A healthy long-running solver is not stopped for elapsed time. Capacity
      or system interruption may resume only after process/checkpoint/artifact
      inspection proves there is no scientific/test/scope failure.

## Task 5 — Aggregate And Sampling Audit

- [ ] Require exactly thirteen active transaction pairs and no extra active
      file before aggregation. Aggregate only the new rows in exact frequency
      order with shape `(13,8)`.
- [ ] Use the accepted per-frequency/aggregate 22/21 array structures and exact
      actual dtypes. Require declared dtype to equal loaded dtype for every
      array and exact units-key coverage.
- [ ] Freshly direct-load, hash and combine the immutable T8aj endpoints,
      accepted T8ao rows, and new T8ap rows into exactly these sequences:

```text
[0.3,0.35,0.4,0.45,0.5]
[0.75,0.8,0.85,0.9,0.95,1.0]
[1.5,1.55,1.6,1.65,1.7,1.725,1.75]
[2.75,2.775,2.8,2.85,2.9,2.95,3.0]
[3.75,3.775,3.8,3.85,3.9,3.95,4.0]
```

- [ ] Use the exact thirteen-row midpoint/parent/children/parent-width mapping
      in design Section 6. Do not infer parents by float adjacency.
- [ ] Record exactly 432 adjacent phase records and 416 child/parent magnitude
      records, parent identity, child spacing, total variation, largest-step
      attribution, cancellation structure, and strict interior extrema.
- [ ] The T8 audit records values only; it emits no GREEN/YELLOW scientific
      acceptance and does not invent another threshold.
- [ ] Write exactly 31 active files and a manifest with exactly 30 non-self
      records:

```text
frequencies/kM_<token>.npz
frequencies/kM_<token>.npz.json
checkpoint_ledger.json
adaptive_refinement_values.npz
adaptive_refinement_values.npz.json
adaptive_sampling_audit.json
manifest.md
```

## Task 6 — Thin Runner, Tests And Independent Audit

- [ ] Add a thin CLI accepting output, accepted T8aj/T8ao source, radial gate,
      and resume paths; it delegates only to the focused module and exits
      nonzero on contract failure.
- [ ] Use fake compute functions for unit/regression coverage; no real solver
      may run during tests.
- [ ] Run focused tests:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/unit/test_tablei_adaptive_refinement.py \
  tests/regression/test_targeted_adaptive_refinement_script.py
```

- [ ] Run Ruff on the exact five paths and fresh full pytest.
- [ ] Run a standalone direct artifact audit that does not call T8ap loader,
      aggregate, metric, or acceptance helpers. Require source/gate hashes,
      `31/30` cardinality, thirteen frequency pairs, exact key/order/shape/
      dtype/units, masks, finiteness, lmax/final-pair data, aggregate identity,
      ledger/manifest hashes, metadata-contract reconstruction, 432/416
      counts, no active temp, and quarantine exclusion.
- [ ] Require the implementation commit diff to contain exactly the frozen
      five paths and no radial solver/adapter, source artifact, config,
      visualization, fixture, Kirchhoff, or unrelated handoff change.
- [ ] Confirm the pre-run scoped implementation commit and its blobs still
      equal the generation contract. Update/archive the T8 handoff and
      `status.md` separately, preserving unrelated worktree files.

## Decision, Dispatch And Stop Rules

Record exactly one:

```text
GREEN / TARGETED ADAPTIVE FREQUENCY EVIDENCE GENERATED
YELLOW / TARGETED ADAPTIVE FREQUENCY EVIDENCE PARTIAL
RED / TARGETED ADAPTIVE FREQUENCY EVIDENCE BLOCKED
```

Only exact GREEN with all thirteen validated transactions, full artifact
contract, tests and scope may dispatch the frozen T7bz prompt to the existing
T7 task. Notify T0 with commit, contract/source/gate/output hashes, per-frequency
runtimes and counts, final-pair maxima, artifact-audit result, tests, exact
decision, and T7 dispatch state.

Stop on any invalid source/gate hash, missing/extra transaction, unsafe cache
reuse, nonfinite value, false mask, final-pair failure outside the accepted
envelope, schema/units/dtype/ordering mismatch, cardinality/ledger/manifest
ambiguity, test/Ruff failure, scope drift, or forbidden output. Do not lower
lmax, relax `1e-4`, omit rows/points/components, fill/interpolate/smooth, alter
the parent criterion, broaden the adapter, start a next midpoint, or push
GitHub.

## Definition Of Done

- thirteen atomic transactions and exact `31/30` package are complete;
- all contracts, units, dtypes, ordering, hashes and provenance are explicit;
- aggregate equals direct transaction stacking and the audit contains exactly
  432 phase plus 416 child/parent records;
- focused tests, Ruff, full pytest, standalone audit, scope and isolation pass;
- one exact decision and frozen downstream dispatch state are recorded.
