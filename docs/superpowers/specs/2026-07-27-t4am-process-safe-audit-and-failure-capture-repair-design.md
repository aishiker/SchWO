# T4am Process-Safe Audit And Failure-Capture Repair Design

## 1. Purpose

T4am repairs the exhausted T4al Phase-A0 attempt without reusing,
executing, or modifying any earlier helper or evidence root.

T4al correctly separated the immutable helper root, mutable-before-close
audit-record root, and reserved absent execution root. It also froze the
audit-record root's stable canonical projection. Its only authorized
`--audit-only` child nevertheless exited `1`.

The durable boundary is exact:

- the helper, audit-record, and control inventories were equal before and
  after the child;
- the reserved execution root remained absent;
- the helper root remained immutable and the audit-record root remained
  empty;
- no execute, driver edit, preflight, scientific runner, official audit,
  solver, witness, or matrix action occurred;
- the launcher discarded child stderr before publishing any record because
  the reviewed success-only publication gate rejected nonzero exit first.

Consequently the exact historical exception is unrecoverable. It is not
scientifically or procedurally valid to promote a plausible explanation to
an established cause.

Independent source review does prove a separate reachable defect: the
T4al helper's process guard scans every `ps` command line for broad marker
substrings and has no PID-ancestry semantics. A legitimate parent launcher
or other harmless control command can therefore become a false positive.
This defect must be closed, but T4am does **not** claim it was the exact
historical trigger.

T4am closes both defects:

1. every audit attempt receives a durable, mutually exclusive success or
   failure terminal record set after no-write pre/post equality;
2. process validation becomes structured, token-aware, and ancestry-aware,
   with a frozen file-based launcher rather than stdin, heredoc, or `-c`.

T4am changes no scientific runner, implementation, live driver, runtime,
complete-290 input contract, canonical result, threshold, tolerance, mode,
point, resolution, or `lmax` contract.

## 2. Immutable T4al Failure Boundary

The exact control root is:

```text
/Volumes/JohnnyTforGR/ResearchWork/GW_Wave_Optics/SchWO/
  runs/phase5/equivalence_preserving_methods_gate/
  control_provenance_witness
```

The exhausted T4al roots are direct children of that control root.

### 2.1 Helper root

```text
t4al_phase_a0_helper_057bb24b_20260727T075721p0800

dev       16777244
inode     1233390
nlink     3
uid       501
gid       20
mode      040500
size      96
mtime_ns  1785110467176422119
ctime_ns  1785110508880737283
```

It contains exactly one regular, non-symlink, nlink-1 file:

```text
t4al_preservation_helper.py

sha256    ce05879486e703e4f1665552ecf91cdbf5f5bfb5f8fc58b494330efa9a05a7ed
size      36513
dev       16777244
inode     1233405
nlink     1
uid       501
gid       20
mode      100400
mtime_ns  1785110467177554089
ctime_ns  1785110508880710782
```

Independent CPython-3.14 AST reconstruction confirms five direct exact
root constants and the reviewed stable audit-record projection.

### 2.2 Audit-record root

```text
t4al_phase_a0_audit_records_057bb24b_20260727T075721p0800

dev       16777244
inode     1233391
nlink     2
uid       501
gid       20
mode      040700
size      64
mtime_ns  1785110249294768176
ctime_ns  1785110249294821718
children  0
```

This empty root is part of the immutable failed attempt. Its current
write-capable mode does not authorize any later population, chmod, repair,
rename, deletion, or reuse.

### 2.3 Reserved execution root and exact counts

```text
t4al_phase_a1_execution_057bb24b_20260727T075721p0800
```

remains absent.

```text
audit-only child launches   1
audit-only natural exit     1
audit-only return code      1
durable child stderr        absent by defective protocol
execute child launches      0
success records/index       0
failure records/index       0
terminal manifests          0
driver snapshots            0
before manifests            0
driver edits                0
T4ai preflights             0
scientific runner CLI       0
official scientific audit   0
solver                      0
witness or matrix           0
```

The exact exception and exact dynamic cause are unrecoverable. T4am must
preserve that epistemic boundary in every record and report.

## 3. Proven Reachable Process-Guard Defect

The T4al helper's process scanner:

- obtains a global process listing;
- performs naive substring tests over whole command lines;
- uses markers including
  `phase5_equivalence_preserving_methods_gate.py`,
  `t4ae_legacy_case_driver.py`, `t4ae_full_image_driver.py`, and
  `synthetic-preflight`;
- has no structured PID, PPID, PGID, SID, or token interpretation;
- has no explicit expected helper/launcher ancestry.

This design permits false rejection if an expected launcher or benign
ancestor command line includes a marker. A fresh harmless probe did not
reproduce that geometry on the current shell because process execution
shape can differ. Therefore the defect is proven reachable, while its role
in the exhausted attempt remains unproven.

The repair must never weaken rejection of an unrelated scientific or
control process.

## 4. Frozen Upstream State

T4am inherits:

