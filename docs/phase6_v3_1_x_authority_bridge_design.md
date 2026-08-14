# Phase 6 V3.1-X implementation-review authority bridge

Gate ID: `phase6_v3_1_x_external_direct_authority_bridge_v1`

Classification: `CONTROL_PLANE_REPAIR` under
`docs/review_gate_liveness_protocol.md`, created by Root-T0 adjudication after
the source implementation gate exhausted repair cycle 2/2.

## Problem

The reviewed V3.1-X implementation is fail-closed, but its production
`IMPLEMENTATION_REVIEW_PATH` names delta recheck 1, whose verdict is
`REPAIR / NOT_ASSESSED`. Delta recheck 2 closed the remaining technical
implementation defects but correctly returned `ESCALATE` because production
cannot accept its own future authority without a separately frozen bridge.

## Exact bounded delta

Only these paths may change:

1. `src/schwgw/validation/phase6_v3_mode_greybody_external_direct_replacement.py`
2. `tests/unit/test_phase6_v3_external_direct.py`
3. `tests/regression/test_phase6_v3_external_direct_publication.py`

The production constant must change from the immutable repair-1 YELLOW path
to exactly:

```text
docs/handoffs/archive/T7_2026-08-13_v3_1_x_authority_bridge_delta_review.md
```

No fallback, environment selector, argv override, alternate path list or live
handoff may be introduced.

## Required tests

Zero-science tests must prove:

- the future path may be absent during T6 preflight;
- a temporary exact-path surrogate containing the required bridge verdict,
  package/source-review identities and all six post-delta implementation
  hashes is accepted by `validate_dispatch`;
- repair-1 YELLOW, delta-recheck-2 ESCALATE, arbitrary path, wrong digest,
  wrong token, missing/current implementation hash, alternate environment,
  wrong argv/cwd/executable/launcher and replay all fail before dispatch
  consumption, root creation or science;
- all previously passed V3.1-X tests, protected identities, exact graphs,
  sentinel budgets, eight-file source closure, lifecycle closure and precision
  witnesses remain unchanged;
- counters remain `Wolfram=0`, `solver=0`, `dispatch=0`, `root=0`.

## Review and dispatch graph

```text
T0 bridge package
  -> formal T7 package ADVANCE
  -> formal T6 exact-three zero-science implementation
  -> formal T7 bridge delta review at the predeclared path
  -> one-use T0 sentinel dispatch binds path + fresh review SHA
  -> V3.1-X sentinel
```

The T7 bridge archive must contain exact case-sensitive tokens:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X AUTHORITY BRIDGE READY FOR ONE-USE SENTINEL DISPATCH
V3.1-X AUTHORITY-BRIDGE
```

It must also bind the bridge package, Root-T0 adjudication, source package,
all three source implementation reviews, and all six post-bridge
implementation hashes. Its digest is supplied only by the later Root-T0
dispatch and is never hardcoded into production.

## Nonclaims

The bridge establishes control-plane reachability only. V3.1-X science stays
`NOT_ASSESSED`; V3.1/V3.1-U stay `FAIL`; no sentinel or official scientific
claim, even-sector external result, full-domain V3, V3.2 or global GREEN is
created.
