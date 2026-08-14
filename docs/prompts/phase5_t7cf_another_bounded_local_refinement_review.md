# T7cf — Another Bounded Local Frequency Evidence Independent Review

Work only in existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` as a
read-only scientific reviewer. Do not create a task, repair artifacts, or start
downstream work. Normal review uses `gpt-5.6-sol/high`.

## Start Gate

Fully read `project.md`, `status.md`, current T0/T4/T7/T8 handoffs, the exact
reviewed candidate design/plans/prompts, T4ad/T7ce gate, T8as artifacts, T7cd
evidence, T8ar sources, and earlier immutable sources. Verify candidate
identity and require exact
`GREEN / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE GENERATED` plus T0 fresh
verification. Stop on mismatch.

Archive the measured pre-review T7ce handoff byte-for-byte at:

```text
docs/handoffs/archive/T7_2026-07-20_pre_t7cf_another_bounded_local_review.md
```

Record its measured SHA-256 before changing the live handoff.

## Allowed Writes

Only `status.md`, `docs/handoffs/T7_current.md`, and the archive path above.

## Independent Artifact Gate

Without T8as loaders, aggregation, sampling, migration, or acceptance helpers:

1. Verify exact five-path implementation commit/parent/blobs and commit
   precedence over all transactions.
2. Direct-load exactly 55 pairs; verify tokens/order/eight points, lmax
   histories/final rows, shapes, actual dtypes, units, finiteness, masks,
   final-pair `<=1e-4`, sidecar/embedded metadata, fingerprints, and ledger.
3. Require exactly 115 active files, 114 manifest records, no
   temp/quarantine, and exact manifest hashes.
4. Independently reconstruct contracts, source/gate/code hashes, atomic
   completion/resume identity, and direct aggregate stacking.
5. Verify immutable T7cd/T8ar/T4ad/T7ce and earlier sources, schemas,
   snapshots, adapter identity, and provenance.

Any artifact/hash/contract/source/nonfinite/mask/convergence/test/scope or
provenance failure is RED.

## Independent Scientific Gate

Hard-code the five sequences and 55-row map from the design; never infer float
adjacency. For exactly 2,352 records require:

```text
phase = np.unwrap(np.angle(F), axis=frequency)
abs(diff(phase)) < pi/2
```

For exactly 1,760 records, with nonnegative magnitudes
`a=|F(k_i)|` and `b=|F(k_j)|`, require:

```text
relative_step(a,b) = abs(a-b) / max(1,a,b)
new_child_step <= exact_T7cd_failed_child_parent_step + 2e-15
```

Use direct immutable complex rows. Report every failure with full attribution,
values, phases, parent/child steps, excess, and diagnostic-only midpoint.
Reconstruct all 80 summaries, variation/cancellation/largest steps, and strict
interior extrema. Invent no threshold.

## Tests And Isolation

Run focused tests, exact-five Ruff, fresh full pytest, `git diff --check`,
exact implementation/artifact/source scope checks, warning classification, and
both frozen forbidden-output searches. Both searches must be empty.

## Exact Decision

```text
ACCEPT GREEN / ANOTHER BOUNDED LOCAL FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL REFINEMENT REQUIRED
REJECT RED / ANOTHER BOUNDED LOCAL FREQUENCY ARTIFACT INVALID
```

GREEN requires the complete artifact gate and all 2,352 phase plus 1,760
hierarchy records to pass. YELLOW is valid artifact plus scientific failure.
Return only to T0 and start nothing.

## Forbidden

No repair, threshold relaxation, lmax extension, automatic/recursive midpoint,
uniform/full grid, production, plot, fixture, Kirchhoff, paper-style work,
downstream dispatch, new/replacement task, or GitHub action.