```text
T4al candidate
  6b27fe58a3946429493a0a69365a6146b4144f49

T4ak candidate
  5aa4ccf46b376b40ab3938ecc12a1bdb9753f657

T4ai candidate
  dc240619ee1269e5e5b95c40b80519a52969f057

primary compute HEAD
  45face32f52537ac4b8ab79cb1746d8ac78e9b82

unchanged live driver
  057bb24beeb0ea90c6a2524b8ca43df05b611ffe252a1f0b631fab149d1259a9

runner
  18e794353c80f9d161f234de399fc2cf1f3c471e3ae3b41ddcf5488bd866a768

T4ah v10 manifest
  0b2b37c0dbd55810b6f3020d0dd69b4c7026d85134c4c9ef065b06a239b3a577

hermetic runtime manifest
  f3ebf3dbf8981500c8d7f714b1740996638f10e32ef17a8377d45ea0b70ab6ca

hermetic runtime identity
  811d3840e858c1ad0a92c665e54dbf99662d884575871ade6ab45c6b40c4db30

complete-290 contract
  77927103da4d853e98dbe7c4d19a2198fb544349cf735bf63faaf02ca31dfd24

consumed witness
  2566 files
  582625016 bytes
  c21828703400ae65b52d516fe7d41e52f2d7255de1f3a6bdd22f5c3cdb13bb97
```

All eight critical consumed-witness mappings remain exact. The canonical
four complete files retain exact hash/stat/inode identities. The three
later frequency pairs and full-image pair remain absent. The external
`/private/tmp/t4ah_diff_inspect.txt` remains the exact zero-byte regular
nlink-1 inode. No T4am root exists at package-review time.

## 5. Fresh Four-Root Phase-A0 Geometry

T4 chooses fresh pairwise-distinct direct children of the exact control
root:

```text
helper_root
  contains only the immutable helper

audit_record_root
  contains the immutable launcher before the first attempt, then receives
  durable attempt records and one terminal manifest

execution_root
  reserved and absent throughout Phase A0 and root-T0 replay
```

The helper freezes five direct full exact `ast.Constant` assignments:

```python
PROJECT_ROOT_TEXT = "<exact absolute project root>"
CONTROL_ROOT_TEXT = "<exact absolute control root>"
HELPER_ROOT_TEXT = "<exact absolute helper root>"
AUDIT_RECORD_ROOT_TEXT = "<exact absolute audit-record root>"
EXECUTION_ROOT_TEXT = "<exact absolute reserved execution root>"
```

The launcher freezes the same five direct full exact constants plus the
exact helper path, exact Python-3.14 executable, and exact expected helper
SHA-256. The helper and launcher reject `JoinedStr`, `BinOp`, `Call`,
environment expansion, `Path.parents`, repeated ascent, cwd/name search,
string stripping, symlink aliases, and implicit root construction.

The launcher is always invoked as a frozen file:

```text
<python3.14> <audit_record_root>/t4am_audit_launcher.py --first-attempt ...
<python3.14> <audit_record_root>/t4am_audit_launcher.py --replay-only ...
```

stdin scripts, heredocs, `python -c`, shell-evaluated commands, and dynamic
launcher generation at invocation time are forbidden.

Before the first helper child:

- helper file is mode `0400` and helper root mode `0500`;
- launcher file is mode `0400`;
- audit-record root contains exactly that launcher;
- execution root and every alias are absent.

The helper root and both frozen source files are never edited after the
first attempt. The audit-record root may receive only the reviewed durable
attempt records after pre/post no-write equality.

## 6. Stable Canonical Audit Payload

The helper's `collect_before()` remains the single pure data path for
`--audit-only` and future `--execute`. It binds all prior frozen scientific,
runtime, complete-input, canonical, preservation, failed-root, helper, and
execution guards.

The audit-record root enters the helper payload only through:

```json
{
  "path": "<exact resolved absolute path>",
  "dev": "<st_dev>",
  "ino": "<st_ino>",
  "uid": "<st_uid>",
  "gid": "<st_gid>",
  "is_directory": true,
  "is_symlink": false,
  "direct_child_of_control": true
}
```

Mode, nlink, size, timestamps, children, filenames, child hashes/stats,
child count, and inventory digest are excluded only from this stable
launcher-evidence projection. They remain mandatory in full launcher
pre/post and final publication records.

