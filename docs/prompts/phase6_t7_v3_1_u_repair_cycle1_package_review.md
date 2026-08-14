# Formal T7 prompt — V3.1-U repair-cycle-1 package review

Perform an archive-only, zero-solver review of the exact combined bounded
repair-1 package supplied by Root T0.  Work in the existing formal T7 task
`019f5ed1-b421-7ec2-9bac-8d134855a1ed`.

Read `project.md`, `docs/review_gate_liveness_protocol.md`, the verdict
template, current status/T0/T7 handoffs, the original V3.1-U package/design and
review prompts, the terminal failure evidence, the formal terminal review
`7aa90e...82f1`, the control-plane clarification `2f661f...0da0`, the new
repair package, its design, this prompt, the T4 implementation prompt and the
future implementation-delta prompt.  Rehash every named identity directly.

Review only package readiness.  Do not edit implementation, run a numerical
solver, acquire a writer lock, mutate a root, or start V3.2.

## Required package checks

Independently verify:

1. the sole class-A item remains
   `v31u_auxiliary_radius_closed_boundary_roundoff` and completed bounded
   scientific repairs remain `0`;
2. the science repair paths are exactly oracle plus the two tests;
3. the only additional control-plane implementation path is the producer,
   making exactly four unique changed paths;
4. the CLI SHA remains
   `01ce96122b1c2dca9f29ec0355dd51ccf0611842fcdc7d0850107d012a6f25a4`;
5. the closed inequality, exponent order/set, match radius, precision schedule,
   318-key selector, 16 thresholds and complete graph are unchanged;
6. the exact/squared-ratio construction is mathematically equivalent at the
   boundary and defines just-below/just-above behavior without tolerance;
7. the mandatory `318*3=954` no-solve geometry proof is complete and cannot
   call a science backend;
8. the start-gate design removes mutable live-handoff equality without adding
   alternate hashes or a bypass, preserves all immutable authorities, and can
   bind a later implementation review plus one-use exact-root T0 dispatch;
9. the fixed-path dispatch design is sufficient despite the frozen CLI and is
   not an environment-, argv-, or boolean-selected authority escape;
10. the failed root is immutable evidence only and a later run must use a
    fresh absent UTC root with zero predecessor-science reuse;
11. all V3.0, source and seven protected identities remain exact and no
    threshold/domain/convention/protected modification is authorized.

Treat any ambiguity in item 9 as a package-level finding now; T4 may not invent
an authority channel later.  Classify every finding under the liveness
protocol with complete blocker fields.

If the package is ready, return exactly:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-U REPAIR CYCLE 1 PACKAGE READY FOR T4
```

If not ready, return `REPAIR / NOT_ASSESSED` with bounded package corrections.
This package review does not consume scientific repair cycle 1.

Write a durable archive at
`docs/handoffs/archive/T7_2026-08-12_v3_1_u_repair_cycle1_package_review.md`,
record its SHA-256, the reviewed package/member hashes, passed/failed item
inventories, protected start/end hashes and nonclaims.  You may update
`T7_current.md`; the repaired design must not depend on its future live hash.

No T4 implementation is authorized unless Root T0 separately dispatches the
unchanged reviewed package.  No science execution, V3.2 or global GREEN.
