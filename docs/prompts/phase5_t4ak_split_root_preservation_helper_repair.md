# T4ak — Split-Root Preservation Helper Repair

Work only in existing T4 task
`019f5fa6-1288-7c01-8a87-4c4370cf5517`. Do not create or reuse a task,
subagent, proxy, or descendant.

## Reasoning Budget

Use `gpt-5.6-sol/high`. Do not use `max` or `ultra`.

## Start Gate

Fully read:

```text
docs/superpowers/specs/
  2026-07-27-t4ak-split-root-preservation-helper-repair-design.md
docs/superpowers/plans/
  2026-07-27-t4ak-split-root-preservation-helper-repair.md
docs/prompts/
  phase5_t7cn_split_root_preservation_helper_review.md
```

Also read project/status/current T0/T4/T7/T8 handoffs, frozen
T4ai/T4aj packages and reviews, all three immutable failed-helper roots,
T4ah v10 evidence, complete consumed witness, runtime/complete-290/runner,
canonical/absence/external/process/transient state.

Require the exact T4ak candidate identity supplied by root T0 and exact:

```text
REVIEW GREEN / T0 SPLIT-ROOT PRESERVATION HELPER REPAIR APPROVED
```

Freshly verify candidate/ref/parent/exact-four, primary/exact-fourteen,
every failed root, unchanged driver, complete witness ledger and mappings,
v10/runtime/complete-290/runner, canonical hash/stat/inodes, external
object, four absent units, and zero unexpected process/transient/link/
bytecode state. Stop on mismatch.

## Phase A0 — Split-Root Helper Freeze Only

1. Choose one fresh unique helper-root path and one distinct reserved
   execution-root path, both direct children of the exact control root.
2. Create only the helper root in mode `0700`. The execution root and all
   aliases must remain absent.
3. Publish exactly one final helper source with
   `O_EXCL|O_NOFOLLOW`, file fsync and parent fsync.
4. Embed project, control, helper, and execution roots as four direct
   full-value `ast.Constant` string assignments. Do not derive or join any
   authoritative root.
5. Expose exact `--project-root`, `--control-root`, `--helper-root`,
   `--execution-root`, and mutually exclusive `--audit-only` /
   `--execute --expected-audit-sha256`.
6. Both modes call the same pure `collect_before()`. It must bind all
   package/evidence/witness/runtime/canonical/absence/external/process/
   transient/link/bytecode guards and exact execution-root absence.
7. Canonical JSON uses sort keys, compact separators, `allow_nan=False`,
   default `ensure_ascii=True`, UTF-8, and no trailing newline.
8. Before audit-only, run the exact AST-semantic static gate. It must inspect
   named assignment node types/values, not raw source substring counts, and
   reject every forbidden root, mutation, shell/eval/exec, cleanup,
   network/install/global, or scientific surface.
9. Run audit-only exactly once under exact CPython 3.14 with explicit
   absolute argv, exact project cwd, bounded exact environment,
   `PYTHONDONTWRITEBYTECODE=1`, and stdout/stderr pipes.
10. Collect complete helper-root inventory in memory immediately before
    child launch and immediately after exit, before publishing captures.
    Require exact equality and execution-root absence.
11. Only after equality may the launcher atomically/no-overwrite/fsync
    publish request, AST result, argv/cwd/env, stdout, empty stderr, exit,
    pre/post inventories, and final manifest.
12. Verify exact helper/capture/manifest hashes and every frozen guard, then
    close files to `0400` and helper root to `0500`.

This turn must not run execute mode, create the execution root,
`preserved_sources`, a driver snapshot, `before_manifest.json`, edit the
driver, run T4ai preflight, or invoke scientific runner CLI, official
audit, solver, witness, or matrix.

On complete PASS return exactly:

```text
CHECKPOINT / T4AK SPLIT-ROOT PRESERVATION HELPER FROZEN
```

Report both exact roots, helper SHA/stat/inode, four AST assignments, exact
argv/cwd/env, stdout/payload/capture/manifest hashes, empty stderr, exit0,
pre/post inventory equality, execution-root absence, all failed-root/
driver/witness/v10/runtime/complete-290/canonical/absence/external/process/
transient guards, and scientific counts `0/0/0`. Then pause.

Any mismatch or failure is immutable and returns HOLD. Do not create another
helper or run another audit-only attempt.

## Phase A1 — Separate Root-T0 Authorization Required

Do not run execute mode unless root T0 later sends a digest-bound exact
authorization identifying the frozen helper, helper root, reserved execution
root, audit payload, execute argv/cwd/environment, and one-shot boundary.

After authorization, execute once. The shared audit and digest match must
pass while the reserved root remains absent. Then create only that execution
root and publish the old-driver snapshot, canonical before manifest, durable
execution records, and launcher captures there with the exact
exclusive/atomic/fsync/reload/stat/inode/nlink/non-alias semantics in the
design. Never reopen or mutate the helper root.

Only complete preservation PASS permits resuming the reviewed T4ai
artifact-local driver/solver-free tests and one fresh exact-Python-3.14
zero-science preflight. On later PASS return exact:

```text
CHECKPOINT / RELOCATED BENCHMARK IDENTITY CONTRACT FROZEN
```

## Stop Conditions

Stop on any package, root, identity, write-scope, process, transient,
bytecode, canonical, test, evidence, or scientific anomaly.

No retry, cleanup, destructive action, outside mutation, witness, official
scientific audit, solver, matrix, pair reuse, canonical write, runner/
science/runtime/complete-290 edit, threshold/tolerance/mode/point/lmax
change, network/install/global mutation, new frequency, production, plot,
fixture, Kirchhoff, paper, GitHub work, or new agent is authorized.
