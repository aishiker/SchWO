# T4aj Pre-Edit Preservation Root-Binding Repair Design

## 1. Purpose

T4aj closes one bounded control-plane failure that occurred before the
reviewed T4ai driver repair could begin. It does not change the T4ai
scientific or provenance design.

Two separate T4ai preservation helpers have now failed before publishing an
old-driver snapshot or before manifest:

1. `t4ai_relocated_identity_remediation_057bb24b_20260727T053846p0800`
   used an incorrect immutable-evidence filename and contained a second
   latent filename-to-hash mapping error.
2. `t4ai_relocated_identity_remediation_057bb24b_20260727T055344p0800`
   corrected those mappings but computed the project root as
   `ROOT.parents[5]`. For that evidence root, `ROOT.parents[5]` is
   `/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics`, while the exact
   project root is
   `/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO`, equal to
   `ROOT.parents[4]`.

The second helper therefore failed on the first canonical-file `lstat`
below a nonexistent upper-level `runs/` path. It published no
`preserved_sources/`, driver snapshot, `before_manifest.json`, temporary
file, or preflight evidence. The live driver was not edited and all
scientific invocation counts remained zero.

The consumed continuation explicitly allowed only one helper execution.
That authorization is exhausted. T4aj is a new reviewed package, not a
retry under the exhausted authorization.

## 2. Immutable Failure Evidence

### 2.1 First failed root

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
    t4ai_relocated_identity_remediation_057bb24b_20260727T053846p0800
```

It contains exactly:

```text
preserve_before.py
  size 8709
  sha256 6386a678c97bedebd73a9f8aba2e0b2d930c758f6909e6d9648aa211f76c0cf9

preserve_before_corrected.py
  size 562
  sha256 f3fa107cbb614e6d1e2641ddfdfbc4a99e94396cd0ee57fdb23d7bd9b1b75c05
```

No snapshot, manifest, temporary publication, driver edit, preflight, or
science exists in that root.

### 2.2 Second failed root

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
    t4ai_relocated_identity_remediation_057bb24b_20260727T055344p0800
```

It contains exactly one regular, non-symlink, nlink-1 file:

```text
preserve_before_final.py
  size 15532
  sha256 b6f4ad36b36c2bd76718fad8d369499a38ca041398b1f1d45ae97a5ca9707ec0
  device 16777244
  inode 1232725
  uid 501
  mode 100644
```

The directory itself was observed as:

```text
device 16777244
inode 1232699
nlink 3
uid 501
mode 040755
```

The helper's exact statements are:

```python
ROOT = Path(__file__).resolve().parent
CONTROL = ROOT.parent
PROJECT = ROOT.parents[5]
```

For this exact root, independent enumeration proves:

```text
ROOT.parents[4]
  /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO

ROOT.parents[5]
  /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics
```

The wrongly constructed first canonical path below the latter root is
absent. The root contains no other path, including no
`preserved_sources`, snapshot, before manifest, bytecode/cache, temporary
publication, or preflight record.

Both failed roots are immutable, defective, non-executable, and
non-reusable. T4aj must not edit, chmod, delete, rename, execute, or
populate either root.

## 3. Frozen T4ai State

T4aj inherits and must preserve:

```text
T4ai reviewed candidate
  dc240619ee1269e5e5b95c40b80519a52969f057

T4ai candidate parent
  7d84746a96184a250acddb044502d2506263b9b9

T4ai ref
  refs/heads/codex/t4ai-relocated-benchmark-identity-binding-repair-candidate

primary compute HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82

unchanged live driver
  057bb24beeb0ea90c6a2524b8ca43df05b611ffe252a1f0b631fab149d1259a9

T4ah v10 preflight
  0b2b37c0dbd55810b6f3020d0dd69b4c7026d85134c4c9ef065b06a239b3a577

complete-290 input contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24

hermetic runtime
  811d3840e858c1ad0a92c665e54dbf99662d884575871ade6ab45c6b40c4db30

runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768
```

