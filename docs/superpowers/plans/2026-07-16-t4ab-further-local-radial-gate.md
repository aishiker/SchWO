# T4ab Further-Local Radial/Q018 Gate Implementation Plan

Date: 2026-07-16

## Goal

Measure complete radial/Q018 support for the 24 frozen further-local
frequencies, validate every structured transition against the direct oracle,
and add one exact sector-aware fail-closed adapter containing only the
measured `(kM, sector, ell, point_id)` envelope.

This is radial-only. It must not compute amplification, sampling metrics,
plots, fixtures, Kirchhoff data, or any production grid.

## Frozen Inputs

```text
frequencies = [
  0.325,0.375,0.825,0.875,0.925,0.975,
  1.525,1.575,1.625,1.675,1.7125,1.7375,
  2.7625,2.7875,2.825,2.875,2.925,2.975,
  3.7625,3.7875,3.825,3.875,3.925,3.975,
]
sectors = [odd, even]
points = exact eight TABLEI_POINTS
M = 1
r_out = 300
r_in_eps = 1e-6
rtol = 1e-10
atol = 1e-12
```

Use the exact token/lmax table in the design. The independently derived
classification cardinality is exactly `81,792` records. Transition count is
measured, not assumed.

Immutable input identity includes:

- exact T8aj, T8ao/T7bx, T4aa/T7by, and T8ap root paths/hashes from the design;
- T7bz evidence at `docs/handoffs/T7_current.md`, SHA-256
  `8edd808e543460f943eb217af248b2edd52d7ea7d1827e99315b4f49f6521d9e`;
- the reviewed seven-file package identity supplied by T0 after exact package
  review GREEN.

Paths and hashes form one identity. Never search for a same-named substitute.

## Frozen File Map

The implementation commit contains exactly:

```text
scripts/phase5_further_local_radial_gate.py
src/schwgw/numerics/q018_further_local_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Additional writes are limited to:

```text
runs/phase5/fig5_fig6_further_local_radial_gate/
docs/phase5_further_local_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-16_pre_t4ab_further_local_radial_gate.md
```

Preserve and exclude unrelated worktree changes.

## Task 1 — Preflight And TDD RED

- [ ] Read the frozen design, both plans, T4ab/T7ca prompts, current T0/T4/T7
      handoffs, T7bz failure evidence, accepted gate/artifacts, current radial
      solver/direct oracle/Table-I source, existing envelope patterns, and the
      two authorized test modules.
- [ ] Freshly verify all immutable paths/hashes and exact package-review GREEN.
      Stop on any mismatch.
- [ ] Record exact source blobs for pre-adapter `radial_solver.py`, direct
      oracle, Table-I points, design/plan/prompt, T7bz evidence, and accepted
      roots in the input contract.
- [ ] Add tests for all 24 tokens, exact lmax windows, strict boundary fields,
      adapter identity, 24 checkpoints, and `81,792` rows.
- [ ] Prove the new adapter is initially unsupported with the expected
      fail-closed TDD RED. Diagnose any unrelated failure before continuing.

## Task 2 — Classification And Atomic Checkpoints

- [ ] Implement the gate with literal frequency/token/lmax data and exact
      `TABLEI_POINTS`.
- [ ] Use only `default_covered`, `default_fail_closed_uncovered`,
      `default_fail_closed_solver_failed`, and `default_error_other`.
- [ ] Require `default_error_other == 0`; never hide a nonfinite or unexpected
      exception as structured coverage.
- [ ] Write exactly 24 atomic `checkpoint/kM_<token>.json` files. Reuse only
      when schema, complete contract, classification snapshot, output hash,
      `complete=true`, and `decision=PASS` match. Quarantine any mismatch.
- [ ] Freeze the classification snapshot before the first classification
      call. It binds the final gate script, pre-adapter radial blob, direct
      oracle, Table-I source, reviewed package, T7bz evidence, and input
      contract.
- [ ] Checkpoint resume compares only with that pre-adapter snapshot, never
      the later final-adapter radial blob.
- [ ] Require a unique complete 81,792-row union before envelope generation.

## Task 3 — Direct Oracle And Literal Envelope

- [ ] Validate every structured recoverable key
      `(kM, sector, ell, point_id)` with the existing direct Riccati/log-
      amplitude oracle; do not infer odd/even symmetry.
- [ ] Record requested and actual backend precision separately.
- [ ] Require finite `psi`, `dpsi_dr`, `A_in`, `A_out`, normalization and
      boundary consistency; effective residual `<1e-7`, normalization/boundary
      residuals `<1e-8`, and maximum tolerance sensitivity `<5e-6`.
- [ ] For each nonempty `(kM,sector)` group select lexicographic first and last
      `(ell,point_id)`, then the first transition for every not-yet-covered
      point ID. Run the deduplicated anchors at requested `70/80/100` dps and
      frozen loose/tight tolerances. Record empty groups explicitly.
- [ ] Compress only consecutive integer ells with identical exact point sets
      at the same `(kM,sector)`. Independently expand and require exact equality
      with raw transition keys.
- [ ] Generate import-time IO-free `q018_further_local_envelope.py` with exact
      tokens, points, sector-aware segments, and source/classification/oracle
      hashes.

## Task 4 — Exact Adapter And Final Snapshot

- [ ] Add only `q018_tablei_further_local_transition` to `radial_solver.py`.
- [ ] Validate exact Schwarzschild background, `M`, sector, binary64
      frequency, point radius/ID, literal membership, `r_out`, `r_in_eps`,
      `rtol`, and `atol` under the existing strict comparison convention.
- [ ] Keep default-covered modes on the ordinary path with zero adapter calls.
- [ ] Emit only
      `q018_tablei_further_local_transition_oracle_used` for measured
      recoverable transitions.
- [ ] Test all frequencies/sectors/point groups and every wrong contract
      field, unmeasured ell/point pair, and near-but-not-exact frequency.
- [ ] Compare positive adapter values directly with saved oracle records.
- [ ] Run focused tests and Ruff, then commit exactly the five frozen paths
      before preflight.
- [ ] Freeze a separate final-adapter snapshot binding the generated envelope,
      final radial blob, exact five-path commit and blobs. Hash-link it to the
      classification snapshot without rewriting prior checkpoints.

## Task 5 — Preflight, Artifacts, Tests And Decision

- [ ] Re-run every transition through the integrated adapter without calling
      the classifier/compressor. Require exact keys, finite fields, residual
      bounds, adapter/warning identity, both snapshots, their bridge, and zero
      failures.
- [ ] Write only:

```text
classification_manifest.json
oracle_validation.json
resume_preflight.json
checkpoint/kM_<token>.json  # exactly 24
manifest.md
```

- [ ] Write `docs/phase5_further_local_radial_gate.md` with counts, hashes,
      maxima, precision qualification, runtimes, limitations, and non-claims.
- [ ] Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
.venv/bin/python -m ruff check \
  scripts/phase5_further_local_radial_gate.py \
  src/schwgw/numerics/q018_further_local_envelope.py \
  src/schwgw/numerics/radial_solver.py \
  tests/physics/test_q018_production_integration_design.py \
  tests/physics/test_radial_solver.py
PYTHONPATH=src .venv/bin/python -m pytest -q
```

