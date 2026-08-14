# Phase 6 V3.1-U bounded resume-controller design

Date: 2026-08-12

Repair gate: `phase6_v3_1_u_resume_controller_repair_1`

This is bounded repair cycle 1 of the distinct V3.1-U gate.  It repairs the
missing control-plane resume implementation required by the already frozen run
contract.  It changes no science formula, solver, selector, domain, threshold,
certificate, convention or completed science byte.

## Frozen interrupted state

The only resumable root is

```text
runs/phase6/classic_scattering/
v3_1_hp_unitarity_deficit_v1_20260811T143911Z_py314
```

Its verified state is:

```text
Route-A committed ordinals: 0..434
next ordinal/key: 435 / kM=8, ell=28, even
remaining Route A: 61 modes / 1,220 ladder records
Route U/B/C: not started
terminal success/failure files: absent
active writer: absent
```

Frozen prefix identities:

```text
records.jsonl: 435 records, 943913 bytes,
  932129a4921cd71b7867bcc2f0e146ed6940eb84403f366b58989e447402b9a0
ladder_records.jsonl: 8700 records, 16898419 bytes,
  8f387abb83115ac76d87170bc5c1220d6effc6f4586c6202bb069fb35cb8d088
checkpoint inventory: 435 entries.  SHA-256 of the compact, no-newline,
  sort-keys JSON map `relative_path -> {sha256,size,mode,nlink}` is
  2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11
mode_checkpoints/route_a_0434.json:
  c61e44e027d05d65a5c8a39868cc138fb4b72df7e6efb6d014d9e03c666ce986
```

The zero-byte `.writer.lock` is preserved as stale-writer evidence.  It is a
regular nlink-1 file with SHA-256 `e3b0c442...b855`.  It must not be manually
deleted.

## Governance identity constraint

The original source ledger binds the exact current bytes:

```text
status.md: 15d29b641b66b061c8865edb72eb811519360bda6a314515fd115cbe1ab96158
T0_current.md: f80779de4990d6d18581d8ee4bccef1393f3a61b6fdb7cdbced272a357ac0ffa
T7_current.md: 61e25ccb891b992cc82426a135dca1bccdaafa3f84ccb9bfa338a6d3e8a4c383
```

Until this root becomes terminal, these three files are frozen.  Formal T7
package and implementation reviews must publish archive-only records and must
not update `T7_current.md`.  T0 must not update status/T0 handoff.  This delayed
control-plane publication is necessary for the original start/end science
ledger to remain exact; it does not waive either independent review.  All
current state is carried in immutable review/dispatch archives and is copied to
the current handoffs immediately after terminalization.

## Allowed implementation scope

T4 may only add:

```text
src/schwgw/validation/phase6_v3_hp_unitarity_resume.py
scripts/phase6_v3_1_hp_unitarity_resume.py
tests/unit/test_phase6_v3_hp_unitarity_resume.py
tests/regression/test_phase6_v3_hp_unitarity_resume_publication.py
```

The original V3.1-U five implementation/test files, seven protected radial
files, frozen V3.0 authorities, original root bytes and all predecessor roots
are read-only.  The controller imports the original V3.1-U implementation as a
science dependency and adds orchestration/provenance only.

## Controller state machine

```text
DISCOVER_READ_ONLY
-> VERIFY_FROZEN_IDENTITIES
-> VALIDATE_ORIGINAL_CONTRACT
-> VALIDATE_CONTIGUOUS_PREFIX
-> CLASSIFY_SYSTEM_INTERRUPTION
-> ACQUIRE_WRITER_EXCLUSION
-> PUBLISH_RESUME_AUTHORITY
-> RECOVER_PREPARED_TRANSACTION
-> APPEND_ROUTE_A
-> FREEZE_ROUTE_MAP
-> APPEND_ROUTE_U
-> APPEND_ROUTE_B
-> APPEND_ROUTE_C
-> ORIGINAL_THRESHOLD_EVALUATION
-> ORIGINAL_VALIDATOR
-> RESUME_VALIDATOR
-> TERMINAL_PASS
```

