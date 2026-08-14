# Formal T7 prompt — V3.1-X sentinel repair-cycle-1 implementation delta

This prompt activates only after package approval and formal T6 zero-science
implementation/preflight.  Perform an incremental archive-only review in
formal T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed`.

Freeze the package, package review, T6 evidence and exact four repaired hashes
at review start.  Recheck only the failed WLS argv-interface item, whether the
four-file delta damaged frozen passed invariants, and protected/source/runtime
identities.  Do not reopen unrelated passed items.

Mandatory checks:

- independently reproduce the exact WolframKernel 14.3 `$CommandLine` vector;
- prove exact-shape-only parsing and negative-form rejection;
- run the real-kernel absent-request handshake and prove rc73 occurs before
  import, source loading and solver execution;
- verify the producer binds the predeclared review path, exact verdict and all
  repaired hashes, while the later dispatch supplies the review digest;
- attack stale/alternate reviews, environments, argv/cwd/executable/launcher,
  dispatch replay and root reuse; all fail closed;
- verify exact four-path scope, unchanged CLI/core/package/graph/method/
  precision/threshold/convention/protected identities and zero science;
- confirm the failed sentinel dispatch/root are never reusable and a later
  sentinel requires a different one-use dispatch and fresh absent UTC root.

If the blocker closes, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 IMPLEMENTATION READY FOR ONE-USE T0 DISPATCH
```

This consumes bounded repair cycle 1 and authorizes only a Root-T0 fresh
sentinel dispatch.  If a complete blocker remains, return `REPAIR` and record
whether it is the same substantive blocker; at most repair cycle 2 remains.

Write only
`docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_implementation_delta_review.md`
and report its SHA-256, inventories, tests, protected start/end identities and
nonclaims.  No sentinel science, official dispatch, V3.2 or global GREEN.

