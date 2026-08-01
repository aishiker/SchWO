# T4ak Split-Root Preservation Helper Repair Design

## 1. Purpose

T4ak repairs the exhausted T4aj Phase-A0 helper-freeze attempt without
reusing or modifying any prior helper or evidence root.

T4aj stopped before launching its audit child. The frozen helper source
contains direct AST constants for the project and control roots, but derives
the evidence root with a `JoinedStr`:

```python
PROJECT_ROOT_TEXT = "/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO"
CONTROL_ROOT_TEXT = (
    "/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/"
    "runs/phase5/equivalence_preserving_methods_gate/control_provenance_witness"
)
EVIDENCE_ROOT_TEXT = f"{CONTROL_ROOT_TEXT}/..."
```

The Phase-A0 static gate correctly stopped because the evidence root was not
an independently frozen full absolute value. `--audit-only` and `--execute`
were never invoked.

Root-T0 static review also found a second, prospective geometry defect in
the T4aj protocol: Phase A0 closes the helper evidence root to mode `0500`,
while Phase A1 asks the same helper to create `preserved_sources/` and
`before_manifest.json` inside that closed root. Reopening an immutable
checkpoint root would weaken the reviewed evidence boundary, while leaving
it closed makes execution impossible.

T4ak therefore freezes the helper in one immutable helper root and reserves
a separate, exact, initially absent execution root. Audit-only never writes.
After an independent root-T0 checkpoint audit, execute mode may create only
the reserved execution root and publish preservation evidence there. The
helper root remains read-only throughout.

T4ak changes no scientific, runtime, input, runner, driver, canonical,
threshold, tolerance, mode, point, resolution, or `lmax` contract.

## 2. Immutable T4aj HOLD

The new immutable root is:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
    t4aj_phase_a0_helper_freeze_057bb24b_20260727T063131p0800
```

Root identity:

```text
device 16777244
inode 1232914
nlink 3
uid 501
mode 040500
```

It contains exactly one regular, non-symlink, nlink-1 file:

```text
t4aj_preservation_helper.py
  size 35405
  sha256 7db5372fe3df771520578048543b04d5cf3dbdcc56b5f3999c2dca1ce2faba9f
  device 16777244
  inode 1232919
  uid 501
  mode 100400
```

Independent CPython-3.14 AST reconstruction gives:

```text
PROJECT_ROOT_TEXT assignment  ast.Constant
CONTROL_ROOT_TEXT assignment  ast.Constant
EVIDENCE_ROOT_TEXT assignment ast.JoinedStr

exact project-root Constant count  1
exact control-root Constant count  1
exact evidence-root Constant count 0
Path.parents attributes            0
unlink/remove/rmtree attributes    0
```

The T4 launcher stopped at its prelaunch static assertion. The exact
boundary is:

```text
helper source publications       1
audit-only child launches        0
execute child launches           0
audit stdout/stderr captures     0
Phase-A0 final manifests         0
preserved driver snapshots       0
before manifests                 0
driver edits                     0
T4ai preflights                  0
scientific runner CLI            0
official scientific audit        0
solver                           0
witness or matrix                0
```

The root and helper are defective, immutable, non-executable, and
non-reusable. They must not be edited, chmodded, deleted, renamed, executed,
or populated.

The two earlier T4ai failed roots remain independently immutable:

```text
t4ai_relocated_identity_remediation_057bb24b_20260727T053846p0800
  preserve_before.py
    6386a678c97bedebd73a9f8aba2e0b2d930c758f6909e6d9648aa211f76c0cf9
  preserve_before_corrected.py
    f3fa107cbb614e6d1e2641ddfdfbc4a99e94396cd0ee57fdb23d7bd9b1b75c05

t4ai_relocated_identity_remediation_057bb24b_20260727T055344p0800
  preserve_before_final.py
    b6f4ad36b36c2bd76718fad8d369499a38ca041398b1f1d45ae97a5ca9707ec0
```

No prior helper authorization may be reused.

## 3. Frozen Upstream State

T4ak inherits:

```text
T4aj candidate
  409a765584afd854ecae6a29ba2d2e9d02424fcd

T4ai candidate
  dc240619ee1269e5e5b95c40b80519a52969f057