Canonical JSON uses literal runner-compatible semantics:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
)
```

encoded UTF-8 with default `ensure_ascii=True` and no newline.

The current helper PID and launcher PID are validation inputs only. They
must never enter the canonical payload, payload digest, or replay equality
surface.

## 7. Ancestry-Aware, Token-Aware Process Contract

The helper receives one explicit `--expected-launcher-pid`. It takes one
structured process snapshot with at least:

```text
pid ppid pgid sid state command
```

The parser must fail closed on missing, duplicate, malformed, ambiguous, or
non-integer identity fields. It must reject ancestry cycles and impossible
self/parent relationships.

The helper verifies:

1. its own PID appears exactly once;
2. its PPID equals the explicit launcher PID;
3. the launcher PID appears exactly once;
4. the helper and launcher relationship is the exact expected direct
   ancestry;
5. self and direct launcher are the only rows eligible for the expected
   ancestry exemption;
6. neither exemption changes any canonical payload field;
7. every other row is inspected using normalized executable/argument
   tokens, not broad whole-command substring matching;
8. unrelated exact scientific runner paths, control-driver paths,
   forbidden driver basenames used as executable/script tokens, malformed
   aliases, and ambiguous tokens fail closed.

The returned canonical process result contains only stable facts such as:

```json
{
  "expected_ancestry_valid": true,
  "unrelated_relevant_processes": [],
  "snapshot_schema": "pid-ppid-pgid-sid-state-command-v1"
}
```

It contains no PID, PPID, PGID, SID, raw command, timestamp, process-list
order, or other replay-variant field.

Required zero-science synthetic tests include:

- exact helper/direct-launcher ancestry PASS;
- marker text in the exact expected launcher row does not self-reject;
- missing self, missing launcher, wrong PPID, duplicated PID, malformed
  numeric field, ancestry cycle, and ambiguous row each reject;
- an unrelated or sibling process with an exact absolute scientific runner
  path rejects;
- an unrelated process with a forbidden script basename as a normalized
  executable/script token rejects;
- harmless prose containing a marker only as non-executable argument data
  does not become a broad-substring false positive;
- no synthetic test launches the real runner, audit, solver, or science.

## 8. Durable Attempt Records On Success Or Failure

The launcher captures in memory before launch:

- exact request and immutable source identities;
- source/AST/dataflow review;
- argv/cwd/bounded environment;
- helper, launcher, helper-root, audit-root, execution-absence, control,
  failed-root, witness, v10/runtime/complete-290, canonical, absence,
  external, link, process, and transient inventories.

It launches the helper once and captures raw stdout bytes, raw stderr bytes,
return code, signal interpretation, and wait/reap state. It then captures
the complete post inventory before any publication.

If pre/post no-write equality, root identities, and execution-root absence
do not hold, it publishes nothing and stops because evidence publication
would no longer be safely attributable.

If those equality guards hold, the launcher must persist the attempt
regardless of child success or failure:

```text
attempt_request.json
source_static_review.json
argv_cwd_environment.json
pre_inventory.json
post_inventory.json
stdout.bin
stderr.bin
child_terminal.json
wait_reap_process_group.json
attempt_guards.json
```

Each file is exclusive/no-follow, atomic, file-fsynced, reloaded, hashed,
and followed by parent fsync. Raw stdout and stderr are preserved exactly,
including empty bytes.

The launcher then publishes one mutually exclusive terminal branch.

### 8.1 Success branch

Success requires exit `0`, no signal, empty stderr, exact canonical stdout,
payload/schema validation, and every guard PASS.

It publishes:

```text
records_index.json
phase_a0_final_manifest.json
```

### 8.2 Failure branch

Any nonzero, signal, nonempty stderr, malformed stdout, payload mismatch,
or post-child semantic failure publishes:

```text
failure_records_index.json
phase_a0_failure_manifest.json
```

The failure manifest states that the authorization is consumed, execution
is forbidden, no success checkpoint exists, and exact stderr/exit evidence
is durable. T4 returns HOLD and no local retry/remediation occurs.

The success and failure final filename sets are disjoint except for the
common attempt records. A terminal manifest binds:

- exact selected branch;
- exact records-index hash and filename set including the terminal
  manifest itself;
- publication order and fsync/reload results;
- intended final modes.

It never claims its own hash/stat or post-close directory timestamp. T4
reports those values after close for root-T0 independent recording.

## 9. Independent Replay Contract

Only a complete success branch may produce:

```text
CHECKPOINT / T4AM PROCESS-SAFE AUDIT HELPER FROZEN
```

Root T0 then independently reads and audits every byte, AST, dataflow,
process-classifier test, record, index, terminal manifest, and frozen guard.
Without writing evidence, root T0 invokes the frozen launcher file once
with `--replay-only`, the same explicit absolute argv/cwd/environment, and
the same helper identity.

Replay-only:

- launches helper through the same child-launch function;
- performs no audit-record or helper-root write;
- requires execution-root absence;
- writes its raw result only to root-T0 memory;
- must reproduce byte-identical helper stdout and payload digest;
- must exit zero with empty stderr;
- must leave helper/audit roots byte/stat/inode identical.

Only complete root-T0 PASS can authorize one digest-bound execute turn.

## 10. Phase Boundary And Safety

T4am Phase A0 authorizes only:

- one fresh helper/audit/execution path triple;
- one immutable helper;
- one immutable file-based launcher;
- static/AST/dataflow and zero-science synthetic classifier tests;
- one `--first-attempt` audit-only child;
- durable success or failure closure.

It does not authorize helper execute, execution-root creation, driver
snapshot, before manifest, driver edit, T4ai preflight, scientific runner,
official audit, solver, witness, matrix, pair reuse, canonical write,
external-file mutation, cleanup, destructive action, network/install/global
mutation, new frequency, production, plots, fixtures, Kirchhoff, paper, or
GitHub work.

Use only the existing T4/T7 tasks. T4 uses `gpt-5.6-sol/high`; `max` and
`ultra` are forbidden. No task, subagent, proxy, or descendant may be
created.