The complete consumed T4ah witness remains 2,566 files and 582,625,016
file bytes with sorted full-path/hash ledger:

```text
c21828703400ae65b52d516fe7d41e52f2d7255de1f3a6bdd22f5c3cdb13bb97
```

The exact critical filename/hash map remains:

```text
prepare_complete_input_witness.py
  369ad2ae7c6bd6af8cacf6de37fde819ea1956905dcea8043684d18c6291a1c2
preparation_result.json
  152130ac0e22c9b05d65b06207692c285fbed67f76b2823391c2843d3d361043
prelaunch_setup_manifest.json
  99d71f6759d1bf97c0de6fb387f8435f3446958b11c7a4805dffffc72b8c2fb3
producer_request.json
  e513e75fb250438c9f0c0660b4192b314e1bb23e50d082533a639b42fa246873
producer_control_audit.json
  b20e481dbd070ea63e9999f43f90e0df99dde2d6e9b756a5a0d77706467d800c
producer_pair_independent_audit.json
  854df348a67bd32e377420e7239dbcacfefb94281eecd1f91b025f2fb98b1792
official_audit_start_gate_failure.json
  ab3741aba87b30be2272c5dde0a793c1e4a838ec0652ecbe31e3dcf11d44c35f
control_runs/t4ah_complete_input_witness_kM_1p58125_20260727T001212p0800/final.json
  247790537ff120c7dbabe7a80016a5f3db26d969639af9cedeb5a1e152e8a8da
```

The four canonical files remain byte/stat/inode exact:

```text
e95d28f4b3d0f35a770430ec074dc47f24b93dc7a2e1785e9646ff4581955f91
3a24f316c9c78c72d382fd68c3409f8833fd10c073e942a56d7e8509c4f595d6
36ff7902d86762ad3f93bf1b386275cc7b5ca89c50c4f8b448a99592089e5bd9
d60277384e6edb1d2192d8a6e0a111cfd21a9be20ddbf976f05d7ec30a712c28
```

Only the two completed canonical frequency pairs may exist. The three
later frequency pairs and the full-image pair remain absent. The external
zero-byte object `/private/tmp/t4ah_diff_inspect.txt` remains immutable.

## 4. Root Binding Without Parent Arithmetic

The new helper must not infer the project root, control root, or evidence
root through `Path.parents[N]`, repeated `.parent`, substring stripping,
relative current-working-directory assumptions, glob discovery, or a
search for the first directory named `SchWO`.

All three roots are explicit absolute launcher arguments:

```text
--project-root
  /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO

--control-root
  /Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/
  runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness

--evidence-root
  one exact fresh child of the control root
```

The helper must verify all of the following before collecting guards:

1. every argument is absolute and resolves strictly;
2. `Path(__file__).resolve().parent` equals the exact evidence root;
3. the evidence root's direct parent equals the exact control root;
4. the driver is exactly `control_root / durable_control_driver_v2.py`;
5. `/usr/bin/git -C project_root rev-parse --show-toplevel` returns the
   exact project-root string;
6. the caller's exact cwd is the project root;
7. candidate/ref/parent/primary identities and exact-four/exact-fourteen
   byte guards pass;
8. all repository-relative paths remain lexically and physically contained
   below the explicit project root;
9. no symlink, hardlink/shared inode, writable protected input, bytecode,
   unexpected transient, process, or path alias is admitted.

The helper source must pass an AST/static gate that rejects `Path.parents`,
numeric parent ascent for any authoritative root, `os.chdir`, `eval`,
`exec`, shell execution, wildcard mutation, deletion, rename of an
existing evidence root, or any network/install/global-environment action.

## 5. Mandatory Two-Checkpoint Protocol

### 5.1 Helper-ready checkpoint

T4 first creates one fresh unique evidence root in mode `0700` and publishes
only a new helper source with `O_EXCL|O_NOFOLLOW`, file fsync, parent fsync,
regular/non-symlink/nlink-1 verification, and final helper mode `0400`.

The helper must implement:

