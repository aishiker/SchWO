# T8as — Another Bounded Local Point-Only Refinement

Work only in existing T8 task `019f5ece-f578-7b91-8f61-df882c656591`.
Do not create or replace a task. Normal execution uses `gpt-5.6-sol/high`.

## Start Gate

Fully read `project.md`, `status.md`, current T0/T4/T7/T8 handoffs, the exact
reviewed candidate design/plans/prompts, T4ad/T7ce evidence, T7cd handoff,
T8ar sources, and earlier immutable sources. Verify candidate identity,
T7ce exact `ACCEPT GREEN / ANOTHER BOUNDED LOCAL RADIAL GATE ACCEPTED`, and
T0 fresh verification. Stop on mismatch or ambiguity.

Only the exact 55 design-table midpoints are authorized. No runtime selection,
inferred adjacency, passing interval, or recursion is allowed.

## Allowed Implementation Paths

Before the first real frequency, create one commit changing exactly:

```text
scripts/phase5_run_another_bounded_local_refinement.py
src/schwgw/io/__init__.py
src/schwgw/io/tablei_another_bounded_local_refinement.py
tests/unit/test_tablei_another_bounded_local_refinement.py
tests/regression/test_another_bounded_local_refinement_script.py
```

Other allowed writes are only:

```text
runs/phase5/fig5_fig6_another_bounded_local_refinement/**
status.md
docs/handoffs/T8_current.md
docs/handoffs/archive/T8_2026-07-20_pre_t8as_another_bounded_local_refinement.md
```

Preserve unrelated worktree changes.

## Required Work

1. Hard-code/validate exact 55 frequencies/tokens/lmax windows, five sequences,
   55-row parent map, point order, units, dtypes, and 115/114 package.
2. Define canonical generation/metadata contracts and schema
   `phase5_t8as_another_bounded_local_refinement_v1_units_dtype_ordering`.
3. Add fake-compute RED tests, implement bounded runner/IO, run focused tests
   and Ruff, then create the exact five-path pre-run commit.
4. Freeze implementation blobs/contracts before the first transaction; commit
   must predate every transaction.
5. Produce exactly 55 atomic NPZ/JSON pairs binding all scientific inputs,
   histories/final rows, masks, unchanged final-pair threshold `1e-4`, warnings,
   hashes, fingerprints, contracts, gate/source hashes, and implementation.
6. Resume only exact complete matching pairs; never reuse across identity or
   recompute a complete matching frequency.
7. Direct-stack all pairs and require exact aggregate identity.
8. Write exactly 115 active files and 114 non-self manifest records, with no
   temp/quarantine.
9. Record exactly 2,352 phase, 1,760 literal-parent hierarchy, and 80 summary
   records with `diagnostic_only=true` and
   `acceptance_decision_emitted=false`; emit no decision or next midpoint.
10. Reload/verify all pairs/roots/contracts/hashes; run focused tests, Ruff,
    fresh full pytest, scope/source checks, `git diff --check`, warning
    classification, and forbidden-output searches.
11. Archive/update only allowed records and return to T0.

## Exact Decision

```text
GREEN / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE GENERATED
YELLOW / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE INCOMPLETE
RED / ANOTHER BOUNDED LOCAL FREQUENCY ARTIFACT INVALID
```

Include commit/parent/five blobs, 55 pair hashes, ledger/contracts, 115/114,
aggregate/audit/manifest roots, exact 2,352/1,760/80 counts, tests, scope, and
non-claims. Return only to T0; do not start T7cf.

## Recovery And Stop Rules

Twelve hours is soft only. Preserve atomic state on confirmed system/capacity
interruption. Genuine failure cannot be bypassed by model switch. No threshold
relaxation, lmax extension, automatic/recursive midpoint, uniform/full grid,
production, plot, fixture, Kirchhoff, paper-style output, new/replacement task,
downstream dispatch, or GitHub action.
