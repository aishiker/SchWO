# T4ah Recursive Input-Package Closure Repair Design

## 1. Purpose

T4ah repairs one bounded control-provenance defect exposed by the valid
T4ag prospective witness:

- the detached witness manifest bound 48 individually hashed inputs;
- the frozen scientific runner also calls
  `tablei_another_bounded_local_refinement._input_records()`;
- before returning its individually hashed records, that function recursively
  enumerates six accepted upstream package directories and requires their
  exact active-file cardinalities;
- the detached snapshot contained only the individually named subset, so the
  first package check saw T8ao `active=5` instead of the required `23`.

This is an input-provisioning and input-provenance closure defect. It is not
a runtime-import failure, solver failure, scientific mismatch, or reason to
change the frozen scientific runner.

T4ah must preserve every T4af/T4ag scientific and process contract while
expanding the detached input manifest to cover every file actually observed
by the frozen recursive package checks.

## 2. Frozen Failure Evidence

The consumed T4ag one-shot witness is immutable:

```text
control root
  runs/phase5/equivalence_preserving_methods_gate/
    control_provenance_witness/
      witness_kM_1p58125_hermetic_20260726T195704p0800

request
  SHA-256 7edbd4efec7388b268146ae71166e80daad910ab5391a95060eee332bf9c91b3

prelaunch
  SHA-256 83d1495a150de7d0508809bfda995dc3dbb709edee719db9ee2aa1fcd2c45459

running
  SHA-256 f0141909150d1c40789097141b77bd7e5d0bf47cc16c56343653f305f8ebd444

final
  SHA-256 935c9e8c12136d1d69bec071e22065760c3bf2f1da855fbb897cbc81d0eb0f1f

stderr
  2769 bytes
  SHA-256 018277d431fb995eaafdb8cf5fa8985f86976d3f4e0fc461ce9a0c484d969366

stdout
  0 bytes
  SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

control audit stdout
  SHA-256 b275b3ab397cfc453b9841481b58cc8219a665f4681feaa69bc498c9d09196d2
```

The exact result was:

- child exit code `1`, no signal;
- child PID `27561`, SID/PGID `27561`, exact-waited and reaped;
- process group empty, zero wait errors;
- supervisor PID `27544` exited and is absent;
- runtime overlay and required import probe matched before and after;
- scientific runner CLI invocation `1`;
- scientific solver invocation `0`;
- official scientific audit invocation `0`;
- no isolated output pair;
- no retry, duplicate, audit, or matrix launch;
- canonical four-file hash/stat/inode guards unchanged;
- all four later work units still absent.

The traceback terminates at:

```text
accepted T8ao cardinality/temp mismatch: active=5
```

The T4ag authorization is consumed. This evidence may not be deleted,
overwritten, repaired, resumed, or reinterpreted as a witness PASS.

## 3. Frozen Identities

T4ah inherits without modification:

```text
primary implementation
  45face32f52537ac4b8ab79cb1746d8ac78e9b82

T4af package candidate
  78b80129515d5c5ae60de9ec3367d6e3d12925d5

T4ag package candidate
  9c1df700602cf998646b90c76b12abb3a69d6a84

scientific runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768

T4ag durable driver
  cc06f1ac7757b7ce5275033381bcac2854544703ec3a598dc25e0fe5fe610804

T4ag Phase-A preflight
  9980fdf2bcc80592fac1cf6719885cc977b51bd5fb635b13e1468901c0afcb9f

runtime overlay manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca

runtime overlay content index
  1803e0f763cac682442b22af8986b240e5830a1a42849c77ae2c7aa96fc39371

benchmark identity
  46403a00663fc331a8b4c9941d66b2c597d2301f883c24804b5a01cd9bc06c48

benchmark environment
  04b4a8c8964716ae0ee46b2a4736cbe47cd1212f60a08a212c2366fbbc387615

CPython 3.14 binary
  b502cb4c5b46b8d4192ec6bcb600ce8922f1afc396fcf646e8765c6eba74a0bf
```

The implementation, runner, Table-I module, configs, upstream artifacts,
canonical pairs, thresholds, tolerances, resolution, modes, points, `lmax`,
independent checks, runtime overlay, and previous evidence are read-only.

## 4. Exact Missing Dependency Geometry

The frozen Table-I code recursively observes every active regular file below
six roots, excluding only paths with a path component exactly equal to
`quarantine`.

Fresh root-T0 reconstruction established:

| Label | Repository-relative root | Required active files | Detached files in failed witness | Missing |
|---|---|---:|---:|---:|
| T8ao | `runs/phase5/fig5_fig6_delta0p1_risk_pilot` | 23 | 5 | 18 |
| T8ap | `runs/phase5/fig5_fig6_targeted_adaptive_refinement` | 31 | 5 | 26 |
| T8aq | `runs/phase5/fig5_fig6_further_local_refinement` | 53 | 5 | 48 |
| T8ar | `runs/phase5/fig5_fig6_literal_failed_child_refinement` | 87 | 5 | 82 |
| T4aa | `runs/phase5/fig5_fig6_targeted_adaptive_radial_gate` | 17 | 4 | 13 |
| T4ad | `runs/phase5/fig5_fig6_another_bounded_local_radial_gate` | 59 | 4 | 55 |

