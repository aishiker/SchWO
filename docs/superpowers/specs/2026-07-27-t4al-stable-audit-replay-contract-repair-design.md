# T4al Stable Audit Replay Contract Repair Design

## 1. Purpose

T4al repairs the exhausted T4ak Phase-A0 helper-freeze attempt without
reusing, executing, or modifying any prior helper or evidence root.

T4ak correctly froze project, control, helper, and execution roots as four
direct full `ast.Constant` strings and kept the reserved execution root
absent. Its prelaunch semantic review nevertheless found a deterministic
checkpoint/replay contradiction before launching `--audit-only`:

- `helper_root_inventory()` requires the helper root to contain only
  `t4ak_preservation_helper.py`;
- that inventory embeds the helper-root directory `mode`, `mtime_ns`, and
  `ctime_ns` in the canonical audit payload;
- the T4ak Phase-A0 protocol then requires the launcher to publish captures
  and its final manifest inside the same helper root and change the root
  from mode `0700` to `0500`;
- root T0 is subsequently required to rerun `--audit-only` with the same
  argv/cwd/environment and obtain byte-identical canonical stdout.

Those requirements cannot all hold. After Phase-A0 publication, the helper
root no longer has the original inventory or directory identity. A root-T0
replay would necessarily fail or produce a different digest.

T4al separates three roles:

1. an immutable **helper root** containing only the frozen helper;
2. a distinct immutable **audit-record root** receiving Phase-A0 launcher
   captures and the final checkpoint manifest;
3. a distinct reserved **execution root**, absent until a later
   digest-bound root-T0 authorization.

The helper's canonical audit payload binds the audit-record root only
through an explicitly frozen stable directory projection. Mutable
publication fields and children are deliberately excluded from that
payload and are instead independently protected by the Phase-A0 launcher
manifest and root-T0 checkpoint audit.

T4al changes no scientific runner, implementation, driver, runtime,
complete-290 input, canonical result, threshold, tolerance, mode, point,
resolution, or `lmax` contract.

## 2. Immutable T4ak HOLD

The exhausted root is:

```text
runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness/
    t4ak_phase_a0_helper_freeze_057bb24b_20260727T071836p0800
```

Root identity:

```text
device    16777244
inode     1233128
nlink     3
uid       501
gid       20
mode      040500
size      96
mtime_ns  1785108132326564256
ctime_ns  1785108248742083942
```

It contains exactly one regular, non-symlink, nlink-1 file:

```text
t4ak_preservation_helper.py
  size      36258
  sha256    77902b3613deaddbc254ba57bd851f7f11b479f73d34c9e7f0dea9b210da23aa
  device    16777244
  inode     1233145
  nlink     1
  uid       501
  gid       20
  mode      100400
  mtime_ns  1785108132432987474
  ctime_ns  1785108176532615184
```

Independent CPython-3.14 AST reconstruction confirms:

```text
PROJECT_ROOT_TEXT assignment    ast.Constant
CONTROL_ROOT_TEXT assignment    ast.Constant
HELPER_ROOT_TEXT assignment     ast.Constant
EXECUTION_ROOT_TEXT assignment  ast.Constant
Path.parents attributes         0
unlink/remove/rmtree attributes 0
eval/exec calls                 0
```

The semantic blocker is independently visible in source:

```text
helper_root_inventory requires exact one-file inventory
helper_root directory identity enters canonical payload
directory identity includes mode/mtime_ns/ctime_ns
Phase-A0 capture publication would alter inventory and directory identity
```

The exact invocation/publication boundary is:

```text
helper publications          1
audit-only child launches    0
execute child launches       0
captures                     0
Phase-A0 manifests           0
driver snapshots             0
before manifests             0
driver edits                 0
T4ai preflights              0
scientific runner CLI        0
official scientific audit    0
solver                       0
witness or matrix            0
```

The reserved T4ak execution root
`t4ak_phase_a1_execution_057bb24b_20260727T071836p0800` remains absent.
The helper root and helper are defective, immutable, non-executable, and
non-reusable. They must not be edited, chmodded, deleted, renamed,
executed, or populated. The three earlier T4ai/T4aj failed roots remain
equally immutable and non-reusable.

## 3. Frozen Upstream State

T4al inherits:

