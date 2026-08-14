# T4ac Literal Failed-Child Radial Gate Plan

## Goal

Build a fail-closed radial/Q018 gate for exactly the 41 frequencies frozen in
`docs/superpowers/specs/2026-07-18-t4ac-t8ar-literal-failed-child-refinement-design.md`.
This is radial-only prerequisite evidence; it must not compute amplification,
T8ar products, plots, fixtures, Kirchhoff, or paper artifacts.

## Frozen Inputs

- current `project.md`, `status.md`, T0/T4/T7/T8 handoffs;
- T7cb handoff SHA-256
  `57cae192228d9d29b1cc39c82cc8c7bd3844811e3a0b35faaa1dbdc2c799bd01`;
- T8aq five root hashes and generation/metadata contracts in the design;
- original frozen seven-file package at commit
  `76b57c90d6e54594ca480e1dcf629af685d9098f`;
- exact 41 frequencies/tokens/lmax windows and 146,416 classification count;
- unchanged physical, boundary, solver, Q018, and tolerance conventions.

Any mismatch stops before implementation or computation.

## Exact Implementation Scope

One pre-compute commit changes exactly:

```text
scripts/phase5_literal_failed_child_radial_gate.py
src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

The adapter label is
`q018_tablei_literal_failed_child_transition`. No IO, observable, scattering,
configuration, fixture, visualization, Kirchhoff, or unrelated path belongs
in the implementation commit.

## Task 1 — Start Gate And TDD RED

- Recheck package commit/blob/SHA identity and T7cb evidence.
- Re-derive all 41 midpoints, tokens, lmax windows, and 146,416 records.
- Add failing tests for literal sector-aware membership, wrong-identity
  fail-closed behavior, default-covered zero-oracle behavior, and snapshot
  provenance.
- Run focused RED tests before implementation.

## Task 2 — Classification Snapshot

- Classify both sectors, every `ell=2..ell_max`, and all eight points.
- Create exactly 41 frequency checkpoint identities.
- Record complete classification rows and measured structured transitions.
- Bind parent-commit radial blob, immutable sources, frozen package, physical
  inputs, and code hashes in a classification snapshot.
- Require exactly 146,416 unique complete Cartesian keys and zero
  default-error-other records.

No adapter edit occurs before this snapshot is immutable.

## Task 3 — Direct Oracle And Literal Envelope

- Run the direct oracle only on measured structured transitions.
- Validate residual, normalization, log derivative, condition, finite values,
  and sensitivity using unchanged thresholds.
- Generate a literal Python envelope containing exactly the measured
  frequency/sector/ell/point membership and saved direct-oracle values.
- Never infer membership, interpolate, load a run file at import time, or
  broaden the public default path.
- Add the exact opt-in adapter and fail closed on every mismatched physical or
  implementation field.

## Task 4 — Final Adapter Snapshot And Commit

- Run focused tests and Ruff on the exact five paths.
- Create one exact five-path implementation commit before any T8ar work.
- Record a final-adapter snapshot binding the commit and all five blobs.
- Prove the final snapshot bridges to the unchanged classification snapshot.
- Verify integrated adapter anchors against saved direct-oracle values and
  require default-covered zero oracle calls.

## Task 5 — Atomic 41-Frequency Gate

- Write one complete atomic checkpoint per frequency under
  `runs/phase5/fig5_fig6_literal_failed_child_radial_gate/`.
- A checkpoint is reusable only when classification snapshot, contract,
  output hash, frequency, implementation identity, and complete/PASS state all
  match exactly.
- Never recompute a complete matching frequency.
- On capacity/system interruption, stop at an atomic boundary and return the
  safe resume identity to T0.
- Any scientific/numerical/nonfinite/test/scope/provenance failure is not a
  capacity interruption and returns YELLOW/RED without model bypass.

## Task 6 — Fresh Verification And Handoff

- Verify 41/41 complete PASS checkpoints and manifest hashes.
- Run direct-oracle preflight on every measured transition.
- Run focused pytest, Ruff, and fresh full pytest.
- Require clean exact-five-path scope, `git diff --check`, and empty forbidden
  output searches.
- Archive the prior T4 handoff byte-for-byte, update status/T4 handoff, and
  return only to T0.

Exact decision:

```text
GREEN / LITERAL FAILED-CHILD RADIAL GATE READY
YELLOW / LITERAL FAILED-CHILD RADIAL EVIDENCE INCOMPLETE
RED / LITERAL FAILED-CHILD RADIAL GATE INVALID
```

T4ac must not dispatch T7cc or T8ar.

## Forbidden Outputs

- no lmax extension;
- no automatic/recursive midpoint;
- no uniform/full grid;
- no T8ar computation or amplification artifact;
- no production, plot, fixture, Kirchhoff, or paper-style output;
- no threshold relaxation or GitHub action.
