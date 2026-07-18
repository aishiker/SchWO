# T8ar — Literal Failed-Child Point-Only Refinement

Work only in existing T8 task `019f5ece-f578-7b91-8f61-df882c656591`.
Do not create or replace a task. Normal execution uses `gpt-5.6-sol/high`.

## Start Gate

Before editing or computing, fully read `project.md`, `status.md`, current
T0/T4/T7/T8 handoffs, the exact reviewed candidate design/plans/prompts,
T4ac/T7cc evidence, T7cb handoff, and immutable T8aj/T8ao/T8ap/T8aq sources.
Verify the candidate identity, T7cc exact
`ACCEPT GREEN / LITERAL FAILED-CHILD RADIAL GATE ACCEPTED`, and T0 fresh
verification. Stop on any mismatch or ambiguity.

The only new frequencies are the exact 41 design-table midpoints. No runtime
selection, inferred adjacency, or passing interval is allowed.

## Allowed Implementation Paths

Before the first real frequency, create one commit changing exactly:

```text
scripts/phase5_run_literal_failed_child_refinement.py
src/schwgw/io/__init__.py
src/schwgw/io/tablei_literal_failed_child_refinement.py
tests/unit/test_tablei_literal_failed_child_refinement.py
tests/regression/test_literal_failed_child_refinement_script.py
```

Other allowed writes are only:

```text
runs/phase5/fig5_fig6_literal_failed_child_refinement/**
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-18_pre_t8ar_literal_failed_child_refinement.md
```

Preserve unrelated worktree changes.

## Required Work

1. Hard-code and independently validate the exact 41 frequencies/tokens/lmax
   windows, five sequences, 41-row parent map, point order, units, dtypes, and
   `87/86` artifact cardinality.
2. Define canonical generation/metadata contracts and schema
   `phase5_t8ar_literal_failed_child_refinement_v1_units_dtype_ordering`.
3. Add fake-compute RED tests, implement the bounded runner/IO, run focused
   tests and Ruff, then create the exact five-path implementation commit.
4. Freeze implementation blobs and contract hashes before the first real
   transaction; the commit must predate all transactions.
5. Produce exactly 41 atomic NPZ/JSON pairs. Each complete pair must bind all
   scientific inputs, histories/final rows, masks, final-pair threshold
   `1e-4`, warnings, hashes, fingerprints, contracts, and implementation.
6. Resume only exact complete matching pairs; never reuse across identity or
   recompute a complete matching frequency.
7. Direct-stack all 41 pairs and require exact aggregate identity.
8. Write exactly 87 active files and 86 non-self manifest records, with no
   temp/quarantine file.
9. Record exactly 1,472 phase, 1,312 literal-parent hierarchy, and 80 summary
   records, but set `diagnostic_only=true` and
   `acceptance_decision_emitted=false`. Do not emit a scientific judgment or
   next midpoint.
10. Reload and verify all pairs/roots/contracts/hashes; run focused tests,
    Ruff, fresh full pytest, scope/source checks, `git diff --check`, warning
    classification, and both forbidden-output searches.
11. Archive/update only allowed coordination records and return to T0.

## Exact Decision

Return exactly one:

```text
GREEN / LITERAL FAILED-CHILD FREQUENCY EVIDENCE GENERATED
YELLOW / LITERAL FAILED-CHILD FREQUENCY EVIDENCE INCOMPLETE
RED / LITERAL FAILED-CHILD FREQUENCY ARTIFACT INVALID
```

Include commit/parent/five blobs, 41 pair hashes, ledger/contracts, 87/86
cardinality, aggregate/audit/manifest roots, exact 1,472/1,312/80 counts,
tests, scope, and non-claims. Return only to T0. Do not start T7cd.

## Recovery And Stop Rules

Twelve hours is a soft notification. On confirmed capacity/system
interruption, preserve atomic state and return safe resume identity. A
scientific/numerical/nonfinite/test/scope/provenance failure cannot be bypassed
by model switch. No threshold relaxation, lmax extension, automatic/recursive
midpoint, uniform/full grid, production, plot, fixture, Kirchhoff, paper-style
work, new task, downstream dispatch, or GitHub action.