```text
T4ak candidate
  5aa4ccf46b376b40ab3938ecc12a1bdb9753f657

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

The consumed T4ah witness remains exactly:

```text
files            2566
file bytes        582625016
full-path ledger  c21828703400ae65b52d516fe7d41e52f2d7255de1f3a6bdd22f5c3cdb13bb97
```

All eight frozen critical filename/hash mappings remain exact. The
canonical four hashes/stat/inodes remain exact:

```text
e95d28f4b3d0f35a770430ec074dc47f24b93dc7a2e1785e9646ff4581955f91
3a24f316c9c78c72d382fd68c3409f8833fd10c073e942a56d7e8509c4f595d6
36ff7902d86762ad3f93bf1b386275cc7b5ca89c50c4f8b448a99592089e5bd9
d60277384e6edb1d2192d8a6e0a111cfd21a9be20ddbf976f05d7ec30a712c28
```

The three later frequency pairs and full-image pair remain absent. The
external `/private/tmp/t4ah_diff_inspect.txt` remains the exact zero-byte,
regular, nlink-1 inode. No T4al root exists at package-review time.

## 4. Five Direct Absolute Root Constants

Before helper publication, T4 chooses three fresh sibling paths below the
exact control root:

```text
helper_root
  created in Phase A0; contains only helper forever

audit_record_root
  created in Phase A0; receives launcher records only

execution_root
  reserved exact path; absent throughout Phase A0 and root-T0 replay
