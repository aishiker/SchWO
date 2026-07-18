# T7cd — Literal Failed-Child Frequency Evidence Independent Review

Work only in existing T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed` as a
read-only scientific reviewer. Do not create a task, repair artifacts, or
start downstream work. Normal review uses `gpt-5.6-sol/high`.

## Start Gate

Fully read `project.md`, `status.md`, current T0/T4/T7/T8 handoffs, the exact
reviewed candidate design/plans/prompts, T4ac/T7cc gate, T8ar artifacts,
T7cb evidence, and immutable T8aj/T8ao/T8ap/T8aq sources. Verify candidate
identity and require T8ar exact
`GREEN / LITERAL FAILED-CHILD FREQUENCY EVIDENCE GENERATED` plus T0 fresh
verification. Stop on mismatch.

Archive the pre-review T7cc handoff byte-for-byte at:

```text
docs/handoffs/archive/T7_2026-07-18_pre_t7cd_literal_failed_child_review.md
```

Record its measured SHA-256 before changing the live handoff.

## Allowed Writes

Only:

```text
status.md
docs/handoffs/T7_current.md
docs/handoffs/archive/T7_2026-07-18_pre_t7cd_literal_failed_child_review.md
```

## Independent Artifact Gate

Without calling any T8ar loader, aggregation, sampling, migration, or
acceptance helper:

1. Verify exact five-path implementation commit/parent/blobs and that it
   predates every transaction.
2. Direct-load exactly 41 NPZ/JSON pairs; verify tokens/order/eight points,
   lmax histories/final rows, shapes, actual dtypes, units, finiteness, true
   masks, final-pair `<=1e-4`, sidecar/embedded metadata, fingerprints, and
   ledger hashes.
3. Require exactly 87 active files, 86 manifest records, and no
   temp/quarantine.
4. Independently reconstruct generation/metadata contracts, source/gate/code
   hashes, atomic completion/resume identity, and manifest.
5. Direct-stack all pairs and require exact aggregate key/order/shape/dtype/
   value identity.
6. Verify all immutable T8aj/T8ao/T8ap/T8aq/T7cb and T4ac/T7cc sources,
   schemas, contracts, snapshots, adapter identity, and provenance.

Any artifact, hash, contract, source, nonfinite, mask, convergence, test,
scope, or provenance failure is RED.

## Independent Scientific Gate

Hard-code the five literal sequences and 41-row parent map from the design;
never infer float adjacency.

For exactly `92*8*2 = 1,472` records:

```text
phase = np.unwrap(np.angle(F), axis=frequency)
abs(diff(phase)) < pi/2
```

For exactly `41*2*8*2 = 1,312` records:

```text
relative_step(a,b) = abs(a-b) / max(1,a,b)
new_child_step <= exact_T7cb_failed_child_step + 2e-15
```

Use direct immutable complex rows, not rounded handoff values. Report every
failure with interval, point/component, complex values, magnitudes, phases,
parent/child steps, excess, and diagnostic-only next midpoint. Reconstruct all
80 summaries, total variations, cancellations, largest steps, and all strict
interior extrema. Invent no threshold.

## Tests And Isolation

Run focused tests, Ruff on the exact five paths, fresh full pytest,
`git diff --check`, exact implementation/artifact/source scope checks,
known-warning classification, and both frozen forbidden-output searches. Both
searches must be empty.

## Exact Decision

Return exactly one:

```text
ACCEPT GREEN / LITERAL FAILED-CHILD FREQUENCY EVIDENCE ACCEPTED
ACCEPT YELLOW / ANOTHER BOUNDED LOCAL REFINEMENT REQUIRED
REJECT RED / LITERAL FAILED-CHILD FREQUENCY ARTIFACT INVALID
```

GREEN requires the complete artifact gate and all 1,472 phase plus 1,312
hierarchy records to pass. YELLOW is valid artifact plus one or more
scientific failures. RED is artifact/computation/test/provenance/scope
invalidity. Return only to T0 and start nothing.

## Forbidden

No repair, threshold relaxation, lmax extension, automatic/recursive
midpoint, uniform/full grid, production, plot, fixture, Kirchhoff, paper-style
work, downstream dispatch, new task, or GitHub action.