- [ ] Require exact commit scope, 24 PASS checkpoints, no active `.tmp`, no
      ambiguous quarantine, and no T8aq/full/uniform/plot/fixture/Kirchhoff/
      paper output.
- [ ] Archive/update T4 handoff and `status.md`, recording exactly one:

```text
GREEN / FURTHER LOCAL RADIAL GATE READY
YELLOW / FURTHER LOCAL RADIAL GATE PARTIAL
RED / FURTHER LOCAL RADIAL GATE BLOCKED
```

## Dispatch And Stop Rules

Only exact GREEN with fresh artifact/test/scope verification may dispatch the
frozen T7ca prompt to the existing T7 task. T4ab reports exact decision,
implementation commit, 24 checkpoint hashes, classification/oracle/preflight
hashes, counts, maxima, precision, runtimes, tests, and dispatch state to T0.

Stop YELLOW/RED on source mismatch, incomplete cardinality, default-other,
nonfinite oracle fields, residual/sensitivity failure, checkpoint/provenance
ambiguity, test/Ruff/scope failure, or forbidden output. Do not relax
thresholds, omit records, interpolate/broaden an adapter, run T8aq, or push
GitHub.

A `30 h` notice is soft and never terminates a healthy process. On a genuine
capacity/system interruption, resume only complete matching checkpoints after
process/source/artifact/test/scope inspection. Never switch models to bypass a
scientific or numerical failure.

## Definition Of Done

- 81,792 rows and 24 atomic PASS checkpoints are complete;
- every transition is oracle-validated and exactly represented by the literal
  sector-aware envelope;
- adapter positive/negative/default-path tests pass;
- focused tests, Ruff, full pytest, provenance, resume, scope, and isolation
  pass fresh;
- one exact decision and downstream state are recorded without observable
  artifacts.