Scientific, threshold, nonfinite, provenance, source or validator failure is
terminal and non-resumable.  Only a dead owner plus an exactly reconstructable
transactional prefix and no failure artifact qualifies as a system
interruption.

## Stable writer exclusion and authority publication

The existing `.writer.lock` is the stable exclusion object.  It is never
renamed, unlinked, replaced or rewritten during any resume attempt.  The
controller opens it with `O_NOFOLLOW`, verifies the frozen inode/dev,
regular/nlink-1/mode/size/SHA, and obtains `flock(LOCK_EX|LOCK_NB)`.  That fd
remains flocked through terminal sealing.  Every later controller uses the same
pathname and inode, so there is no handoff interval in which the exclusion
object is absent.  Concurrent controllers fail closed.

Under the held flock the controller rechecks that the original PID is dead, no
exact-root writer process exists, and `lsof` reports no other writable fd for
the lock or JSONL files.  It then creates the next monotone
`resume_control/attempt_NNNN/` directory.  The zero-byte original lock is copied
as an identity-bearing snapshot inside the attempt, but the stable lock itself
stays in place and byte-identical.  At successful terminal sealing it is chmod
0444 and retained in the terminal manifest as resume-exclusion evidence; the
fd is released only after the root is 0555 and both validators pass.

Every control-plane JSON is published with one primitive:

1. O_EXCL-create an attempt-local staging file;
2. full-write and fsync the complete canonical bytes;
3. atomically move it to an absent final name using Darwin
   `renamex_np(RENAME_EXCL)` on the same filesystem;
4. fsync the destination directory.

If the no-replace atomic primitive is unavailable, the controller fails closed.
A crash before the atomic move leaves only a staging file; a crash after it
leaves only a complete final file.  No partial final-name authority is legal.
Incomplete staging files are retained as evidence and never parsed as committed
authority.

Before any science call the attempt atomically publishes:

```text
attempt_intent.json
prelock_liveness.json
stable_writer_lock_snapshot.bin
writer_exclusion.json
resume_authority.json
resume_source_start.json
authority_commit.json
```

`authority_commit.json` is last and hashes the complete prior set.  No solver
intent or science call is reachable before it exists and validates.  A crash
before it creates an `ABANDONED_PRE_SCIENCE` attempt; the next monotone attempt
retains and inventories every committed final file and every staging fragment,
then publishes an `abandoned_attempt_adjudication.json`.  A crash after it
creates a committed authority ancestor for the next attempt.  Neither state
requires deleting or rewriting a prior attempt.

The authority binds both formal T7 archive-only approvals, the T0 dispatch
authority, controller/CLI/tests, original run/source/inventory and five science
implementation hashes, seven protected hashes, all prefix sizes/hashes/counts,
the 435-checkpoint identity inventory, next key, runtime/argv/cwd, stable-lock
identity and no-writer evidence.  A later system interruption validates the
complete committed/abandoned attempt chain before publishing its monotone
successor.

## Transactional append protocol

Existing JSONL files are opened only with
`O_WRONLY|O_APPEND|O_NOFOLLOW`.  `fstat` must match the validated inode/dev,
nlink, mode, size and prefix hash.  No seek-write, truncate, replace or
reformat is allowed.  Every canonical JSONL record is full-written and fsynced.

Before solving one mode/node group, the controller atomically publishes an
immutable intent containing the exact input, logical solver-call ordinals and
source/authority identity.  After the solve and before any append, it atomically
publishes an immutable prepared transaction containing the intent identity,
the exact canonical byte blocks and hashes for every target JSONL, and the
checkpoint bytes/hash.  Prepared, checkpoint and commit final names therefore
can never contain partial bytes.

Each prepared transaction records every target file's validated preappend
inode/dev/mode/nlink/size/hash.  Under the stable flock, recovery treats the
bytes after that exact preappend size as follows:

