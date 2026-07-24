# T7ch — Equivalence-Preserving Methods Independent Review

Work only in existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` as an independent reviewer. Do not
create or replace a task, repair code/artifacts, or start any downstream work.
Normal review uses `gpt-5.6-sol/high`.

## Start Gate

Fully read `project.md`, `status.md`, current T0/T4/T7/T8 handoffs, the exact
reviewed five-file methods package, T4ae note/artifacts, T7cf evidence,
immutable T4ad/T8as sources, and applicable physics/architecture/numerics/
validation/extension documents.

Require exact:

```text
GREEN / EQUIVALENCE-PRESERVING METHODS GATE READY
```

Verify package identity, exact T4ae implementation commit/parent/path blobs,
baseline-before-edit precedence, artifact hashes, and source/config/cache
identity before evaluating results.

## Independent Checks

1. Direct-load the legacy and optimized benchmark artifacts without T4ae
   acceptance helpers.
2. Recompute exact schema/dtype/unit/order/mask equality and all complex,
   magnitude, guarded-phase, residual, lmax-delta, NRMSE, and L-infinity
   metrics under the predeclared error budget.
3. Recompute wall/user/system CPU, peak RSS, solve/cache counts, per-stage
   timings, and every performance ratio from raw records.
4. Verify all five existing frequency cases and the full accepted `241x241`
   image regression; forbid resampling, smoothing, clipping, lower
   resolution, or changed normalization.
5. Audit complete cache keys and independently inject identity mismatches.
   Radius-specific certified oracle states must not be merged.
6. Audit serial/two-worker stable ordering, worker/thread bounds, atomic
   resume, stale/partial/corrupt checkpoint rejection, and no recomputation
   of complete matching work.
7. Audit typed subsystem separation and explicit convention/provenance
   metadata. Confirm the legacy adapter preserves behavior, the generic API
   does not hard-code Schwarzschild separability, and no new spin-2 physics
   is implemented or claimed.
8. Run focused tests, exact-scope Ruff, fresh full pytest,
   `git diff --check`, exact commit/worktree/source checks, warning
   classification, and forbidden-output searches.

## Exact Decision

Return exactly one:

```text
ACCEPT GREEN / EQUIVALENCE-PRESERVING METHODS GATE ACCEPTED
ACCEPT YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE
REJECT RED / EQUIVALENCE-PRESERVING METHODS GATE INVALID
```

GREEN requires every scientific-equivalence, provenance, performance,
interface, deterministic-order, cache, checkpoint, test, and scope check.
Return only to T0.

## Forbidden

No repair, tolerance/threshold/lmax/frequency/mode/point change, new
scientific package, production, plot, fixture, Kirchhoff, paper-style output,
task creation/replacement, downstream dispatch, or GitHub action.