```text
--audit-only
--execute --expected-audit-sha256 <exact digest>
```

Both modes call the same pure `collect_before()` function.

`--audit-only` performs all identity, witness-ledger, candidate, canonical,
absence, external-object, process, transient, no-bytecode, and containment
checks. It emits exactly one canonical JSON object to stdout, uses the
runner-compatible default `ensure_ascii=True`, emits no stderr on success,
and writes nothing. The launcher may atomically capture stdout, stderr,
exit status, argv, cwd, environment allowlist, and pre/post full evidence-
root inventory in separate no-overwrite/fsynced records.

The pre/post inventories must prove that the helper itself made no change.
The only launcher-created paths permitted before the checkpoint are the
helper and its immutable audit-only capture records. No snapshot,
`preserved_sources`, before manifest, driver edit, preflight, or science is
allowed.

T4 then returns exactly:

```text
CHECKPOINT / T4AJ PRESERVATION HELPER FROZEN
```

and stops. It must report the helper hash/stat/inode, exact argv/cwd/env,
audit-only stdout hash and canonical payload hash, empty stderr, exit zero,
pre/post inventories, and all frozen guards.

### 5.2 Root-T0 execution authorization

Root T0 independently reads the helper completely, parses its AST, checks
the literal argument/root contract, recomputes the audit-only payload, and
verifies that both failed roots and every frozen guard remain exact.

Only a fresh PASS permits one exact:

```text
AUTHORIZED / EXECUTE T4AJ PRESERVATION AND RESUME T4AI PHASE A
```

The T7 package GREEN alone does not authorize helper execution.

## 6. One-Shot Preservation Execution

After the explicit execution authorization, T4 runs the frozen helper
exactly once with the exact reviewed argv/cwd/environment and
`--expected-audit-sha256`.

Execution must:

1. rerun the identical `collect_before()` function;
2. require its canonical payload SHA-256 to equal the reviewed audit-only
   digest;
3. create `preserved_sources/` with exclusive no-follow publication;
4. copy the exact old driver bytes to one new nlink-1 regular snapshot;
5. verify exact hash, size, mode, inode separation, and no alias;
6. fsync the snapshot and parent;
7. atomically publish one canonical `before_manifest.json` with no replace,
   file fsync, and parent fsync;
8. verify final manifest bytes by independent reload and digest;
9. set snapshot mode `0400`, evidence subdirectories `0500`, and evidence
   root `0500` only after all publications pass;
10. prove no bytecode/cache, lock/tmp/partial, process, canonical, external,
    or absent-unit drift.

No deletion, unlink, overwrite, move of an existing path, glob/wildcard,
recursive cleanup, or mutation outside the fresh evidence root is allowed.
If this frozen helper execution fails, T4 preserves the root and returns
HOLD. No additional attempt is implied or authorized.

## 7. Resumption Of T4ai Phase A

Only successful preservation permits the already reviewed T4ai work:

- modify only the artifact-local durable driver and solver-free tests;
- implement deterministic root-specific full seven-field benchmark
  identity binding while retaining the fixed primary matrix identity;
- preserve runner-exact `_json_safe` plus default `ensure_ascii=True`;
- retain the Unicode detached-root positive and `ensure_ascii=False`
  rejection;
- run one fresh exact-Python-3.14 full zero-science preflight;
- keep scientific runner CLI, official audit, and solver invocation counts
  exactly `0/0/0`;
- return exact
  `CHECKPOINT / RELOCATED BENCHMARK IDENTITY CONTRACT FROZEN`.

No witness, official scientific audit, solver, matrix, pair reuse,
canonical write, runtime/input/science change, or downstream action is
authorized by T4aj.

## 8. Safety And Budget

- Existing T4 and T7 tasks only.
- T4 uses `gpt-5.6-sol/high`; `max` and `ultra` are forbidden.
- No task, subagent, proxy, or descendant.
- No network, install, global mutation, destructive cleanup, new
  frequency, production, plot, fixture, Kirchhoff, paper, or GitHub work.