- empty: append the complete prepared block;
- an exact byte prefix of the prepared block, including a partial JSON line:
  append only the missing tail;
- the complete prepared block: append nothing;
- any longer, mismatched, unauthenticated, duplicate or gapped suffix: fail
  closed.

All appends use `O_WRONLY|O_APPEND|O_NOFOLLOW`; each missing tail is full-written
and fsynced.  No existing byte is truncated, sought over, replaced or rewritten.
Commit order is ladder/data blocks, fsync, atomic checkpoint publication,
directory fsync, then atomic transaction-commit publication.

Recovery rules are deterministic:

- no intent: calculate that exact next ordinal once;
- atomic intent but no atomic prepared record: retain the interrupted intent and
  calculate that not-yet-prepared ordinal once under the successor authority;
- staging fragment but no final prepared record: retain the fragment as
  incomplete evidence; it is not authenticated science and may be recalculated;
- prepared plus an exact partial/full suffix: complete only the missing prepared
  tail, then continue checkpoint/commit publication;
- mode present but checkpoint absent: atomically publish the prepared
  checkpoint;
- committed: never solve or append again;
- any byte mismatch, unknown suffix, duplicate/gap or bytes without a complete
  prepared record: fail closed; never truncate.

The same protocol covers Route A, Route U and Route B.  Route C is first written
to attempt-local staging.  An interrupted external solve without an atomic
prepared record is retained and may be rerun under a successor authority.  Once
the exact 23-record canonical output and raw-output identities are atomically
prepared, the formal files use the same authenticated byte-prefix/atomic
publication rules and are never recalculated.

After every append and at terminal, the original prefix byte ranges must still
hash to the two frozen prefix hashes above.

## Terminal provenance and validation

The original `source_start.json` stays byte-identical.  Original immutable
science sources are rehashed and the original source-start/end equality is
preserved.  Additive files are published separately:

```text
resume_source_map.json
resume_authority_index.json
```

The original threshold evaluator, sealer, manifest builder and terminal
artifact schemas remain authoritative.  The manifest already hashes additional
regular files, so all resume control artifacts become bound evidence.

Terminal success requires both:

1. original `validate_official_candidate(..., validate_live_sources=True)`;
2. the additive resume validator rebuilding every authority, transaction,
   prefix hash, solver-call ordinal and terminal artifact.

`validate_live_sources=False` is forbidden for formal closure.

## Required tests and reviews

Positive real-filesystem tests cover synthetic prefixes 0/1/435/495, exact
calls 435..495, immutable prefix hashes, full Route-A-before-route-map ordering,
Route U/B/C recovery, a second system interruption, original+resume validators
and manifest inclusion.  Forced process death is injected before/during/after
every atomic authority publication and at every byte boundary of each prepared
JSONL block; exact authenticated prefixes must resume byte-identically.

Negative tests cover hash/size/inode/mode/nlink drift; duplicate/gap/reorder,
unauthenticated or mismatched torn JSONL and wrong key;
missing/extra/bad checkpoint; live PID/flock/open fd;
symlink/hardlink/nonregular files; package/protected/review drift; wrong runtime
or authority order; prepared/suffix mismatch; partial write at every transaction
phase; early route map; unauthorized U/B/C content; any terminal failure; and
coordination-file drift.

Tests must exercise real `O_APPEND`, `fsync`, `O_EXCL`, flock and injected
interruptions on temporary copies.  Mock-only evidence is insufficient.

After T4 implements and passes all tests/dry runs without touching the real
root, formal T7 performs an archive-only implementation delta review.  Only
then may T0 freeze a one-use dispatch authority and instruct T4 to resume the
real root.

## Non-claims

This repair does not accept V3.1-U science, change the failed predecessor r3,
authorize V3.2, close full-domain V3, close common absolute phase, establish Li
equivalence or permit global GREEN.