The six roots contain exactly 270 active members. Twenty-eight are already
present in the 48-item contract; 242 are missing. The corrected complete
witness contract therefore contains exactly 290 distinct target paths.

Fresh root-T0 inventory identities are:

| Label | Files | Bytes | Content index SHA-256 |
|---|---:|---:|---|
| T8ao | 23 | 874263 | `261eba4ff93798930b59a56c506f88c782ea3f5c708e87b1ef0efe1ace14368d` |
| T8ap | 31 | 2578480 | `d0904b22948a340b65a8bd067a623a86a7b610d0abd253c888948d02f8b3dcaa` |
| T8aq | 53 | 5846336 | `11facd27f6256908a41f675bb6ad25ffd59ca9a6ec5ce107fe481574e4eaf86e` |
| T8ar | 87 | 12385978 | `4e33ad4c1bf6ab5d19635d87ad85a0226fc84edb9e747a00500d251e2c7d4d76` |
| T4aa | 17 | 52851473 | `7f539922b54f09447226a2a99bdb79c7ec59c5dd6470f36703ccb11f1a8879df` |
| T4ad | 59 | 324890249 | `2900b37dff15b4afada49586c114f4f1fcd2740be91304d05009d42484b4532c` |

Combined:

```text
270-member package content index
  720216bc1c37603cad06f6c88f5dbda26128604d9c3b3720927875cbda11c8c6

270-member package membership index
  9f0a743db65793ff4aa28ea9f0890985914a0c3b4bc9a96622a5fefdea28b0d1

290-entry corrected driver contract index
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
```

These indexes use the exact canonicalization below. There is no locale,
collation service, shell sort, Node `localeCompare`, filesystem enumeration
order, or platform-dependent comparison:

1. A repository-relative path is a Unicode string containing `/` separators.
   Sort keys with Python `sorted` / ordinary `str` comparison, i.e. Unicode
   code-point lexicographic order.
2. Canonical JSON is UTF-8 encoding of
   `json.dumps(value, allow_nan=False, ensure_ascii=False,
   separators=(",", ":"), sort_keys=True)`, with no trailing newline.
3. An index is SHA-256 of those exact canonical JSON bytes.
4. Each per-package content payload is a list in path order. Every item has
   exactly `{"path": <repository-relative path>, "sha256": <lowercase
   hex>, "size": <integer bytes>}`.
5. The combined-content payload is the globally path-sorted flattening of
   those records, with exactly one additional field
   `"label": <lowercase package label>`.
6. The membership payload is globally path-sorted and contains exactly
   `{"label": <lowercase package label>, "ordinal": <one-based integer>,
   "path": <repository-relative path>}`. `ordinal` is the position in that
   package's complete code-point-sorted active inventory, including old
   semantic overlaps.
7. The final driver-contract payload is globally sorted by
   `target_repository_path`; each item has exactly
   `{"role": <string>, "sha256": <lowercase hex>,
   "target_repository_path": <repository-relative path>}`.

All 270 current source members are regular, non-symlink, `nlink=1`, have
distinct device/inode identities, and contain no active `.tmp`, `.partial`,
or lock file. T4/T7 must independently recompute these facts; the values
above are frozen acceptance identities, not permission to trust an
unverified copy.

## 5. Closed Contract Construction

The driver must change the witness input schema to a new version and derive
the complete contract deterministically.

### 5.1 Preserve the existing semantic records

All 48 existing roles, paths, and hashes remain exact. No existing semantic
record may be removed, renamed, redirected, or weakened.

### 5.2 Add recursive package members

For each of the six exact roots:

1. recursively enumerate repository-relative paths in the frozen Unicode
   code-point order from section 4;
2. exclude only a path component exactly equal to `quarantine`;
3. reject any symlink, hardlink/shared inode, special file, path escape,
   bytecode/cache, `.tmp`, `.partial`, lock, case/Unicode alias, duplicate,
   unexpected directory, unexpected count, or source drift;
4. require the exact active count and content index in section 4;
5. retain the existing semantic role when a path is already one of the 48
   records;
6. add every other member using deterministic roles:

```text
tablei-package:<lowercase-label>:<three-digit one-based ordinal>
```

The ordinal is the member position in the complete sorted active inventory
of that package, including members that already have semantic roles.

The final contract is sorted by `target_repository_path`, has 290 entries,
and must equal the frozen index:

```text
77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
```

The contract generator must verify that every member of the six package
inventories appears exactly once in the final contract with the same hash.
It must not infer acceptance from count alone.

## 6. Detached Publication And Manifest Rules