primary compute HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82

unchanged driver
  057bb24beeb0ea90c6a2524b8ca43df05b611ffe252a1f0b631fab149d1259a9

runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768

T4ah v10 manifest
  0b2b37c0dbd55810b6f3020d0dd69b4c7026d85134c4c9ef065b06a239b3a577

hermetic runtime
  811d3840e858c1ad0a92c665e54dbf99662d884575871ade6ab45c6b40c4db30

complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24
```

The consumed T4ah witness remains:

```text
files             2566
file bytes         582625016
full-path ledger   c21828703400ae65b52d516fe7d41e52f2d7255de1f3a6bdd22f5c3cdb13bb97
```

Its eight exact critical filename/hash mappings remain those frozen in the
T4aj design and must be checked without relabeling.

The four canonical files remain byte/stat/inode exact:

```text
e95d28f4b3d0f35a770430ec074dc47f24b93dc7a2e1785e9646ff4581955f91
3a24f316c9c78c72d382fd68c3409f8833fd10c073e942a56d7e8509c4f595d6
36ff7902d86762ad3f93bf1b386275cc7b5ca89c50c4f8b448a99592089e5bd9
d60277384e6edb1d2192d8a6e0a111cfd21a9be20ddbf976f05d7ec30a712c28
```

The three later frequency pairs and full-image pair remain absent. The
external `/private/tmp/t4ah_diff_inspect.txt` remains the same zero-byte,
regular, nlink-1 inode.

## 4. Four Independent Absolute Root Constants

Before writing helper bytes, T4 chooses two fresh sibling paths below the
exact control root:

```text
helper_root
  created in Phase A0

execution_root
  reserved exact path; absent throughout Phase A0
