# Formal T7 prompt — V3.1-X authority-bridge package review

Use only in formal T7 task `019f5ed1-b421-7ec2-9bac-8d134855a1ed`.

Root T0 will supply the exact SHA-256 of
`configs/phase6_v3_1_x_authority_bridge_package.json`. Read that canonical
package, every bound member, `docs/review_gate_liveness_protocol.md`, and the
source V3.1-X implementation reviews completely.

This is a distinct T0-adjudicated control-plane gate, not repair cycle 3 and
not a scientific review. Independently determine whether the package:

- preserves every closed scientific/numerical implementation item and all
  protected/source identities;
- restricts T6 to the exact three paths and one fixed future review path;
- has a non-circular authority graph: T7 review bytes bind final
  implementation hashes, while a later T0 dispatch binds the review digest;
- rejects predecessor YELLOW/ESCALATE, arbitrary authority surfaces and
  replay;
- requires zero-science implementation and adversarial testing;
- contains no dispatch, numerical run, V3.2 or global-GREEN authorization.

If ready, publish a distinct UTC archive and update `T7_current.md` with:

```text
ADVANCE_DECISION: ADVANCE
CLAIM_STATUS: NOT_ASSESSED
GATE_LABEL: ACCEPT GREEN / V3.1-X AUTHORITY-BRIDGE PACKAGE READY FOR T6
```

Otherwise use the liveness protocol's complete finding schema. Do not edit
the package, design, prompts, implementation, tests, status or T0/T4/T6
handoffs. Do not run Wolfram/solver or create dispatch/root. Package GREEN
only authorizes Root T0 to send the unchanged implementation prompt to formal
T6.
