# Formal T7 prompt — V3.1-U resume-controller package repair-1 delta review

You are the existing formal SchWO T7 task.  Delta-review this bounded
control-plane package repair read-only and independently.  Do not edit
package/design/prompt/science
or current-handoff bytes, acquire or rename the real writer lock, append to the
real root, run any radial/AP/Wolfram solve, dispatch T4 or start V3.2.

## Frozen candidate

```text
configs/phase6_v3_1_u_resume_controller_package.json
  2fcd2e4cc57845b32573047fa3989e1bfcd4f520eefcea6f6df6504d164602fe
docs/phase6_v3_1_u_resume_controller_design.md
  094235c0ce0158521da81ec0587899dc6dc942ab92866e8afe8f3102487fa9d7
docs/prompts/phase6_t4_v3_1_u_resume_controller.md
  72e40f540d3f406c6d1af79931d425b9efc8e5517f21d6e91ba9b1c8b0333b05
docs/prompts/phase6_t7_v3_1_u_resume_controller_delta_review.md
  d61acbb61787746a5442dedbf52caa7815376bff482edd2ba5450e1c278e457a
```

Gate: `phase6_v3_1_u_resume_controller_repair_1`.

This is bounded control-plane package repair 1 of the distinct V3.1-U gate.
The previous archive-only review is:

```text
docs/handoffs/archive/
T7_2026-08-12_v3_1_u_resume_controller_package_review.md
  daba09ea92781596d54e9eefee729cfa0a1c117862443fa6445f4ab0d20f2c76
```

It froze all passed items and identified exactly two failed items:
`v31ur_lock_authority_crash_chain` and
`v31ur_transaction_partial_suffix_recovery`.  Recheck only those failed items,
the protected identities and whether the repair broke a passed invariant.  Do
not reopen a passed item without exact causal evidence.  The package changes no
science byte and does not accept V3.1-U.

## Archive-only governance

The original `source_start.json` binds the exact current bytes of `status.md`,
`docs/handoffs/T0_current.md` and `docs/handoffs/T7_current.md`.  Rehash all
three at start/end and do not modify them.  Persist this review only as:

```text
docs/handoffs/archive/
T7_2026-08-12_v3_1_u_resume_controller_package_delta_review_1.md
```

This delayed current-surface publication preserves the original start/end
provenance; it does not waive or weaken independent review.

## Required independent checks

Read fully the governance protocol/template, the prior T7 package-review
archive, all four repaired candidate files and their changed hunks, and every
protected/current identity.  Rehash the interrupted root prefix only to confirm
the already-passed invariant remains intact; do not redo unrelated science
review.

Independently verify:

1. `.writer.lock` is now one stable never-renamed/unlinked/replaced pathname;
   its original inode and bytes remain fixed, its nonblocking flock is held
   through terminal 0555 dual validation, and no crash boundary can leave the
   root without a discoverable exclusion object;
2. every authority/prepared/checkpoint/commit final name is published only from
   complete fsynced staging bytes using same-filesystem Darwin
   `renamex_np(RENAME_EXCL)` plus directory fsync; a crash yields either staging
   evidence or a complete final file, never a partial final authority;
3. `authority_commit.json` is the last pre-science publication; incomplete
   attempts are preserved and explicitly adjudicated, while committed and
   abandoned attempts form a deterministic monotone chain;
4. a complete atomic prepared record authenticates exact JSONL byte blocks and
   their preappend identities; after process death, an exact partial suffix is
   completed by appending only the missing tail, while any mismatch, unknown
   bytes, duplicate or gap remains terminal without truncate/rewrite/re-solve;
5. the same semantics cover Route A/U/B and staged Route C, including the
   distinction between an unauthenticated staging fragment that may be
   recalculated and prepared/committed science that may not;
6. the required forced-death real-filesystem tests cover every authority
   publication boundary and every prepared byte boundary, plus concurrency,
   tamper and second-interruption cases;
7. authority still binds package approval,
   final controller bytes, T7 implementation approval, one-use T0 dispatch,
   original/prefix/protected identities, runtime and liveness evidence;
8. a second system interruption is now safely resumable through a monotone attempt
   chain, while scientific/provenance/threshold/nonfinite failure remains
   terminal and non-resumable;
9. the previously passed prefix/source/protected/current/validator/nonclaim
   invariants remain unchanged, including checkpoint-map digest
   `2269f129814c26d609cf3fdd0a451a5fd35661a576cf4d030f4f7b9516366d11`.

Use the dual-axis verdict and complete finding schema.  New unrelated advice is
FOLLOW_UP_DEBT unless it directly invalidates this bounded controller claim.

If and only if the unchanged package is sufficient for bounded T4
implementation and temp-copy validation, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U RESUME-CONTROLLER REPAIR PACKAGE READY FOR T4
```

If a class-A defect exists, return `REPAIR` with all nine blocker fields.  If
safe resume is impossible without changing frozen science, return `ESCALATE`
with causal evidence.  Do not dispatch downstream work.  Return the archive
path/SHA and confirm `T7_current.md` remained byte-identical.
