# T7co — Stable Audit Replay Contract Repair Review

Work only in existing T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed` as an independent read-only
reviewer. Use `gpt-5.6-sol/high`. Do not create a task, subagent, proxy, or
descendant.

## Required Reading

Fully read:

- `project.md`, `status.md`, current T0/T4/T7/T8 handoffs;
- the exact four-file T4al candidate supplied by root T0;
- frozen T4ai/T4aj/T4ak design, plan, reviewer and executor prompts and
  exact decisions;
- all four immutable failed-helper roots and every file in them;
- live driver, T4ah v10 evidence, complete-290, hermetic runtime, complete
  consumed witness, unusable isolated pair, canonical/absence/external/
  process/transient state.

Verify candidate commit, parent, ref, exact four added paths,
commit/worktree blobs, sizes, SHA-256 values, and `git diff --check`.
Review only that exact identity.

## Independent Review

Check that:

1. The T4ak root contains exactly helper SHA
   `77902b3613deaddbc254ba57bd851f7f11b479f73d34c9e7f0dea9b210da23aa`,
   size `36258`, inode `1233145`, mode `0400`, and no capture or manifest.
2. All four authoritative T4ak root assignments are direct
   `ast.Constant` strings; audit-only/execute counts are zero.
3. The exact blocker is real: helper-root inventory requires one file,
   includes mode/mtime/ctime, while the frozen protocol would add captures
   and chmod the same root before root-T0 replay.
4. The reserved T4ak execution root remains absent; the T4ak attempt and
   all three older failed roots are exhausted and immutable.
5. Driver `057bb24b...59a9`, runner `18e79435...a768`, v10/runtime/
   complete-290, consumed witness, canonical four, external object, absent
   units, and process/transient/link guards remain exact.
6. T4al uses three pairwise-distinct direct-child roots: immutable helper,
   immutable audit-record, and reserved absent execution.
7. Project/control/helper/audit-record/execution assignments are five full
   exact `ast.Constant` strings and implicit construction is rejected.
8. Helper root is closed before the first audit and forever contains only
   the helper; captures can never be published there.
9. Audit-record root is created before the first audit and receives only
   launcher captures/manifest after child exit.
10. The canonical helper payload binds the audit-record root through
    exactly path/dev/inode/uid/gid/is-directory/non-symlink/direct-child.
11. Mode, nlink, size, timestamps, children, names, child bytes/stats/
    hashes, counts, inventory digest, and full directory identity are
    explicitly excluded from that payload.
12. The exclusion is limited to launcher evidence, not any scientific,
    runtime, input, canonical, preservation, helper, or execution guard.
13. Full pre/post child inventories and full audit-root
    hash/stat/inode/mode/publication/fsync records remain mandatory launcher
    evidence and are independently rechecked by root T0.
14. Terminal evidence is explicitly non-self-referential:
    `records_index.json` covers all earlier records, while
    `phase_a0_final_manifest.json` binds the index and exact filename set
    including itself but does not claim its own hash/stat or a post-close
    directory timestamp. T4 reports those terminal/post-close identities
    for root-T0 independent recording.
15. Ordinary capture publication cannot change the control hazard payload;
    symlink/hardlink/bytecode/lock/tmp/partial/quarantine anomalies still
    fail closed.
16. Audit-only and execute share the same pure `collect_before()`;
    execution-root absence and complete scientific/provenance guards remain
    in the canonical payload.
17. Canonical stdout uses default `ensure_ascii=True`, UTF-8, sorted compact
    JSON, `allow_nan=False`, and no newline.
18. Phase A0 runs audit-only once, writes captures only after no-write
    inventory equality, and stops at
    `CHECKPOINT / T4AL STABLE AUDIT REPLAY HELPER FROZEN`.
19. Root T0 must independently read/AST-check and rerun the exact same
    audit-only argv without writes; stdout bytes and digest must equal the
    captured first run.
20. Execute is separately authorized, digest-bound, one-shot, and writes
    only to the absent execution root while helper/audit roots stay
    untouched.
21. Snapshot/before-manifest durability and no-retry semantics remain at
    least as strict as T4ak.
22. Preservation PASS may resume only the already reviewed T4ai
    artifact-local repair and one zero-science preflight.
23. No witness, scientific audit, solver, matrix, pair reuse, canonical
    write, scientific/runtime/input/threshold change, destructive action,
    downstream work, or GitHub action is authorized.
24. T4 uses sol/high only; max and ultra are forbidden.
25. No task, subagent, proxy, or descendant is created.

Any incomplete stable-projection schema, mutable capture data in the audit
payload, helper-root mutation, self-referential terminal manifest, missing
full launcher evidence, replay non-determinism, weakened evidence/scientific
gate, or implicit retry is a blocker.

## No Writes Or Dispatch

Do not edit files, artifacts, environment, status, handoffs, or candidate.
Do not execute any failed helper, audit-only, execute, preflight, witness,
official audit, solver, matrix, or science. Do not dispatch T4/T7ch/T8 or
perform GitHub actions.

## Exact Decision

Return to root T0 with exactly one:

```text
REVIEW GREEN / T0 STABLE AUDIT REPLAY CONTRACT REPAIR APPROVED
REVIEW YELLOW / T0 STABLE AUDIT REPLAY CONTRACT CHANGES REQUIRED
REVIEW RED / T0 STABLE AUDIT REPLAY CONTRACT REPAIR INVALID
```

Then report exact candidate identity, independent evidence, and bounded
blockers if any.
