# T4af Control-Provenance Witness Repair Design

Date: 2026-07-25

Status: T0 bounded-repair candidate after the exact T4ae decision
`YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE`. This
document does not change the frozen T4ae scientific, numerical, performance,
artifact, or interface contract. It authorizes no new scientific frequency.

## 1. Trigger And Exact Defect

T4ae produced two complete optimized NPZ/JSON pairs. Both pairs independently
pass their scientific, schema, ordering, finite-pattern, fingerprint,
warning, cache, residual, provenance, and atomic-transaction audits. The
second pair, at `kM=1.58125`, nevertheless lacks a durable record of the
original runner's final exit code and stderr because the Codex exec-session
handle was not retained.

The later audit exited `0`, but it cannot reconstruct the original process
exit. T4ae therefore correctly stopped with YELLOW. The defect is limited to
control-plane provenance; it is not evidence of a numerical or scientific
failure.

This repair must retain both facts:

1. the original `kM=1.58125` exit/stderr record is irrecoverable and must
   never be claimed otherwise;
2. a new, separately identified reproducibility witness may add prospective
   control evidence, but may not replace or overwrite the original pair.

## 2. Immutable Starting Identity

```text
T4ae methods candidate          39f89289c01af7ae1709ee1e4458450d0e88b49e
candidate parent                8fb8608c187280dc39fd56a78b976e6cf75a6ada
T4ae implementation commit      45face32f52537ac4b8ab79cb1746d8ac78e9b82
implementation parent           39f89289c01af7ae1709ee1e4458450d0e88b49e
committed runner SHA-256        18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
optimized benchmark identity    46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48
```

The exact fourteen implementation paths at `45face32...`, all frozen T4ae
design/plan/prompts, the legacy baseline, accepted goldens, and existing
optimized pairs remain immutable.

Existing optimized pair hashes:

```text
kM=0.86875
  NPZ      e95d28f4b3d0f35a770430ec074dc47f24b93dc7a2e1785e9646ff4581955f91
  sidecar  3a24f316c9c78c72d382fd68c3409f8833fd10c073e942a56d7e8509c4f595d6
kM=1.58125
  NPZ      36ff7902d86762ad3f93bf1b386275cc7b5ca89c50c4f8b448a99592089e5bd9
  sidecar  d60277384e6edb1d2192d8a6e0a111cfd21a9be20ddbf976f05d7ec30a712c28
```

Before and after every repair action, T4af must verify these four hashes and
must verify that no live runner, lock, temporary, partial, or quarantine file
exists.

## 3. Unchanged Contracts And Non-Claims

Every frozen T4ae condition remains in force, including:

- physical conventions, solver tolerances, frequencies, modes, points,
  lmax, image resolution, independent validation, and scientific thresholds;
- exact schema/dtype/unit/axis/mask/order requirements;
- the predeclared complex, magnitude, guarded-phase, residual, image,
  determinism, cache, checkpoint, performance, and resource gates;
- exact-fourteen implementation scope and implementation identity;
- no new spin-2 physics claim;
- no new frequency, production, plot, fixture, Kirchhoff, paper-style
  output, or GitHub action.

The witness is not counted as a sixth frequency case, is not included in the
performance aggregate, is not a cache/checkpoint input, and is not eligible
for downstream scientific use.

## 4. Two-Phase Authorization

T4af has two strictly separated phases.

### 4.1 Phase A — durable-control freeze, no scientific compute

