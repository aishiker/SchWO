# Formal T7 prompt — V3.1-X sentinel repair-cycle-1 package review

Perform an archive-only, zero-solver review in the existing formal T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed`.

Read completely: `project.md`; the review-gate liveness protocol and verdict
template; current status/T0/T7 handoffs; the V3.1-X package/design/review
chain; the failed sentinel dispatch/root; formal sentinel terminal review;
the new repair package and design; this prompt; the T6 implementation prompt;
and the future implementation-delta prompt.  Rehash every identity directly.

Review package readiness only.  Do not edit implementation, invoke
WolframKernel, run a solver, create a dispatch/root, or start V3.2.

Independently verify:

1. the sole class-A blocker and its complete nine fields remain exactly the
   WLS command-line mismatch classified by formal T7;
2. this is V3.1-X bounded repair 1 with completed repairs `0/2`, not V3.1-U
   repair cycle 3;
3. the exact change scope is WLS, producer authority binding and two tests;
4. the frozen process argv is five elements and an independent zero-science
   WolframKernel 14.3 probe establishes `$ScriptCommandLine={}` and exact
   `$CommandLine={kernel,-script,WLS,request,output}`;
5. the repair accepts only that exact shape and rejects missing, extra,
   reordered, alternate-executable/mode/script and fallback forms;
6. the positive handshake reaches only the absent-request guard with rc73,
   before import/source loading/solver activity;
7. the future review/dispatch chain is non-circular and binds the repaired six
   hashes without hard-coding the future review digest;
8. the failed dispatch/root remain immutable and forbidden, and any later
   sentinel must use a different one-use dispatch and fresh absent UTC root;
9. package, graph, method, overlay, precision, threshold, convention,
   environment and seven protected identities remain unchanged.

If ready, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X SENTINEL REPAIR CYCLE 1 PACKAGE READY FOR T6
```

Otherwise return `REPAIR / NOT_ASSESSED` with complete bounded findings.
Package review does not consume repair cycle 1.

Write only the durable archive
`docs/handoffs/archive/T7_2026-08-13_v3_1_x_sentinel_repair_cycle1_package_review.md`
and report its SHA-256.  No implementation, science, dispatch, V3.2 or global
GREEN is authorized.