```

The helper source must contain four direct assignments whose AST values are
single `ast.Constant` strings:

```python
PROJECT_ROOT_TEXT = "<full exact project root>"
CONTROL_ROOT_TEXT = "<full exact control root>"
HELPER_ROOT_TEXT = "<full exact helper root>"
EXECUTION_ROOT_TEXT = "<full exact reserved execution root>"
```

For these four assignments:

- `JoinedStr`, `BinOp`, `Call`, implicit path joining, substring
  construction, environment expansion, and string formatting are forbidden;
- source-text substring counting is not an acceptance test;
- the static gate uses parsed AST assignment semantics;
- every value must equal the corresponding explicit absolute launcher
  argument;
- helper and execution roots must be distinct direct children of the
  control root;
- helper root must resolve strictly and equal
  `Path(__file__).resolve().parent`;
- execution root must be absent, including no symlink, throughout every
  audit-only run.

No authoritative root may use `Path.parents`, repeated `.parent`, root-name
search, cwd-relative discovery, glob discovery, string stripping, or
environment-derived substitution. A single direct `.parent` comparison is
allowed only to prove each child belongs directly to the explicit control
root.

## 5. Shared Read-Only Audit Contract

The frozen helper exposes exactly:

```text
--audit-only
--execute --expected-audit-sha256 <digest>
```

Both modes accept the same explicit absolute:

```text
--project-root
--control-root
--helper-root
--execution-root
```

Both modes call one pure `collect_before()` before any write. It verifies:

1. all four AST-frozen strings equal argv exactly;
2. exact cwd and `/usr/bin/git -C project_root rev-parse --show-toplevel`;
3. candidate/ref/parent/primary and exact-four/exact-fourteen bytes;
4. the three immutable failed helper roots and exact inventories;
5. unchanged driver, v10, runtime, complete-290, runner;
6. the complete 2,566-file witness ledger and eight mappings;
7. canonical hash/stat/inodes and later-unit absence;
8. external-object identity;
9. process, lock/tmp/partial, quarantine allowlist, bytecode allowlist,
   symlink/hardlink, containment, and alias guards;
10. helper-root exact inventory and reserved execution-root absence.

Canonical JSON is exactly:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

The default `ensure_ascii=True` is retained. The canonical payload contains
no trailing newline. Successful audit-only stdout must equal those canonical
bytes exactly, with empty stderr and exit zero.

Audit-only writes nothing anywhere. T4 must prove this with full in-memory
pre/post helper-root inventories collected before child launch and before
any launcher capture publication. Only exact equality permits atomic,
no-overwrite, fsynced capture publication in the helper root.

## 6. Phase A0 Helper-Ready Checkpoint

T4 may:

1. create one helper root mode `0700`;
2. reserve, but not create, one exact execution-root path;
3. publish exactly one helper source with
   `O_EXCL|O_NOFOLLOW`, file fsync, parent fsync, nlink-1/non-alias checks;
4. perform a non-writing AST gate;
5. run audit-only exactly once;
6. after pre/post equality, publish request, exact argv/cwd/environment,
   AST result, stdout, empty stderr, exit, inventories, and final manifest;
7. verify all hashes and guards;
8. close helper and captures to `0400` and helper root to `0500`.

The Phase-A0 AST gate must independently verify:

- the four named assignments are direct exact `ast.Constant` strings;
- the helper/execution constants equal the selected paths;
- `Path.parents` is absent;
- no `eval`, `exec`, `os.chdir`, shell execution, deletion/unlink,
  wildcard cleanup, network/install/global mutation, scientific surface, or
  mutation outside the reserved execution root exists;
- audit-only reaches no mutation function;
- execution writes only after the shared digest check.

The gate must not use raw source substring counts as a substitute for AST.

Phase A0 stops at:

```text
CHECKPOINT / T4AK SPLIT-ROOT PRESERVATION HELPER FROZEN
```

No helper execute, execution-root creation, snapshot, before manifest,
driver edit, preflight, or science is authorized.

## 7. Root-T0 Independent Audit

Root T0 completely reads and parses the frozen helper and every capture. It
independently:

- validates the four direct AST assignments and all forbidden surfaces;
- verifies helper-root and reserved execution-root geometry;
- recomputes all frozen identities and witness/canonical guards;
- reruns audit-only once with exact argv/cwd/environment and pipes;
- proves stdout bytes/payload digest, empty stderr, exit zero, and no write;
- verifies helper root remains immutable and execution root remains absent.

Only complete PASS permits one exact execution authorization bound to:

- helper source SHA/stat/inode;
- exact helper and execution roots;
- exact audit payload SHA-256;
- exact execute argv/cwd/environment.

## 8. One-Shot Split-Root Execution

Execute mode first reruns the identical `collect_before()` and requires the
canonical payload digest to equal
`--expected-audit-sha256`. Only then may it atomically begin the reserved
execution root.

Execution must:

1. require the exact execution path and every alias spelling absent;
2. create that direct child once with mode `0700` and fsync the control root;
3. verify directory type, ownership, device/inode, non-symlink, and
   separation from all protected paths;
4. create an `artifacts/` child exclusively;
5. copy the exact old-driver bytes to one regular nlink-1 snapshot with a
   distinct inode, fsync, exact hash/size/mode verification, then mode
   `0400`;
6. publish one canonical `before_manifest.json` through a same-filesystem
   exclusive temporary file and no-replace rename, with file and directory
   fsync;
7. independently reload the final manifest and verify exact bytes/digest;
8. publish a durable helper execution result inside the execution root;
9. leave the helper root untouched;
10. leave the execution root writable only until the supervising launcher
    has atomically published exact argv/cwd/env/stdout/stderr/exit and final
    guard records, then close files to `0400`, subdirectories and root to
    `0500`.

No deletion, unlink, overwrite, cleanup, move of an existing path, outside
write, network/install/global mutation, or retry is allowed. If failure
occurs after execution-root creation, the partial root is immutable. If the
shared pre-write audit fails, execution root remains absent and the
authorization is consumed.

Successful preservation alone permits resumption of the already reviewed
T4ai artifact-local driver/test repair and one fresh exact-Python-3.14
zero-science preflight.

## 9. Safety And Budget

- Existing T4 and T7 tasks only.
- T4 uses `gpt-5.6-sol/high`; `max` and `ultra` are forbidden.
- No task, subagent, proxy, or descendant.
- No witness, official scientific audit, solver, matrix, pair reuse,
  canonical write, scientific/runtime/input/threshold change, destructive
  operation, new frequency, production, plot, fixture, Kirchhoff, paper, or
  GitHub action.