```

The helper source contains five direct assignments whose AST values are
single full exact `ast.Constant` strings:

```python
PROJECT_ROOT_TEXT = "<full exact project root>"
CONTROL_ROOT_TEXT = "<full exact control root>"
HELPER_ROOT_TEXT = "<full exact helper root>"
AUDIT_RECORD_ROOT_TEXT = "<full exact audit-record root>"
EXECUTION_ROOT_TEXT = "<full exact reserved execution root>"
```

For all five assignments:

- `JoinedStr`, `BinOp`, `Call`, implicit joining, formatting, environment
  expansion, and substring construction are forbidden;
- the static gate uses parsed AST assignment semantics, never raw source
  substring counts;
- values must equal explicit absolute argv exactly;
- helper, audit-record, and execution roots are pairwise distinct direct
  children of the exact control root;
- helper root strictly resolves to `Path(__file__).resolve().parent`;
- audit-record root strictly resolves and is a real directory;
- execution root and every alias spelling remain absent.

No authoritative root may use `Path.parents`, repeated ascent, cwd/root-name
discovery, glob search, string stripping, or environment-derived
substitution.

## 5. Stable Audit-Record Projection

Both helper modes call one pure `collect_before()` before any write. The
audit-record root enters the canonical payload only as:

```json
{
  "path": "<exact resolved absolute audit-record root>",
  "dev": "<st_dev>",
  "ino": "<st_ino>",
  "uid": "<st_uid>",
  "gid": "<st_gid>",
  "is_directory": true,
  "is_symlink": false,
  "direct_child_of_control": true
}
```

The following mutable or publication-dependent properties are forbidden in
that canonical projection:

```text
mode
nlink
size
atime / mtime / ctime / birthtime
children or child count
file names
file bytes, sizes, hashes, stats, or inventory digests
full audit-record-root directory identity
```

The helper may scan the control tree for forbidden symlink/hardlink,
bytecode, lock/tmp/partial, and quarantine anomalies, but ordinary
Phase-A0 capture files must not change the resulting guard payload.

This exclusion is narrow and explicit. It does not weaken evidence
durability:

- the Phase-A0 launcher records the full pre-child and post-child
  inventories before capture publication;
- the launcher publishes a non-self-referential terminal pair: a
  `records_index.json` covering every earlier record and a
  `phase_a0_final_manifest.json` binding that index, the exact expected
  filename set (including the terminal manifest name), publication order,
  fsync evidence, and intended final modes;
- root T0 independently rechecks the entire immutable audit-record root;
- none of those mutable publication records is a scientific or
  preservation input to `collect_before()`.

No file may claim its own hash/stat or a post-publication directory
timestamp. The T4 checkpoint reports the independently reloaded terminal
manifest hash/stat plus the post-close audit-root identity. Root T0
independently recomputes and records the complete final inventory and
post-close identity.

The helper-root payload remains strict: it requires the helper root to
contain exactly one frozen helper and may include its complete immutable
file/root identity because that root is closed before the first audit and
is never subsequently mutated.

## 6. Shared Read-Only Audit Contract

The helper exposes exactly:

```text
--audit-only
--execute --expected-audit-sha256 <digest>
```

Both modes accept the same explicit absolute:

```text
--project-root
--control-root
--helper-root
--audit-record-root
--execution-root
```

Both modes call the same pure `collect_before()` and verify:

1. all five AST-frozen strings equal argv;
2. exact cwd and git top-level;
3. candidate/ref/parent/primary and exact-four/exact-fourteen bytes;
4. all four immutable failed-helper roots and exact inventories;
5. unchanged driver, v10, runtime, complete-290, and runner;
6. complete witness ledger and eight mappings;
7. canonical hash/stat/inodes and later-unit absence;
8. external-object identity;
9. process, lock/tmp/partial, quarantine, bytecode, link, containment, and
   alias guards;
10. exact immutable helper-root inventory;
11. exact stable audit-record-root projection;
12. reserved execution-root absence.

Canonical JSON is exactly:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

Default `ensure_ascii=True` is retained. Successful audit-only stdout is
exactly those bytes with no newline, empty stderr, and exit zero.

Audit-only writes nothing anywhere. T4 proves this by collecting complete
in-memory helper-root, audit-record-root, execution-root-absence, and
bounded control-scope inventories immediately before child launch and
immediately after exit, before publishing any capture. All must match
exactly.

## 7. Phase A0 Three-Root Checkpoint

T4 may:

1. choose all three fresh exact paths and reject every alias/collision;
2. create helper and audit-record roots mode `0700`; keep execution absent;
3. publish exactly one helper using `O_EXCL|O_NOFOLLOW`, file fsync, parent
   fsync, nlink-1/non-alias checks, set helper mode `0400`, then close the
   helper root to mode `0500` **before** the first audit;
4. verify the helper-root full identity is now immutable;
5. perform the exact AST/dataflow static gate;
6. run audit-only exactly once under exact CPython 3.14;
7. require exit zero, empty stderr, exact canonical stdout, pre/post
   inventory equality, helper-root immutability, and execution absence;
8. publish request, argv/cwd/environment, AST/dataflow result, stdout,
   empty stderr, exit, pre/post inventories, stable-projection proof, and
   payload-schema proof only in the audit-record root;
9. publish `records_index.json` last among indexed records, covering every
   earlier record but not itself or the terminal manifest;
10. publish `phase_a0_final_manifest.json` after the index. It binds the
    index hash, exact expected final filename set including itself,
    publication order, fsync/reload proofs, and intended final modes. It
    must not claim its own hash/stat or post-close directory timestamps;
11. independently reload both terminal files and verify every indexed
    file/hash/stat/inode/nlink/mode and the exact filename set;
12. close record files to `0400` and audit-record root to `0500`, fsync,
    then report the terminal-manifest hash/stat and post-close root identity
    at the checkpoint for root-T0 independent recording;
13. reverify helper root untouched and execution root absent.

The Phase-A0 static gate must prove:

- five direct exact constants and three-root separation;
- helper root receives no capture or later write;
- audit-only reaches no mutation function;
- canonical payload contains exactly the allowed stable audit-root
  projection and excludes every forbidden mutable field/inventory;
- execute reaches mutation only after shared digest equality and writes
  only in the reserved execution root;
- no `Path.parents`, root inference, shell/eval/exec, deletion, cleanup,
  network/install/global, scientific, or outside-root mutation surface.

Phase A0 stops at:

```text
CHECKPOINT / T4AL STABLE AUDIT REPLAY HELPER FROZEN
```

No execute, execution-root creation, snapshot, before manifest, driver
edit, preflight, or science is authorized.

## 8. Root-T0 Independent Replay

Root T0 completely reads and parses the helper and audit-record root. It:

- validates all five direct AST constants and forbidden surfaces;
- validates helper/audit/execution geometry and the exact stable projection;
- confirms the helper root contains only the helper and is byte/stat/inode
  unchanged;
- verifies the complete immutable audit-record-root manifest and captures;
- recomputes every frozen evidence, witness, canonical, and absence guard;
- inventories helper/audit/control scopes in memory;
- reruns audit-only once with exact argv/cwd/environment and pipes;
- proves exact captured stdout byte equality and digest, empty stderr,
  exit zero, execution absence, and complete pre/post inventory equality;
- verifies helper and audit-record roots remain immutable.

Because capture publication does not enter `collect_before()` except
through the stable projection, the replay must be byte-identical. Any
difference stops the project and does not authorize execution.

Only complete PASS permits one exact digest-bound execute authorization.

## 9. One-Shot Execution And T4ai Resume

Execute mode first recomputes the identical `collect_before()` while helper
and audit-record roots remain untouched and execution root remains absent.
The canonical digest must equal `--expected-audit-sha256`.

Only then may it create the exact reserved execution root and publish the
old-driver snapshot, canonical `before_manifest.json`, helper execution
result, and supervising launcher records there with exclusive/no-follow,
atomic no-replace, fsync, reload, exact hash/stat/inode/nlink/non-alias, and
final read-only semantics already frozen by T4ak. Helper and audit-record
roots remain untouched.

Any failure consumes authorization. A partial execution root is immutable;
no retry, cleanup, or reuse is implied.

Successful preservation alone permits resumption of the already reviewed
T4ai artifact-local driver/test repair and one fresh exact-Python-3.14
zero-science preflight.

## 10. Safety And Budget

- Existing T4 and T7 tasks only.
- T4 uses `gpt-5.6-sol/high`; `max` and `ultra` are forbidden.
- No task, subagent, proxy, or descendant.
- No witness, official scientific audit, solver, matrix, pair reuse,
  canonical write, scientific/runtime/input/threshold change, destructive
  operation, new frequency, production, plot, fixture, Kirchhoff, paper,
  or GitHub action.
