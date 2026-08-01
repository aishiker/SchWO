# T4ag Hermetic Runtime-Provenance Repair Plan

## Goal

Repair only the missing isolated Python runtime dependencies that caused the
valid T4af prospective witness to fail at import. Preserve that RED evidence,
freeze a content-addressed read-only runtime overlay under zero-science
preflight, and permit a new prospective witness only after independent T7
package review and root-T0 checkpoint audit.

## Task 1 — Package Review

T7 reads the exact T4ag four-file candidate, T4af package, failed witness,
driver/preflight evidence, runner import graph, installed-package identities,
canonical guards, and current process/transient state.

Only exact:

```text
REVIEW GREEN / T0 RUNTIME REPAIR PACKAGE APPROVED
```

permits Task 2.

## Task 2 — Runtime Source And Old-Evidence Freeze

Using the same T4 task with `gpt-5.6-sol/ultra`:

1. verify every frozen identity and the T4af RED evidence;
2. verify zero scientific/control process and zero transient state;
3. preserve the old driver and old evidence without overwrite;
4. verify exact installed SciPy 1.17.1 and PyYAML 6.0.3 source roots,
   distribution metadata, absence of links/special files, and source hashes;
5. stop on any drift or unreviewed dependency requirement.

No scientific runner, solver, witness, audit, or matrix process may start.

## Task 3 — Build The Hermetic Overlay

Create one fresh unique evidence root under the frozen control root.

- Copy only SciPy and PyYAML distribution files.
- Exclude and reject bytecode, `__pycache__`, `.pth`, links, special files,
  path escapes, duplicate targets, and pre-existing destinations.
- Use exclusive writes, file and directory fsync, source before/after hashes,
  target re-hashes, read-only permissions, and atomic content-addressed
  publication.
- Record package versions, RECORD/WHEEL/METADATA hashes, compiled extensions,
  Mach-O dependencies, source/target stat identities, and a canonical index.
- Record NumPy 2.4.6 origin/configuration as part of the accepted base Python
  runtime without copying the Homebrew symlink farm.

Any failed build remains immutable failed evidence and stops the package. It
cannot be cleaned or retried without root-T0 review.

## Task 4 — Bounded Driver Remediation

Modify only the artifact-local durable driver and solver-free tests:

- add the closed runtime-overlay manifest/binding schema;
- require exact `PYTHONPATH`, `PYTHONNOUSERSITE=1`, isolated `HOME`, and
  no-bytecode environment;
- validate the overlay and imported module origins before and after every
  scientific child;
- bind the same overlay to the matching official audit;
- preserve every existing process, source/input, audit, path, canonical, and
  scientific contract unchanged.

The single existing proxy may provide read-only control-plane review. No new
subagent or descendant is allowed.

## Task 5 — Full Zero-Science Preflight

After static review:

1. run the import-only probe for exact required modules and origins;
2. run the complete prior T4af solver-free suite plus runtime-overlay
   positive/negative/fault cases;
3. run AST, Ruff, `git diff --check`, raw/capture index, Python/environment,
   old-evidence, canonical hash/stat/inode, absent-unit, process/transient,
   symlink/hardlink, and no-bytecode checks;
4. prove scientific runner CLI invocation `0`, official audit invocation
   `0`, and solver invocation `0`.

Return exactly:

```text
CHECKPOINT / HERMETIC RUNTIME ENVIRONMENT FROZEN
```

Then pause.

## Task 6 — Root-T0 Checkpoint Audit

T0 independently recomputes:

- builder and driver source hashes/diffs;
- every overlay source and target hash/stat/mode/inode;
- runtime manifest and canonical index;
- module origins, versions, compiled-extension and Mach-O closure;
- all preflight raw records, captures, tests, rejection reasons, and zero
  science counts;
- frozen identities, old evidence, canonical guards, absent units, and
  process/transient state.

Only a complete fresh PASS permits:

```text
AUTHORIZED / HERMETIC-RUNTIME CONTROL-PROVENANCE WITNESS COMPUTE
```

## Task 7 — One New Prospective Witness

Run one isolated existing `kM=1.58125` witness with:

- detached clean exact implementation `45face32...`;
- exhaustive 48-item actual-input contract;
- the frozen runtime overlay and new durable driver;
- exact Python/runner/benchmark identities;
- write-disjoint output and strict canonical read-only guards.

After producer exit0/empty stderr/reaped/PG-empty and atomic pair PASS, run
the matching official audit through the same driver and runtime overlay.
Then compare witness, canonical, legacy, and golden data under the unchanged
T4af contract.

Any failure consumes the authorization and stops. Do not retry.

## Task 8 — Conditional Matrix And Final Review

Only after root-T0 witness PASS:

```text
2.91875 -> 3.759375 -> 3.89375 -> full 241x241
```

Run one unit at a time with durable producer plus official audit and all
canonical guards. Complete the frozen T4ae verification. Only T4 exact GREEN
plus root-T0 full fresh PASS permits the frozen T7ch review.

## Scope And Non-Claims

No global environment change, install, network dependency retrieval,
implementation/runner/config/input edit, scientific criterion change,
frequency expansion, production/plot/fixture/Kirchhoff/paper/GitHub work, or
new task/subagent is authorized.