Every one of the 290 source files must be copied into the detached exact
implementation snapshot at its exact repository-relative target.

For every source and target:

- lstat before copying;
- reject source or target alias, symlink, hardlink/shared inode, special
  file, path escape, duplicate path, and pre-existing destination;
- copy without following links using exclusive creation;
- flush and fsync file and created parent directories;
- verify exact source/target SHA-256 and size;
- publish with no-overwrite atomic semantics;
- set the detached target read-only;
- re-lstat and re-hash the source after all copies;
- bind source/target path, realpath, hash, size, mode, device, inode, nlink,
  role, and repository-relative target in the input manifest.

The complete detached package directories must contain exactly the frozen
active inventories and no extra file. No `quarantine` subtree is copied.

The detached source, input manifest, runtime overlay, output root, control
root, canonical optimized tree, and source roots must remain pairwise
non-overlapping and non-aliased.

## 7. Bounded Driver Change

T4ah may modify only:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/durable_control_driver_v2.py
```

and fresh T4ah control/preflight evidence beneath the same control root.

Allowed code changes are limited to:

- the new witness input-manifest schema;
- deterministic six-package inventory and 290-entry contract generation;
- exact frozen count/content/index validation;
- detached manifest validation for the added members;
- positive and negative solver-free tests for this closure;
- immutable bindings to the T4ag RED witness and previous T4ag
  driver/preflight/overlay evidence.

The existing durable supervision, runtime overlay, import probes,
post-Popen fault behavior, locks, atomic records, producer/official-audit
binding, source manifest, matrix semantics, scientific commands, canonical
guards, and scientific acceptance criteria must remain unchanged.

No runner, implementation, package source, config, input, threshold,
tolerance, resolution, mode, point, `lmax`, scientific check, canonical
pair, legacy/golden artifact, or frozen package file may be modified.

## 8. Phase A — Exact Zero-Science Freeze

Before editing, T4 must preserve the exact T4ag driver and all T4ag RED
evidence in a fresh unique no-overwrite evidence root.

T4 then:

1. changes only the bounded driver surface in section 7;
2. statically proves the 290-entry contract and all six inventories;
3. runs all prior exact Python-3.14 T4ag tests, CLI captures, rejection
   cases, runtime-overlay cases, process/fault/lock/audit cases;
4. adds positive and negative tests for missing, extra, quarantined,
   wrong-hash, wrong-role, wrong-path, wrong-count, source-drift, symlink,
   hardlink/shared-inode, writable-target, alias, `.tmp`, `.partial`, lock,
   duplicate, and package-index mismatch;
5. proves a solver-free detached synthetic fixture reaches the Table-I
   recursive package checks with exact cardinalities;
6. runs AST, Ruff, `git diff --check`, raw/capture index, Python/runtime,
   old-evidence, canonical, absence, process, transient, link, and
   no-bytecode checks.

Scientific runner CLI, official audit, and solver invocation counts must all
be exactly zero.

Any failed preflight is immutable failed evidence and stops. It is not
retried without a new root-T0 decision.

Complete PASS returns exactly:

```text
CHECKPOINT / RECURSIVE INPUT PACKAGE CONTRACT FROZEN
```

and pauses for root T0.

## 9. Independent Review And New Witness

T7 must independently review this exact four-file T4ah package before T4ah
starts. T4ah requires exact:

```text
REVIEW GREEN / T0 RECURSIVE INPUT PACKAGE REPAIR APPROVED
```

After Phase A, root T0 independently audits the complete driver diff,
contract/inventory indexes, every raw record/capture/test, environment,
frozen evidence, canonical guards, absence, and process state.

Only complete root-T0 PASS permits a new, separately reviewed one-shot:

```text
AUTHORIZED / COMPLETE-INPUT CONTROL-PROVENANCE WITNESS COMPUTE
```

That witness is still only the existing isolated `kM=1.58125` case.
Failure consumes the authorization; no retry or duplicate is implicit.

## 10. Conditional Matrix And Non-Claims

Only after the producer, matching official audit, scientific equivalence,
metadata allowlist, canonical guards, and root-T0 witness audit all pass may
T0 authorize:

```text
2.91875 -> 3.759375 -> 3.89375 -> full 241x241
```

one unit at a time.

T4ah authorizes no new frequency, production expansion, plot, fixture,
Kirchhoff calculation, paper claim, GitHub action, global environment
change, install, network retrieval, cleanup, or destructive action.

## 11. Orchestration And Reasoning Budget

Use only the existing T4 and T7 tasks. Do not create a task, subagent,
proxy, or descendant.

T4 code work uses `gpt-5.6-sol/high`. It may use
`gpt-5.6-sol/max` only after root T0 determines that a genuinely complex
code/science/safety/provenance interaction exceeds `high`. T4 code work
must not use `ultra`. Mechanical inventory, manifest, hash/path, formatting,
and ordinary test maintenance remain at `high`.
