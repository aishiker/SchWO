# T4ac — Literal Failed-Child Radial/Q018 Gate

Work only in existing T4 task `019f5fa6-1288-7c01-8a87-4c4370cf5517`.
Do not create or replace a task. Use `gpt-5.6-sol/high` for normal execution.

## Start Gate

Before any edit or computation, fully read `project.md`, `status.md`, current
T0/T4/T7/T8 handoffs, the reviewed candidate design, T4ac plan, all four
candidate prompts, T7cb handoff, and immutable T8aq/T4ab evidence. Verify the
candidate commit/blob/SHA identity supplied by T0. Stop on any mismatch.

The candidate authorizes exactly 41 literal failed-child frequencies,
146,416 classification records, unchanged lmax seed rule/max 360, both
sectors, every `ell=2..ell_max`, and the exact eight points. It is not a
uniform/full grid or automatic recursion.

## Allowed Implementation Paths

Create one pre-compute commit changing exactly:

```text
scripts/phase5_literal_failed_child_radial_gate.py
src/schwgw/numerics/q018_tablei_literal_failed_child_envelope.py
src/schwgw/numerics/radial_solver.py
tests/physics/test_q018_production_integration_design.py
tests/physics/test_radial_solver.py
```

Other allowed writes are only:

```text
runs/phase5/fig5_fig6_literal_failed_child_radial_gate/**
docs/phase5_literal_failed_child_radial_gate.md
status.md
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-18_pre_t4ac_literal_failed_child_radial_gate.md
```

Preserve unrelated worktree changes.

## Required Work

1. Re-derive exact frequencies/tokens/lmax windows and 146,416 Cartesian keys.
2. Add focused RED tests before implementation.
3. Classify all records and freeze a pre-adapter classification snapshot.
4. Measure structured transitions; never assume their count.
5. Direct-oracle every transition with unchanged residual, normalization,
   log-derivative, condition, finiteness, and sensitivity checks.
6. Generate an exact sector-aware literal envelope and opt-in adapter
   `q018_tablei_literal_failed_child_transition`; default-covered modes make
   zero oracle calls and every mismatch fails closed.
7. Run focused tests and Ruff, then create the exact five-path implementation
   commit before completing the final adapter snapshot.
8. Produce exactly 41 atomic complete/PASS checkpoints plus four roots. Reuse
   only a complete checkpoint with exact snapshot/contract/output/commit
   identity; never recompute a complete matching frequency.
9. Run direct-oracle resume preflight, focused tests, Ruff, fresh full pytest,
   scope checks, `git diff --check`, and forbidden-output searches.
10. Archive/update only the allowed coordination records and return to T0.

## Exact Decision

Return exactly one:

```text
GREEN / LITERAL FAILED-CHILD RADIAL GATE READY
YELLOW / LITERAL FAILED-CHILD RADIAL EVIDENCE INCOMPLETE
RED / LITERAL FAILED-CHILD RADIAL GATE INVALID
```

Include implementation commit/parent/five blobs, 41 checkpoint hashes,
classification and transition counts, both snapshot hashes, oracle/preflight
maxima, artifact hashes, tests, scope, and non-claims. Do not start T7cc or
T8ar; return only to T0.

## Stop Rules

No threshold relaxation, lmax extension, automatic/recursive midpoint,
uniform/full grid, amplification, production, plot, fixture, Kirchhoff,
paper-style output, new task, or GitHub action. A scientific/numerical/
nonfinite/test/scope/provenance failure is not a capacity interruption.