Using `gpt-5.6-sol/ultra`, T4 may create an artifact-local control driver only
under:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
```

The driver is orchestration instrumentation, not scientific implementation
code. Before any witness computation it must:

1. freeze its own source SHA-256, Python/environment identity, exact argv,
   cwd, and allowed output roots;
2. use argv arrays rather than a shell to start the scientific child;
3. write an atomic prelaunch record before starting the child;
4. persist child PID/start time, stdout and stderr to distinct files;
5. survive a Codex control-stream disconnect without depending on an
   in-memory exec handle;
6. wait for the exact child and atomically write a final record containing
   exit code, terminating signal if any, end time, elapsed time, and
   stdout/stderr hashes and byte counts;
7. fail closed on a missing/ambiguous final record, unexpected process,
   duplicate runner, path escape, or output collision.

Synthetic preflight must cover normal exit `0`, nonzero exit, signal
termination, nonempty stdout/stderr, stale lock rejection, duplicate launch
rejection, and atomic-final-record behavior. Phase A must return the exact
intermediate checkpoint:

```text
CHECKPOINT / DURABLE CONTROL DRIVER FROZEN
```

T4 must then pause. T0 must freshly inspect the source, hash, synthetic raw
records, process state, paths, and scope before issuing the exact follow-up:

```text
AUTHORIZED / CONTROL-PROVENANCE WITNESS COMPUTE
```

No witness or remaining benchmark computation may precede that follow-up.

### 4.2 Phase B — one isolated witness, then conditional continuation

After the exact T0 authorization, the frozen driver may run one and only one
isolated witness for existing case `kM=1.58125`.

The witness must use:

- a detached clean source snapshot at exact implementation commit
  `45face32...`;
- the exact committed runner bytes and exact benchmark/environment identity;
- content-verified read-only upstream inputs;
- an isolated output root that cannot resolve to the canonical optimized
  output root;
- the same physical inputs, solver tolerances, mode/point/lmax ordering,
  thread controls, and independent checks as the canonical run.

The input-mount/copy manifest must enumerate every source and target path,
file hash, mutability rule, and resolved real path. No writable symlink or
path may lead from the witness output to a canonical artifact.

## 5. Witness Acceptance

The isolated witness passes only if all of the following are true:

1. durable final control record exists and binds the exact PID, argv, cwd,
   driver SHA, runner SHA, implementation commit, benchmark identity, start
   and end times;
2. child exit is exactly `0`, no terminating signal exists, stderr is empty,
   and stdout contains the expected terminal `optimized_case_complete`
   record;
3. the witness NPZ/JSON pair and its independent runner audit both complete
   with exit `0`, with no temporary, lock, partial, or quarantine residue;
4. direct no-helper loading proves exact schema/dtype/unit/axis/mask/order,
   finite pattern, warning classification, cache accounting, fingerprints,
   and scientific arrays;
5. every scientific array is bitwise equal to the canonical optimized pair,
   the immutable legacy baseline, and the accepted golden where applicable;
6. path-dependent metadata differs only in a predeclared allowlist limited
   to isolated output paths, witness/control identity, timestamps, and raw
   resource/timing observations;
7. the four canonical optimized hashes in section 2 remain unchanged and no
   canonical file was opened for write.

The new record proves only that the same frozen implementation can reproduce
the case under durable prospective control. It does not retroactively assert
an exit code for the original run.

Any scientific, numerical, identity, provenance, warning, schema, ordering,
finite-pattern, or canonical-hash mismatch is RED. A system/capacity loss or
missing durable final record is YELLOW. Neither result permits a retry or
continuation without a new T0 decision.

## 6. Conditional Completion Of The Original Matrix

Only after the isolated witness passes and T0 freshly verifies it may T4af
continue the original frozen T4ae matrix.

The two canonical complete cases remain immutable and are not recomputed.
The only allowed canonical computations are the still-absent work units, in
this fixed order:

```text
kM=2.91875
kM=3.759375
kM=3.89375
full accepted 241x241 image configuration
```

Each work unit must use the already-frozen implementation and the same
durable control driver. Each final control record and atomic artifact pair
must be validated before the next work unit starts. A control anomaly,
scientific anomaly, code-change requirement, or identity mismatch stops the
matrix immediately.

No code change is authorized. If canonical code, tests, runner behavior, or
the driver must be changed after its Phase-A freeze, T4 must stop and return
to T0; existing matching work remains immutable.

## 7. Allowed Writes

Before witness acceptance:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/**
docs/handoffs/T4_current.md
docs/handoffs/archive/T4_2026-07-25_pre_t4af_control_provenance_witness.md
status.md
```

After witness acceptance, the original T4ae output paths may additionally
receive only the four absent canonical work units and the already-frozen
methods manifest/note updates. Existing pair paths are write-forbidden.

No implementation, frozen design/plan/prompt, legacy/golden, upstream
artifact, configuration, threshold, task, or downstream path may change.

## 8. Model And Process Policy

- Driver design, code authoring/modification, debugging, identity decisions,
  anomaly handling, and scientific/provenance interpretation require
  `gpt-5.6-sol/ultra`.
- After driver/source/config/resume identities are frozen and T0 has issued
  the exact Phase-B authorization, fixed-command launch, polling, and raw
  metric collection may use `gpt-5.6-terra/medium`.
- Any anomaly returns immediately to `gpt-5.6-sol/ultra`.
- A model/control-stream interruption must never kill a healthy unique
  runner, create a duplicate, or recompute a complete matching work unit.

## 9. Final Decision

After the witness and the entire original T4ae verification matrix, T4
returns exactly one original methods-gate decision:

```text
GREEN / EQUIVALENCE-PRESERVING METHODS GATE READY
YELLOW / EQUIVALENCE-PRESERVING METHODS EVIDENCE INCOMPLETE
RED / EQUIVALENCE-PRESERVING METHODS GATE INVALID
```

T4af never dispatches T7ch or any downstream task.
