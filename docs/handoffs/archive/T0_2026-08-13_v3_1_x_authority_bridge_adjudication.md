# Root T0 adjudication — V3.1-X implementation-review authority bridge

Date: 2026-08-13

```text
ADJUDICATION: REDESIGN CONTROL PLANE / PRESERVE SCIENCE BYTES
SOURCE_GATE: phase6_v3_1_x_external_direct_route_v1
SOURCE_VERDICT: ESCALATE / T0 ADJUDICATION REQUIRED
NEW_GATE: phase6_v3_1_x_external_direct_authority_bridge_v1
```

Formal T7 delta recheck 2 exhausted the two bounded implementation repairs.
All scientific and numerical implementation items are closed, but production
`IMPLEMENTATION_REVIEW_PATH` still names the immutable repair-1 YELLOW review.
Consequently every future sentinel dispatch is rejected before consumption,
root creation or science.

Root T0 chooses liveness option 2: redesign the control-plane gate. This is
not repair cycle 3, does not rename the old blocker, and does not alter the
V3.1-X scientific gate. The distinct bridge gate may change only the fixed
implementation-review authority path and the zero-science tests that prove
its semantics.

## Frozen source evidence

- V3.1-X package:
  `configs/phase6_v3_1_x_external_direct_route_package.json`, SHA-256
  `6a4ab0f690afab975c981f65fc80e0e3f48541da00c4023330ee94274146f752`.
- Initial implementation review: SHA-256
  `43227b575af051b7beee0c1e568c7842b6724bbb12bb85aebc8389d6b7d2c393`.
- Delta recheck 1: SHA-256
  `e1dde2575e8ad328062ef360a5146bb02d29d2ea3b462ea5e72d566d4d645285`.
- Delta recheck 2: SHA-256
  `549440b9d528112eb4cad4882fdae16d105295ad8f86e077ebfe1a163edbb26c`.
- Final reviewed exact-six implementation hashes are those recorded in delta
  recheck 2. The seven protected radial identities and external snapshot
  identities remain exact.

## Non-circular bridge

The sole future production authority path is predeclared as:

```text
docs/handoffs/archive/T7_2026-08-13_v3_1_x_authority_bridge_delta_review.md
```

T6 may wire only that path into production and add zero-science positive and
adversarial tests. T6 cannot create the archive and cannot predict or hardcode
its digest. Formal T7 later publishes the exact archive after independently
reviewing the bounded delta. A subsequent Root-T0 dispatch supplies the fresh
archive SHA-256; production independently rehashes it and requires exact
`ADVANCE / NOT_ASSESSED / GREEN` tokens plus all six post-bridge
implementation hashes.

This construction has no self-hash cycle. The future review authenticates the
implementation, while the later dispatch authenticates the review.

## Hard boundaries

- No WolframKernel, solver, sentinel, official run, dispatch or evidence root.
- No change to formula, threshold, domain, precision, graph, overlay,
  scientific input identity or solver behavior.
- No change to the WLS, core numerical module, CLI or protected radial files.
- No reuse of predecessor, failed-root or sentinel science.
- No V3.2 and no global GREEN.

Formal T7 package review is required before T6 implementation. Formal T7
delta-only verification is required after T6. Only an identity-bound
`ADVANCE` from that distinct bridge gate permits Root T0 to create the one-use
35-call sentinel dispatch.
