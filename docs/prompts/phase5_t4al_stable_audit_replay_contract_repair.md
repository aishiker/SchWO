# T4al — Stable Audit Replay Contract Repair

Work only in existing T4 task
`019f5fa6-1288-7c01-8a87-4c4370cf5517`. Do not create or reuse a task,
subagent, proxy, or descendant.

## Reasoning Budget

Use `gpt-5.6-sol/high`. Do not use `max` or `ultra`.

## Start Gate

Fully read:

```text
docs/superpowers/specs/
  2026-07-27-t4al-stable-audit-replay-contract-repair-design.md
docs/superpowers/plans/
  2026-07-27-t4al-stable-audit-replay-contract-repair.md
docs/prompts/
  phase5_t7co_stable_audit_replay_contract_review.md
```

Also read project/status/current T0/T4/T7/T8 handoffs, frozen
T4ai/T4aj/T4ak packages and reviews, all four immutable failed-helper
roots, v10/runtime/complete-290/runner evidence, complete consumed witness,
canonical/absence/external/process/transient state.

Require the exact T4al candidate identity supplied by root T0 and exact:

```text
REVIEW GREEN / T0 STABLE AUDIT REPLAY CONTRACT REPAIR APPROVED
```

Freshly verify candidate/ref/parent/exact-four, primary/exact-fourteen,
every failed root, unchanged driver, complete witness ledger and mappings,
v10/runtime/complete-290/runner, canonical hash/stat/inodes, external
object, four absent units, and zero unexpected process/transient/link/
bytecode state. Stop on mismatch.

## Phase A0 — Three-Root Helper Freeze Only

1. Choose fresh unique pairwise-distinct helper-root, audit-record-root, and
   reserved execution-root paths, all direct children of the exact control
   root.
2. Create helper and audit-record roots mode `0700`. Execution root and all
   aliases remain absent.
3. Publish exactly one final helper source using `O_EXCL|O_NOFOLLOW`, file
   fsync and parent fsync.
4. Embed project, control, helper, audit-record, and execution roots as five
   direct full-value `ast.Constant` string assignments. Derivation or
   implicit construction is forbidden.
5. Expose exact `--project-root`, `--control-root`, `--helper-root`,
   `--audit-record-root`, `--execution-root`, and mutually exclusive
   `--audit-only` / `--execute --expected-audit-sha256`.
6. Both modes call the same pure `collect_before()`.
7. The helper-root inventory remains strict and contains only the helper.
   Set helper mode `0400` and helper-root mode `0500` before audit-only;
   never reopen or mutate that root.
8. Bind audit-record root in the canonical payload only through the exact
   stable projection: path/dev/inode/uid/gid/is-directory/non-symlink/
   direct-child. Reject mode/nlink/size/all timestamps/all child or
   inventory fields from that projection.
9. The AST/dataflow static gate must prove the exact projection schema,
   helper-root immutability, capture-only audit root, execution-root
   absence, shared collect-before path, and forbidden-surface exclusions.
   Raw substring counting is not an acceptance test.
10. Canonical JSON uses sorted keys, compact separators,
    `allow_nan=False`, default `ensure_ascii=True`, UTF-8, and no newline.
11. Run audit-only exactly once under exact CPython 3.14 with explicit
    absolute argv, exact project cwd, bounded environment,
    `PYTHONDONTWRITEBYTECODE=1`, and stdout/stderr pipes.
12. Collect complete helper-root, audit-record-root, execution-absence, and
    bounded control inventories in memory immediately before child launch
    and immediately after exit, before publishing captures. Require exact
    equality.
13. Require exit zero, empty stderr, exact canonical stdout, helper root
    unchanged, and execution root absent.
14. Only after equality may the launcher publish request, AST/dataflow
    result, argv/cwd/env, stdout/stderr/exit, pre/post inventories,
    stable-projection/payload-schema proofs, publication/fsync records, and
    other non-terminal captures exclusively in the audit-record root.
15. Publish `records_index.json` covering every earlier record, then
    `phase_a0_final_manifest.json` binding the index, exact expected final
    filename set including itself, publication order, fsync/reload proofs,
    and intended final modes. The terminal manifest must not claim its own
    hash/stat or a post-close directory timestamp.
16. Independently reload both terminal files and verify exact indexed
    file/hash/stat/inode/nlink/mode records and filename set.
17. Close files `0400` and audit-record root `0500`, fsync, report the
    terminal-manifest hash/stat and post-close root identity for root-T0
    independent recording, and reverify helper root untouched and
    execution root absent.

This turn must not run execute mode, create the execution root, copy the
driver, publish a before manifest, edit the driver, run T4ai preflight, or
invoke scientific runner CLI, official audit, solver, witness, or matrix.

On complete PASS return exactly:

```text
CHECKPOINT / T4AL STABLE AUDIT REPLAY HELPER FROZEN
```

Report all three exact roots, helper/audit-record identities, five AST
assignments, stable-projection schema, exact argv/cwd/env, stdout/payload/
capture/manifest hashes, empty stderr, exit0, pre/post equality, helper-root
immutability, execution-root absence, all failed-root/driver/witness/v10/
runtime/complete-290/canonical/absence/external/process/transient guards,
and scientific counts `0/0/0`. Then pause.

Any mismatch or failure is immutable and returns HOLD. Do not create
another helper or run another audit-only attempt.

## Phase A1 — Separate Root-T0 Authorization Required

Do not run execute unless root T0 later sends a digest-bound exact
authorization identifying the frozen helper, helper/audit/execution roots,
captured and independently replayed audit digest, exact execute
argv/cwd/environment, and one-shot boundary.

After authorization, execute once. The shared audit and digest match must
pass while helper and audit-record roots remain untouched and execution
root remains absent. Then create only the execution root and publish the
old-driver snapshot, canonical before manifest, durable execution records,
and launcher captures there with reviewed exclusive/atomic/fsync/reload/
stat/inode/nlink/non-alias semantics.

Only complete preservation PASS permits resuming the reviewed T4ai
artifact-local driver/solver-free tests and one fresh exact-Python-3.14
zero-science preflight. On later PASS return exact:

```text
CHECKPOINT / RELOCATED BENCHMARK IDENTITY CONTRACT FROZEN
```

## Stop Conditions

Stop on any package, root, identity, projection, replay, write-scope,
process, transient, bytecode, canonical, test, evidence, or scientific
anomaly.

No retry, cleanup, destructive action, outside mutation, witness, official
scientific audit, solver, matrix, pair reuse, canonical write, runner/
science/runtime/complete-290 edit, threshold/tolerance/mode/point/lmax
change, network/install/global mutation, new frequency, production, plot,
fixture, Kirchhoff, paper, GitHub work, or new agent is authorized.
